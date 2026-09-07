"""Spec 01-pool.md section 9 worked examples (as revised 2026-09-07 under Q21), to the
cent, the section 7 pool interest identity, and the rate conversions."""

from __future__ import annotations

from decimal import Decimal

import pytest

from crt.io.deal_terms import DealTerms
from crt.io.rep_lines import RepLine
from crt.pool.projection import PoolProjection, collection_months_for_payment_date, project_pool
from crt.pool.rates import RateError, mdr_from_cer, smm_from_cpr
from crt.pool.rep_line import monthly_rate, project_rep_line_month

pytestmark = pytest.mark.fast

D = Decimal


def test_smm_and_mdr_match_the_spec_reference_values() -> None:
    # Spec 01 section 2 reference values (40-digit context); 28 digits agree on the prefix.
    assert str(smm_from_cpr(D("0.10"))).startswith("0.008741610954696705")
    assert str(mdr_from_cer(D("0.01"))).startswith("0.000837177359120559")
    assert smm_from_cpr(D("0")) == D("0")
    assert mdr_from_cer(D("0")) == D("0")
    with pytest.raises(RateError):
        smm_from_cpr(D("1"))
    with pytest.raises(RateError):
        mdr_from_cer(D("-0.01"))


def test_rep_line_17_month_1_and_2_every_intermediate() -> None:
    # Inputs of spec 01 section 9: B = 5,703,897,138.22, N = 350, rate 6.933 %.
    rate = monthly_rate(D("0.06933"))
    assert rate == D("0.0057775")
    smm = smm_from_cpr(D("0.10"))
    mdr = mdr_from_cer(D("0"))

    month1 = project_rep_line_month(
        group=17, month=1, balance=D("5703897138.22"), remaining_term=350,
        rate=rate, smm=smm, mdr=mdr,
    )
    # Spec 01 section 9 as revised 2026-09-07 (Q21): P1-P5 on the beginning balance.
    assert month1.credit_event_amount == D("0.00")  # P1
    assert month1.prepayment == D("49861249.71")  # P2
    # P3: Bs = 5,654,035,888.51
    assert month1.balance_begin - month1.credit_event_amount - month1.prepayment == D("5654035888.51")
    assert month1.scheduled_payment == D("37683632.42")  # P4
    assert month1.interest == D("32666192.35")  # P4
    assert month1.scheduled_principal == D("5017440.07")  # P5
    assert month1.balance_end == D("5649018448.44")
    assert month1.remaining_term_end == 349
    # Section 7: 30 days' interest on the prepayment, by hand:
    # 49,861,249.71 x 0.0057775 = 288,073.3701995... -> 288,073.37.
    assert month1.prepayment_interest == D("288073.37")

    month2 = project_rep_line_month(
        group=17, month=2, balance=month1.balance_end, remaining_term=349,
        rate=rate, smm=smm, mdr=mdr,
    )
    assert month2.credit_event_amount == D("0.00")
    assert month2.prepayment == D("49381521.55")
    assert month2.balance_begin - month2.credit_event_amount - month2.prepayment == D("5599636926.89")
    assert month2.scheduled_payment == D("37354216.77")
    assert month2.interest == D("32351902.35")
    assert month2.scheduled_principal == D("5002314.42")
    assert month2.balance_end == D("5594634612.47")
    assert month2.remaining_term_end == 348
    # 49,381,521.55 x 0.0057775 = 285,301.7407551... -> 285,301.74.
    assert month2.prepayment_interest == D("285301.74")

    contribution = (
        month1.scheduled_principal + month1.prepayment
        + month2.scheduled_principal + month2.prepayment
    )
    assert contribution == D("109262525.75")


def test_pool_totals_months_1_to_3_and_payment_date_aggregates(pool_10_0: PoolProjection) -> None:
    # Spec 01 section 9 pool totals at 10 % CPR, 0 % CER (revised 2026-09-07 under Q21).
    expected = {
        1: ("20731726.12", "199143963.97", "0.00", "22561275861.75"),
        2: ("20666043.58", "197221896.21", "0.00", "22343387921.96"),
        3: ("20600572.48", "195317204.65", "0.00", "22127470144.83"),
    }
    for month, (sched, prepay, ce, upb) in expected.items():
        pm = pool_10_0.months[month - 1]
        assert pm.month == month
        assert pm.scheduled_principal == D(sched)
        assert pm.prepayment == D(prepay)
        assert pm.credit_event_amount == D(ce)
        assert pm.upb_end == D(upb)

    pd1 = pool_10_0.payment_period(1)
    assert pd1.collection_months == (1, 2)
    assert pd1.stated_principal == D("437763629.88")
    assert pd1.upb_end == D("22343387921.96")
    assert pd1.upb_prev == D("22781151551.84")
    assert pd1.credit_event_amount == D("0.00")
    assert pd1.stated_principal_floor_excess_to_a_h == D("0")

    pd2 = pool_10_0.payment_period(2)
    assert pd2.collection_months == (3,)
    assert pd2.stated_principal == D("215917777.13")
    assert pd2.upb_end == D("22127470144.83")
    assert pd2.upb_prev == D("22343387921.96")

    assert len(pool_10_0.months) == 241
    assert len(pool_10_0.payment_periods) == 240
    assert pool_10_0.payment_period(240).collection_months == (241,)


