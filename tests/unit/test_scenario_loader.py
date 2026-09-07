"""Scenario YAML files: the two examples load; malformed files and vector schedules the
engine cannot honour are rejected with a message naming the file and the field."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from crt.scenarios.loader import (
    FlatVector,
    RampVector,
    ScenarioFileError,
    ScenarioVectorUnsupportedError,
    StepVector,
    load_scenario,
    load_scenario_file,
    scenario_as_dict,
)
from crt.scenarios.scenario import ScenarioError

pytestmark = pytest.mark.fast

D = Decimal

VALID = """\
name: unit
cpr_pct: 10
cer_pct: 0.25
sofr_pct: 3.65786
early_redemption: true
delinquency_test_satisfied: true
"""


def _write(tmp_path: Path, text: str, name: str = "s.yaml") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_example_files_load(project_root: Path) -> None:
    pricing = load_scenario(project_root / "scenarios/pricing_speed.yaml")
    assert (pricing.cpr, pricing.cer, pricing.early_redemption) == (D("0.10"), D("0.00"), True)
    assert pricing.sofr_rate == D("0.0365786")
    assert pricing.delinquency_test_satisfied is True
    stress = load_scenario(project_root / "scenarios/stress_5cpr_2_5cer.yaml")
    assert (stress.cpr, stress.cer, stress.early_redemption) == (D("0.05"), D("0.0250"), False)
    stress_file = load_scenario_file(project_root / "scenarios/stress_5cpr_2_5cer.yaml")
    assert stress_file.name == "stress-5cpr-2.5cer"
    assert isinstance(stress_file.cpr_pct, FlatVector)


def test_values_are_decimal_never_float(tmp_path: Path) -> None:
    scenario = load_scenario(_write(tmp_path, VALID))
    assert isinstance(scenario.cer, Decimal) and scenario.cer == D("0.0025")
    assert scenario_as_dict(scenario)["cer_pct"] == "0.25"


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (VALID.replace("cer_pct: 0.25\n", ""), "missing required field(s) ['cer_pct']"),
        (VALID + "cdr_pct: 1\n", "unknown field(s) ['cdr_pct']"),
        (VALID.replace("cpr_pct: 10", "cpr_pct: '10'"), "field 'cpr_pct' must be a number"),
        (VALID.replace("cpr_pct: 10", "cpr_pct: 100"), "0 <= value < 100"),
        (VALID.replace("early_redemption: true", "early_redemption: yes please"), "true or false"),
        (VALID + "rm_pct: 1\n", "'rm_pct' = 1 is not supported in v1"),
        (VALID.replace("delinquency_test_satisfied: true", "delinquency_test_satisfied: false"),
         "'distressed_principal_balance_usd_by_payment_date' is required"),
        ("- just\n- a list\n", "top level must be a mapping"),
        ("name: [unterminated\n", "not valid YAML"),
        (VALID.replace("cpr_pct: 10", "cpr_pct: {kind: bumpy, value_pct: 1}"), "'kind' must be one of"),
        (VALID.replace("cpr_pct: 10", "cpr_pct: {kind: ramp, start_pct: 6, end_pct: 18}"),
         "missing key(s) ['over_months']"),
        (VALID.replace("cpr_pct: 10",
                       "cpr_pct: {kind: steps, steps: [{from_month: 2, value_pct: 5}]}"),
         "must start at from_month 1"),
        (VALID.replace("cpr_pct: 10",
                       "cpr_pct: {kind: steps, steps: [{from_month: 1, value_pct: 5}, "
                       "{from_month: 1, value_pct: 6}]}"),
         "strictly increasing"),
    ],
)
def test_malformed_files_are_rejected_with_a_specific_message(
    tmp_path: Path, text: str, message: str
) -> None:
    path = _write(tmp_path, text)
    with pytest.raises(ScenarioFileError) as excinfo:
        load_scenario_file(path)
    assert str(path) in str(excinfo.value)
    assert message in str(excinfo.value)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ScenarioFileError, match="scenario file not found"):
        load_scenario(tmp_path / "nope.yaml")


def test_vector_files_validate_but_are_rejected_by_the_engine(tmp_path: Path) -> None:
    ramp = _write(
        tmp_path,
        VALID.replace("cpr_pct: 10", "cpr_pct: {kind: ramp, start_pct: 6, end_pct: 18, over_months: 12}"),
        "ramp.yaml",
    )
    scenario_file = load_scenario_file(ramp)
    assert scenario_file.cpr_pct == RampVector(start_pct=D(6), end_pct=D(18), over_months=12)
    with pytest.raises(ScenarioVectorUnsupportedError) as excinfo:
        scenario_file.to_scenario()
    assert "field 'cpr_pct' is a 'ramp' vector" in str(excinfo.value)
    assert "rejected rather than flattened" in str(excinfo.value)

    steps = _write(
        tmp_path,
        VALID.replace(
            "cer_pct: 0.25",
            "cer_pct: {kind: steps, steps: [{from_month: 1, value_pct: 0.5}, "
            "{from_month: 13, value_pct: 1.0}]}",
        ),
        "steps.yaml",
    )
    scenario_file = load_scenario_file(steps)
    assert isinstance(scenario_file.cer_pct, StepVector)
    assert [s.from_month for s in scenario_file.cer_pct.steps] == [1, 13]
    with pytest.raises(ScenarioVectorUnsupportedError, match="field 'cer_pct' is a 'steps' vector"):
        load_scenario(steps)

    # A ramp whose end point is out of range is malformed, not merely unsupported.
    bad_ramp = _write(
        tmp_path,
        VALID.replace("cpr_pct: 10", "cpr_pct: {kind: ramp, start_pct: 6, end_pct: 100, over_months: 12}"),
        "bad_ramp.yaml",
    )
    with pytest.raises(ScenarioFileError, match="value 100 % must satisfy"):
        load_scenario_file(bad_ramp)

    # The long flat form is honoured.
    flat = _write(tmp_path, VALID.replace("cpr_pct: 10", "cpr_pct: {kind: flat, value_pct: 15}"), "flat.yaml")
    assert load_scenario(flat).cpr == D("0.15")


def test_loader_errors_are_scenario_errors() -> None:
    assert issubclass(ScenarioFileError, ScenarioError)
    assert issubclass(ScenarioVectorUnsupportedError, ScenarioFileError)
