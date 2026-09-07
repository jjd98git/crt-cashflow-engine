"""CRT Cashflow Engine GUI.  Run with ``streamlit run src/crt/gui/app.py``.

Display only: the engine runs in-process through ``crt.api.run_scenario`` and every
number on screen comes from a ``RunResult``.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from crt.api import RunResult, run_scenario
from crt.gui import formatting as fmt
from crt.gui.deal_view import DealDisplay, load_deal_display
from crt.gui.editor import (
    EditorDefaults,
    defaults_from_file,
    describe_file,
    scenario_editor,
    scenario_files,
)
from crt.gui.results import render_compare, render_results
from crt.gui.tieout_status import load_tieout_status
from crt.scenarios.loader import ScenarioFileError, load_scenario_file
from crt.scenarios.scenario import Scenario
from crt.tieout.run import (
    DEAL_TERMS_PATH,
    DEFAULT_PROJECT_ROOT,
    PoolCache,
    TieoutInputs,
    load_inputs,
)

PROJECT_ROOT = DEFAULT_PROJECT_ROOT
SCENARIOS_DIR = PROJECT_ROOT / "scenarios"


@st.cache_resource
def engine_inputs(root: Path) -> TieoutInputs:
    return load_inputs(root)


@st.cache_resource
def pool_cache(root: Path) -> PoolCache:
    return PoolCache(engine_inputs(root))


def run(scenario: Scenario, name: str, source: Path | None) -> RunResult | None:
    """Run through the API; show any engine refusal verbatim and return None."""
    try:
        return run_scenario(
            scenario,
            project_root=PROJECT_ROOT,
            inputs=engine_inputs(PROJECT_ROOT),
            pool_cache=pool_cache(PROJECT_ROOT),
            scenario_name=name,
            scenario_source=source,
        )
    except (ValueError, RuntimeError) as error:
        st.error(f"{type(error).__name__}: {error}")
        return None


def sidebar_deal(display: DealDisplay) -> None:
    st.sidebar.header("Deal")
    st.sidebar.markdown(f"**{display.name}**")
    st.sidebar.markdown(
        f"Cut-off Date Balance: **{fmt.money(display.cut_off_date_balance)}**  \n"
        f"Cut-off {display.cut_off_date}, closing {display.closing_date}, first Payment Date "
        f"{display.first_payment_date}, Scheduled Maturity PD "
        f"{display.scheduled_maturity_payment_date_number}  \n"
        f"SOFR Rate (flat): {display.sofr_rate_flat_pct} %"
    )
    with st.sidebar.expander("Reference Tranches (Table 3)"):
        st.table(
            {
                "Tranche": [t.tranche + (" *" if t.note_issued else "") for t in display.tranches],
                "Initial notional": [fmt.money(t.initial_class_notional_amount) for t in display.tranches],
                "Subordination %": [format(t.initial_subordination_pct, "f") for t in display.tranches],
            }
        )
        st.caption("* Original Note issued against this tranche")
    with st.sidebar.expander("Original Notes (Table 1)"):
        st.table(
            {
                "Note": [n.note for n in display.notes],
                "Balance": [fmt.money(n.original_class_principal_balance) for n in display.notes],
                "Margin %": [format(n.margin_pct, "f") for n in display.notes],
                "Coupon %": [format(n.initial_class_coupon_pct, "f") for n in display.notes],
                "WAL": [format(n.expected_wal_years_table1, "f") for n in display.notes],
                "Window": [n.expected_principal_window_table1 for n in display.notes],
            }
        )


def sidebar_tieout() -> None:
    st.sidebar.header("Tie-out status")
    status = load_tieout_status(PROJECT_ROOT)
    if status is None:
        st.sidebar.warning("docs/validation/tieout.md not found or has no summary; run `python -m crt.tieout`.")
        return
    st.sidebar.markdown(f"Overall: **{status.overall or 'unknown'}** ({status.timestamp_utc or 'undated'})")
    st.sidebar.table(
        {
            "Family": [r.family for r in status.rows],
            "Pass": [r.passed for r in status.rows],
            "Fail": [r.failed for r in status.rows],
            "Status": [r.status for r in status.rows],
        }
    )
    if status.secondary_check:
        st.sidebar.caption(status.secondary_check)


def editor_defaults(key: str, files: tuple[Path, ...]) -> EditorDefaults | None:
    """Preset picker; returns the defaults for the editor, or None if the file is unusable."""
    labels = ["(blank)"] + [path.name for path in files]
    choice = st.selectbox("Scenario file", labels, key=f"{key}_preset")
    if choice == "(blank)":
        return EditorDefaults(
            name="ad-hoc", cpr_pct="10", cer_pct="0", sofr_pct="3.65786",
            early_redemption=True, delinquency_test_satisfied=True, source=None,
        )
    path = SCENARIOS_DIR / choice
    try:
        st.markdown(describe_file(load_scenario_file(path)))
        return defaults_from_file(path)
    except ScenarioFileError as error:
        st.error(f"{type(error).__name__}: {error}")
        return None


def editor_block(key: str, files: tuple[Path, ...]) -> tuple[Scenario | None, str, Path | None]:
    defaults = editor_defaults(key, files)
    if defaults is None:
        return None, "", None
    # Widget keys include the preset so that choosing another file resets the values.
    output = scenario_editor(f"{key}_{defaults.source.name if defaults.source else 'blank'}", defaults)
    return output.scenario, output.name, output.source


def main() -> None:
    st.set_page_config(page_title="CRT Cashflow Engine", layout="wide")
    st.title("CRT Cashflow Engine — STACR 2026-DNA1")
    inputs = engine_inputs(PROJECT_ROOT)
    sidebar_deal(load_deal_display(PROJECT_ROOT / DEAL_TERMS_PATH, inputs.deal))
    sidebar_tieout()
    files = scenario_files(SCENARIOS_DIR)
    mode = st.radio("Mode", ["Single run", "Compare"], horizontal=True)

    if mode == "Single run":
        scenario, name, source = editor_block("single", files)
        if st.button("Run", type="primary", disabled=scenario is None) and scenario is not None:
            st.session_state["single_result"] = run(scenario, name, source)
        result = st.session_state.get("single_result")
        if result is not None:
            render_results(result)
        return

    left, right = st.columns(2)
    with left:
        st.markdown("### Scenario A")
        scenario_a, name_a, source_a = editor_block("a", files)
    with right:
        st.markdown("### Scenario B")
        scenario_b, name_b, source_b = editor_block("b", files)
    ready = scenario_a is not None and scenario_b is not None
    if st.button("Run both", type="primary", disabled=not ready) and ready:
        assert scenario_a is not None and scenario_b is not None
        result_a = run(scenario_a, name_a, source_a)
        result_b = run(scenario_b, name_b, source_b)
        st.session_state["compare_results"] = (
            (result_a, result_b) if result_a is not None and result_b is not None else None
        )
    results = st.session_state.get("compare_results")
    if results is not None:
        render_compare(*results)


main()
