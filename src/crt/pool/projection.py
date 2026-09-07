"""Reference Pool projection over collection months and its aggregation into Payment
Dates (spec ``01-pool.md`` sections 4-6; ``00-overview.md`` section 2.1).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.io.rep_lines import RepLine
from crt.money import ZERO, require_decimal_context
from crt.pool.rates import mdr_from_cer, smm_from_cpr
from crt.pool.rep_line import RepLineMonth, monthly_rate, project_rep_line_month

# Spec 00 section 2.1: Payment Date n = 1 is March 2026; month m = 1 is January 2026.
# The first Payment Date receives collection months {1, 2}; Payment Date n >= 2
# receives month n + 1 (A4, P67, P68).
FIRST_PAYMENT_DATE_COLLECTION_MONTHS: tuple[int, ...] = (1, 2)
SCHEDULED_MATURITY_PAYMENT_DATE = 240  # P8 / P21: Payment Date 240 = February 2046
LAST_COLLECTION_MONTH = 241  # spec 01 section 6: Payment Date 240 carries month 241


class PoolProjectionError(ValueError):
    """The pool projection violated an identity or received bad inputs."""


def collection_months_for_payment_date(payment_date_number: int) -> tuple[int, ...]:
    """``M(n)``: the collection months feeding Payment Date ``n`` (A4)."""
    if payment_date_number < 1:
        raise PoolProjectionError(f"Payment Date number {payment_date_number} < 1")
    if payment_date_number == 1:
        return FIRST_PAYMENT_DATE_COLLECTION_MONTHS
    return (payment_date_number + 1,)


@dataclass(frozen=True)
class PoolMonth:
    """Pool totals for one collection month (spec 01 section 4): sums of cent amounts."""

    month: int
    scheduled_principal: Decimal
    interest: Decimal
    credit_event_amount: Decimal
    prepayment: Decimal
    upb_end: Decimal


@dataclass(frozen=True)
class StatedPrincipalClauses:
    """The five clauses of Stated Principal (YAML: principal.stated_principal, P96).

    In the v1 run clauses (b), (d) and (e) are zero (Modeling Assumptions (h), (k), (l)).
    """

    scheduled_principal_collected: Decimal  # (a)
    partial_prepayments: Decimal  # (b)
    non_credit_event_removals_upb: Decimal  # (c): payments in full (P104)
    negative_upb_adjustments: Decimal  # (d)
    positive_upb_adjustments: Decimal  # (e)

    def stated_principal(self) -> Decimal:
        """Clauses (a)+(b)+(c)+(d)-(e), floored at zero."""
        gross = (
            self.scheduled_principal_collected
            + self.partial_prepayments
            + self.non_credit_event_removals_upb
            + self.negative_upb_adjustments
        )
        return max(ZERO, gross - self.positive_upb_adjustments)

    def floor_excess_to_a_h(self) -> Decimal:
        """The excess of clause (e) over (a)-(d), which the PPM adds to A-H (P96)."""
        gross = (
            self.scheduled_principal_collected
            + self.partial_prepayments
            + self.non_credit_event_removals_upb
            + self.negative_upb_adjustments
        )
        return max(ZERO, self.positive_upb_adjustments - gross)


@dataclass(frozen=True)
class PaymentPeriod:
    """Pool aggregates for one Payment Date (spec 01 sections 5-6)."""

    payment_date_number: int
    collection_months: tuple[int, ...]
    scheduled_principal: Decimal
    prepayment: Decimal
    stated_principal: Decimal
    stated_principal_floor_excess_to_a_h: Decimal
    credit_event_amount: Decimal
    upb_end: Decimal
    upb_prev: Decimal


@dataclass(frozen=True)
class PoolProjection:
    cpr: Decimal
    cer: Decimal
    smm: Decimal
    mdr: Decimal
    cut_off_date_balance: Decimal
    rep_line_months: tuple[tuple[RepLineMonth, ...], ...]  # [rep-line index][month - 1]
    months: tuple[PoolMonth, ...]  # index month - 1, months 1..241
    payment_periods: tuple[PaymentPeriod, ...]  # index n - 1, Payment Dates 1..240

    def payment_period(self, payment_date_number: int) -> PaymentPeriod:
        period = self.payment_periods[payment_date_number - 1]
        if period.payment_date_number != payment_date_number:
            raise PoolProjectionError("payment periods are mis-indexed")
        return period


def project_pool(
    rep_lines: tuple[RepLine, ...],
    *,
    cpr: Decimal,
    cer: Decimal,
    cut_off_date_balance: Decimal,
) -> PoolProjection:
    """Project every rep-line through month 241 and aggregate into Payment Dates 1..240."""
    require_decimal_context()
    smm = smm_from_cpr(cpr)
    mdr = mdr_from_cer(cer)

    opening_total = sum((line.outstanding_principal_balance for line in rep_lines), ZERO)
    if opening_total != cut_off_date_balance:  # P10
        raise PoolProjectionError(
            f"rep-line balances sum to {opening_total}, not the Cut-off Date Balance "
            f"{cut_off_date_balance}"
        )

    per_line: list[tuple[RepLineMonth, ...]] = []
    for line in rep_lines:
        rate = monthly_rate(line.interest_rate)
        balance = line.outstanding_principal_balance
        term = line.remaining_term_months
        history: list[RepLineMonth] = []
        for month in range(1, LAST_COLLECTION_MONTH + 1):
            result = project_rep_line_month(
                group=line.group,
                month=month,
                balance=balance,
                remaining_term=term,
                rate=rate,
                smm=smm,
                mdr=mdr,
            )
            history.append(result)
            balance = result.balance_end
            term = result.remaining_term_end
        per_line.append(tuple(history))

    months: list[PoolMonth] = []
    for month_index in range(LAST_COLLECTION_MONTH):
        rows = [history[month_index] for history in per_line]
        months.append(
            PoolMonth(
                month=month_index + 1,
                scheduled_principal=sum((r.scheduled_principal for r in rows), ZERO),
                interest=sum((r.interest for r in rows), ZERO),
                credit_event_amount=sum((r.credit_event_amount for r in rows), ZERO),
                prepayment=sum((r.prepayment for r in rows), ZERO),
                upb_end=sum((r.balance_end for r in rows), ZERO),
            )
        )

    periods: list[PaymentPeriod] = []
    upb_prev = cut_off_date_balance  # A5: UPB_prev[1] = Cut-off Date Balance
    for n in range(1, SCHEDULED_MATURITY_PAYMENT_DATE + 1):
        month_numbers = collection_months_for_payment_date(n)
        feeding = [months[m - 1] for m in month_numbers]
        sched = sum((pm.scheduled_principal for pm in feeding), ZERO)
        prepay = sum((pm.prepayment for pm in feeding), ZERO)
        credit_events = sum((pm.credit_event_amount for pm in feeding), ZERO)
        clauses = StatedPrincipalClauses(
            scheduled_principal_collected=sched,  # (a): every payment timely (P69)
            partial_prepayments=ZERO,  # (b): no curtailments (P72)
            non_credit_event_removals_upb=prepay,  # (c): payments in full (P104)
            negative_upb_adjustments=ZERO,  # (d): no modifications, RM = 0 (P74)
            positive_upb_adjustments=ZERO,  # (e): no data corrections (P77)
        )
        upb_end = months[max(month_numbers) - 1].upb_end
        periods.append(
            PaymentPeriod(
                payment_date_number=n,
                collection_months=month_numbers,
                scheduled_principal=sched,
                prepayment=prepay,
                stated_principal=clauses.stated_principal(),
                stated_principal_floor_excess_to_a_h=clauses.floor_excess_to_a_h(),
                credit_event_amount=credit_events,
                upb_end=upb_end,
                upb_prev=upb_prev,
            )
        )
        # Pool identity per Payment Date: the pool loses exactly Stated Principal +
        # Credit Event Amount (spec 00 section 3.3).
        if upb_prev - clauses.stated_principal() - credit_events != upb_end:
            raise PoolProjectionError(
                f"Payment Date {n}: UPB_prev {upb_prev} - Stated Principal - Credit Event "
                f"Amount != UPB_end {upb_end}"
            )
        upb_prev = upb_end

    return PoolProjection(
        cpr=cpr,
        cer=cer,
        smm=smm,
        mdr=mdr,
        cut_off_date_balance=cut_off_date_balance,
        rep_line_months=tuple(per_line),
        months=tuple(months),
        payment_periods=tuple(periods),
    )
