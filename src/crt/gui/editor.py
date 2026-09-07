"""The scenario editor widget: PPM grid values selectable, free-form override, and the
``Scenario`` class's own validation messages shown verbatim (never swallowed)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

import streamlit as st

from crt.scenarios.grid import PPM_CER_AXIS_PCT, PPM_CPR_AXIS_PCT
from crt.scenarios.loader import (
    FlatVector,
    ScenarioFile,
    ScenarioFileError,
    load_scenario_file,
    scenario_from_values,
)
from crt.scenarios.scenario import Scenario, ScenarioError

CUSTOM = "Custom…"


@dataclass(frozen=True)
class EditorDefaults:
    """Initial widget values; taken from a scenario file or typed by the user."""

    name: str
    cpr_pct: str
    cer_pct: str
    sofr_pct: str
    early_redemption: bool
    delinquency_test_satisfied: bool
    source: Path | None


@dataclass(frozen=True)
class EditorOutput:
    scenario: Scenario | None  # None when a value failed validation (shown to the user)
    name: str
    source: Path | None


def defaults_from_file(path: Path) -> EditorDefaults:
    """Flat values of a scenario file as editor defaults.  Vector files load for display
    of their name but the editor cannot represent them; the message is shown to the user."""
    scenario_file = load_scenario_file(path)

    def flat(key: str) -> str:
        vector = scenario_file.vector(key)
        if not isinstance(vector, FlatVector):
            raise ScenarioFileError(
                f"{path}: field {key!r} is a {vector.kind!r} vector; the editor shows flat "
                "values only"
            )
        return format(vector.value_pct, "f")

    return EditorDefaults(
        name=scenario_file.name,
        cpr_pct=flat("cpr_pct"),
        cer_pct=flat("cer_pct"),
        sofr_pct=flat("sofr_pct"),
        early_redemption=scenario_file.early_redemption,
        delinquency_test_satisfied=scenario_file.delinquency_test_satisfied,
        source=path,
    )


def scenario_files(directory: Path) -> tuple[Path, ...]:
    if not directory.is_dir():
        return ()
    return tuple(sorted(directory.glob("*.yaml")))


def _grid_or_custom(
    label: str, axis: tuple[Decimal, ...], default: str, key: str, help_text: str
) -> str:
    """A selectbox over the PPM grid plus a free-form text override.  Returns the text."""
    options = [format(value, "f") for value in axis] + [CUSTOM]
    normalised_default = _normalise(default)
    matching = [o for o in options[:-1] if _normalise(o) == normalised_default]
    index = options.index(matching[0]) if matching else len(options) - 1
    choice = st.selectbox(label, options, index=index, key=f"{key}_grid", help=help_text)
    if choice == CUSTOM:
        return st.text_input(f"{label} override (percent)", value=default, key=f"{key}_custom")
    return choice


def _normalise(text: str) -> str:
    try:
        return format(Decimal(text.strip()).normalize(), "f")
    except InvalidOperation:
        return text.strip()


def _parse_percent(text: str, field: str) -> Decimal | None:
    try:
        return Decimal(text.strip())
    except InvalidOperation:
        st.error(f"{field}: {text!r} is not a number (write percentages such as 7.5)")
        return None


def scenario_editor(key: str, defaults: EditorDefaults) -> EditorOutput:
    name = st.text_input("Scenario name", value=defaults.name, key=f"{key}_name")
    cpr_text = _grid_or_custom(
        "CPR (%)", PPM_CPR_AXIS_PCT, defaults.cpr_pct, f"{key}_cpr", "PPM grid values (T25)"
    )
    cer_text = _grid_or_custom(
        "CER (%)", PPM_CER_AXIS_PCT, defaults.cer_pct, f"{key}_cer", "PPM grid values (T26, RM = 0)"
    )
    sofr_text = st.text_input(
        "SOFR Rate (%, flat)",
        value=defaults.sofr_pct,
        key=f"{key}_sofr",
        help="Modeling Assumption (r): 3.65786 % flat (P12)",
    )
    early = st.toggle(
        "Early redemption (February 2031 or 10 % clean-up)",
        value=defaults.early_redemption,
        key=f"{key}_early",
        help="T18: off = To Scheduled Maturity Date, on = To Early Redemption Date",
    )
    delinquency = st.toggle(
        "Delinquency Test satisfied every Payment Date",
        value=defaults.delinquency_test_satisfied,
        key=f"{key}_delinquency",
        help="Modeling Assumption (e), T10 / P73. Off requires the Distressed Principal "
        "Balance input, which the GUI does not take yet: the engine will refuse to run.",
    )
    cpr = _parse_percent(cpr_text, "CPR")
    cer = _parse_percent(cer_text, "CER")
    sofr = _parse_percent(sofr_text, "SOFR Rate")
    if cpr is None or cer is None or sofr is None:
        return EditorOutput(scenario=None, name=name, source=None)
    try:
        scenario = scenario_from_values(
            cpr_pct=cpr,
            cer_pct=cer,
            sofr_pct=sofr,
            early_redemption=early,
            delinquency_test_satisfied=delinquency,
        )
    except ScenarioError as error:
        st.error(f"{type(error).__name__}: {error}")
        return EditorOutput(scenario=None, name=name, source=None)
    source = defaults.source if _unchanged(defaults, scenario) else None
    st.caption(scenario.label())
    return EditorOutput(scenario=scenario, name=name.strip() or "ad-hoc", source=source)


def _unchanged(defaults: EditorDefaults, scenario: Scenario) -> bool:
    """True when the edited values still equal the file's, so the manifest may cite it."""
    return (
        Decimal(defaults.cpr_pct).scaleb(-2) == scenario.cpr
        and Decimal(defaults.cer_pct).scaleb(-2) == scenario.cer
        and Decimal(defaults.sofr_pct).scaleb(-2) == scenario.sofr_rate
        and defaults.early_redemption == scenario.early_redemption
        and defaults.delinquency_test_satisfied == scenario.delinquency_test_satisfied
    )


def describe_file(scenario_file: ScenarioFile) -> str:
    description = scenario_file.description.strip() if scenario_file.description else ""
    return f"**{scenario_file.name}** — {description}" if description else f"**{scenario_file.name}**"
