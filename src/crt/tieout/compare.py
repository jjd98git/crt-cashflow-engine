"""Comparisons of spec ``03-tieout.md`` sections 3.1-3.5 with the A13 criteria and the
BRIEF section 7 tolerances.  Every model number is the engine's unrounded value; every
PPM number is the transcribed string parsed exactly.  ``diff`` is model minus PPM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from crt.io.deal_terms import NOTE_CLASSES, DealTerms
from crt.io.ppm_tables import (
    CreditEventSensitivityCell,
    DecliningBalanceCell,
    DecliningBalanceWalRow,
    Table1Row,
    WalCell,
)
from crt.money import HUNDRED, ZERO, round_half_up
from crt.scenarios.grid import PRICING_SPEED_CPR_PCT
from crt.tieout.wal import balance_after_payment_date, principal_window, weighted_average_life
from crt.waterfall.engine import WaterfallResult
from crt.waterfall.interest import payment_date

# BRIEF section 7 tolerances.
WAL_TOLERANCE_YEARS = Decimal("0.02")
WAL_MILESTONE_TOLERANCE_YEARS = Decimal("0.10")
PERCENTAGE_POINT_TOLERANCE = Decimal("0.25")
# A13: printed precision of the two percentage families.
DECLINING_BALANCE_PRINTED_PLACES = 0  # T28: whole percent
CREDIT_EVENT_SENSITIVITY_PRINTED_PLACES = 1  # printed to 0.1 %

GridKey = tuple[Decimal, Decimal, bool]  # (CPR %, CER %, early redemption)


class TieoutError(ValueError):
    """The tie-out could not be assembled (missing scenario, unparseable row label)."""


def grid_key(cpr_pct: Decimal, cer_pct: Decimal, early_redemption: bool) -> GridKey:
    """Normalise the axis values so that "0" and "0.00" address the same run."""
    return (Decimal(cpr_pct).normalize(), Decimal(cer_pct).normalize(), early_redemption)


def _run_for(runs: dict[GridKey, WaterfallResult], cpr: Decimal, cer: Decimal, early: bool) -> WaterfallResult:
    key = grid_key(cpr, cer, early)
    if key not in runs:
        raise TieoutError(f"no waterfall run for CPR {cpr} %, CER {cer} %, early redemption {early}")
    return runs[key]


@dataclass(frozen=True)
class WindowResult:
    note: str
    model_first: int | None
    model_last: int | None
    ppm_first: int
    ppm_last: int

    @property
    def passes(self) -> bool:
        return (self.model_first, self.model_last) == (self.ppm_first, self.ppm_last)


@dataclass(frozen=True)
class WalCellResult:
    note: str
    early_redemption: bool
    cpr_pct: Decimal
    cer_pct: Decimal
    model: Decimal | None
    printed: str
    ppm: Decimal

    @property
    def diff(self) -> Decimal | None:
        return None if self.model is None else self.model - self.ppm

    @property
    def within_tolerance(self) -> bool:
        return self.diff is not None and abs(self.diff) <= WAL_TOLERANCE_YEARS

    @property
    def within_milestone(self) -> bool:
        return self.diff is not None and abs(self.diff) <= WAL_MILESTONE_TOLERANCE_YEARS


@dataclass(frozen=True)
class DecliningBalanceResult:
    note: str
    cpr_pct: Decimal
    row_label: str
    payment_date_number: int
    model_pct: Decimal
    printed: str
    ppm: Decimal

    @property
    def diff(self) -> Decimal:
        return self.model_pct - self.ppm

    @property
    def round_match(self) -> bool:
        return round_half_up(self.model_pct, DECLINING_BALANCE_PRINTED_PLACES) == self.ppm  # A13

    @property
    def within_brief_tolerance(self) -> bool:
        return abs(self.diff) <= PERCENTAGE_POINT_TOLERANCE


@dataclass(frozen=True)
class DecliningBalanceWalResult:
    note: str
    cpr_pct: Decimal
    early_redemption: bool
    model: Decimal | None
    printed: str
    ppm: Decimal

    @property
    def diff(self) -> Decimal | None:
        return None if self.model is None else self.model - self.ppm

    @property
    def within_tolerance(self) -> bool:
        return self.diff is not None and abs(self.diff) <= WAL_TOLERANCE_YEARS


@dataclass(frozen=True)
class WindowBandResult:
    """Spec 03 section 2 secondary check: the last principal Payment Date lies in the
    twelve-month band ending at the first row printed 0 and after the last row > 0."""

    note: str
    cpr_pct: Decimal
    model_last: int | None
    after_payment_date: int
    on_or_before_payment_date: int

    @property
    def passes(self) -> bool:
        return (
            self.model_last is not None
            and self.after_payment_date < self.model_last <= self.on_or_before_payment_date
        )


@dataclass(frozen=True)
class CreditEventSensitivityResult:
    early_redemption: bool
    cer_pct: Decimal
    cpr_pct: Decimal
    model_pct: Decimal
    printed: str
    ppm: Decimal

    @property
    def diff(self) -> Decimal:
        return self.model_pct - self.ppm

    @property
    def round_match(self) -> bool:
        return round_half_up(self.model_pct, CREDIT_EVENT_SENSITIVITY_PRINTED_PLACES) == self.ppm

    @property
    def within_brief_tolerance(self) -> bool:
        return abs(self.diff) <= PERCENTAGE_POINT_TOLERANCE


def compare_table1_windows(
    runs: dict[GridKey, WaterfallResult], table1: dict[str, Table1Row]
) -> tuple[WindowResult, ...]:
    """Section 3.3: Table 1 windows at 10 % CPR, CER 0, early redemption on (T2, T38)."""
    run = _run_for(runs, PRICING_SPEED_CPR_PCT, ZERO, True)
    results: list[WindowResult] = []
    for note in NOTE_CLASSES:
        window = principal_window(run, note)
        first, last = table1[note].expected_principal_window
        results.append(
            WindowResult(
                note=note,
                model_first=None if window is None else window[0],
                model_last=None if window is None else window[1],
                ppm_first=first,
                ppm_last=last,
            )
        )
    return tuple(results)


def compare_wal_cells(
    runs: dict[GridKey, WaterfallResult], cells: tuple[WalCell, ...]
) -> tuple[WalCellResult, ...]:
    """Sections 3.2 and 3.4: every RM = 0 WAL cell of the four Original Notes."""
    results: list[WalCellResult] = []
    for cell in cells:
        if cell.rm_pct != ZERO:
            continue  # RM > 0 rows are out of scope (spec 00 section 5)
        run = _run_for(runs, cell.cpr_pct, cell.cer_pct, cell.early_redemption)
        results.append(
            WalCellResult(
                note=cell.note_class,
                early_redemption=cell.early_redemption,
                cpr_pct=cell.cpr_pct,
                cer_pct=cell.cer_pct,
                model=weighted_average_life(run, cell.note_class),
                printed=cell.printed,
                ppm=cell.wal_years,
            )
        )
    return tuple(results)


_ROW_LABEL = re.compile(r"^February 25, (\d{4})( and thereafter)?$")


def declining_balance_payment_date_number(row_label: str, deal: DealTerms) -> int:
    """"February 25, 2026 + k" -> Payment Date 12 k (spec 03 section 3.1)."""
    match = _ROW_LABEL.match(row_label)
    if match is None:
        raise TieoutError(f"Declining Balances row label {row_label!r} is not a February 25 date")
    year = int(match.group(1))
    k = year - deal.closing_date.year
    n = 12 * k
    if n < 1 or payment_date(n, deal.first_payment_date) != date(year, 2, 25):
        raise TieoutError(f"row label {row_label!r} does not map to a Payment Date")
    return n


def compare_declining_balances(
    runs: dict[GridKey, WaterfallResult],
    cells: tuple[DecliningBalanceCell, ...],
    deal: DealTerms,
) -> tuple[DecliningBalanceResult, ...]:
    """Section 3.1: CER 0, early redemption off; model = 100 x CPB after PD 12k / original.
    The Closing Date row is 100 by construction and is not a cell."""
    results: list[DecliningBalanceResult] = []
    for cell in cells:
        if cell.row_label == "Closing Date":
            continue
        n = declining_balance_payment_date_number(cell.row_label, deal)
        run = _run_for(runs, cell.cpr_pct, ZERO, False)
        original = deal.notes[cell.note_class].original_class_principal_balance
        balance = balance_after_payment_date(run, cell.note_class, n)
        results.append(
            DecliningBalanceResult(
                note=cell.note_class,
                cpr_pct=cell.cpr_pct,
                row_label=cell.row_label,
                payment_date_number=n,
                model_pct=HUNDRED * balance / original,
                printed=cell.printed,
                ppm=cell.pct_of_original_balance,
            )
        )
    return tuple(results)


def compare_declining_balance_wal_rows(
    runs: dict[GridKey, WaterfallResult], rows: tuple[DecliningBalanceWalRow, ...]
) -> tuple[DecliningBalanceWalResult, ...]:
    """The two WAL rows printed under each Declining Balances table (same targets as 3.2)."""
    results: list[DecliningBalanceWalResult] = []
    for row in rows:
        run = _run_for(runs, row.cpr_pct, ZERO, row.early_redemption)
        results.append(
            DecliningBalanceWalResult(
                note=row.note_class,
                cpr_pct=row.cpr_pct,
                early_redemption=row.early_redemption,
                model=weighted_average_life(run, row.note_class),
                printed=row.printed,
                ppm=row.wal_years,
            )
        )
    return tuple(results)


def compare_window_bands(
    runs: dict[GridKey, WaterfallResult],
    cells: tuple[DecliningBalanceCell, ...],
    deal: DealTerms,
) -> tuple[WindowBandResult, ...]:
    """Section 2 secondary check for every (Note, CPR) of the Declining Balances tables."""
    by_key: dict[tuple[str, Decimal], list[DecliningBalanceCell]] = {}
    for cell in cells:
        by_key.setdefault((cell.note_class, cell.cpr_pct), []).append(cell)
    results: list[WindowBandResult] = []
    for (note, cpr), group in by_key.items():
        last_positive = 0  # the Closing Date row (100 %) is Payment Date 0
        first_zero: int | None = None
        for cell in group:
            if cell.row_label == "Closing Date":
                continue
            n = declining_balance_payment_date_number(cell.row_label, deal)
            if cell.pct_of_original_balance > ZERO:
                last_positive = max(last_positive, n)
            elif first_zero is None or n < first_zero:
                first_zero = n
        if first_zero is None:
            raise TieoutError(f"{note} at {cpr} % CPR has no row printed 0")
        run = _run_for(runs, cpr, ZERO, False)
        window = principal_window(run, note)
        results.append(
            WindowBandResult(
                note=note,
                cpr_pct=cpr,
                model_last=None if window is None else window[1],
                after_payment_date=last_positive,
                on_or_before_payment_date=first_zero,
            )
        )
    return tuple(results)


def compare_credit_event_sensitivity(
    runs: dict[GridKey, WaterfallResult],
    cells: tuple[CreditEventSensitivityCell, ...],
    deal: DealTerms,
) -> tuple[CreditEventSensitivityResult, ...]:
    """Section 3.5: 100 x cumulative Credit Event Amount to the Maturity Date / Cut-off
    Date Balance."""
    results: list[CreditEventSensitivityResult] = []
    for cell in cells:
        run = _run_for(runs, cell.cpr_pct, cell.cer_pct, cell.early_redemption)
        model = HUNDRED * run.cumulative_credit_event_amount() / deal.cut_off_date_balance
        results.append(
            CreditEventSensitivityResult(
                early_redemption=cell.early_redemption,
                cer_pct=cell.cer_pct,
                cpr_pct=cell.cpr_pct,
                model_pct=model,
                printed=cell.printed,
                ppm=cell.cumulative_credit_event_pct,
            )
        )
    return tuple(results)
