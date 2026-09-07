"""The four performance tests and the Cumulative Net Loss Percentage
(spec ``02-waterfall.md`` sections 3.2-3.3; YAML: performance_tests.*)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.io.deal_terms import CUMULATIVE_NET_LOSS_BAND_LENGTH
from crt.money import ZERO, round7


class PerformanceTestError(ValueError):
    """A test needed an input the scenario did not provide."""


@dataclass(frozen=True)
class TestOutcomes:
    minimum_credit_enhancement: bool
    cumulative_net_loss: bool
    delinquency: bool
    class_a1_cumulative_net_loss: bool

    @property
    def subordinate_tests_pass(self) -> bool:
        """The three tests gating the Subordinate Reduction Amount
        (YAML: performance_tests.gating_summary)."""
        return self.minimum_credit_enhancement and self.cumulative_net_loss and self.delinquency


def cumulative_net_loss_percentage(
    cumulative_principal_loss: Decimal,
    cumulative_principal_recovery: Decimal,
    cut_off_date_balance: Decimal,
) -> Decimal:
    """``round7((cum Principal Loss - cum Principal Recovery) / Cut-off Date Balance)``,
    the sums including the current Payment Date (P10 denominator; R3)."""
    if cut_off_date_balance <= ZERO:
        raise PerformanceTestError("Cut-off Date Balance must be positive")
    return round7((cumulative_principal_loss - cumulative_principal_recovery) / cut_off_date_balance)


def minimum_credit_enhancement_test(subordinate_pct: Decimal, threshold: Decimal) -> bool:
    """Passes when ``Subordinate Percentage >= 3.525 %`` (P15)."""
    return subordinate_pct >= threshold


def cumulative_net_loss_threshold(payment_date_number: int, schedule: tuple[Decimal, ...]) -> Decimal:
    """The P52 threshold for Payment Date ``n``: bands of 12 Payment Dates from March 2026,
    the last band applying "and thereafter"."""
    if payment_date_number < 1:
        raise PerformanceTestError(f"Payment Date number {payment_date_number} < 1")
    band = (payment_date_number - 1) // CUMULATIVE_NET_LOSS_BAND_LENGTH
    return schedule[min(band, len(schedule) - 1)]


def cumulative_net_loss_test(
    cnl_pct: Decimal, payment_date_number: int, schedule: tuple[Decimal, ...]
) -> bool:
    """Passes when the Cumulative Net Loss Percentage does not exceed the band threshold."""
    return cnl_pct <= cumulative_net_loss_threshold(payment_date_number, schedule)


def average_distressed_principal_balance(
    distressed_by_payment_date: tuple[Decimal, ...],
    payment_date_number: int,
    averaging_payment_dates: int,
) -> Decimal:
    """Average over Payment Dates ``max(1, n - 5) .. n`` (P54: six, or all since the
    Closing Date before the sixth).  Raises if the vector is shorter than ``n``."""
    if len(distressed_by_payment_date) < payment_date_number:
        raise PerformanceTestError(
            f"Distressed Principal Balance missing for Payment Date {payment_date_number}"
        )
    first = max(1, payment_date_number - averaging_payment_dates + 1)
    window = distressed_by_payment_date[first - 1 : payment_date_number]
    return sum(window, ZERO) / Decimal(len(window))


def delinquency_test(
    average_distressed: Decimal,
    subordinate_pct: Decimal,
    upb_prev: Decimal,
    principal_loss_amount: Decimal,
    factor: Decimal,
) -> bool:
    """``AvgDPB < 50 % x (SubPct x UPB_prev - Principal Loss Amount)`` (P17, P53; A5)."""
    return average_distressed < factor * (subordinate_pct * upb_prev - principal_loss_amount)


def class_a1_cumulative_net_loss_test(
    cnl_pct: Decimal, threshold: Decimal, *, failed_on_a_prior_payment_date: bool
) -> bool:
    """Clause (1): CNL % <= 1.00 % (P16); clause (2): satisfied on every prior Payment
    Date -- once failed, it stays failed."""
    if failed_on_a_prior_payment_date:
        return False
    return cnl_pct <= threshold
