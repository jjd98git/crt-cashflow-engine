"""GUI helpers that need no Streamlit: the tie-out status parser, the deal display, the
formatting boundary and the CSV bundle."""

from __future__ import annotations

import io
import json
import zipfile
from decimal import Decimal
from pathlib import Path

import pytest

from crt.api import run_scenario
from crt.gui.deal_view import load_deal_display
from crt.gui.downloads import bundle_file_name, csv_bundle_bytes
from crt.gui.formatting import money, percent_of_fraction, summary_table, wal
from crt.gui.tieout_status import load_tieout_status, parse_tieout_status
from crt.io.deal_terms import DealTerms
from crt.scenarios.loader import load_scenario
from crt.tieout.run import DEAL_TERMS_PATH

pytestmark = pytest.mark.fast

D = Decimal

SAMPLE_REPORT = """\
# Tie-out — STACR 2026-DNA1 — 2026-09-07T16:04:09Z
Manifest: engine version 0.0.1, ...

## 1. Summary
| family | cells | pass | fail | worst \\|diff\\| | tolerance | status |
|---|---|---|---|---|---|---|
| Table 1 windows | 4 | 4 | 0 | 0 | exact month | PASS |
| WAL CER>0 | 336 | 324 | 12 | 0.0836 | ±0.02 yr | FAIL |
Secondary window-band check (spec 03 section 2): 24 (Note, CPR) pairs, 0 failing.
Overall: FAIL.

## 2. Table 1 principal windows
| Note | model first |
"""


def test_parse_tieout_status_sample() -> None:
    status = parse_tieout_status(SAMPLE_REPORT)
    assert status is not None
    assert status.timestamp_utc == "2026-09-07T16:04:09Z"
    assert [r.family for r in status.rows] == ["Table 1 windows", "WAL CER>0"]
    assert status.rows[1].failed == "12" and status.rows[1].status == "FAIL"
    assert status.rows[0].worst_abs_diff == "0"
    assert status.overall == "FAIL"
    assert status.secondary_check is not None and status.secondary_check.startswith("Secondary")


def test_parse_tieout_status_missing_or_empty(tmp_path: Path) -> None:
    assert parse_tieout_status("") is None
    assert parse_tieout_status("# no summary here\n") is None
    assert load_tieout_status(tmp_path) is None


def test_load_tieout_status_from_checked_in_report(project_root: Path) -> None:
    status = load_tieout_status(project_root)
    if status is None:
        pytest.skip("docs/validation/tieout.md is absent")
    assert {r.family for r in status.rows} >= {"Table 1 windows", "WAL CER 0"}
    assert status.overall in {"PASS", "FAIL"}


def test_deal_display(project_root: Path, deal: DealTerms) -> None:
    display = load_deal_display(project_root / DEAL_TERMS_PATH, deal)
    assert "2026-DNA1" in display.name
    assert display.cut_off_date_balance == D("22781151551.84")
    assert [t.tranche for t in display.tranches][:3] == ["A-H", "A-1", "A-1H"]
    assert display.tranches[0].initial_subordination_pct == D("4.800")
    assert [n.note for n in display.notes] == ["A-1", "M-1", "M-2A", "M-2B"]
    assert display.notes[0].margin_pct == D("0.85")
    assert display.notes[0].expected_principal_window_table1 == "1-37"
    assert display.sofr_rate_flat_pct == D("3.65786")


def test_formatting_is_string_only() -> None:
    assert money(D("10346250.00")) == "10,346,250.00"
    assert money(D("37850000")) == "37,850,000.00"
    assert money(None) == "n/a"
    assert percent_of_fraction(D("0.0352500")) == "3.52500 %"
    assert wal(D("1.58681234")) == "1.59"
    assert wal(None) == "n/a"


def test_summary_table_and_csv_bundle(project_root: Path) -> None:
    source = project_root / "scenarios/pricing_speed.yaml"
    result = run_scenario(
        load_scenario(source),
        project_root=project_root,
        scenario_name="pricing-speed",
        scenario_source=source,
        timestamp="2026-01-01T00:00:00Z",
    )
    table = summary_table(result)
    assert list(table.index) == ["A-1", "M-1", "M-2A", "M-2B"]
    assert table.loc["A-1", "Total principal"] == "275,900,000.00"
    assert table.loc["M-2B", "Last principal PD"] == "60 (2031-02-25)"

    payload = csv_bundle_bytes(result)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = sorted(archive.namelist())
        assert names == sorted(
            ["pool_months.csv", "structure.csv", "note_cashflows.csv", "note_summary.csv",
             "pool_totals.csv", "manifest.json"]
        )
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["run_id"] == result.manifest.run_id
    assert csv_bundle_bytes(result) == payload  # same result -> same bytes
    assert bundle_file_name(result) == f"crt_run_pricing-speed_{result.manifest.run_id}.zip"
