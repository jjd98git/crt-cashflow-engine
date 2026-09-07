"""The Payment Date loop (spec ``00-overview.md`` section 4; ``02-waterfall.md``).

For each Payment Date the engine, in this order and never any other
(YAML: principal.sequencing_within_payment_date, P90-P92):

1. reads the pool aggregates of the Reporting Period;
2. computes the Senior / Subordinate Percentage on the state immediately prior;
3. computes losses, recoveries, write-down / write-up and the Cumulative Net Loss
   Percentage including this Payment Date;
4. evaluates the four tests;
5. on the Maturity Date: Step 1 then 100 % payment of every Class Principal Balance, stop;
6. otherwise Step 1 (write-down / write-up), Step 2 (Senior Reduction Amount), Step 3
   (Subordinate Reduction Amount), Step 4 (Supplemental Reduction Amount);
7. derives the Note cashflows and asserts the accounting identities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from crt.io.appendix_g import CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE, AppendixG
from crt.io.deal_terms import (
    CLASS_A1_ADDITIONAL_REDUCTION_START_PAYMENT_DATE,
    NOTE_CLASSES,
    TRANCHE_ORDER,
    DealTerms,
)
from crt.money import ZERO, require_decimal_context, round2
from crt.pool.projection import PaymentPeriod, PoolProjection
from crt.scenarios.scenario import Scenario
from crt.waterfall.interest import (
    accrual_period_days,
    class_coupon,
    interest_accrual_amount,
    payment_date,
)
from crt.waterfall.losses import (
    PrincipalLossClauses,
    PrincipalRecoveryClauses,
    a_h_increase_on_write_down,
    principal_loss_clauses_v1,
    principal_recovery_clauses_v1,
    recovery_principal,
    tranche_write_down_amount,
    tranche_write_up_amount,
)
from crt.waterfall.percentages import (
    offered_reference_tranche_percentage,
    senior_percentage,
    subordinate_percentage,
)
from crt.waterfall.performance_tests import (
    PerformanceTestError,
    TestOutcomes,
    average_distressed_principal_balance,
    class_a1_cumulative_net_loss_test,
    cumulative_net_loss_percentage,
    cumulative_net_loss_test,
    cumulative_net_loss_threshold,
    delinquency_test,
    minimum_credit_enhancement_test,
)
from crt.waterfall.steps import (
    StepResult,
    step1_tranche_write_down,
    step1_tranche_write_up,
    step2_senior_reduction,
    step3_subordinate_reduction,
    step4_supplemental_reduction,
)
from crt.waterfall.tranches import OFFERED_TRANCHES, TrancheState


class WaterfallError(ValueError):
    """The waterfall reached an inconsistent state."""


class IdentityError(WaterfallError):
    """An accounting identity of spec 00 section 3.3 is broken."""


@dataclass(frozen=True)
class NoteCashflow:
    """What one Original Note receives / loses on a Payment Date (spec 02 section 10)."""

    note: str
    balance_before: Decimal
    principal_paid: Decimal
    write_down: Decimal
    write_up: Decimal
    balance_after: Decimal
    coupon: Decimal
    accrual_days: int
    interest_accrual: Decimal
    interest_payment: Decimal


@dataclass(frozen=True)
class PaymentDateRecord:
    """Every quantity of one Payment Date, for the report, the WAL and the tests."""

    payment_date_number: int
    payment_date: date
    is_maturity_date: bool
    maturity_reason: str | None
    pool: PaymentPeriod
    senior_pct: Decimal
    subordinate_pct: Decimal
    principal_loss_clauses: PrincipalLossClauses
    principal_recovery_clauses: PrincipalRecoveryClauses
    principal_loss_amount: Decimal
    principal_recovery_amount: Decimal
    tranche_write_down: Decimal
    tranche_write_up: Decimal
    recovery_principal: Decimal
    a_h_increase_on_write_down: Decimal
    cumulative_net_loss_pct: Decimal
    cumulative_net_loss_threshold: Decimal
    tests: TestOutcomes
    senior_reduction: Decimal
    class_a1_reduction: Decimal
    subordinate_reduction: Decimal
    class_a1_additional_reduction: Decimal
    offered_reference_tranche_pct: Decimal
    supplemental_reduction: Decimal
    write_down_step: StepResult
    write_up_step: StepResult
    senior_step: StepResult | None
    subordinate_step: StepResult | None
    supplemental_step: StepResult | None
    maturity_payment_by_tranche: dict[str, Decimal]
    balances_before: dict[str, Decimal]
    balances_after: dict[str, Decimal]
    notes: dict[str, NoteCashflow]
    return_amount: Decimal


@dataclass(frozen=True)
class WaterfallResult:
    scenario: Scenario
    records: tuple[PaymentDateRecord, ...]

    @property
    def maturity_payment_date_number(self) -> int:
        return self.records[-1].payment_date_number

    def cumulative_credit_event_amount(self) -> Decimal:
        """Sum of Credit Event Amounts over every Payment Date up to the Maturity Date."""
        return sum((record.pool.credit_event_amount for record in self.records), ZERO)


def _evaluate_tests(
    *,
    n: int,
    deal: DealTerms,
    scenario: Scenario,
    subordinate_pct: Decimal,
    upb_prev: Decimal,
    principal_loss_amount: Decimal,
    cnl_pct: Decimal,
    class_a1_failed_before: bool,
) -> TestOutcomes:
    """The four tests of spec 02 section 3.3 on the 'immediately prior' state."""
    mce = minimum_credit_enhancement_test(
        subordinate_pct, deal.minimum_credit_enhancement_threshold  # P15
    )
    cnl = cumulative_net_loss_test(cnl_pct, n, deal.cumulative_net_loss_test_schedule)  # P52
    if scenario.delinquency_test_satisfied:
        delinquency = True  # Modeling Assumption (e), T10 / P73
    else:
        if scenario.distressed_principal_balance_by_payment_date is None:
            raise PerformanceTestError(
                f"Payment Date {n}: the Delinquency Test flag is false and the Distressed "
                "Principal Balance input is missing; it is never defaulted to zero"
            )
        average = average_distressed_principal_balance(
            scenario.distressed_principal_balance_by_payment_date,
            n,
            deal.delinquency_test_averaging_payment_dates,  # P54
        )
        delinquency = delinquency_test(
            average,
            subordinate_pct,
            upb_prev,
            principal_loss_amount,
            deal.delinquency_test_factor,  # P53
        )
    class_a1 = class_a1_cumulative_net_loss_test(
        cnl_pct,
        deal.class_a1_cumulative_net_loss_threshold,  # P16
        failed_on_a_prior_payment_date=class_a1_failed_before,
    )
    return TestOutcomes(
        minimum_credit_enhancement=mce,
        cumulative_net_loss=cnl,
        delinquency=delinquency,
        class_a1_cumulative_net_loss=class_a1,
    )


def _maturity_reason(n: int, upb_end: Decimal, deal: DealTerms, scenario: Scenario) -> str | None:
    """Spec 02 section 9: why Payment Date ``n`` is the Maturity Date, or None."""
    if upb_end == ZERO:
        return "pool UPB is zero (Early Termination Date clauses (iii)/(iv))"
    if n == deal.scheduled_maturity_payment_date_number:  # P8 / P21
        return "Scheduled Maturity Date"
    if scenario.early_redemption:
        if n == deal.earliest_early_redemption_payment_date_number:  # P64, (m)(i)
            return "Early Redemption Date: February 2031 Payment Date"
        # A11: the UPB at the end of the related Reporting Period is tested (P63, (m)(ii)).
        if upb_end <= deal.clean_up_threshold * deal.cut_off_date_balance:
            return "Early Redemption Date: pool UPB <= 10 % of the Cut-off Date Balance"
    return None


def _class_a1_reduction_amount(
    n: int,
    *,
    class_a1_test_satisfied: bool,
    appendix_g: AppendixG,
    senior_reduction: Decimal,
    recovery_principal_amount: Decimal,
) -> Decimal:
    """Class A-1 Reduction Amount (T41, P60-P62; reading A6): deemed zero when the Class
    A-1 Cumulative Net Loss Test fails; Appendix G through Payment Date 36; limb (B)
    thereafter."""
    if not class_a1_test_satisfied:
        return ZERO
    if n <= CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE:
        return appendix_g.aggregate_for_payment_date(n)
    return senior_reduction - recovery_principal_amount


def _note_cashflows(
    *,
    n: int,
    deal: DealTerms,
    scenario: Scenario,
    prior: dict[str, Decimal],
    state: TrancheState,
    write_down_step: StepResult,
    write_up_step: StepResult,
    principal_by_note: dict[str, Decimal],
) -> dict[str, NoteCashflow]:
    days = accrual_period_days(n, deal.closing_date, deal.first_payment_date)
    cashflows: dict[str, NoteCashflow] = {}
    for note in NOTE_CLASSES:
        terms = deal.notes[note]
        coupon = class_coupon(scenario.sofr_rate, terms.margin, terms.class_coupon_minimum_rate)
        accrual = interest_accrual_amount(prior[note], coupon, days)
        cashflows[note] = NoteCashflow(
            note=note,
            balance_before=prior[note],
            principal_paid=principal_by_note[note],
            write_down=write_down_step.allocated(note),
            write_up=write_up_step.allocated(note),
            balance_after=state.balances[note],
            coupon=coupon,
            accrual_days=days,
            interest_accrual=accrual,
            # P107: minus Modification Loss / plus Modification Gain allocated to interest,
            # both zero in v1 (RM = 0).
            interest_payment=accrual - ZERO + ZERO,
        )
        # Spec 00 section 3.3: Class Principal Balance == Class Notional Amount.
        expected_after = prior[note] - principal_by_note[note] - write_down_step.allocated(
            note
        ) + write_up_step.allocated(note)
        if expected_after != state.balances[note]:
            raise IdentityError(
                f"Payment Date {n}: {note} Class Principal Balance {expected_after} != Class "
                f"Notional Amount {state.balances[note]}"
            )
    return cashflows


def run_waterfall(
    pool: PoolProjection, deal: DealTerms, appendix_g: AppendixG, scenario: Scenario
) -> WaterfallResult:
    """Run the hypothetical structure from Payment Date 1 to the Maturity Date."""
    require_decimal_context()
    if pool.cpr != scenario.cpr or pool.cer != scenario.cer:
        raise WaterfallError("pool projection does not belong to this scenario")
    if pool.cut_off_date_balance != deal.cut_off_date_balance:
        raise WaterfallError("pool projection Cut-off Date Balance differs from the deal terms")

    state = TrancheState.initial(deal.initial_class_notional_amounts)
    cumulative_principal_loss = ZERO
    cumulative_principal_recovery = ZERO
    class_a1_failed_before = False
    records: list[PaymentDateRecord] = []

    for n in range(1, deal.scheduled_maturity_payment_date_number + 1):
        period = pool.payment_period(n)
        prior = state.snapshot()

        # Spec 02 section 2: percentages on the state immediately prior (A5 denominator).
        senior_pct = senior_percentage(prior, period.upb_prev)
        subordinate_pct = subordinate_percentage(senior_pct)

        # Spec 02 section 3.1: losses and recoveries.
        loss_clauses = principal_loss_clauses_v1(
            period.credit_event_amount,
            preliminary_loss_share=deal.preliminary_principal_loss_share_of_credit_event_amount,
        )
        recovery_clauses = principal_recovery_clauses_v1()
        principal_loss = loss_clauses.total()
        principal_recovery = recovery_clauses.total()
        write_down = tranche_write_down_amount(principal_loss, principal_recovery)
        write_up = tranche_write_up_amount(principal_loss, principal_recovery)
        recovery_principal_amount = recovery_principal(
            period.credit_event_amount, write_down, write_up
        )

        # Spec 02 section 3.2: cumulative including this Payment Date.
        cumulative_principal_loss += principal_loss
        cumulative_principal_recovery += principal_recovery
        cnl_pct = cumulative_net_loss_percentage(
            cumulative_principal_loss, cumulative_principal_recovery, deal.cut_off_date_balance
        )

        # Spec 02 section 3.3: the four tests.
        tests = _evaluate_tests(
            n=n,
            deal=deal,
            scenario=scenario,
            subordinate_pct=subordinate_pct,
            upb_prev=period.upb_prev,
            principal_loss_amount=principal_loss,
            cnl_pct=cnl_pct,
            class_a1_failed_before=class_a1_failed_before,
        )
        if not tests.class_a1_cumulative_net_loss:
            class_a1_failed_before = True  # clause (2): permanent

        maturity_reason = _maturity_reason(n, period.upb_end, deal, scenario)

        # Step 1: Tranche Write-down / Write-up Amount (on or prior to the Maturity Date).
        write_down_step = step1_tranche_write_down(
            state,
            prior,
            write_down,
            clause_d_principal_loss=loss_clauses.modification_loss_principal_priorities,
        )
        write_up_step = step1_tranche_write_up(state, prior, write_up)
        a_h_increase = a_h_increase_on_write_down(write_down, period.credit_event_amount)
        state.increase("A-H", a_h_increase)
        # Q19: Stated Principal clause (e) floor excess to A-H (P96); zero in v1, timing
        # within the Payment Date not stated by the spec.
        state.increase("A-H", period.stated_principal_floor_excess_to_a_h)
        return_amount = sum((write_down_step.allocated(note) for note in NOTE_CLASSES), ZERO)

        if maturity_reason is not None:
            # Spec 02 section 9: no Steps 2-4; 100 % of each Class Principal Balance.
            maturity_payment = {name: state.balances[name] for name in TRANCHE_ORDER}
            principal_by_note = {note: state.balances[note] for note in NOTE_CLASSES}
            for name in TRANCHE_ORDER:
                state.reduce(name, state.balances[name])
            notes = _note_cashflows(
                n=n,
                deal=deal,
                scenario=scenario,
                prior=prior,
                state=state,
                write_down_step=write_down_step,
                write_up_step=write_up_step,
                principal_by_note=principal_by_note,
            )
            records.append(
                PaymentDateRecord(
                    payment_date_number=n,
                    payment_date=payment_date(n, deal.first_payment_date),
                    is_maturity_date=True,
                    maturity_reason=maturity_reason,
                    pool=period,
                    senior_pct=senior_pct,
                    subordinate_pct=subordinate_pct,
                    principal_loss_clauses=loss_clauses,
                    principal_recovery_clauses=recovery_clauses,
                    principal_loss_amount=principal_loss,
                    principal_recovery_amount=principal_recovery,
                    tranche_write_down=write_down,
                    tranche_write_up=write_up,
                    recovery_principal=recovery_principal_amount,
                    a_h_increase_on_write_down=a_h_increase,
                    cumulative_net_loss_pct=cnl_pct,
                    cumulative_net_loss_threshold=cumulative_net_loss_threshold(
                        n, deal.cumulative_net_loss_test_schedule
                    ),
                    tests=tests,
                    senior_reduction=ZERO,
                    class_a1_reduction=ZERO,
                    subordinate_reduction=ZERO,
                    class_a1_additional_reduction=ZERO,
                    offered_reference_tranche_pct=ZERO,
                    supplemental_reduction=ZERO,
                    write_down_step=write_down_step,
                    write_up_step=write_up_step,
                    senior_step=None,
                    subordinate_step=None,
                    supplemental_step=None,
                    maturity_payment_by_tranche=maturity_payment,
                    balances_before=prior,
                    balances_after=state.snapshot(),
                    notes=notes,
                    return_amount=return_amount,
                )
            )
            break

        # Step 2: Senior Reduction Amount (spec 02 section 6).
        if tests.subordinate_tests_pass:
            senior_reduction = round2(senior_pct * period.stated_principal) + recovery_principal_amount
        else:
            senior_reduction = period.stated_principal + recovery_principal_amount
        class_a1_reduction = _class_a1_reduction_amount(
            n,
            class_a1_test_satisfied=tests.class_a1_cumulative_net_loss,
            appendix_g=appendix_g,
            senior_reduction=senior_reduction,
            recovery_principal_amount=recovery_principal_amount,
        )
        senior_step = step2_senior_reduction(
            state,
            prior,
            senior_reduction,
            class_a1_reduction=class_a1_reduction,
            class_a1_test_satisfied=tests.class_a1_cumulative_net_loss,
        )

        # Step 3: Subordinate Reduction Amount (spec 02 section 7).
        subordinate_reduction = (
            period.stated_principal + recovery_principal_amount - senior_reduction
        )
        subordinate_step = step3_subordinate_reduction(state, prior, subordinate_reduction)

        # Step 4: Supplemental Reduction Amount (spec 02 section 8), on the balances as
        # reduced by Steps 1-3.
        if (
            n >= CLASS_A1_ADDITIONAL_REDUCTION_START_PAYMENT_DATE  # P59
            and tests.class_a1_cumulative_net_loss
        ):
            class_a1_additional = state.balances["A-1"] + state.balances["A-1H"]
        else:
            class_a1_additional = ZERO
        offered_total = sum((state.balances[name] for name in OFFERED_TRANCHES), ZERO)
        offered_pct = offered_reference_tranche_percentage(
            offered_total, class_a1_additional, period.upb_end
        )
        supplemental_reduction = (
            round2(
                period.upb_end
                * max(ZERO, offered_pct - deal.supplemental_reduction_threshold)  # P58
            )
            + class_a1_additional
        )
        supplemental_step = step4_supplemental_reduction(
            state,
            prior,
            supplemental_reduction,
            class_a1_additional_reduction=class_a1_additional,
        )

        # Spec 00 section 3.3: the twelve Class Notional Amounts sum to the pool UPB.
        structure_total = state.total()
        if structure_total != period.upb_end:
            raise IdentityError(
                f"Payment Date {n}: sum of Class Notional Amounts {structure_total} != pool "
                f"UPB {period.upb_end} (difference {structure_total - period.upb_end})"
            )

        principal_by_note = {
            note: senior_step.allocated(note)
            + subordinate_step.allocated(note)
            + supplemental_step.allocated(note)
            for note in NOTE_CLASSES
        }
        notes = _note_cashflows(
            n=n,
            deal=deal,
            scenario=scenario,
            prior=prior,
            state=state,
            write_down_step=write_down_step,
            write_up_step=write_up_step,
            principal_by_note=principal_by_note,
        )
        records.append(
            PaymentDateRecord(
                payment_date_number=n,
                payment_date=payment_date(n, deal.first_payment_date),
                is_maturity_date=False,
                maturity_reason=None,
                pool=period,
                senior_pct=senior_pct,
                subordinate_pct=subordinate_pct,
                principal_loss_clauses=loss_clauses,
                principal_recovery_clauses=recovery_clauses,
                principal_loss_amount=principal_loss,
                principal_recovery_amount=principal_recovery,
                tranche_write_down=write_down,
                tranche_write_up=write_up,
                recovery_principal=recovery_principal_amount,
                a_h_increase_on_write_down=a_h_increase,
                cumulative_net_loss_pct=cnl_pct,
                cumulative_net_loss_threshold=cumulative_net_loss_threshold(
                    n, deal.cumulative_net_loss_test_schedule
                ),
                tests=tests,
                senior_reduction=senior_reduction,
                class_a1_reduction=class_a1_reduction,
                subordinate_reduction=subordinate_reduction,
                class_a1_additional_reduction=class_a1_additional,
                offered_reference_tranche_pct=offered_pct,
                supplemental_reduction=supplemental_reduction,
                write_down_step=write_down_step,
                write_up_step=write_up_step,
                senior_step=senior_step,
                subordinate_step=subordinate_step,
                supplemental_step=supplemental_step,
                maturity_payment_by_tranche={name: ZERO for name in TRANCHE_ORDER},
                balances_before=prior,
                balances_after=state.snapshot(),
                notes=notes,
                return_amount=return_amount,
            )
        )

    if not records or not records[-1].is_maturity_date:
        raise WaterfallError("the run did not reach a Maturity Date")
    return WaterfallResult(scenario=scenario, records=tuple(records))
