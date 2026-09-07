"""The A-1 WAL hand check of spec 03 section 1 and the register-value assertions of
BRIEF section 8 ("if the YAML says the M-1 margin is X, a test asserts the engine used X").
"""

from __future__ import annotations

import csv
import re
from decimal import Decimal
from pathlib import Path

import pytest

from crt.io.appendix_g import CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE, AppendixG
from crt.io.deal_terms import CLASS_A1_ADDITIONAL_REDUCTION_START_PAYMENT_DATE, DealTerms
from crt.money import round_half_up
from crt.pool.projection import PoolProjection
from crt.scenarios.grid import PPM_CER_AXIS_PCT, PPM_CPR_AXIS_PCT, ppm_grid, ppm_scenario
from crt.tieout.wal import balance_reduction, principal_window, time_fraction, weighted_average_life
from crt.waterfall.engine import run_waterfall
from crt.waterfall.interest import accrual_period_days, class_coupon

pytestmark = pytest.mark.fast

D = Decimal


def _register(root: Path) -> dict[str, str]:
    with (root / "docs/assumptions.csv").open(newline="", encoding="utf-8") as handle:
        return {row["id"]: row["value"] for row in csv.DictReader(handle)}


def test_time_fraction_a9() -> None:
    assert time_fraction(1) == D(38) / D(360)
    assert time_fraction(12) == D(368) / D(360)
    assert time_fraction(60) == D(1808) / D(360)


def test_a1_wal_hand_check(deal: DealTerms, appendix_g: AppendixG, pool_10_0: PoolProjection) -> None:
    scenario = ppm_scenario(
        cpr_pct=D("10"), cer_pct=D("0"), early_redemption=False, sofr_rate=deal.sofr_rate_flat
    )
    result = run_waterfall(pool_10_0, deal, appendix_g, scenario)
    original = deal.notes["A-1"].original_class_principal_balance
    one_cent = D("0.01")
    # The weights come from the waterfall, not from the spec paragraph.  The A8 pair
    # split (ratio of the balances immediately prior to each Payment Date) pays A-1 one
    # cent more than the printed Appendix G column on Payment Dates 3, 5, 7, 9 and 11
    # (Q20), so the weights are exact to the cent, not to the printed percentage.
    for n in range(1, 13):
        assert abs(balance_reduction(result, "A-1", n) - D("0.0375") * original) <= one_cent
    for n in range(13, 37):
        assert balance_reduction(result, "A-1", n) == D("0.0150") * original
    assert abs(balance_reduction(result, "A-1", 37) - D("0.1900") * original) <= 5 * one_cent
    assert balance_reduction(result, "A-1", 38) == D("0")
    assert sum((balance_reduction(result, "A-1", n) for n in range(1, 38)), D(0)) == original
    expected = (
        D("0.0375") * sum((time_fraction(n) for n in range(1, 13)), D(0))
        + D("0.0150") * sum((time_fraction(n) for n in range(13, 37)), D(0))
        + D("0.19") * time_fraction(37)
    )
    wal = weighted_average_life(result, "A-1")
    assert wal is not None
    assert abs(wal - expected) < D("1e-9")  # the five cents move the WAL by 4.5e-10 years
    assert round_half_up(wal, 4) == D("1.5868")
    assert round_half_up(wal, 2) == D("1.59")
    assert principal_window(result, "A-1") == (1, 37)


