"""The public run API reproduces the spec 02 section 12 worked example and the Table 1
windows, and its CSV export is byte-deterministic except for the manifest timestamp."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from crt.api import (
    MANIFEST_FILE_NAME,
    TABLE_NAMES,
    RunResult,
    compare_summaries,
    export_csv,
    month_end_date,
    run_scenario,
)
from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER
from crt.scenarios.loader import load_scenario, scenario_from_values
from crt.tieout.run import DEAL_TERMS_PATH

pytestmark = pytest.mark.fast

D = Decimal


@pytest.fixture(scope="module")
def pricing_speed(project_root: Path) -> RunResult:
    source = project_root / "scenarios/pricing_speed.yaml"
    return run_scenario(
        load_scenario(source),
        project_root=project_root,
        scenario_name="pricing-speed",
        scenario_source=source,
        timestamp="2026-01-01T00:00:00Z",
    )


def test_month_end_dates() -> None:
    cut_off = date(2025, 12, 31)
    assert month_end_date(cut_off, 1) == date(2026, 1, 31)
    assert month_end_date(cut_off, 2) == date(2026, 2, 28)
    assert month_end_date(cut_off, 13) == date(2027, 1, 31)
    assert month_end_date(cut_off, 241) == date(2046, 1, 31)


def test_payment_date_1_note_numbers_match_spec_02_section_12(pricing_speed: RunResult) -> None:
    rows = {r.note: r for r in pricing_speed.note_cashflows if r.payment_date_number == 1}
    expected = {
        "A-1": ("10346250.00", "265553750.00", "1243718.57"),
        "M-1": ("14657659.91", "261242340.09", "1285103.57"),
        "M-2A": ("0", "37850000", "187655.00"),
        "M-2B": ("0", "37850000", "187655.00"),
    }
    for note, (principal, balance_after, interest) in expected.items():
        assert rows[note].payment_date == date(2026, 3, 25)
        assert rows[note].principal_paid == D(principal), note
        assert rows[note].balance_after == D(balance_after), note
        assert rows[note].interest == D(interest), note
        assert rows[note].accrual_days == 36
    first = pricing_speed.structure[0]
    assert first.senior_pct == D("0.9647500")
    assert first.senior_reduction == D("422332461.93")
    assert first.subordinate_reduction == D("15431167.95")
    assert first.balances_after["A-H"] == D("21276215056.99")
    assert sum(first.balances_after.values(), D(0)) == first.pool_upb_end == D("22343387921.96")


def test_table1_windows_and_maturity(pricing_speed: RunResult) -> None:
    windows = {
        s.note: (s.first_principal_payment_date_number, s.last_principal_payment_date_number)
        for s in pricing_speed.note_summaries
    }
    assert windows == {"A-1": (1, 37), "M-1": (1, 45), "M-2A": (45, 53), "M-2B": (53, 60)}
    assert pricing_speed.manifest.maturity_payment_date_number == 60
    assert pricing_speed.pool_totals.maturity_payment_date == date(2031, 2, 25)
    for summary in pricing_speed.note_summaries:
        assert summary.final_balance == D(0)
        assert summary.total_principal == summary.original_balance
        assert summary.wal_years is not None and isinstance(summary.wal_years, Decimal)


def test_pool_months_identity_and_extent(pricing_speed: RunResult) -> None:
    months = pricing_speed.pool_months
    assert months[0].month == 1 and months[0].month_end == date(2026, 1, 31)
    assert months[0].balance_begin == pricing_speed.pool_totals.cut_off_date_balance
    # Payment Date 60 carries collection month 61; nothing after the Maturity Date.
    assert months[-1].month == 61 and months[-1].payment_date_number == 60
    assert months[0].payment_date_number == months[1].payment_date_number == 1
    for row in months:
        assert (
            row.balance_begin - row.scheduled_principal - row.credit_event_amount - row.prepayment
            == row.balance_end
        )
    totals = pricing_speed.pool_totals
    assert (
        totals.cut_off_date_balance
        - totals.total_scheduled_principal
        - totals.total_prepayment
        - totals.total_credit_event_amount
        == totals.ending_balance
        == months[-1].balance_end
    )


def test_manifest_contents(pricing_speed: RunResult, project_root: Path) -> None:
    manifest = pricing_speed.manifest
    assert manifest.engine_version == "0.0.1"
    assert manifest.timestamp_utc == "2026-01-01T00:00:00Z"
    assert len(manifest.run_id) == 16
    assert DEAL_TERMS_PATH.as_posix() in manifest.input_sha256
    assert "scenarios/pricing_speed.yaml" in manifest.input_sha256
    assert manifest.scenario["cpr_pct"] == "10"  # Decimal("0.10").scaleb(2), exact
    assert manifest.scenario["early_redemption"] is True
    assert manifest.decimal_precision >= 28
    assert "A9" in manifest.conventions_in_force
    if (project_root / ".git").exists():
        assert manifest.git_commit is not None and len(manifest.git_commit) == 40


def test_to_frames_converts_only_at_the_boundary(pricing_speed: RunResult) -> None:
    frames = pricing_speed.to_frames()
    assert set(frames) == set(TABLE_NAMES)
    structure = frames["structure"]
    assert structure.height == 60
    for tranche in TRANCHE_ORDER:
        assert f"balance_after_{tranche}" in structure.columns
    assert structure["senior_pct"][0] == "0.9647500"  # exact digits, never "0E-7"
    assert structure["cumulative_net_loss_pct"][0] == "0.0000000"
    as_float = pricing_speed.to_frames(money_as="float")
    assert as_float["note_cashflows"]["principal_paid"].dtype.is_float()
    # The result itself is untouched: still Decimal.
    assert isinstance(pricing_speed.note_cashflows[0].principal_paid, Decimal)


def test_export_csv_is_byte_deterministic_except_timestamp(
    pricing_speed: RunResult, project_root: Path, tmp_path: Path
) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    written = export_csv(pricing_speed, first_dir)
    assert [p.name for p in written] == [f"{n}.csv" for n in TABLE_NAMES] + [MANIFEST_FILE_NAME]
    source = project_root / "scenarios/pricing_speed.yaml"
    second = run_scenario(
        load_scenario(source),
        project_root=project_root,
        scenario_name="pricing-speed",
        scenario_source=source,
        timestamp="1970-01-01T00:00:00Z",
    )
    export_csv(second, second_dir)
    for name in TABLE_NAMES:
        assert (first_dir / f"{name}.csv").read_bytes() == (second_dir / f"{name}.csv").read_bytes()
    first_manifest = json.loads((first_dir / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
    second_manifest = json.loads((second_dir / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
    assert first_manifest.pop("timestamp_utc") != second_manifest.pop("timestamp_utc")
    assert first_manifest == second_manifest
    assert first_manifest["run_id"] == pricing_speed.manifest.run_id
    header = (first_dir / "note_cashflows.csv").read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("note,payment_date_number,payment_date,balance_before")
    assert b"\r\n" not in (first_dir / "structure.csv").read_bytes()


def test_compare_summaries_is_b_minus_a(pricing_speed: RunResult, project_root: Path) -> None:
    stress = run_scenario(
        scenario_from_values(
            cpr_pct=D(5),
            cer_pct=D("2.50"),
            sofr_pct=D("3.65786"),
            early_redemption=False,
            delinquency_test_satisfied=True,
        ),
        project_root=project_root,
        scenario_name="stress",
        timestamp="2026-01-01T00:00:00Z",
    )
    differences = compare_summaries(pricing_speed, stress)
    assert {d.note for d in differences} == set(NOTE_CLASSES)
    by_key = {(d.note, d.metric): d for d in differences}
    write_downs = by_key[("M-2B", "total_write_downs")]
    assert write_downs.a == D(0)
    assert write_downs.b is not None and write_downs.b > D(0)
    assert write_downs.b_minus_a == write_downs.b - write_downs.a
    assert stress.manifest.maturity_payment_date_number == 240
    # Every row is scanned for the schema: maturity_reason is None until Payment Date 240.
    stress_frames = stress.to_frames()
    assert stress_frames["structure"].height == 240
    assert stress_frames["structure"]["maturity_reason"][-1] == "Scheduled Maturity Date"
