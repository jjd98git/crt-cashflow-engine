"""Typed accessor for ``data/deal_terms/stacr_2026_dna1.yaml``.

Only the fields the v1 engine consumes are exposed.  Every leaf in the YAML is a mapping
``{value, page, section, quote}``; this module reads ``value`` and validates it.  YAML
floats are constructed as ``Decimal`` from the raw scalar text so that no rate or
percentage ever passes through a Python ``float`` (CLAUDE.md rule 3; spec 00 section 3.1).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml

from crt.io.yaml_decimal import DecimalSafeLoader
from crt.money import ZERO, percent_to_fraction

# The twelve Reference Tranches of Table 3 in the PPM's order (spec 02 section 1).
TRANCHE_ORDER: tuple[str, ...] = (
    "A-H",
    "A-1",
    "A-1H",
    "M-1",
    "M-1H",
    "M-2A",
    "M-2AH",
    "M-2B",
    "M-2BH",
    "B-1H",
    "B-2H",
    "B-3H",
)
# The four Original Notes and their Corresponding Reference Tranches
# (YAML: original_notes.correspondence).
NOTE_CLASSES: tuple[str, ...] = ("A-1", "M-1", "M-2A", "M-2B")

# Constants the PPM states in prose (register ids in comments; no numeric YAML leaf).
# P59: the Class A-1 Additional Reduction Amount starts on the 39th Payment Date.
CLASS_A1_ADDITIONAL_REDUCTION_START_PAYMENT_DATE = 39
# P52 / spec 02 section 3.3: each Cumulative Net Loss Test band is 12 Payment Dates.
CUMULATIVE_NET_LOSS_BAND_LENGTH = 12
EXPECTED_CUMULATIVE_NET_LOSS_BANDS = 13  # P52: twelve dated bands plus "and thereafter"


class DealTermsError(ValueError):
    """The deal-terms YAML is missing or inconsistent for a field the engine needs."""




@dataclass(frozen=True)
class NoteTerms:
    """Table 1 terms of one Original Note (YAML: original_notes.<X>)."""

    name: str
    original_class_principal_balance: Decimal  # P3-P6
    margin: Decimal  # P36-P39, as a fraction (0.85% -> 0.0085)
    class_coupon_minimum_rate: Decimal  # P7, fraction
    initial_class_coupon: Decimal  # P42-P45, fraction
    expected_wal_years_table1: Decimal  # T39 / Table 1
    expected_principal_window_table1: tuple[int, int]  # T38


@dataclass(frozen=True)
class DealTerms:
    """The deal facts the v1 engine consumes, all typed and validated."""

    closing_date: date  # P1
    cut_off_date: date  # P9
    cut_off_date_balance: Decimal  # P10
    first_payment_date: date  # P19 / P71
    scheduled_maturity_payment_date_number: int  # P8 / P21: 240
    earliest_early_redemption_payment_date_number: int  # P64: 60
    clean_up_threshold: Decimal  # P63, fraction of the Cut-off Date Balance (0.10)
    initial_class_notional_amounts: dict[str, Decimal]  # P24-P31, P3-P6
    notes: dict[str, NoteTerms]
    sofr_rate_flat: Decimal  # P12, fraction
    minimum_credit_enhancement_threshold: Decimal  # P15, fraction (0.03525)
    class_a1_cumulative_net_loss_threshold: Decimal  # P16, fraction (0.0100)
    cumulative_net_loss_test_schedule: tuple[Decimal, ...]  # P52, 13 fractions
    delinquency_test_factor: Decimal  # P53, fraction (0.50)
    delinquency_test_averaging_payment_dates: int  # P54: 6
    supplemental_reduction_threshold: Decimal  # P58, fraction (0.0550)
    preliminary_principal_loss_share_of_credit_event_amount: Decimal  # P14, fraction (0.25)
    appendix_g_aggregate_payment_dates_1_to_12: Decimal  # P60
    appendix_g_aggregate_payment_dates_13_to_36: Decimal  # P61

    def pair_of(self, note_tranche: str) -> str:
        """The H tranche paired with a Note tranche (YAML: reference_tranches.structure_note)."""
        if note_tranche not in NOTE_CLASSES:
            raise DealTermsError(f"{note_tranche} is not a Note tranche")
        return note_tranche + "H"


def _leaf(mapping: dict[str, Any], path: str) -> Any:
    """Return ``value`` of the leaf at dotted ``path``; raise if absent or not a leaf."""
    node: Any = mapping
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            raise DealTermsError(f"deal terms: missing field {path!r}")
        node = node[key]
    if not isinstance(node, dict) or "value" not in node:
        raise DealTermsError(f"deal terms: {path!r} is not a leaf with a 'value'")
    value = node["value"]
    if value is None:
        raise DealTermsError(f"deal terms: {path!r} has a null value")
    return value


def _money(mapping: dict[str, Any], path: str) -> Decimal:
    value = _leaf(mapping, path)
    if not isinstance(value, str):
        raise DealTermsError(f"deal terms: {path!r} must be a quoted dollar string, got {value!r}")
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise DealTermsError(f"deal terms: {path!r} = {value!r} is not a Decimal") from None
    if amount < ZERO:
        raise DealTermsError(f"deal terms: {path!r} is negative")
    return amount


def _percent(mapping: dict[str, Any], path: str) -> Decimal:
    """A percentage leaf (YAML int or Decimal) returned as a fraction."""
    value = _leaf(mapping, path)
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise DealTermsError(f"deal terms: {path!r} must be numeric, got {value!r}")
    return percent_to_fraction(Decimal(value))


def _integer(mapping: dict[str, Any], path: str) -> int:
    value = _leaf(mapping, path)
    if isinstance(value, bool) or not isinstance(value, int):
        raise DealTermsError(f"deal terms: {path!r} must be an integer, got {value!r}")
    return value


def _date(mapping: dict[str, Any], path: str) -> date:
    value = _leaf(mapping, path)
    if not isinstance(value, date):
        raise DealTermsError(f"deal terms: {path!r} must be a date, got {value!r}")
    return value


_MONTH_NUMBER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def _payment_date_number_from_month_text(
    text: str, *, first_payment_date: date, path: str
) -> int:
    """Convert "Payment Date in February 2046" to its Payment Date number ``n``."""
    match = re.fullmatch(r"Payment Date in ([A-Z][a-z]+) (\d{4})", text.strip())
    if match is None or match.group(1) not in _MONTH_NUMBER:
        raise DealTermsError(
            f"deal terms: {path!r} = {text!r} is not 'Payment Date in <Month> <Year>'"
        )
    month = _MONTH_NUMBER[match.group(1)]
    year = int(match.group(2))
    months_after_first = (year - first_payment_date.year) * 12 + (
        month - first_payment_date.month
    )
    if months_after_first < 0:
        raise DealTermsError(f"deal terms: {path!r} precedes the first Payment Date")
    return months_after_first + 1


def _window(text: str, *, path: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)-(\d+)", text.strip())
    if match is None:
        raise DealTermsError(f"deal terms: {path!r} = {text!r} is not a 'first-last' window")
    first, last = int(match.group(1)), int(match.group(2))
    if first > last:
        raise DealTermsError(f"deal terms: {path!r} window {text!r} is reversed")
    return first, last


def _cumulative_net_loss_schedule(mapping: dict[str, Any]) -> tuple[Decimal, ...]:
    path = "performance_tests.cumulative_net_loss_test_schedule_pct"
    value = _leaf(mapping, path)
    if not isinstance(value, list) or len(value) != EXPECTED_CUMULATIVE_NET_LOSS_BANDS:
        raise DealTermsError(
            f"deal terms: {path!r} must list {EXPECTED_CUMULATIVE_NET_LOSS_BANDS} bands"
        )
    thresholds: list[Decimal] = []
    for index, band in enumerate(value, start=1):
        if not isinstance(band, dict) or "threshold_pct" not in band or "period" not in band:
            raise DealTermsError(f"deal terms: {path!r} band {index} is malformed")
        threshold = band["threshold_pct"]
        if isinstance(threshold, bool) or not isinstance(threshold, (int, Decimal)):
            raise DealTermsError(f"deal terms: {path!r} band {index} threshold is not numeric")
        expected_start_year = 2026 + index - 1
        period = str(band["period"])
        if not period.startswith(f"March {expected_start_year}"):
            raise DealTermsError(
                f"deal terms: {path!r} band {index} period {period!r} does not start in "
                f"March {expected_start_year}"
            )
        thresholds.append(percent_to_fraction(Decimal(threshold)))
    if thresholds != sorted(thresholds):
        raise DealTermsError(f"deal terms: {path!r} is not non-decreasing")
    return tuple(thresholds)


def load_deal_terms(path: Path) -> DealTerms:
    """Load and validate the deal-terms YAML for the fields the engine needs."""
    if not path.is_file():
        raise DealTermsError(f"{path}: file not found")
    with path.open(encoding="utf-8") as handle:
        raw = yaml.load(handle, Loader=DecimalSafeLoader)
    if not isinstance(raw, dict):
        raise DealTermsError(f"{path}: top level is not a mapping")

    first_payment_date = _date(raw, "deal.first_payment_date")
    cut_off_date_balance = _money(raw, "deal.cut_off_date_balance_usd")

    initial_class_notional_amounts: dict[str, Decimal] = {}
    for tranche in TRANCHE_ORDER:
        initial_class_notional_amounts[tranche] = _money(
            raw, f"reference_tranches.{tranche}.initial_class_notional_amount_usd"
        )
    tranche_total = sum(initial_class_notional_amounts.values(), ZERO)
    # YAML: reference_tranches.sum_equals_cut_off_balance (P10)
    if tranche_total != cut_off_date_balance:
        raise DealTermsError(
            f"deal terms: sum of initial Class Notional Amounts {tranche_total} != Cut-off Date "
            f"Balance {cut_off_date_balance}"
        )

    notes: dict[str, NoteTerms] = {}
    for note in NOTE_CLASSES:
        prefix = f"original_notes.{note}"
        original_balance = _money(raw, f"{prefix}.original_class_principal_balance_usd")
        if original_balance != initial_class_notional_amounts[note]:
            raise DealTermsError(
                f"deal terms: {note} Note balance {original_balance} != Reference Tranche "
                f"notional {initial_class_notional_amounts[note]}"
            )
        notes[note] = NoteTerms(
            name=note,
            original_class_principal_balance=original_balance,
            margin=_percent(raw, f"{prefix}.margin_pct"),
            class_coupon_minimum_rate=_percent(raw, f"{prefix}.class_coupon_minimum_rate_pct"),
            initial_class_coupon=_percent(raw, f"{prefix}.initial_class_coupon_pct"),
            expected_wal_years_table1=Decimal(_leaf(raw, f"{prefix}.expected_wal_years_table1")),
            expected_principal_window_table1=_window(
                str(_leaf(raw, f"{prefix}.expected_principal_window_months_table1")),
                path=f"{prefix}.expected_principal_window_months_table1",
            ),
        )

    sofr_rate_flat = _percent(raw, "modeling_assumptions.r_sofr_flat_pct")
    for note in NOTE_CLASSES:
        # P42-P45: the Initial Class Coupons equal SOFR Rate + margin (spec 02 section 10).
        if notes[note].initial_class_coupon != sofr_rate_flat + notes[note].margin:
            raise DealTermsError(
                f"deal terms: {note} initial coupon {notes[note].initial_class_coupon} != SOFR "
                f"{sofr_rate_flat} + margin {notes[note].margin}"
            )

    appendix_g = _leaf(raw, "principal.appendix_g_schedule")
    if not isinstance(appendix_g, dict):
        raise DealTermsError("deal terms: principal.appendix_g_schedule is not a mapping")
    try:
        aggregate_1_to_12 = Decimal(str(appendix_g["payment_periods_1_to_12"]["aggregate_usd"]))
        aggregate_13_to_36 = Decimal(str(appendix_g["payment_periods_13_to_36"]["aggregate_usd"]))
    except (KeyError, TypeError, InvalidOperation):
        raise DealTermsError(
            "deal terms: principal.appendix_g_schedule aggregates missing"
        ) from None

    return DealTerms(
        closing_date=_date(raw, "deal.closing_date"),
        cut_off_date=_date(raw, "deal.cut_off_date"),
        cut_off_date_balance=cut_off_date_balance,
        first_payment_date=first_payment_date,
        scheduled_maturity_payment_date_number=_payment_date_number_from_month_text(
            str(_leaf(raw, "deal.scheduled_maturity_date")),
            first_payment_date=first_payment_date,
            path="deal.scheduled_maturity_date",
        ),
        earliest_early_redemption_payment_date_number=_payment_date_number_from_month_text(
            str(_leaf(raw, "termination.earliest_time_based_call_option_date")),
            first_payment_date=first_payment_date,
            path="termination.earliest_time_based_call_option_date",
        ),
        clean_up_threshold=_percent(
            raw, "termination.clean_up_threshold_pct_of_cut_off_balance"
        ),
        initial_class_notional_amounts=initial_class_notional_amounts,
        notes=notes,
        sofr_rate_flat=sofr_rate_flat,
        minimum_credit_enhancement_threshold=_percent(
            raw, "performance_tests.minimum_credit_enhancement_threshold_pct"
        ),
        class_a1_cumulative_net_loss_threshold=_percent(
            raw, "performance_tests.class_a1_cumulative_net_loss_threshold_pct"
        ),
        cumulative_net_loss_test_schedule=_cumulative_net_loss_schedule(raw),
        delinquency_test_factor=_percent(raw, "performance_tests.delinquency_test_factor_pct"),
        delinquency_test_averaging_payment_dates=_integer(
            raw, "performance_tests.delinquency_test_averaging_months"
        ),
        supplemental_reduction_threshold=_percent(
            raw, "principal.supplemental_reduction_threshold_pct"
        ),
        preliminary_principal_loss_share_of_credit_event_amount=_percent(
            raw, "modeling_assumptions.d_preliminary_principal_loss_pct_of_credit_event_amount"
        ),
        appendix_g_aggregate_payment_dates_1_to_12=aggregate_1_to_12,
        appendix_g_aggregate_payment_dates_13_to_36=aggregate_13_to_36,
    )
