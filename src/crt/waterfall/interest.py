"""Payment Date calendar and Note interest (spec ``02-waterfall.md`` section 10;
YAML: coupon.*, interest.*; C4, C11, P20, P50).  Not a tie-out target."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from crt.money import ZERO, round2

DAYS_IN_YEAR_ACT_360 = Decimal(360)  # P20: actual/360


def payment_date(payment_date_number: int, first_payment_date: date) -> date:
    """The 25th of the month ``n - 1`` months after the first Payment Date, without
    Business Day adjustment (Modeling Assumption (q), P71; spec 00 section 2.1)."""
    if payment_date_number < 1:
        raise ValueError(f"Payment Date number {payment_date_number} < 1")
    months = first_payment_date.month - 1 + (payment_date_number - 1)
    year = first_payment_date.year + months // 12
    month = months % 12 + 1
    return date(year, month, first_payment_date.day)


def accrual_period_days(payment_date_number: int, closing_date: date, first_payment_date: date) -> int:
    """Days from the prior Payment Date (the Closing Date for n = 1) to the day before
    this Payment Date, inclusive = PD[n] - PD[n-1] (P50)."""
    end = payment_date(payment_date_number, first_payment_date)
    start = closing_date if payment_date_number == 1 else payment_date(
        payment_date_number - 1, first_payment_date
    )
    return (end - start).days


def class_coupon(sofr_rate: Decimal, margin: Decimal, minimum_rate: Decimal) -> Decimal:
    """``max(minimum rate, SOFR Rate + margin)`` (P36-P39, P7)."""
    return max(minimum_rate, sofr_rate + margin)


def interest_accrual_amount(balance_prior: Decimal, coupon: Decimal, days: int) -> Decimal:
    """``round2(balance immediately prior x coupon x days / 360)`` (P107, R2)."""
    if days <= 0:
        raise ValueError(f"Accrual Period of {days} days")
    if balance_prior <= ZERO:
        return ZERO
    return round2(balance_prior * coupon * Decimal(days) / DAYS_IN_YEAR_ACT_360)
