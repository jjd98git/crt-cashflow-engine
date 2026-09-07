"""PPM tie-out regression (BRIEF section 7; spec 03-tieout.md).

The grid is run once per session and ``docs/validation/tieout.md`` is regenerated.  Each
family is a separate test so that a partial failure is informative.  A failing test here
is a correct outcome to report, never something to weaken.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from crt.io.deal_terms import NOTE_CLASSES
from crt.io.ppm_tables import load_wal_table
from crt.money import ZERO
from crt.tieout.compare import (
    PERCENTAGE_POINT_TOLERANCE,
    WAL_TOLERANCE_YEARS,
    grid_key,
)
from crt.tieout.report import render_report
from crt.tieout.run import (
    DIAGNOSTICS_LOG_PATH,
    MANIFEST_PATH,
    REPORT_PATH,
    TieoutRun,
    write_tieout,
)

pytestmark = pytest.mark.tieout


@pytest.fixture(scope="module")
def tieout(project_root: Path) -> TieoutRun:
    return write_tieout(project_root)


def _describe(cells: list[str]) -> str:
    return "\n".join(cells)


def test_report_and_manifest_written(project_root: Path, tieout: TieoutRun) -> None:
    report = (project_root / REPORT_PATH).read_text(encoding="utf-8")
    assert report == tieout.report
    assert report.startswith("# Tie-out — STACR 2026-DNA1 — ")
    manifest = json.loads((project_root / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["engine_version"] == tieout.manifest.engine_version
    assert len(manifest["git_commit"]) == 40
    assert len(manifest["input_sha256"]) == 8
    assert manifest["decimal_precision"] >= 28


def test_grid_has_96_runs_and_48_pool_projections(tieout: TieoutRun) -> None:
    assert len(tieout.runs) == 96
    assert len({(k[0], k[1]) for k in tieout.runs}) == 48
    for key, run in tieout.runs.items():
        assert run.records[-1].is_maturity_date, key
        if key[2]:
            assert run.maturity_payment_date_number <= 60, key
        else:
            assert run.maturity_payment_date_number == 240, key


def test_a_table1_windows_exact(tieout: TieoutRun) -> None:
    failures = [
        f"{w.note}: model {w.model_first}-{w.model_last} vs PPM {w.ppm_first}-{w.ppm_last}"
        for w in tieout.results.windows
        if not w.passes
    ]
    assert [w.note for w in tieout.results.windows] == list(NOTE_CLASSES)
    assert not failures, _describe(failures)


def test_b_wal_cer0_within_0_02(tieout: TieoutRun) -> None:
    cells = tieout.results.wal_cer0
    assert len(cells) == 48
    failures = [
        f"{c.note} {'early' if c.early_redemption else 'sched'} CPR {c.cpr_pct}: "
        f"model {c.model} vs PPM {c.printed} (diff {c.diff})"
        for c in cells
        if not c.within_tolerance
    ]
    assert not failures, _describe(failures)


def test_b2_declining_balance_wal_rows_equal_wal_table_cells(
    project_root: Path, tieout: TieoutRun
) -> None:
    """README cross-check: the WAL rows under the Declining Balances tables are the same
    targets as the CER-0 WAL cells, so they must pass together."""
    wal_cells = {
        grid_key(c.cpr_pct, c.cer_pct, c.early_redemption) + (c.note_class,): c.wal_years
        for c in load_wal_table(
            project_root / "data/ppm_tables/wal_tables.csv", note_classes=NOTE_CLASSES
        )
        if c.rm_pct == ZERO and c.cer_pct == ZERO
    }
    assert len(tieout.results.declining_wal_rows) == 48
    failures: list[str] = []
    for row in tieout.results.declining_wal_rows:
        key = grid_key(row.cpr_pct, ZERO, row.early_redemption) + (row.note,)
        assert wal_cells[key] == row.ppm, key
        if not row.within_tolerance:
            failures.append(f"{row.note} CPR {row.cpr_pct} early={row.early_redemption}: "
                            f"{row.model} vs {row.printed}")
    assert not failures, _describe(failures)


def test_c_declining_balances_round_match(tieout: TieoutRun) -> None:
    cells = tieout.results.declining
    assert len(cells) == 366  # 6 CPR x (4 + 18 + 19 + 20) dated rows
    failures = [
        f"{c.note} CPR {c.cpr_pct} {c.row_label} (PD {c.payment_date_number}): "
        f"model {c.model_pct:.4f} vs PPM {c.printed}"
        for c in cells
        if not c.round_match
    ]
    assert not failures, _describe(failures)
    outside_brief = sum(1 for c in cells if not c.within_brief_tolerance)
    # Reported, not asserted (A13 / Q16): whole-percent printing cannot hold +/-0.25 pp.
    assert outside_brief <= len(cells)


def test_c2_secondary_window_bands(tieout: TieoutRun) -> None:
    failures = [
        f"{b.note} CPR {b.cpr_pct}: last principal PD {b.model_last} not in "
        f"({b.after_payment_date}, {b.on_or_before_payment_date}]"
        for b in tieout.results.window_bands
        if not b.passes
    ]
    assert len(tieout.results.window_bands) == 24
    assert not failures, _describe(failures)


def test_d_wal_cer_positive_within_0_02(tieout: TieoutRun) -> None:
    cells = tieout.results.wal_cer_positive
    assert len(cells) == 336
    failures = [
        f"{c.note} {'early' if c.early_redemption else 'sched'} CER {c.cer_pct}% CPR {c.cpr_pct}: "
        f"model {c.model:.4f} vs PPM {c.printed} (diff {c.diff:+.4f}, tolerance "
        f"{WAL_TOLERANCE_YEARS})"
        for c in cells
        if not c.within_tolerance
    ]
    assert not failures, _describe(failures)


def test_e_credit_event_sensitivity_round_match(tieout: TieoutRun) -> None:
    cells = tieout.results.credit_event_sensitivity
    assert len(cells) == 96
    failures = [
        f"{'early' if c.early_redemption else 'sched'} CER {c.cer_pct}% CPR {c.cpr_pct}: "
        f"model {c.model_pct:.4f} vs PPM {c.printed} (diff {c.diff:+.4f} pp)"
        for c in cells
        if not c.round_match
    ]
    assert not failures, _describe(failures)
    assert all(abs(c.diff) <= PERCENTAGE_POINT_TOLERANCE for c in cells)


def test_determinism_byte_identical_except_timestamp(project_root: Path, tieout: TieoutRun) -> None:
    """Two full runs on the same inputs differ only in the timestamp line of the report
    and the timestamp key of the manifest."""
    second = write_tieout(project_root, timestamp="1970-01-01T00:00:00Z")
    first_lines = tieout.report.splitlines()
    second_lines = second.report.splitlines()
    assert first_lines[0] != second_lines[0]
    assert first_lines[1:] == second_lines[1:]
    first_manifest = json.loads(tieout.manifest.to_json())
    second_manifest = json.loads(second.manifest.to_json())
    first_manifest.pop("timestamp_utc")
    second_manifest.pop("timestamp_utc")
    assert first_manifest == second_manifest
    # Rendering the same results with another timestamp is a pure function of the inputs
    # (the hand-maintained diagnostics log included under section 7 is one of them).
    log_path = project_root / DIAGNOSTICS_LOG_PATH
    diagnostics_log = log_path.read_text(encoding="utf-8") if log_path.is_file() else None
    rerendered = render_report(tieout.results, second.manifest, diagnostics_log=diagnostics_log)
    assert rerendered.splitlines()[1:] == first_lines[1:]
    # Leave the checked-in report with a real timestamp.
    write_tieout(project_root)


def test_model_values_are_decimal(tieout: TieoutRun) -> None:
    for cell in tieout.results.wal_cer0:
        assert isinstance(cell.model, Decimal)
    for cell in tieout.results.declining:
        assert isinstance(cell.model_pct, Decimal)
