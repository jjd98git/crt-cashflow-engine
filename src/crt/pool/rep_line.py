"""One rep-line, one collection month (spec ``01-pool.md`` section 3, steps P1-P5).

The order inside a month is fixed by the spec and must never change:
scheduled payment -> interest -> scheduled principal -> credit events -> prepayments ->
roll the remaining term.  Every dollar amount is rounded to the cent at the step the spec
names (R1, register A7) and nowhere else.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.money import ONE, TWELVE, ZERO, round2


class RepLineProjectionError(ValueError):
    """A rep-line month produced an impossible state (negative balance, no term left)."""


@dataclass(frozen=True)
class RepLineMonth:
    """Every intermediate of one rep-line month, to the cent."""

    group: int
    month: int
    balance_begin: Decimal
    remaining_term_begin: int
    scheduled_payment: Decimal  # P1
    interest: Decimal  # P2 (A15)
    scheduled_principal: Decimal  # P3
    credit_event_amount: Decimal  # P4
    prepayment: Decimal  # P5
    balance_end: Decimal
    remaining_term_end: int


def monthly_rate(annual_rate: Decimal) -> Decimal:
    """``r = rate / 12`` as an exact Decimal division at context precision (spec 01 section 3)."""
    return annual_rate / TWELVE


def scheduled_payment(balance: Decimal, rate: Decimal, remaining_term: int) -> Decimal:
    """Step P1: level payment from the outstanding balance, the monthly rate and the
    remaining term (Modeling Assumption (c), register T7 / P76), rounded to the cent (R1).
    """
    if remaining_term >= 2:
        discount = ONE - (ONE + rate) ** (-remaining_term)  # integer power in Decimal
        return round2(balance * rate / discount)
    if remaining_term == 1:
        return round2(balance * (ONE + rate))  # final instalment
    raise RepLineProjectionError("a positive balance with no remaining term is a data error")


def project_rep_line_month(
    *,
    group: int,
    month: int,
    balance: Decimal,
    remaining_term: int,
    rate: Decimal,
    smm: Decimal,
    mdr: Decimal,
) -> RepLineMonth:
    """Apply steps P1-P5 to one rep-line for one collection month."""
    if balance < ZERO:
        raise RepLineProjectionError(f"rep-line {group} month {month}: negative balance {balance}")

    if balance == ZERO:
        # Spec 01 section 8: a fully paid rep-line has zero flows; the term still rolls.
        return RepLineMonth(
            group=group,
            month=month,
            balance_begin=balance,
            remaining_term_begin=remaining_term,
            scheduled_payment=ZERO,
            interest=ZERO,
            scheduled_principal=ZERO,
            credit_event_amount=ZERO,
            prepayment=ZERO,
            balance_end=ZERO,
            remaining_term_end=remaining_term - 1,
        )

    if remaining_term <= 0:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: positive balance {balance} with remaining term "
            f"{remaining_term}"
        )

    # P1 - scheduled monthly payment.
    payment = scheduled_payment(balance, rate, remaining_term)

    # P2 - interest for the month, 30/360 on the beginning balance (A15).
    interest = round2(balance * rate)

    # P3 - scheduled principal (Stated Principal clause (a)).
    if remaining_term >= 2:
        sched_principal = min(balance, payment - interest)
    else:
        sched_principal = balance
    if sched_principal < ZERO:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: negative scheduled principal {sched_principal}"
        )
    balance_after_scheduled = balance - sched_principal

    # P4 - credit events on the balance net of scheduled principal (A2, A3).
    credit_event = round2(balance_after_scheduled * mdr)
    balance_after_credit_events = balance_after_scheduled - credit_event

    # P5 - prepayments in full on the balance net of scheduled principal and credit
    # events (A1, A3; Modeling Assumption (g); no curtailments, P72).
    prepayment = round2(balance_after_credit_events * smm)
    balance_end = balance_after_credit_events - prepayment

    if balance_end < ZERO:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: negative ending balance {balance_end}"
        )
    # Identity (spec 00 section 3.3, assert): B[m] = B[m-1] - SchedPrin - CE - Prepay.
    if balance_end != balance - sched_principal - credit_event - prepayment:
        raise RepLineProjectionError(f"rep-line {group} month {month}: balance identity broken")

    return RepLineMonth(
        group=group,
        month=month,
        balance_begin=balance,
        remaining_term_begin=remaining_term,
        scheduled_payment=payment,
        interest=interest,
        scheduled_principal=sched_principal,
        credit_event_amount=credit_event,
        prepayment=prepayment,
        balance_end=balance_end,
        remaining_term_end=remaining_term - 1,
    )
