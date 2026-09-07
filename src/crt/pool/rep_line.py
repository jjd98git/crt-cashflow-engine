"""One rep-line, one collection month (spec ``01-pool.md`` section 3, steps P1-P5, as
amended 2026-09-07 under Q21).

The order inside a month is fixed by the spec and must never change:
credit events and prepayments in full, both on the beginning-of-month balance ->
survivors -> scheduled payment and interest of the survivors -> scheduled principal ->
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
    scheduled_payment: Decimal  # P4, on the surviving balance
    interest: Decimal  # P4 (A15): survivors' interest, 30/360 on the surviving balance
    scheduled_principal: Decimal  # P5
    credit_event_amount: Decimal  # P1 (A2, revised 2026-09-07 per Q21)
    prepayment: Decimal  # P2 (A1, A3 revised 2026-09-07 per Q21)
    prepayment_interest: Decimal  # spec 01 section 7 (A15): 30 days' interest on prepayments
    balance_end: Decimal
    remaining_term_end: int


def monthly_rate(annual_rate: Decimal) -> Decimal:
    """``r = rate / 12`` as an exact Decimal division at context precision (spec 01 section 3)."""
    return annual_rate / TWELVE


def scheduled_payment(balance: Decimal, rate: Decimal, remaining_term: int) -> Decimal:
    """Step P4: level payment from the outstanding (surviving) balance, the monthly rate
    and the remaining term (Modeling Assumption (c), register T7 / P76), rounded to the
    cent (R1).
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
            prepayment_interest=ZERO,
            balance_end=ZERO,
            remaining_term_end=remaining_term - 1,
        )

    if remaining_term <= 0:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: positive balance {balance} with remaining term "
            f"{remaining_term}"
        )

    # P1 - credit events on the beginning-of-month balance (A2, revised 2026-09-07 per Q21):
    # the Credit Event UPB is the balance before the month's scheduled principal.
    credit_event = round2(balance * mdr)

    # P2 - prepayments in full on the beginning-of-month balance (A1, A3 revised per Q21;
    # Modeling Assumption (g); no curtailments, P72).  Not net of credit events.
    prepayment = round2(balance * smm)

    # P3 - the surviving loans are the only ones that amortize this month.
    survivor = balance - credit_event - prepayment
    if survivor < ZERO:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: removals {credit_event + prepayment} exceed "
            f"balance {balance}"
        )

    # P4 - scheduled payment and interest of the survivors (Modeling Assumption (c), A15).
    payment = scheduled_payment(survivor, rate, remaining_term)
    interest = round2(survivor * rate)

    # P5 - scheduled principal (Stated Principal clause (a)).
    if remaining_term >= 2:
        sched_principal = min(survivor, payment - interest)
    else:
        sched_principal = survivor
    if sched_principal < ZERO:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: negative scheduled principal {sched_principal}"
        )
    balance_end = survivor - sched_principal

    # Spec 01 section 7 (A15; Modeling Assumption (g)): the prepaying loans pay off with
    # 30 days' interest on their balance, in addition to the survivors' interest above.
    # Credit Event Reference Obligations pay no interest in the month they are removed.
    prepayment_interest = round2(prepayment * rate)

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
        prepayment_interest=prepayment_interest,
        balance_end=balance_end,
        remaining_term_end=remaining_term - 1,
    )
