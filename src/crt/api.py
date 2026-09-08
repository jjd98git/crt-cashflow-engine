"""Public run API: one scenario in, one ``RunResult`` out (BRIEF section 9).

This is the surface the Streamlit GUI and, later, the AI shell call.  It does not add
any cashflow arithmetic of its own: every dollar in a ``RunResult`` is read off the pool
projection (``crt.pool.projection``) or the waterfall records (``crt.waterfall.engine``),
the WAL and the principal windows come from ``crt.tieout.wal``, and the only sums taken
here are the per-Note and per-tranche lifetime totals, the running (cumulative) tranche
write-downs and the pool totals, which are plain additions of engine cents.  Money stays ``Decimal`` inside ``RunResult``; ``to_frames`` is the single
place where it is converted (to ``str`` or ``float``) and that conversion is display-only.
"""

from __future__ import annotations

import calendar
import csv
import hashlib
import json
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Literal

import polars as pl

from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER, DealTerms
from crt.money import ZERO, round7
from crt.pool.projection import PoolProjection, collection_months_for_payment_date
from crt.scenarios.loader import scenario_as_dict
from crt.scenarios.scenario import Scenario
from crt.tieout.manifest import (
    CONVENTIONS_IN_FORCE,
    ManifestError,
    engine_version,
    git_commit,
    sha256_of,
    utc_timestamp,
)
from crt.tieout.run import (
    APPENDIX_G_PATH,
    DEAL_TERMS_PATH,
    DEFAULT_PROJECT_ROOT,
    REP_LINES_PATH,
    PoolCache,
    TieoutInputs,
    load_inputs,
)
from crt.tieout.wal import principal_window, weighted_average_life
from crt.waterfall.engine import PaymentDateRecord, WaterfallResult, run_waterfall
from crt.waterfall.interest import payment_date

# Inputs hashed into every scenario-run manifest, relative to the project root.
SCENARIO_RUN_INPUT_FILES: tuple[Path, ...] = (
    DEAL_TERMS_PATH,
    REP_LINES_PATH,
    APPENDIX_G_PATH,
    Path("docs/assumptions.csv"),
)
# Names of the tables ``to_frames`` and ``export_csv`` produce, in a fixed order.
TABLE_NAMES: tuple[str, ...] = (
    "pool_months",
    "structure",
    "tranche_allocations",
    "note_cashflows",
    "note_summary",
    "tranche_summary",
    "pool_totals",
)
MANIFEST_FILE_NAME = "manifest.json"
RUN_ID_HEX_LENGTH = 16

MoneyAs = Literal["str", "float"]


class RunApiError(ValueError):
    """The run could not be assembled from the engine output."""


# --------------------------------------------------------------------------------------
# Row types (all money Decimal)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PoolMonthRow:
    """Pool totals of one collection month (spec 01 section 4; spec 00 section 2.1)."""

    month: int
    month_end: date
    payment_date_number: int  # the Payment Date this month feeds (A4)
    balance_begin: Decimal
    scheduled_principal: Decimal
    prepayment: Decimal
    credit_event_amount: Decimal
    interest: Decimal
    balance_end: Decimal


