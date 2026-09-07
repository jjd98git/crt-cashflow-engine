"""Weighted Average Life and principal windows (spec ``03-tieout.md`` sections 1-2;
register A9, A10)."""

from __future__ import annotations

from decimal import Decimal

from crt.money import ZERO
from crt.waterfall.engine import WaterfallResult

# A9: t[n] = (30 n + 8) / 360 years from the Closing Date 2026-02-17 to the unadjusted
# 25th of the Payment Date month, 30/360.  8 = days from the 17th to the 25th.
WAL_CLOCK_MONTH_DAYS = Decimal(30)
WAL_CLOCK_CLOSING_TO_FIRST_25TH_DAYS = Decimal(8)
WAL_CLOCK_DAYS_IN_YEAR = Decimal(360)


def time_fraction(payment_date_number: int) -> Decimal:
    """``t[n] = (30 n + 8) / 360`` (A9), unrounded (R5)."""
    if payment_date_number < 1:
        raise ValueError(f"Payment Date number {payment_date_number} < 1")
    return (
        WAL_CLOCK_MONTH_DAYS * Decimal(payment_date_number)
        + WAL_CLOCK_CLOSING_TO_FIRST_25TH_DAYS
    ) / WAL_CLOCK_DAYS_IN_YEAR


def balance_reduction(result: WaterfallResult, note: str, payment_date_number: int) -> Decimal:
    """``R[X, n]``: net reduction of the Class Principal Balance on Payment Date ``n``
    (principal paid + write-down - write-up; the Maturity Date 100 % payment included) (A10).
    """
    record = result.records[payment_date_number - 1]
    cashflow = record.notes[note]
    return cashflow.balance_before - cashflow.balance_after


def weighted_average_life(result: WaterfallResult, note: str) -> Decimal | None:
    """``WAL = sum R t / sum R`` over Payment Dates through the Maturity Date; ``None``
    when the Note was never reduced (spec: report n/a, never 0)."""
    numerator = ZERO
    denominator = ZERO
    for record in result.records:
        reduction = balance_reduction(result, note, record.payment_date_number)
        if reduction == ZERO:
            continue
        numerator += reduction * time_fraction(record.payment_date_number)
        denominator += reduction
    if denominator == ZERO:
        return None
    return numerator / denominator


def principal_window(result: WaterfallResult, note: str) -> tuple[int, int] | None:
    """First and last Payment Date with principal paid > 0 (write-downs excluded; the
    Maturity Date payment included).  ``None`` if no principal was ever paid."""
    paid = [
        record.payment_date_number
        for record in result.records
        if record.notes[note].principal_paid > ZERO
    ]
    if not paid:
        return None
    return paid[0], paid[-1]


def balance_after_payment_date(result: WaterfallResult, note: str, payment_date_number: int) -> Decimal:
    """Class Principal Balance after Payment Date ``n``; zero after the Maturity Date."""
    if payment_date_number > result.maturity_payment_date_number:
        return ZERO
    return result.records[payment_date_number - 1].notes[note].balance_after