def test_rep_line_17_month_1_credit_event_hand_case(
    deal: DealTerms, rep_lines: tuple[RepLine, ...]
) -> None:
    # Spec 01 section 9, credit-event hand case: group 17, month 1, 10 % CPR, 1 % CER.
    rate = monthly_rate(D("0.06933"))
    smm = smm_from_cpr(D("0.10"))
    mdr = mdr_from_cer(D("0.01"))
    month1 = project_rep_line_month(
        group=17, month=1, balance=D("5703897138.22"), remaining_term=350,
        rate=rate, smm=smm, mdr=mdr,
    )
    assert month1.credit_event_amount == D("4775173.54")  # P1: round2(B x MDR)
    assert month1.prepayment == D("49861249.71")  # P2: unchanged from the CER 0 case
    assert month1.balance_begin - month1.credit_event_amount - month1.prepayment == D("5649260714.97")
    assert month1.scheduled_payment == D("37651806.33")
    assert month1.interest == D("32638603.78")
    assert month1.scheduled_principal == D("5013202.55")
    assert month1.balance_end == D("5644247512.42")
    assert month1.remaining_term_end == 349

    # Pool month 1 for the same scenario (spec 01 section 9).
    pool = project_pool(
        rep_lines, cpr=D("0.10"), cer=D("0.01"), cut_off_date_balance=deal.cut_off_date_balance
    )
    pm = pool.months[0]
    assert pm.scheduled_principal == D("20714216.91")
    assert pm.prepayment == D("199143963.97")
    assert pm.credit_event_amount == D("19071864.30")
    assert pm.upb_end == D("22542221506.66")
    assert pool.payment_period(1).credit_event_amount == pm.credit_event_amount + pool.months[1].credit_event_amount


def test_pool_interest_is_survivor_interest_plus_prepayment_interest(
    pool_10_0: PoolProjection,
) -> None:
    # Spec 01 section 7: PoolInterest[m] = Int[m] + sum_i round2(Prepay[i,m] x r[i]).
    for pm, rows in zip(pool_10_0.months, zip(*pool_10_0.rep_line_months, strict=True), strict=True):
        assert pm.interest == sum((r.interest for r in rows), D(0))
        assert pm.prepayment_interest == sum((r.prepayment_interest for r in rows), D(0))
        assert pm.pool_interest == pm.interest + pm.prepayment_interest
    # Group 17 month 1 (spec 01 section 9 / hand value above): 32,666,192.35 + 288,073.37.
    line17 = pool_10_0.rep_line_months[16][0]
    assert line17.group == 17
    assert line17.interest + line17.prepayment_interest == D("32954265.72")


def test_zero_cpr_zero_cer_level_pay_identity(
    deal: DealTerms, rep_lines: tuple[RepLine, ...]
) -> None:
    pool = project_pool(
        rep_lines, cpr=D("0"), cer=D("0"), cut_off_date_balance=deal.cut_off_date_balance
    )
    line17 = pool.rep_line_months[16]
    assert line17[0].group == 17
    assert line17[0].scheduled_payment == D("38015953.09")
    # Spec 01 section 9: the recomputed payment is unchanged in month 2 (exact engine value).
    assert line17[1].scheduled_payment == D("38015953.09")
    for month in pool.months:
        assert month.prepayment == D("0")
        assert month.credit_event_amount == D("0")


def test_collection_month_mapping_a4() -> None:
    assert collection_months_for_payment_date(1) == (1, 2)
    assert collection_months_for_payment_date(2) == (3,)
    assert collection_months_for_payment_date(240) == (241,)


def test_rep_line_month_identity_holds_for_every_line_and_month(pool_10_0: PoolProjection) -> None:
    for history in pool_10_0.rep_line_months:
        for row in history:
            assert row.balance_end == (
                row.balance_begin - row.scheduled_principal - row.credit_event_amount - row.prepayment
            )
            assert row.balance_end >= 0