@dataclass(frozen=True)
class StructureRow:
    """One Payment Date of the hypothetical structure (spec 02), with every Reference
    Tranche's Class Notional Amount after the date."""

    payment_date_number: int
    payment_date: date
    is_maturity_date: bool
    maturity_reason: str | None
    stated_principal: Decimal
    credit_event_amount: Decimal
    principal_loss_amount: Decimal
    principal_recovery_amount: Decimal
    tranche_write_down: Decimal
    tranche_write_up: Decimal
    recovery_principal: Decimal
    senior_pct: Decimal
    subordinate_pct: Decimal
    cumulative_net_loss_pct: Decimal
    cumulative_net_loss_threshold: Decimal
    test_minimum_credit_enhancement: bool
    test_cumulative_net_loss: bool
    test_delinquency: bool
    test_class_a1_cumulative_net_loss: bool
    senior_reduction: Decimal
    class_a1_reduction: Decimal
    subordinate_reduction: Decimal
    class_a1_additional_reduction: Decimal
    offered_reference_tranche_pct: Decimal
    supplemental_reduction: Decimal
    pool_upb_end: Decimal
    # Every dict below is keyed by TRANCHE_ORDER and read straight off the engine's
    # PaymentDateRecord / StepResult objects (nothing is recomputed here).
    balances_before: dict[str, Decimal]  # Class Notional Amounts immediately prior
    # Principal allocated on the Payment Date: Steps 2-4 (Senior, Subordinate and
    # Supplemental Reduction Amounts) plus the Maturity Date 100 % payment (spec 02
    # sections 6-9).
    principal_allocated: dict[str, Decimal]
    write_down_allocated: dict[str, Decimal]  # Step 1 Tranche Write-down Amount
    write_up_allocated: dict[str, Decimal]  # Step 1 Tranche Write-up Amount
    # Increases of a Class Notional Amount on the Payment Date.  Only A-H ever grows: the
    # Supplemental Senior Increase Amount (spec 02 section 8), the A-H increase on
    # write-down (section 5) and the Stated Principal clause (e) floor excess (Q19); every
    # other tranche is zero.  Needed for the per-tranche identity below.
    increase_allocated: dict[str, Decimal]
    # Running sum of write_down_allocated over Payment Dates 1..n (a Decimal addition).
    cumulative_write_down: dict[str, Decimal]
    balances_after: dict[str, Decimal]


@dataclass(frozen=True)
class TrancheAllocationRow:
    """What one Reference Tranche received or lost on one Payment Date (the long form of
    the ``StructureRow`` dicts, one row per Payment Date and tranche).  Per row:
    ``balance_before - principal - write_down + write_up + increase == balance_after``."""

    payment_date_number: int
    payment_date: date
    tranche: str
    balance_before: Decimal
    principal: Decimal
    write_down: Decimal
    write_up: Decimal
    increase: Decimal
    cumulative_write_down: Decimal
    balance_after: Decimal


@dataclass(frozen=True)
class NoteCashflowRow:
    """What one Original Note receives / loses on one Payment Date (spec 02 section 10)."""

    note: str
    payment_date_number: int
    payment_date: date
    balance_before: Decimal
    coupon: Decimal
    accrual_days: int
    interest: Decimal
    principal_paid: Decimal
    write_down: Decimal
    write_up: Decimal
    balance_after: Decimal


@dataclass(frozen=True)
class NoteSummary:
    """Lifetime figures of one Original Note."""

    note: str
    original_balance: Decimal
    wal_years: Decimal | None  # A9 / A10, unrounded (R6); None if never reduced
    first_principal_payment_date_number: int | None
    first_principal_payment_date: date | None
    last_principal_payment_date_number: int | None
    last_principal_payment_date: date | None
    total_principal: Decimal
    total_interest: Decimal
    total_write_downs: Decimal
    total_write_ups: Decimal
    final_balance: Decimal


@dataclass(frozen=True)
class TrancheSummary:
    """Lifetime figures of one Reference Tranche (plain sums of the allocation rows)."""

    tranche: str
    initial_class_notional_amount: Decimal
    initial_pct_of_pool: Decimal  # initial notional / Cut-off Date Balance, round7 (R3)
    total_principal: Decimal
    total_write_downs: Decimal
    total_write_ups: Decimal
    total_increases: Decimal
    final_balance: Decimal


@dataclass(frozen=True)
class PoolTotals:
    """Pool totals over the collection months feeding Payment Dates 1..Maturity Date
    (nothing after the Maturity Date is computed, spec 00 section 2.2)."""

    cut_off_date_balance: Decimal
    first_month: int
    last_month: int
    last_month_end: date
    total_scheduled_principal: Decimal
    total_prepayment: Decimal
    total_credit_event_amount: Decimal
    total_interest: Decimal
    ending_balance: Decimal
    maturity_payment_date_number: int
    maturity_payment_date: date
    maturity_reason: str


