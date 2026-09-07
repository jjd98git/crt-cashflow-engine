"""Spec 02-waterfall.md section 12 worked examples (Payment Dates 1 and 2, the synthetic
$1,000,000 Credit Event), the Senior Percentage knife-edge, the Appendix G pair split,
and the synthetic Supplemental Reduction limbs."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from crt.io.appendix_g import AppendixG
from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER, DealTerms
from crt.pool.projection import PoolProjection
from crt.scenarios.grid import ppm_scenario
from crt.scenarios.scenario import Scenario, ScenarioError
from crt.tieout.wal import principal_window
from crt.waterfall.allocation import allocate_pair, split_pair
from crt.waterfall.engine import WaterfallResult, run_waterfall
from crt.waterfall.percentages import senior_percentage, subordinate_percentage
from crt.waterfall.performance_tests import (
    PerformanceTestError,
    cumulative_net_loss_threshold,
    minimum_credit_enhancement_test,
)
from crt.waterfall.steps import step4_supplemental_reduction
from crt.waterfall.tranches import TrancheState

pytestmark = pytest.mark.fast

D = Decimal

AFTER_PD1 = {
    "A-H": "21276215056.99",
    "A-1": "265553750.00",
    "A-1H": "14013693.92",
    "M-1": "261242340.09",
    "M-1H": "13786173.96",
    "M-2A": "37850000",
    "M-2AH": "2017015",
    "M-2B": "37850000",
    "M-2BH": "2017015",
    "B-1H": "102515181",
    "B-2H": "273373818",
    "B-3H": "56953878",
}
AFTER_PD2 = {
    "A-H": "21078800619.58",
    "A-1": "255207500.00",
    "A-1H": "13467705.84",
    "M-1": "254012755.15",
    "M-1H": "13404657.26",
}


@pytest.fixture(scope="module")
def result_10_0(deal: DealTerms, appendix_g: AppendixG, pool_10_0: PoolProjection) -> WaterfallResult:
    scenario = ppm_scenario(
        cpr_pct=D("10"), cer_pct=D("0"), early_redemption=False, sofr_rate=deal.sofr_rate_flat
    )
    return run_waterfall(pool_10_0, deal, appendix_g, scenario)


def test_senior_percentage_knife_edge(deal: DealTerms) -> None:
    senior = senior_percentage(deal.initial_class_notional_amounts, deal.cut_off_date_balance)
    assert senior == D("0.9647500")
    sub = subordinate_percentage(senior)
    assert sub == D("0.0352500")
    assert minimum_credit_enhancement_test(sub, deal.minimum_credit_enhancement_threshold)


def test_allocate_pair_reproduces_appendix_g_columns(deal: DealTerms) -> None:
    state = TrancheState.initial(deal.initial_class_notional_amounts)
    prior = state.snapshot()
    allocation = allocate_pair(state, prior, "A-1", D("10892238.08"))
    assert allocation.note_amount == D("10346250.00")
    assert allocation.h_amount == D("545988.08")
    allocation = allocate_pair(state, prior, "A-1", D("4356895.23"))
    assert allocation.note_amount == D("4138500.00")
    assert allocation.h_amount == D("218395.23")


def test_split_pair_sends_everything_to_the_other_member_when_one_is_zero() -> None:
    allocation = split_pair(
        D("100.00"), note_prior=D("900"), h_prior=D("100"), note_current=D("0"), h_current=D("50")
    )
    assert (allocation.note_amount, allocation.h_amount) == (D("0"), D("50"))


def test_payment_date_1_worked_example(result_10_0: WaterfallResult) -> None:
    record = result_10_0.records[0]
    assert record.payment_date.isoformat() == "2026-03-25"
    assert record.senior_pct == D("0.9647500")
    assert record.subordinate_pct == D("0.0352500")
    assert record.principal_loss_amount == D("0")
    assert record.tranche_write_down == D("0")
    assert record.recovery_principal == D("0")
    assert record.cumulative_net_loss_pct == D("0.0000000")
    assert record.tests.subordinate_tests_pass and record.tests.class_a1_cumulative_net_loss
    assert record.senior_reduction == D("422332461.93")
    assert record.class_a1_reduction == D("10892238.08")
    assert record.senior_step is not None
    assert record.senior_step.allocated("A-1") == D("10346250.00")
    assert record.senior_step.allocated("A-1H") == D("545988.08")
    assert record.senior_step.allocated("A-H") == D("411440223.85")
    assert record.subordinate_reduction == D("15431167.95")
    assert record.subordinate_step is not None
    assert record.subordinate_step.allocated("M-1") == D("14657659.91")
    assert record.subordinate_step.allocated("M-1H") == D("773508.04")
    assert record.class_a1_additional_reduction == D("0")
    assert record.offered_reference_tranche_pct == D("0.0283901")
    assert record.supplemental_reduction == D("0")
    for tranche in TRANCHE_ORDER:
        assert record.balances_after[tranche] == D(AFTER_PD1[tranche]), tranche
    assert sum(record.balances_after.values()) == D("22343387921.96")


def test_payment_date_1_note_cashflows(result_10_0: WaterfallResult) -> None:
    notes = result_10_0.records[0].notes
    expected = {
        "A-1": ("10346250.00", "265553750.00", "0.0450786", "1243718.57"),
        "M-1": ("14657659.91", "261242340.09", "0.0465786", "1285103.57"),
        "M-2A": ("0", "37850000", "0.0495786", "187655.00"),
        "M-2B": ("0", "37850000", "0.0495786", "187655.00"),
    }
    for note, (principal, balance, coupon, interest) in expected.items():
        cashflow = notes[note]
        assert cashflow.principal_paid == D(principal), note
        assert cashflow.write_down == D("0")
        assert cashflow.balance_after == D(balance), note
        assert cashflow.coupon == D(coupon), note
        assert cashflow.accrual_days == 36
        assert cashflow.interest_accrual == D(interest), note
        assert cashflow.interest_payment == D(interest), note


def test_payment_date_2_worked_example(result_10_0: WaterfallResult) -> None:
    # Spec 02 section 12 Payment Date 2 as revised 2026-09-07 under Q21 (five cents moved).
    record = result_10_0.records[1]
    assert record.payment_date.isoformat() == "2026-04-25"
    assert record.senior_pct == D("0.9647500")
    assert record.senior_reduction == D("208306675.49")
    assert record.senior_step is not None
    assert record.senior_step.allocated("A-1") == D("10346250.00")
    assert record.senior_step.allocated("A-1H") == D("545988.08")
    assert record.senior_step.allocated("A-H") == D("197414437.41")
    assert record.subordinate_reduction == D("7611101.64")
    assert record.subordinate_step is not None
    assert record.subordinate_step.allocated("M-1") == D("7229584.94")
    assert record.subordinate_step.allocated("M-1H") == D("381516.70")
    assert record.offered_reference_tranche_pct == D("0.0278309")
    for tranche, balance in AFTER_PD2.items():
        assert record.balances_after[tranche] == D(balance), tranche
    assert sum(record.balances_after.values()) == D("22127470144.83")
    assert record.notes["A-1"].accrual_days == 31
    for note in NOTE_CLASSES:
        assert record.notes[note].balance_after == record.balances_after[note]


def _pool_with_synthetic_credit_event(pool: PoolProjection, amount: Decimal) -> PoolProjection:
    """The spec's synthetic case: Credit Event Amount of ``amount`` on Payment Date 1 with
    the same pool numbers; the pool would have lost the Credit Event UPB, so every later
    UPB is lower by ``amount`` to keep the pool identity."""
    periods = list(pool.payment_periods)
    periods[0] = replace(
        periods[0], credit_event_amount=amount, upb_end=periods[0].upb_end - amount
    )
    for index in range(1, len(periods)):
        periods[index] = replace(
            periods[index],
            upb_end=periods[index].upb_end - amount,
            upb_prev=periods[index].upb_prev - amount,
        )
    return replace(pool, payment_periods=tuple(periods))


def test_synthetic_one_million_credit_event(
    deal: DealTerms, appendix_g: AppendixG, pool_10_0: PoolProjection
) -> None:
    pool = _pool_with_synthetic_credit_event(pool_10_0, D("1000000.00"))
    scenario = ppm_scenario(
        cpr_pct=D("10"), cer_pct=D("0"), early_redemption=False, sofr_rate=deal.sofr_rate_flat
    )
    record = run_waterfall(pool, deal, appendix_g, scenario).records[0]
    assert record.principal_loss_amount == D("250000.00")
    assert record.principal_recovery_amount == D("0")
    assert record.tranche_write_down == D("250000.00")
    assert record.write_down_step.allocated("B-3H") == D("250000.00")
    assert record.write_down_step.total_allocated() == D("250000.00")
    assert record.recovery_principal == D("750000.00")
    assert record.a_h_increase_on_write_down == D("0")
    assert record.senior_reduction == D("422332461.93") + D("750000.00")
    assert record.return_amount == D("0")
    assert sum(record.balances_after.values()) == D("22343387921.96") - D("1000000.00")
    assert record.balances_after["B-3H"] == D("56953878") - D("250000.00")


def test_delinquency_test_flag_false_without_input_raises(
    deal: DealTerms, appendix_g: AppendixG, pool_10_0: PoolProjection
) -> None:
    scenario = Scenario(
        cpr=D("0.10"), cer=D("0"), rm=D("0"), early_redemption=False,
        delinquency_test_satisfied=False, sofr_rate=deal.sofr_rate_flat,
    )
    with pytest.raises(PerformanceTestError, match="Distressed Principal Balance"):
        run_waterfall(pool_10_0, deal, appendix_g, scenario)


def test_scenario_rejects_rm_and_out_of_range_rates(deal: DealTerms) -> None:
    with pytest.raises(ScenarioError):
        Scenario(cpr=D("0.10"), cer=D("0"), rm=D("0.0001"), early_redemption=False,
                 delinquency_test_satisfied=True, sofr_rate=deal.sofr_rate_flat)
    with pytest.raises(ScenarioError):
        Scenario(cpr=D("1"), cer=D("0"), rm=D("0"), early_redemption=False,
                 delinquency_test_satisfied=True, sofr_rate=deal.sofr_rate_flat)


def test_cumulative_net_loss_threshold_bands(deal: DealTerms) -> None:
    schedule = deal.cumulative_net_loss_test_schedule
    assert cumulative_net_loss_threshold(1, schedule) == D("0.0010")
    assert cumulative_net_loss_threshold(12, schedule) == D("0.0010")
    assert cumulative_net_loss_threshold(13, schedule) == D("0.0020")
    assert cumulative_net_loss_threshold(144, schedule) == D("0.0120")
    assert cumulative_net_loss_threshold(145, schedule) == D("0.0130")
    assert cumulative_net_loss_threshold(240, schedule) == D("0.0130")


def test_supplemental_reduction_5_50_limb_synthetic(deal: DealTerms) -> None:
    # Synthetic: offered tranches at 6.00 % of a $1bn pool -> 0.50 % x UPB = $5,000,000
    # is allocated M-1 first (spec 02 section 8) and A-H grows by the same amount.
    balances = {name: D("0") for name in TRANCHE_ORDER}
    balances.update({"A-H": D("940000000.00"), "M-1": D("57000000.00"), "M-1H": D("3000000.00")})
    state = TrancheState.initial(balances)
    prior = state.snapshot()
    upb_end = D("1000000000.00")
    offered = D("60000000.00")
    offered_pct = (offered / upb_end).quantize(D("0.0000001"))
    assert offered_pct == D("0.0600000")
    supplemental = (upb_end * (offered_pct - deal.supplemental_reduction_threshold)).quantize(D("0.01"))
    assert supplemental == D("5000000.00")
    step = step4_supplemental_reduction(state, prior, supplemental, class_a1_additional_reduction=D("0"))
    assert step.allocated("M-1") == D("4750000.00")
    assert step.allocated("M-1H") == D("250000.00")
    assert state.balances["A-H"] == D("945000000.00")
    assert state.total() == upb_end


def test_supplemental_reduction_payment_date_39_limb_synthetic(deal: DealTerms) -> None:
    balances = {name: D("0") for name in TRANCHE_ORDER}
    balances.update({"A-H": D("900000000.00"), "A-1": D("9500000.00"), "A-1H": D("500000.00")})
    state = TrancheState.initial(balances)
    prior = state.snapshot()
    class_a1_additional = state.balances["A-1"] + state.balances["A-1H"]
    step = step4_supplemental_reduction(
        state, prior, class_a1_additional, class_a1_additional_reduction=class_a1_additional
    )
    assert step.allocated("A-1") == D("9500000.00")
    assert step.allocated("A-1H") == D("500000.00")
    assert state.balances["A-1"] == D("0") and state.balances["A-1H"] == D("0")
    assert state.balances["A-H"] == D("910000000.00")


def test_zero_cpr_retires_a1_on_payment_date_39(
    deal: DealTerms, appendix_g: AppendixG, rep_lines_pool_0_0: PoolProjection
) -> None:
    scenario = ppm_scenario(
        cpr_pct=D("0"), cer_pct=D("0"), early_redemption=False, sofr_rate=deal.sofr_rate_flat
    )
    result = run_waterfall(rep_lines_pool_0_0, deal, appendix_g, scenario)
    record_38 = result.records[37]
    record_39 = result.records[38]
    assert record_38.balances_after["A-1"] > 0
    # From Payment Date 37 limb (B) makes the Class A-1 Reduction Amount the whole Senior
    # Reduction Amount, so Step 2 priority 1 retires A-1/A-1H on Payment Date 39 before
    # Step 4 runs; the Class A-1 Additional Reduction Amount then finds nothing left.
    assert record_39.class_a1_reduction == record_39.senior_reduction
    assert record_39.senior_step is not None
    assert record_39.senior_step.allocated("A-1") == record_38.balances_after["A-1"]
    assert record_39.senior_step.allocated("A-1H") == record_38.balances_after["A-1H"]
    assert record_39.class_a1_additional_reduction == D("0")
    assert record_39.balances_after["A-1"] == D("0")
    assert record_39.balances_after["A-1H"] == D("0")
    assert principal_window(result, "A-1") == (1, 39)
