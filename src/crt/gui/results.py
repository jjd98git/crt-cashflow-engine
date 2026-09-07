"""Rendering of one run and of a two-run comparison.  Every number shown here is read
from a ``RunResult`` (or ``compare_summaries``); this module formats and plots only."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from crt.api import TABLE_NAMES, RunResult, compare_summaries
from crt.gui import formatting as fmt
from crt.gui.downloads import bundle_file_name, csv_bundle_bytes
from crt.io.deal_terms import NOTE_CLASSES


def manifest_line(result: RunResult) -> str:
    manifest = result.manifest
    commit = manifest.git_commit[:12] if manifest.git_commit else "no git commit"
    return (
        f"Run `{manifest.run_id}` — engine {manifest.engine_version}, {commit}, "
        f"{manifest.timestamp_utc} — {result.scenario.label()} — Maturity Date PD "
        f"{manifest.maturity_payment_date_number} ({manifest.maturity_reason})"
    )


def render_downloads(result: RunResult, key: str) -> None:
    columns = st.columns(3)
    columns[0].download_button(
        "Download CSV bundle (zip)",
        data=csv_bundle_bytes(result),
        file_name=bundle_file_name(result),
        mime="application/zip",
        key=f"{key}_zip",
    )
    columns[1].download_button(
        "Download manifest.json",
        data=result.manifest.to_json(),
        file_name=f"manifest_{result.manifest.run_id}.json",
        mime="application/json",
        key=f"{key}_manifest",
    )
    columns[2].button(
        "Excel export — Phase 5",
        disabled=True,
        key=f"{key}_excel",
        help="The auditable workbook export is Phase 5 and is not built yet.",
    )


def render_results(result: RunResult, key: str = "single") -> None:
    st.caption(manifest_line(result))
    st.subheader("Summary per Note")
    st.dataframe(fmt.summary_table(result))
    st.dataframe(fmt.pool_totals_table(result))

    st.subheader("Reference Tranche balances after each Payment Date")
    st.caption("Class Notional Amounts; A-H omitted from the chart (see the structure table).")
    st.line_chart(fmt.tranche_balance_chart_frame(result))

    st.subheader("Note principal and interest")
    note = st.selectbox("Note", NOTE_CLASSES, key=f"{key}_flows_note")
    st.bar_chart(fmt.note_flows_chart_frame(result, note))

    st.subheader("Pool balance by collection month")
    st.line_chart(fmt.pool_balance_chart_frame(result))

    st.subheader("Full tables")
    for table in TABLE_NAMES:
        with st.expander(table.replace("_", " ")):
            st.dataframe(fmt.display_table(result, table))

    st.subheader("Downloads")
    render_downloads(result, key)


def _overlay(frame_a: pd.DataFrame, frame_b: pd.DataFrame) -> pd.DataFrame:
    """Side-by-side columns of two runs on a shared index (an outer join, no arithmetic)."""
    return pd.concat([frame_a, frame_b], axis=1)


def render_compare(result_a: RunResult, result_b: RunResult) -> None:
    left, right = st.columns(2)
    for column, label, result in ((left, "A", result_a), (right, "B", result_b)):
        with column:
            st.markdown(f"**Scenario {label}: {result.manifest.scenario_name}**")
            st.caption(manifest_line(result))
            st.dataframe(fmt.summary_table(result))

    st.subheader("Note balances, A vs B")
    st.line_chart(
        _overlay(
            fmt.note_balance_chart_frame(result_a, label="A"),
            fmt.note_balance_chart_frame(result_b, label="B"),
        )
    )
    st.subheader("Pool balance, A vs B")
    st.line_chart(
        _overlay(
            fmt.pool_balance_chart_frame(result_a, label="A"),
            fmt.pool_balance_chart_frame(result_b, label="B"),
        )
    )
    st.subheader("Differences (B − A), computed by the engine API")
    st.dataframe(fmt.difference_table(compare_summaries(result_a, result_b)))

    st.subheader("Downloads")
    st.markdown("Scenario A")
    render_downloads(result_a, "compare_a")
    st.markdown("Scenario B")
    render_downloads(result_b, "compare_b")