@dataclass(frozen=True)
class RunManifest:
    """Provenance of one scenario run (BRIEF section 2: deterministic, reproducible)."""

    run_id: str  # sha256 of everything below except the timestamp, first 16 hex digits
    engine_version: str
    git_commit: str | None  # None when the project is not a git checkout
    timestamp_utc: str
    decimal_precision: int
    input_sha256: dict[str, str]
    conventions_in_force: tuple[str, ...]
    scenario_name: str
    scenario_source: str | None  # the scenario file, if the scenario came from one
    scenario: dict[str, Any]
    maturity_payment_date_number: int
    maturity_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "engine_version": self.engine_version,
            "git_commit": self.git_commit,
            "timestamp_utc": self.timestamp_utc,
            "decimal_precision": self.decimal_precision,
            "input_sha256": dict(self.input_sha256),
            "conventions_in_force": list(self.conventions_in_force),
            "scenario_name": self.scenario_name,
            "scenario_source": self.scenario_source,
            "scenario": dict(self.scenario),
            "maturity_payment_date_number": self.maturity_payment_date_number,
            "maturity_reason": self.maturity_reason,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


# --------------------------------------------------------------------------------------
# The result
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RunResult:
    manifest: RunManifest
    scenario: Scenario
    deal: DealTerms  # the deal terms the run used (the exporter cites them by register id)
    pool_months: tuple[PoolMonthRow, ...]
    structure: tuple[StructureRow, ...]
    tranche_allocations: tuple[TrancheAllocationRow, ...]
    note_cashflows: tuple[NoteCashflowRow, ...]
    note_summaries: tuple[NoteSummary, ...]
    tranche_summaries: tuple[TrancheSummary, ...]
    pool_totals: PoolTotals
    waterfall: WaterfallResult
    pool: PoolProjection

    def summary_for(self, note: str) -> NoteSummary:
        for summary in self.note_summaries:
            if summary.note == note:
                return summary
        raise RunApiError(f"no summary for Note {note!r}")

    def tranche_summary_for(self, tranche: str) -> TrancheSummary:
        for summary in self.tranche_summaries:
            if summary.tranche == tranche:
                return summary
        raise RunApiError(f"no summary for Reference Tranche {tranche!r}")

    def to_frames(self, *, money_as: MoneyAs = "str") -> dict[str, pl.DataFrame]:
        """DISPLAY ONLY.  One polars DataFrame per table in ``TABLE_NAMES``.  Every
        ``Decimal`` is converted here and nowhere else: ``"str"`` keeps the exact digits
        (``format(x, "f")``), ``"float"`` is for charts and is lossy.  Nothing returned
        from here may be fed back into a calculation."""
        return {
            # infer_schema_length=None: scan every row, because a column such as
            # maturity_reason is None on every Payment Date but the last.
            name: pl.DataFrame(
                [_display_row(row, money_as) for row in self._rows(name)],
                orient="row",
                infer_schema_length=None,
            )
            if self._rows(name)
            else pl.DataFrame()
            for name in TABLE_NAMES
        }

    def _rows(self, table: str) -> list[dict[str, Any]]:
        if table == "pool_months":
            return [_as_flat_dict(row) for row in self.pool_months]
        if table == "structure":
            return [_structure_row_dict(row) for row in self.structure]
        if table == "tranche_allocations":
            return [_as_flat_dict(row) for row in self.tranche_allocations]
        if table == "note_cashflows":
            return [_as_flat_dict(row) for row in self.note_cashflows]
        if table == "note_summary":
            return [_as_flat_dict(row) for row in self.note_summaries]
        if table == "tranche_summary":
            return [_as_flat_dict(row) for row in self.tranche_summaries]
        if table == "pool_totals":
            return [_as_flat_dict(self.pool_totals)]
        raise RunApiError(f"unknown table {table!r}; expected one of {TABLE_NAMES}")


