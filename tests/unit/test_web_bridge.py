"""The browser bridge (``web/engine_bridge.py``) and the site build script, run natively.

What these prove: the bridge returns engine values as strings that agree with a direct
``run_scenario`` call, relays engine refusals verbatim, produces the CSV bundle and the
workbook; ``crt.api`` imports without polars (the browser has none); the run manifest
degrades to ``git_commit = None`` when git is unavailable; and ``scripts/build_web.py``
ships every input file and the vendored dependency wheels with matching SHA-256 hashes,
with a worker that never refers to a package index.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

from crt import api
from crt.api import MANIFEST_FILE_NAME, TABLE_NAMES, run_scenario
from crt.money import round_half_up
from crt.scenarios.loader import load_scenario
from crt.tieout.manifest import ManifestError

pytestmark = pytest.mark.fast


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolves annotations via sys.modules
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def bridge(project_root: Path) -> ModuleType:
    module = _load_module(project_root / "web" / "engine_bridge.py", "engine_bridge_under_test")
    module.init_session(str(project_root))
    return module


@pytest.fixture(scope="module")
def build_web(project_root: Path) -> ModuleType:
    return _load_module(project_root / "scripts" / "build_web.py", "build_web_under_test")


@pytest.fixture
def offline_wheels(build_web: ModuleType, monkeypatch: pytest.MonkeyPatch) -> dict[str, bytes]:
    """Stand in for ``pip download`` (no network in the fast suite): write one deterministic
    fake wheel per pinned requirement, named the way pip would name it."""
    contents: dict[str, bytes] = {}

    def fake_download(requirements: tuple[str, ...], out_dir: Path) -> list[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        wheels: list[Path] = []
        for requirement in requirements:
            name, version = requirement.split("==", 1)
            wheel = out_dir / f"{name}-{version}-py3-none-any.whl"
            wheel.write_bytes(f"fake wheel {requirement}\n".encode() * 7)
            contents[wheel.name] = wheel.read_bytes()
            wheels.append(wheel)
        return wheels

    monkeypatch.setattr(build_web, "download_wheels", fake_download)
    return contents


PRICING_SPEED_FORM = {
    "name": "pricing-speed",
    "cpr_pct": "10",
    "cer_pct": "0",
    "sofr_pct": "3.65786",
    "early_redemption": True,
    "delinquency_test_satisfied": True,
    "source": "scenarios/pricing_speed.yaml",
}


def test_crt_api_imports_without_polars() -> None:
    code = "import sys; sys.modules['polars'] = None; import crt.api; print('imported')"
    completed = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert completed.stdout.strip() == "imported"


def test_manifest_git_commit_is_none_without_git(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_git(root: Path) -> str:
        raise ManifestError(f"git rev-parse HEAD failed in {root}: simulated absence")

    monkeypatch.setattr(api, "git_commit", no_git)
    scenario = load_scenario(project_root / "scenarios" / "pricing_speed.yaml")
    result = run_scenario(scenario, project_root=project_root, timestamp="2026-01-01T00:00:00Z")
    assert result.manifest.git_commit is None
    assert len(result.manifest.run_id) == 16


def test_init_session_describes_deal_presets_and_tieout(
    bridge: ModuleType, project_root: Path
) -> None:
    info = json.loads(bridge.init_session(str(project_root)))
    assert info["engine_version"] == "0.0.1"
    assert info["deal"]["cut_off_date_balance"] == "22,781,151,551.84"
    assert info["ppm_grid"]["cpr_pct"] == ["0", "5", "10", "15", "25", "35"]
    assert info["ppm_grid"]["cer_pct"][1] == "0.25"
    presets = {p["path"]: p for p in info["presets"]}
    pricing = presets["scenarios/pricing_speed.yaml"]
    assert pricing["error"] is None
    assert (pricing["cpr_pct"], pricing["cer_pct"], pricing["sofr_pct"]) == ("10", "0", "3.65786")
    assert pricing["early_redemption"] is True
    assert info["tieout_status"] is not None and info["tieout_status"]["rows"]
    assert info["table_names"] == list(TABLE_NAMES)


def test_run_form_matches_run_scenario(bridge: ModuleType, project_root: Path) -> None:
    payload = json.loads(bridge.run_form(json.dumps(PRICING_SPEED_FORM)))
    assert payload["ok"], payload
    source = project_root / "scenarios" / "pricing_speed.yaml"
    direct = run_scenario(
        load_scenario(source),
        project_root=project_root,
        scenario_name="pricing-speed",
        scenario_source=source,  # the bridge cites the unchanged preset file too
    )

    assert payload["manifest"]["scenario_source"] == "scenarios/pricing_speed.yaml"
    assert payload["run_id"] == direct.manifest.run_id  # same inputs, same hash
    assert len(payload["payment_dates"]) == len(direct.structure) == 60
    a1 = payload["summary"][0]
    assert a1["note"] == "A-1"
    wal = direct.summary_for("A-1").wal_years
    assert wal is not None
    assert a1["wal_years"] == format(round_half_up(wal, 2), ".2f")
    assert a1["total_principal"] == format(direct.summary_for("A-1").total_principal, ",.2f")
    assert a1["first_principal"] == "1 (2026-03-25)"
    # Chart series are the exact engine digits, one per Payment Date and tranche.
    last = direct.structure[-1]
    for tranche in payload["tranche_order"]:
        assert payload["balances_after"][tranche][-1] == format(last.balances_after[tranche], "f")
        assert len(payload["write_downs"][tranche]) == 60
    assert set(payload["tables"]) == set(TABLE_NAMES)
    assert len(payload["tables"]["structure"]["rows"]) == 60
    assert len(payload["tables"]["tranche_allocations"]["rows"]) == 60 * 12
    assert payload["tables"]["pool_totals"]["rows"][0][0] == "22781151551.84"
    assert payload["files"]["csv_zip"].endswith(f"_{payload['run_id']}.zip")
    assert payload["files"]["xlsx"].endswith(".xlsx")


def test_downloads_are_the_gui_payloads(bridge: ModuleType) -> None:
    payload = json.loads(bridge.run_form(json.dumps(PRICING_SPEED_FORM)))
    run_id = payload["run_id"]
    bundle = base64.b64decode(bridge.csv_bundle_base64(run_id))
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        names = set(archive.namelist())
        assert names == {f"{name}.csv" for name in TABLE_NAMES} | {MANIFEST_FILE_NAME}
        manifest = json.loads(archive.read(MANIFEST_FILE_NAME))
        assert manifest["run_id"] == run_id
    workbook = base64.b64decode(bridge.workbook_base64(run_id))
    assert workbook[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(workbook)) as archive:
        assert "xl/workbook.xml" in archive.namelist()


def test_run_form_relays_refusals_verbatim(bridge: ModuleType) -> None:
    bad_number = json.loads(bridge.run_form(json.dumps({**PRICING_SPEED_FORM, "cpr_pct": "ten"})))
    assert bad_number["ok"] is False
    assert "cpr_pct" in bad_number["error"] and "'ten'" in bad_number["error"]

    out_of_range = json.loads(bridge.run_form(json.dumps({**PRICING_SPEED_FORM, "cer_pct": "100"})))
    assert out_of_range["ok"] is False
    assert out_of_range["error"].startswith("ScenarioError:")

    no_vector = json.loads(
        bridge.run_form(json.dumps({**PRICING_SPEED_FORM, "delinquency_test_satisfied": False}))
    )
    assert no_vector["ok"] is False  # the engine refuses: no Distressed Principal Balance input
    assert "Distressed" in no_vector["error"] or "distressed" in no_vector["error"]

    unknown = bridge.run_form(json.dumps({**PRICING_SPEED_FORM, "early_redemption": "yes"}))
    assert json.loads(unknown)["ok"] is False


def test_bridge_keeps_only_recent_results(bridge: ModuleType) -> None:
    for cpr in ("0", "5", "15", "25", "35"):
        payload = json.loads(bridge.run_form(json.dumps({**PRICING_SPEED_FORM, "cpr_pct": cpr})))
        assert payload["ok"], payload
    assert len(bridge._session().results) <= bridge.MAX_KEPT_RESULTS
    with pytest.raises(bridge.BridgeError):
        bridge.csv_bundle_base64("not-a-run")


def test_build_web_collects_every_input(build_web: ModuleType, project_root: Path) -> None:
    files = build_web.collect_project_files(project_root)
    relative = {p.relative_to(project_root).as_posix() for p in files}
    assert "pyproject.toml" in relative
    assert "data/deal_terms/stacr_2026_dna1.yaml" in relative
    assert "data/ppm_tables/appendix_c_rep_lines.csv" in relative
    assert "data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv" in relative
    assert "docs/assumptions.csv" in relative
    assert "docs/validation/tieout.md" in relative
    assert "scenarios/pricing_speed.yaml" in relative
    assert all(p.is_file() for p in files)


def test_build_web_manifest_hashes_match(
    build_web: ModuleType, project_root: Path, tmp_path: Path, offline_wheels: dict[str, bytes]
) -> None:
    dist = build_web.build(project_root, tmp_path / "dist", skip_wheel=True)
    manifest = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["wheel"] is None
    assert manifest["engine_version"] == "0.0.1"
    paths = {entry["path"] for entry in manifest["files"]}
    assert {"engine_bridge.py", "build_info.json", "pyproject.toml"} <= paths
    for entry in manifest["files"]:
        shipped = dist / entry["path"]
        assert shipped.is_file(), entry
        assert hashlib.sha256(shipped.read_bytes()).hexdigest() == entry["sha256"]
        assert shipped.stat().st_size == entry["bytes"]
    for name in build_web.PAGE_FILES:
        assert (dist / name).is_file()
    assert (dist / "diag.html").is_file()


def test_build_web_vendors_dependency_wheels(
    build_web: ModuleType, project_root: Path, tmp_path: Path, offline_wheels: dict[str, bytes]
) -> None:
    """The manifest's ``wheels`` list is the vendored dependencies in install order, each
    shipped under wheels/ with the SHA-256 and byte count of the file actually served."""
    assert build_web.VENDORED_WHEELS == ("et_xmlfile==2.0.0", "openpyxl==3.1.5")
    dist = build_web.build(project_root, tmp_path / "dist", skip_wheel=True)
    manifest = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    wheels = manifest["wheels"]
    assert [w["requirement"] for w in wheels] == list(build_web.VENDORED_WHEELS)
    assert len(offline_wheels) == len(wheels)
    for entry in wheels:
        assert entry["path"] == f"wheels/{entry['file_name']}"
        shipped = dist / entry["path"]
        assert shipped.is_file(), entry
        assert shipped.read_bytes() == offline_wheels[entry["file_name"]]
        assert hashlib.sha256(shipped.read_bytes()).hexdigest() == entry["sha256"]
        assert shipped.stat().st_size == entry["bytes"]


def test_build_web_worker_never_contacts_a_package_index(
    build_web: ModuleType, project_root: Path, tmp_path: Path, offline_wheels: dict[str, bytes]
) -> None:
    dist = build_web.build(project_root, tmp_path / "dist", skip_wheel=True)
    for name in ("worker.js", "index.html", "app.js", "diag.html"):
        text = (dist / name).read_text(encoding="utf-8").lower()
        assert "pypi" not in text, name
        assert "pythonhosted" not in text, name
    worker = (dist / "worker.js").read_text(encoding="utf-8")
    assert "deps=False" in worker
    assert "emfs:" in worker
    assert "manifest.wheels" in worker


def test_download_wheels_fetches_pinned_wheels_only(build_web: ModuleType, tmp_path: Path) -> None:
    """``pip download`` is invoked binary-only, without dependencies, into the given
    directory; the result is one wheel per requirement in requirement order."""
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> None:
        calls.append(command)
        dest = Path(command[command.index("--dest") + 1])
        # pip writes them in whatever order it resolves; the function must reorder.
        (dest / "openpyxl-3.1.5-py2.py3-none-any.whl").write_bytes(b"o")
        (dest / "et_xmlfile-2.0.0-py3-none-any.whl").write_bytes(b"e")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(build_web.subprocess, "run", fake_run)
        wheels = build_web.download_wheels(("et_xmlfile==2.0.0", "openpyxl==3.1.5"), tmp_path / "w")
    assert [w.name for w in wheels] == [
        "et_xmlfile-2.0.0-py3-none-any.whl",
        "openpyxl-3.1.5-py2.py3-none-any.whl",
    ]
    assert len(calls) == 1
    assert "--only-binary=:all:" in calls[0] and "--no-deps" in calls[0]
    assert calls[0][-2:] == ["et_xmlfile==2.0.0", "openpyxl==3.1.5"]