def test_register_values_used_by_the_engine(project_root: Path, deal: DealTerms, appendix_g: AppendixG) -> None:
    reg = _register(project_root)
    pct = lambda value: D(value).scaleb(-2)

    assert deal.notes["A-1"].margin == pct(reg["P36"]) == D("0.0085")
    assert deal.notes["M-1"].margin == pct(reg["P37"]) == D("0.0100")
    assert deal.notes["M-2A"].margin == pct(reg["P38"]) == D("0.0130")
    assert deal.notes["M-2B"].margin == pct(reg["P39"]) == D("0.0130")
    assert deal.minimum_credit_enhancement_threshold == pct(reg["P15"]) == D("0.03525")
    assert deal.class_a1_cumulative_net_loss_threshold == pct(reg["P16"]) == D("0.0100")
    assert deal.supplemental_reduction_threshold == pct(reg["P58"]) == D("0.0550")
    assert CLASS_A1_ADDITIONAL_REDUCTION_START_PAYMENT_DATE == int(reg["P59"]) == 39
    assert deal.appendix_g_aggregate_payment_dates_1_to_12 == D(reg["P60"])
    assert deal.appendix_g_aggregate_payment_dates_13_to_36 == D(reg["P61"])
    assert appendix_g.aggregate_for_payment_date(1) == D(reg["P60"]) == D("10892238.08")
    assert appendix_g.aggregate_for_payment_date(36) == D(reg["P61"]) == D("4356895.23")
    assert CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE == 36
    assert deal.clean_up_threshold == pct(reg["P63"]) == D("0.10")
    assert deal.sofr_rate_flat == pct(reg["P12"]) == D("0.0365786")
    assert deal.cut_off_date_balance == D(reg["P10"])
    assert deal.closing_date.isoformat() == reg["P1"]
    assert deal.cut_off_date.isoformat() == reg["P9"]
    assert deal.delinquency_test_factor == pct(reg["P53"]) == D("0.50")
    assert deal.delinquency_test_averaging_payment_dates == int(reg["P54"]) == 6
    assert reg["P14"].startswith("25%")
    assert deal.preliminary_principal_loss_share_of_credit_event_amount == D("0.25")
    assert reg["P64"].startswith("2031-02") and deal.earliest_early_redemption_payment_date_number == 60
    assert reg["P8"] == "2046-02" and deal.scheduled_maturity_payment_date_number == 240

    for tranche, row_id in (("A-H", "P24"), ("A-1H", "P25"), ("M-1H", "P26"), ("M-2AH", "P27"),
                            ("M-2BH", "P28"), ("B-1H", "P29"), ("B-2H", "P30"), ("B-3H", "P31"),
                            ("A-1", "P3"), ("M-1", "P4"), ("M-2A", "P5"), ("M-2B", "P6")):
        assert deal.initial_class_notional_amounts[tranche] == D(reg[row_id]), tranche

    # P52: "Mar2026-Feb2027 0.10; Mar2027-Feb2028 0.20; ...; Mar2038+ 1.30"
    thresholds = [D(m) for m in re.findall(r" (\d\.\d\d)(?:;|$)", reg["P52"])]
    assert len(thresholds) == 13
    assert deal.cumulative_net_loss_test_schedule == tuple(t.scaleb(-2) for t in thresholds)

    # T25 / T26: the grid axes.
    assert [str(x) for x in PPM_CPR_AXIS_PCT] == reg["T25"].split("; ")
    cer_rows = re.findall(r"\((\d\.\d\d), 0\.00\)", reg["T26"])
    assert [str(x) for x in PPM_CER_AXIS_PCT] == cer_rows
    assert len(ppm_grid(sofr_rate=deal.sofr_rate_flat)) == 96


def test_coupon_and_accrual_period(deal: DealTerms) -> None:
    assert class_coupon(deal.sofr_rate_flat, deal.notes["M-1"].margin, D("0")) == D("0.0465786")
    assert class_coupon(D("-0.05"), deal.notes["A-1"].margin, D("0")) == D("0")  # P7 floor
    assert accrual_period_days(1, deal.closing_date, deal.first_payment_date) == 36
    assert accrual_period_days(2, deal.closing_date, deal.first_payment_date) == 31
    # Payment Date 13 is 2027-03-25; its Accrual Period runs from 2027-02-25: 28 days.
    assert accrual_period_days(13, deal.closing_date, deal.first_payment_date) == 28