def _as_flat_dict(row: Any) -> dict[str, Any]:
    return dict(vars(row))


# The per-tranche dicts of a StructureRow; the structure table keeps only balances_after
# (expanded to one column per tranche) and the rest is the tranche_allocations table.
_STRUCTURE_ROW_TRANCHE_DICTS: tuple[str, ...] = (
    "balances_before",
    "principal_allocated",
    "write_down_allocated",
    "write_up_allocated",
    "increase_allocated",
    "cumulative_write_down",
)


def _structure_row_dict(row: StructureRow) -> dict[str, Any]:
    flat = _as_flat_dict(row)
    for name in _STRUCTURE_ROW_TRANCHE_DICTS:
        flat.pop(name)
    balances = flat.pop("balances_after")
    for tranche in TRANCHE_ORDER:
        flat[f"balance_after_{tranche}"] = balances[tranche]
    return flat


def _display_value(value: Any, money_as: MoneyAs) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f") if money_as == "str" else float(value)
    return value


def _display_row(row: dict[str, Any], money_as: MoneyAs) -> dict[str, Any]:
    return {key: _display_value(value, money_as) for key, value in row.items()}


# --------------------------------------------------------------------------------------
# Building the tables from the engine output
# --------------------------------------------------------------------------------------


def month_end_date(cut_off_date: date, month: int) -> date:
    """Last calendar day of collection month ``m`` (``m = 1`` is the month after the
    Cut-off Date month; spec 00 section 2.1, Modeling Assumptions (f), (g))."""
    if month < 1:
        raise RunApiError(f"collection month {month} < 1")
    months_after = cut_off_date.month - 1 + month
    year = cut_off_date.year + months_after // 12
    month_of_year = months_after % 12 + 1
    return date(year, month_of_year, calendar.monthrange(year, month_of_year)[1])


def _feeding_payment_date_by_month(last_payment_date_number: int) -> dict[int, int]:
    mapping: dict[int, int] = {}
    for n in range(1, last_payment_date_number + 1):
        for month in collection_months_for_payment_date(n):
            mapping[month] = n
    return mapping


def _pool_month_rows(
    pool: PoolProjection, deal: DealTerms, maturity_payment_date_number: int
) -> tuple[PoolMonthRow, ...]:
    feeding = _feeding_payment_date_by_month(maturity_payment_date_number)
    last_month = max(feeding)
    rows: list[PoolMonthRow] = []
    previous_end = deal.cut_off_date_balance  # m = 0 is the Cut-off Date state
    for pool_month in pool.months[:last_month]:
        index = pool_month.month - 1
        balance_begin = sum((line[index].balance_begin for line in pool.rep_line_months), ZERO)
        if balance_begin != previous_end:
            raise RunApiError(
                f"collection month {pool_month.month}: rep-line beginning balances sum to "
                f"{balance_begin}, not the prior month-end UPB {previous_end}"
            )
        rows.append(
            PoolMonthRow(
                month=pool_month.month,
                month_end=month_end_date(deal.cut_off_date, pool_month.month),
                payment_date_number=feeding[pool_month.month],
                balance_begin=balance_begin,
                scheduled_principal=pool_month.scheduled_principal,
                prepayment=pool_month.prepayment,
                credit_event_amount=pool_month.credit_event_amount,
                interest=pool_month.interest,
                balance_end=pool_month.upb_end,
            )
        )
        previous_end = pool_month.upb_end
    return tuple(rows)


