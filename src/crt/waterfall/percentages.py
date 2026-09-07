"""Senior Percentage and Subordinate Percentage (spec ``02-waterfall.md`` section 2;
YAML: principal.senior_percentage, principal.subordinate_percentage; P95, A5, A12)."""

from __future__ import annotations

from decimal import Decimal

from crt.money import ONE, ZERO, round7
from crt.waterfall.tranches import SENIOR_TRANCHES


class PercentageError(ValueError):
    """A percentage denominator is not positive."""


def senior_percentage(prior_balances: dict[str, Decimal], upb_prev: Decimal) -> Decimal:
    """``round7((CNA[A-H] + CNA[A-1] + CNA[A-1H]) / UPB_prev)`` on the balances immediately
    prior to the Payment Date; ``UPB_prev`` is the Cut-off Date Balance on Payment Date 1
    and the prior Reporting Period's ending UPB thereafter (A5)."""
    if upb_prev <= ZERO:
        raise PercentageError(f"Senior Percentage denominator UPB_prev = {upb_prev} is not positive")
    senior_total = sum((prior_balances[name] for name in SENIOR_TRANCHES), ZERO)
    return round7(senior_total / upb_prev)  # R3


def subordinate_percentage(senior_pct: Decimal) -> Decimal:
    """``100 % - Senior Percentage`` (P95)."""
    return ONE - senior_pct


def offered_reference_tranche_percentage(
    offered_total: Decimal, class_a1_additional_reduction: Decimal, upb_end: Decimal
) -> Decimal:
    """``round7((Offered - ClassA1Additional) / UPB_end)`` (P103); 0 when ``UPB_end`` = 0."""
    if upb_end <= ZERO:
        return ZERO
    return round7((offered_total - class_a1_additional_reduction) / upb_end)  # R3
