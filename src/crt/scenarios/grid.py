"""The PPM scenario grid (spec ``00-overview.md`` section 1; register T25, T26, T18)."""

from __future__ import annotations

from decimal import Decimal

from crt.money import percent_to_fraction
from crt.scenarios.scenario import Scenario

# T25: CPR columns of every PPM table, in percent.
PPM_CPR_AXIS_PCT: tuple[Decimal, ...] = tuple(Decimal(x) for x in ("0", "5", "10", "15", "25", "35"))
# T26: CER rows with RM = 0 of the WAL tables (and every row of the Credit Event
# Sensitivity tables), in percent.
PPM_CER_AXIS_PCT: tuple[Decimal, ...] = tuple(
    Decimal(x) for x in ("0.00", "0.25", "0.50", "1.00", "1.50", "2.50", "3.00", "5.00")
)
# T18: the two bases printed for every WAL and Credit Event Sensitivity cell.
PPM_EARLY_REDEMPTION_AXIS: tuple[bool, ...] = (False, True)
PRICING_SPEED_CPR_PCT = Decimal(10)  # P65


def ppm_scenario(
    *, cpr_pct: Decimal, cer_pct: Decimal, early_redemption: bool, sofr_rate: Decimal
) -> Scenario:
    """One PPM grid point under Modeling Assumptions (a)-(s)."""
    return Scenario(
        cpr=percent_to_fraction(cpr_pct),
        cer=percent_to_fraction(cer_pct),
        rm=Decimal(0),  # T26 / T16: RM = 0 rows only in v1
        early_redemption=early_redemption,
        delinquency_test_satisfied=True,  # T10 / P73: Modeling Assumption (e)
        sofr_rate=sofr_rate,
    )


def ppm_grid(*, sofr_rate: Decimal) -> tuple[Scenario, ...]:
    """6 CPR x 8 CER x 2 bases = 96 scenarios, CER-major within CPR so that the pool
    projection cache (keyed by CPR and CER) is reused by both bases back to back."""
    scenarios: list[Scenario] = []
    for cpr_pct in PPM_CPR_AXIS_PCT:
        for cer_pct in PPM_CER_AXIS_PCT:
            for early_redemption in PPM_EARLY_REDEMPTION_AXIS:
                scenarios.append(
                    ppm_scenario(
                        cpr_pct=cpr_pct,
                        cer_pct=cer_pct,
                        early_redemption=early_redemption,
                        sofr_rate=sofr_rate,
                    )
                )
    return tuple(scenarios)