def _principal_allocated(record: PaymentDateRecord) -> dict[str, Decimal]:
    """Principal allocated to each tranche on the Payment Date: the Step 2-4 amounts
    recorded by the engine, or the 100 % Maturity Date payment (spec 02 section 9).  On
    the Maturity Date the engine records no Step 2-4 results, and before it the maturity
    payment dict is all zeros, so the two never overlap."""
    n = record.payment_date_number
    steps = (record.senior_step, record.subordinate_step, record.supplemental_step)
    if record.is_maturity_date:
        if any(step is not None for step in steps):
            raise RunApiError(f"Payment Date {n}: Maturity Date with Step 2-4 results")
        return {name: record.maturity_payment_by_tranche[name] for name in TRANCHE_ORDER}
    if any(step is None for step in steps):
        raise RunApiError(f"Payment Date {n}: Step 2-4 results missing before the Maturity Date")
    return {
        name: sum((step.allocated(name) for step in steps if step is not None), ZERO)
        + record.maturity_payment_by_tranche[name]
        for name in TRANCHE_ORDER
    }


def _increase_allocated(record: PaymentDateRecord) -> dict[str, Decimal]:
    """Class Notional Amount increases on the Payment Date, all of which go to A-H: the
    Supplemental Senior Increase Amount (equal to the Supplemental Reduction Amount, spec 02
    section 8), the A-H increase on write-down (section 5) and the Stated Principal clause
    (e) floor excess (Q19).  Every other tranche is zero."""
    increases = {name: ZERO for name in TRANCHE_ORDER}
    increases["A-H"] = (
        record.supplemental_reduction
        + record.a_h_increase_on_write_down
        + record.pool.stated_principal_floor_excess_to_a_h
    )
    return increases


def _structure_rows(waterfall: WaterfallResult) -> tuple[StructureRow, ...]:
    rows: list[StructureRow] = []
    cumulative_write_down = {name: ZERO for name in TRANCHE_ORDER}
    for record in waterfall.records:
        n = record.payment_date_number
        principal = _principal_allocated(record)
        write_down = {name: record.write_down_step.allocated(name) for name in TRANCHE_ORDER}
        write_up = {name: record.write_up_step.allocated(name) for name in TRANCHE_ORDER}
        increase = _increase_allocated(record)
        for name in TRANCHE_ORDER:
            # Spec 00 section 3.3 per tranche: the balance moves only by what the engine
            # allocated to it on this Payment Date.
            expected_after = (
                record.balances_before[name]
                - principal[name]
                - write_down[name]
                + write_up[name]
                + increase[name]
            )
            if expected_after != record.balances_after[name]:
                raise RunApiError(
                    f"Payment Date {n}: {name} before {record.balances_before[name]} - principal "
                    f"{principal[name]} - write-down {write_down[name]} + write-up "
                    f"{write_up[name]} + increase {increase[name]} = {expected_after} != after "
                    f"{record.balances_after[name]}"
                )
            cumulative_write_down[name] += write_down[name]
        rows.append(
            StructureRow(
                payment_date_number=record.payment_date_number,
                payment_date=record.payment_date,
                is_maturity_date=record.is_maturity_date,
                maturity_reason=record.maturity_reason,
                stated_principal=record.pool.stated_principal,
                credit_event_amount=record.pool.credit_event_amount,
                principal_loss_amount=record.principal_loss_amount,
                principal_recovery_amount=record.principal_recovery_amount,
                tranche_write_down=record.tranche_write_down,
                tranche_write_up=record.tranche_write_up,
                recovery_principal=record.recovery_principal,
                senior_pct=record.senior_pct,
                subordinate_pct=record.subordinate_pct,
                cumulative_net_loss_pct=record.cumulative_net_loss_pct,
                cumulative_net_loss_threshold=record.cumulative_net_loss_threshold,
                test_minimum_credit_enhancement=record.tests.minimum_credit_enhancement,
                test_cumulative_net_loss=record.tests.cumulative_net_loss,
                test_delinquency=record.tests.delinquency,
                test_class_a1_cumulative_net_loss=record.tests.class_a1_cumulative_net_loss,
                senior_reduction=record.senior_reduction,
                class_a1_reduction=record.class_a1_reduction,
                subordinate_reduction=record.subordinate_reduction,
                class_a1_additional_reduction=record.class_a1_additional_reduction,
                offered_reference_tranche_pct=record.offered_reference_tranche_pct,
                supplemental_reduction=record.supplemental_reduction,
                pool_upb_end=record.pool.upb_end,
                balances_before={name: record.balances_before[name] for name in TRANCHE_ORDER},
                principal_allocated=principal,
                write_down_allocated=write_down,
                write_up_allocated=write_up,
                increase_allocated=increase,
                cumulative_write_down=dict(cumulative_write_down),
                balances_after={name: record.balances_after[name] for name in TRANCHE_ORDER},
            )
        )
    return tuple(rows)


def _tranche_allocation_rows(
    structure: tuple[StructureRow, ...],
) -> tuple[TrancheAllocationRow, ...]:
    rows: list[TrancheAllocationRow] = []
    for row in structure:
        for tranche in TRANCHE_ORDER:
            rows.append(
                TrancheAllocationRow(
                    payment_date_number=row.payment_date_number,
                    payment_date=row.payment_date,
                    tranche=tranche,
                    balance_before=row.balances_before[tranche],
                    principal=row.principal_allocated[tranche],
                    write_down=row.write_down_allocated[tranche],
                    write_up=row.write_up_allocated[tranche],
                    increase=row.increase_allocated[tranche],
                    cumulative_write_down=row.cumulative_write_down[tranche],
                    balance_after=row.balances_after[tranche],
                )
            )
    return tuple(rows)


def _tranche_summaries(
    structure: tuple[StructureRow, ...], deal: DealTerms
) -> tuple[TrancheSummary, ...]:
    summaries: list[TrancheSummary] = []
    for tranche in TRANCHE_ORDER:
        initial = deal.initial_class_notional_amounts[tranche]  # P24-P31, P3-P6
        summaries.append(
            TrancheSummary(
                tranche=tranche,
                initial_class_notional_amount=initial,
                # A display ratio (the workbook's README legend), rounded per R3 (P51).
                initial_pct_of_pool=round7(initial / deal.cut_off_date_balance),  # P10
                total_principal=sum((r.principal_allocated[tranche] for r in structure), ZERO),
                total_write_downs=sum((r.write_down_allocated[tranche] for r in structure), ZERO),
                total_write_ups=sum((r.write_up_allocated[tranche] for r in structure), ZERO),
                total_increases=sum((r.increase_allocated[tranche] for r in structure), ZERO),
                final_balance=structure[-1].balances_after[tranche],
            )
        )
    return tuple(summaries)


def _note_cashflow_rows(waterfall: WaterfallResult) -> tuple[NoteCashflowRow, ...]:
    rows: list[NoteCashflowRow] = []
    for note in NOTE_CLASSES:
        for record in waterfall.records:
            cashflow = record.notes[note]
            rows.append(
                NoteCashflowRow(
                    note=note,
                    payment_date_number=record.payment_date_number,
                    payment_date=record.payment_date,
                    balance_before=cashflow.balance_before,
                    coupon=cashflow.coupon,
                    accrual_days=cashflow.accrual_days,
                    interest=cashflow.interest_payment,
                    principal_paid=cashflow.principal_paid,
                    write_down=cashflow.write_down,
                    write_up=cashflow.write_up,
                    balance_after=cashflow.balance_after,
                )
            )
    return tuple(rows)


def _note_summaries(waterfall: WaterfallResult, deal: DealTerms) -> tuple[NoteSummary, ...]:
    summaries: list[NoteSummary] = []
    for note in NOTE_CLASSES:
        cashflows = [record.notes[note] for record in waterfall.records]
        window = principal_window(waterfall, note)
        first_n = window[0] if window is not None else None
        last_n = window[1] if window is not None else None
        summaries.append(
            NoteSummary(
                note=note,
                original_balance=deal.notes[note].original_class_principal_balance,
                wal_years=weighted_average_life(waterfall, note),
                first_principal_payment_date_number=first_n,
                first_principal_payment_date=(
                    payment_date(first_n, deal.first_payment_date) if first_n else None
                ),
                last_principal_payment_date_number=last_n,
                last_principal_payment_date=(
                    payment_date(last_n, deal.first_payment_date) if last_n else None
                ),
                total_principal=sum((c.principal_paid for c in cashflows), ZERO),
                total_interest=sum((c.interest_payment for c in cashflows), ZERO),
                total_write_downs=sum((c.write_down for c in cashflows), ZERO),
                total_write_ups=sum((c.write_up for c in cashflows), ZERO),
                final_balance=cashflows[-1].balance_after,
            )
        )
    return tuple(summaries)


def _pool_totals(
    pool_months: tuple[PoolMonthRow, ...], deal: DealTerms, waterfall: WaterfallResult
) -> PoolTotals:
    last_record = waterfall.records[-1]
    if last_record.maturity_reason is None:
        raise RunApiError("the waterfall's last record is not a Maturity Date")
    return PoolTotals(
        cut_off_date_balance=deal.cut_off_date_balance,
        first_month=pool_months[0].month,
        last_month=pool_months[-1].month,
        last_month_end=pool_months[-1].month_end,
        total_scheduled_principal=sum((m.scheduled_principal for m in pool_months), ZERO),
        total_prepayment=sum((m.prepayment for m in pool_months), ZERO),
        total_credit_event_amount=sum((m.credit_event_amount for m in pool_months), ZERO),
        total_interest=sum((m.interest for m in pool_months), ZERO),
        ending_balance=pool_months[-1].balance_end,
        maturity_payment_date_number=last_record.payment_date_number,
        maturity_payment_date=last_record.payment_date,
        maturity_reason=last_record.maturity_reason,
    )


def _run_id(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:RUN_ID_HEX_LENGTH]


def _manifest(
    *,
    root: Path,
    scenario: Scenario,
    scenario_name: str,
    scenario_source: Path | None,
    waterfall: WaterfallResult,
    timestamp: str,
) -> RunManifest:
    input_sha256 = {path.as_posix(): sha256_of(root / path) for path in SCENARIO_RUN_INPUT_FILES}
    if scenario_source is not None:
        input_sha256[_relative_or_absolute(scenario_source, root)] = sha256_of(scenario_source)
    try:
        commit: str | None = git_commit(root)
    except ManifestError:
        commit = None
    version = engine_version(root)
    scenario_dict = scenario_as_dict(scenario)
    last = waterfall.records[-1]
    if last.maturity_reason is None:
        raise RunApiError("the waterfall's last record is not a Maturity Date")
    run_id = _run_id(
        {
            "engine_version": version,
            "git_commit": commit,
            "input_sha256": input_sha256,
            "scenario": scenario_dict,
            "decimal_precision": getcontext().prec,
        }
    )
    return RunManifest(
        run_id=run_id,
        engine_version=version,
        git_commit=commit,
        timestamp_utc=timestamp,
        decimal_precision=getcontext().prec,
        input_sha256=input_sha256,
        conventions_in_force=CONVENTIONS_IN_FORCE,
        scenario_name=scenario_name,
        scenario_source=(
            None if scenario_source is None else _relative_or_absolute(scenario_source, root)
        ),
        scenario=scenario_dict,
        maturity_payment_date_number=last.payment_date_number,
        maturity_reason=last.maturity_reason,
    )


def _relative_or_absolute(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


# --------------------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------------------


def run_scenario(
    scenario: Scenario,
    deal: DealTerms | None = None,
    *,
    project_root: Path = DEFAULT_PROJECT_ROOT,
    inputs: TieoutInputs | None = None,
    pool_cache: PoolCache | None = None,
    scenario_name: str = "ad-hoc",
    scenario_source: Path | None = None,
    timestamp: str | None = None,
) -> RunResult:
    """Run one scenario end to end.

    ``deal`` defaults to the reference deal loaded from ``project_root`` (the only deal
    the v1 engine knows); passing one substitutes it for the loaded terms.  ``inputs`` and
    ``pool_cache`` let a caller (the GUI) reuse loaded inputs and pool projections across
    runs.  ``timestamp`` is for tests only; production runs stamp the current UTC time.
    """
    if inputs is None:
        inputs = load_inputs(project_root)
    if deal is not None and deal is not inputs.deal:
        inputs = replace(inputs, deal=deal)
    if pool_cache is None:
        pool_cache = PoolCache(inputs)
    pool = pool_cache.get(scenario.cpr, scenario.cer)
    waterfall = run_waterfall(pool, inputs.deal, inputs.appendix_g, scenario)

    pool_months = _pool_month_rows(pool, inputs.deal, waterfall.maturity_payment_date_number)
    structure = _structure_rows(waterfall)
    manifest = _manifest(
        root=project_root,
        scenario=scenario,
        scenario_name=scenario_name,
        scenario_source=scenario_source,
        waterfall=waterfall,
        timestamp=timestamp if timestamp is not None else utc_timestamp(),
    )
    return RunResult(
        manifest=manifest,
        scenario=scenario,
        deal=inputs.deal,
        pool_months=pool_months,
        structure=structure,
        tranche_allocations=_tranche_allocation_rows(structure),
        note_cashflows=_note_cashflow_rows(waterfall),
        note_summaries=_note_summaries(waterfall, inputs.deal),
        tranche_summaries=_tranche_summaries(structure, inputs.deal),
        pool_totals=_pool_totals(pool_months, inputs.deal, waterfall),
        waterfall=waterfall,
        pool=pool,
    )


def _csv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def export_csv(result: RunResult, out_dir: Path) -> tuple[Path, ...]:
    """Write one CSV per table plus ``manifest.json`` into ``out_dir``; return the paths.

    Byte-deterministic for the same inputs: fixed column order, ``\\n`` line endings,
    exact Decimal digits, and the manifest sorted by key.  Only the manifest's
    ``timestamp_utc`` differs between two runs of the same scenario."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name in TABLE_NAMES:
        rows = result._rows(name)
        path = out_dir / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            if rows:
                writer.writerow(list(rows[0]))
                for row in rows:
                    writer.writerow([_csv_cell(value) for value in row.values()])
        written.append(path)
    manifest_path = out_dir / MANIFEST_FILE_NAME
    manifest_path.write_text(result.manifest.to_json(), encoding="utf-8", newline="\n")
    written.append(manifest_path)
    return tuple(written)


# --------------------------------------------------------------------------------------
# Comparing two runs (the GUI's Compare mode; differences computed here, in Decimal)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SummaryDifference:
    note: str
    metric: str
    a: Decimal | int | None
    b: Decimal | int | None
    b_minus_a: Decimal | int | None


COMPARED_METRICS: tuple[str, ...] = (
    "wal_years",
    "first_principal_payment_date_number",
    "last_principal_payment_date_number",
    "total_principal",
    "total_interest",
    "total_write_downs",
    "final_balance",
)


def compare_summaries(a: RunResult, b: RunResult) -> tuple[SummaryDifference, ...]:
    """Per-Note differences ``b - a`` of the summary metrics (``None`` when either side
    has no value, e.g. a Note that never received principal)."""
    differences: list[SummaryDifference] = []
    for note in NOTE_CLASSES:
        summary_a = a.summary_for(note)
        summary_b = b.summary_for(note)
        for metric in COMPARED_METRICS:
            value_a = getattr(summary_a, metric)
            value_b = getattr(summary_b, metric)
            delta = None if value_a is None or value_b is None else value_b - value_a
            differences.append(
                SummaryDifference(note=note, metric=metric, a=value_a, b=value_b, b_minus_a=delta)
            )
    return tuple(differences)
