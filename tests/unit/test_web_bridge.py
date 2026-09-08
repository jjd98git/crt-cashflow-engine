"""The browser bridge (``web/engine_bridge.py``) and the site build script, run natively.

What these prove: the bridge returns engine values as strings that agree with a direct
``run_scenario`` call, relays engine refusals verbatim, produces the CSV bundle and the
workbook; ``crt.api`` imports without polars (the browser has none); the run manifest
degrades to ``git_commit = None`` when git is unavailable; and ``scripts/build_web.py``
ships every input file, the vendored dependency wheels, the self-hosted Pyodide runtime and
Chart.js with matching SHA-256 hashes, packs the manifest, every project file and every
wheel into ``data/bundle.js`` (what the worker loads with importScripts, so that no data
file is ever fetched), lists both runtime candidates (this site, then jsdelivr), and gives
index.html a Chart.js fallback; no page refers to a package index.
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
            # Real wheels are zip files (not UTF-8 text): start with bytes that are not.
            wheel.write_bytes(b"PK\x03\x04\xff\xfe" + f"fake wheel {requirement}\n".encode() * 7)
            contents[wheel.name] = wheel.read_bytes()
            wheels.append(wheel)
        return wheels

    monkeypatch.setattr(build_web, "download_wheels", fake_download)
    return contents


FAKE_LOCK = {
    "info": {"version": "0.29.3", "python": "3.13.2"},
    "packages": {
        # A synthetic dependency chain: the closure must follow ``depends``, not guess.
        "micropip": {
            "file_name": "micropip-9.9-py3-none-any.whl",
            "sha256": "m" * 64,
            "version": "9.9",
            "depends": ["packaging"],
        },
        "packaging": {
            "file_name": "packaging-1.0-py3-none-any.whl",
            "sha256": "p" * 64,
            "version": "1.0",
            "depends": [],
        },
        "pyyaml": {
            "file_name": "pyyaml-6.0-cp313-cp313-pyodide_2025_0_wasm32.whl",
            "sha256": "y" * 64,
            "version": "6.0",
            "depends": [],
        },
        "unused": {
            "file_name": "unused-0-py3-none-any.whl",
            "sha256": "u" * 64,
            "version": "0",
            "depends": [],
        },
    },
}


@pytest.fixture
def offline_runtime(build_web: ModuleType, monkeypatch: pytest.MonkeyPatch) -> dict[str, bytes]:
    """Stand in for the pinned downloads (Pyodide runtime, Chart.js): write deterministic
    fake bytes under the requested file name, a parseable lock file for
    ``pyodide-lock.json``.  Returns file name -> bytes for what the build must ship."""
    contents: dict[str, bytes] = {}

    def fake_fetch(download: object, cache_dir: Path) -> Path:
        cache_dir.mkdir(parents=True, exist_ok=True)
        name = str(download.file_name)  # type: ignore[attr-defined]
        target = cache_dir / name
        if name == build_web.PYODIDE_LOCK_FILE:
            target.write_text(json.dumps(FAKE_LOCK), encoding="utf-8")
        else:
            target.write_bytes(f"fake runtime file {name}\n".encode() * 3)
        contents[name] = target.read_bytes()
        return target

    monkeypatch.setattr(build_web, "fetch_pinned", fake_fetch)
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


@pytest.fixture
def built_dist(
    build_web: ModuleType,
    project_root: Path,
    tmp_path: Path,
    offline_wheels: dict[str, bytes],
    offline_runtime: dict[str, bytes],
) -> Path:
    """One offline build (no engine wheel) of the site into a temporary directory."""
    return build_web.build(
        project_root, tmp_path / "dist", skip_wheel=True, cache_dir=tmp_path / "cache"
    )


def _manifest(dist: Path) -> dict[str, object]:
    manifest: dict[str, object] = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    return manifest


def _check_shipped(dist: Path, entry: dict[str, object], served: str) -> Path:
    shipped = dist / served
    assert shipped.is_file(), entry
    assert hashlib.sha256(shipped.read_bytes()).hexdigest() == entry["sha256"], entry
    assert shipped.stat().st_size == entry["bytes"], entry
    return shipped


def test_build_web_manifest_hashes_match(build_web: ModuleType, built_dist: Path) -> None:
    dist = built_dist
    manifest = _manifest(dist)
    assert manifest["wheel"] is None
    assert manifest["engine_version"] == "0.0.1"
    files = manifest["files"]
    assert isinstance(files, list)
    paths = {entry["path"] for entry in files}
    assert {"engine_bridge.py", "build_info.json", "pyproject.toml"} <= paths
    for entry in files:
        _check_shipped(dist, entry, str(entry["served"]))
        assert entry["served"] == build_web.served_name(str(entry["sha256"]))
    for name in build_web.PAGE_FILES:
        assert (dist / name).is_file()
    assert (dist / "diag.html").is_file()
    # The served manifest is the readable copy, byte for byte.
    assert (dist / "manifest.bin").read_bytes() == (dist / "manifest.json").read_bytes()
    assert manifest["served_manifest"] == "manifest.bin"


def test_build_web_vendors_dependency_wheels(
    build_web: ModuleType, built_dist: Path, offline_wheels: dict[str, bytes]
) -> None:
    """The manifest's ``wheels`` list is the vendored dependencies in install order, each
    served as files/<hash>.bin with the SHA-256 and byte count of the file actually served."""
    assert build_web.VENDORED_WHEELS == ("et_xmlfile==2.0.0", "openpyxl==3.1.5")
    wheels = _manifest(built_dist)["wheels"]
    assert isinstance(wheels, list)
    assert [w["requirement"] for w in wheels] == list(build_web.VENDORED_WHEELS)
    assert len(offline_wheels) == len(wheels)
    for entry in wheels:
        assert entry["path"] == f"wheels/{entry['file_name']}"  # logical name, kept
        shipped = _check_shipped(built_dist, entry, str(entry["served"]))
        assert shipped.read_bytes() == offline_wheels[str(entry["file_name"])]


def test_build_web_worker_loads_data_as_script_and_never_fetches_it(built_dist: Path) -> None:
    """The worker imports data/bundle.js and fetches no manifest, project file or wheel:
    the only fetch() is the runtime probe (pyodide-lock.json).  No page names a package
    index.  (``manifest.json`` records the build-time *source* of each download; it is
    not code.)"""
    for name in ("worker.js", "index.html", "app.js", "diag.html"):
        text = (built_dist / name).read_text(encoding="utf-8").lower()
        for host in ("pypi", "pythonhosted"):
            assert host not in text, f"{name} mentions {host}"
    worker = (built_dist / "worker.js").read_text(encoding="utf-8")
    assert "importScripts(url)" in worker
    assert 'const BUNDLE_SCRIPT = "data/bundle.js"' in worker
    assert "self.CRT_BUNDLE" in worker
    for forbidden in ("manifest.bin", "manifest.json", "files/", ".whl", "entry.served"):
        assert forbidden not in worker, f"worker.js still refers to {forbidden}"
    code_lines = [
        line for line in worker.splitlines() if not line.strip().startswith(("*", "//", "/*"))
    ]
    fetch_lines = [line for line in code_lines if "fetch(" in line]
    assert len(fetch_lines) == 1, fetch_lines  # the probe, and nothing else
    assert "controller.signal" in fetch_lines[0]
    assert 'const LOCK_FILE = "pyodide-lock.json"' in worker
    assert "PROBE_TIMEOUT_MS = 10000" in worker
    assert "LOAD_PYODIDE_TIMEOUT_MS = 90000" in worker
    assert '"runtime-failed"' in worker
    # Integrity survives the packing: decode, hash, compare against the manifest entry.
    assert "crypto.subtle.digest" in worker and "does not match the manifest" in worker
    assert "atob(" in worker and "TextEncoder" in worker
    assert "deps=False" in worker
    assert "emfs:" in worker
    assert "manifest.wheels" in worker
    # Pyodide 0.29.3 hangs when instantiateStreaming refuses a mislabelled .wasm; the
    # worker wraps it, compiles from an ArrayBuffer and reports the URL instead.
    assert "WebAssembly.instantiateStreaming = " in worker
    assert '"application/wasm"' in worker and "arrayBuffer()" in worker
    app = (built_dist / "app.js").read_text(encoding="utf-8")
    assert '"runtime-failed"' in app and '"start"' in app  # restart at the next candidate
    assert "WARNING: origins" not in app  # the origins line is informational now


def test_build_web_index_has_chartjs_fallback(built_dist: Path) -> None:
    """Chart.js comes from this site, with an onerror fallback to the same pinned release
    on cdnjs; app.js reports which one loaded."""
    index = (built_dist / "index.html").read_text(encoding="utf-8")
    assert 'src="vendor/chart.umd.min.js"' in index
    assert 'onerror="crtChartFailed()"' in index and 'onload="crtChartLoaded()"' in index
    assert "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.min.js" in index
    assert "window.CRT_CHART" in index
    app = (built_dist / "app.js").read_text(encoding="utf-8")
    assert "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.min.js" in app
    assert "chartSource" in app


def test_build_web_bundle_holds_every_file_with_matching_hashes(
    build_web: ModuleType, built_dist: Path
) -> None:
    """``data/bundle.js`` parses to CRT_BUNDLE holding the manifest, both runtime
    candidates and one entry per manifest file / wheel whose decoded bytes have the
    manifest's SHA-256 and byte count (and equal the served .bin file)."""
    manifest = _manifest(built_dist)
    bundle = build_web.read_bundle(built_dist / "data")
    assert bundle["format"] == build_web.BUNDLE_FORMAT == 1
    assert bundle["parts"] == []
    assert bundle["manifest"] == manifest
    assert manifest["bundle"] == "data/bundle.js"
    assert bundle["runtime"] == [
        {"name": "this site", "indexURL": "pyodide/"},
        {"name": "jsdelivr", "indexURL": "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/"},
    ]
    assert manifest["runtime"]["candidates"] == bundle["runtime"]  # type: ignore[index]
    entries = bundle["entries"]
    assert isinstance(entries, dict)
    expected = list(manifest["files"]) + list(manifest["wheels"])  # type: ignore[call-overload]
    if manifest["wheel"]:
        expected.append(manifest["wheel"])
    assert set(entries) == {str(item["path"]) for item in expected}
    for item in expected:
        entry = entries[str(item["path"])]
        if entry["encoding"] == "utf-8":
            data = str(entry["data"]).encode("utf-8")
        else:
            assert entry["encoding"] == "base64"
            data = base64.b64decode(entry["data"], validate=True)
        assert len(data) == entry["bytes"] == item["bytes"], item["path"]
        digest = hashlib.sha256(data).hexdigest()
        assert digest == entry["sha256"] == item["sha256"], item["path"]
        assert data == (built_dist / str(item["served"])).read_bytes()
    # Text stays text (a YAML file), wheels are base64.
    assert entries["data/deal_terms/stacr_2026_dna1.yaml"]["encoding"] == "utf-8"
    assert all(entries[str(w["path"])]["encoding"] == "base64" for w in manifest["wheels"])  # type: ignore[index]
    text = (built_dist / "data" / "bundle.js").read_text(encoding="ascii")  # ASCII-only JS
    assert text.startswith("self.CRT_BUNDLE = {") and text.endswith("};\n")


def test_bundle_entry_decides_by_content(build_web: ModuleType) -> None:
    text = build_web.bundle_entry("a.md", "caf\u00e9\r\n".encode())
    assert text["encoding"] == "utf-8" and text["data"] == "caf\u00e9\r\n" and text["bytes"] == 7
    binary = build_web.bundle_entry("w.whl", b"PK\x03\x04\xff\xfe")
    assert binary["encoding"] == "base64"
    assert base64.b64decode(str(binary["data"])) == b"PK\x03\x04\xff\xfe"
    assert binary["sha256"] == hashlib.sha256(b"PK\x03\x04\xff\xfe").hexdigest()


def test_write_bundle_splits_into_parts_over_the_limit(
    build_web: ModuleType, tmp_path: Path
) -> None:
    """Over the part limit, bundle.js keeps the header and lists the part scripts, each
    part Object.assigns its entries; read_bundle reassembles the same entries."""
    entries = [build_web.bundle_entry(f"f{i}.txt", (f"line {i}\n" * 40).encode()) for i in range(6)]
    header = {"manifest": {"generated_utc": "x"}, "runtime": []}
    names = build_web.write_bundle(tmp_path / "data", header, entries, part_limit=1000)
    assert names[0] == "bundle.js" and len(names) > 2
    assert names[1:] == [f"bundle-{i}.js" for i in range(1, len(names))]
    head = (tmp_path / "data" / "bundle.js").read_text(encoding="ascii")
    assert '"entries":{}' in head and '"parts":["bundle-1.js"' in head
    part = (tmp_path / "data" / "bundle-1.js").read_text(encoding="ascii")
    assert part.startswith("Object.assign(self.CRT_BUNDLE.entries, {") and part.endswith("});\n")
    bundle = build_web.read_bundle(tmp_path / "data")
    assert bundle["parts"] == names[1:]
    assert bundle["entries"] == {str(e["path"]): e for e in entries}
    # Under the limit: one file, entries inline.
    single = build_web.write_bundle(tmp_path / "one", header, entries, part_limit=10**9)
    assert single == ["bundle.js"]
    assert build_web.read_bundle(tmp_path / "one")["entries"] == bundle["entries"]


def test_build_web_manifest_runtime_and_vendor_sections(
    build_web: ModuleType, built_dist: Path, offline_runtime: dict[str, bytes]
) -> None:
    """``runtime`` lists what loadPyodide + loadPackage fetch from pyodide/ (the lock's
    dependency closure of micropip and pyyaml), ``vendor`` lists Chart.js; every entry
    carries the hash and byte count of the shipped file."""
    manifest = _manifest(built_dist)
    runtime = manifest["runtime"]
    assert isinstance(runtime, dict)
    assert runtime["pyodide_version"] == build_web.PYODIDE_VERSION == "0.29.3"
    assert runtime["index_url"] == "pyodide/"
    assert runtime["packages"] == ["micropip", "pyyaml"]
    names = [entry["file_name"] for entry in runtime["files"]]
    assert names[:5] == [
        "pyodide.js",
        "pyodide.asm.js",
        "pyodide.asm.wasm",
        "python_stdlib.zip",
        "pyodide-lock.json",
    ]
    # From FAKE_LOCK: micropip -> packaging, pyyaml; "unused" is not shipped.
    assert names[5:] == [
        "micropip-9.9-py3-none-any.whl",
        "packaging-1.0-py3-none-any.whl",
        "pyyaml-6.0-cp313-cp313-pyodide_2025_0_wasm32.whl",
    ]
    for entry in runtime["files"]:
        assert entry["path"] == f"pyodide/{entry['file_name']}"
        shipped = _check_shipped(built_dist, entry, str(entry["path"]))
        assert shipped.read_bytes() == offline_runtime[str(entry["file_name"])]
        assert len(str(entry["sha256"])) == 64
    vendor = manifest["vendor"]
    assert isinstance(vendor, list) and len(vendor) == 1
    chart = vendor[0]
    assert (chart["name"], chart["version"]) == ("Chart.js", "4.5.1")
    assert chart["path"] == "vendor/chart.umd.min.js"
    shipped = _check_shipped(built_dist, chart, str(chart["path"]))
    assert shipped.read_bytes() == offline_runtime["chart.umd.min.js"]


def test_build_web_serves_neutral_names(build_web: ModuleType, built_dist: Path) -> None:
    """Every served path for a project file or wheel ends in ``.bin``; apart from the
    Pyodide runtime (which keeps its own names) and manifest.json, no ``.whl``, ``.yaml``,
    ``.csv`` or ``.json`` exists anywhere under dist."""
    manifest = _manifest(built_dist)
    entries = list(manifest["files"]) + list(manifest["wheels"])  # type: ignore[call-overload]
    if manifest["wheel"]:
        entries.append(manifest["wheel"])
    assert entries
    for entry in entries:
        served = str(entry["served"])
        assert served.startswith("files/") and served.endswith(".bin"), entry
        assert served.count("/") == 1
    filtered = {".whl", ".yaml", ".yml", ".csv", ".json", ".md", ".toml", ".py"}
    for path in built_dist.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(built_dist).as_posix()
        if relative.startswith(f"{build_web.PYODIDE_SUBDIR}/") or relative == "manifest.json":
            continue
        assert path.suffix not in filtered, relative
    assert sorted(p.name for p in (built_dist / "data").iterdir()) == ["bundle.js"]


def test_fetch_pinned_caches_and_verifies(build_web: ModuleType, tmp_path: Path) -> None:
    """A download is fetched once, verified against the pin, and reused from the cache
    while it still matches; a wrong hash is refused and leaves nothing under the name."""
    payload = b"runtime bytes\n"
    digest = hashlib.sha256(payload).hexdigest()
    calls: list[str] = []

    def fake_urlopen(url: str, timeout: float = 0) -> io.BytesIO:
        calls.append(url)
        return io.BytesIO(payload)  # BytesIO is a context manager, like the real response

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(build_web.urllib.request, "urlopen", fake_urlopen)
        good = build_web.Download("https://example.invalid/pyodide.js", "pyodide.js", digest)
        first = build_web.fetch_pinned(good, tmp_path / "cache")
        assert first.read_bytes() == payload
        second = build_web.fetch_pinned(good, tmp_path / "cache")
        assert second == first and calls == [good.url]  # cache hit, no second download
        (tmp_path / "cache" / "pyodide.js").write_bytes(b"corrupted")
        build_web.fetch_pinned(good, tmp_path / "cache")
        assert len(calls) == 2 and first.read_bytes() == payload  # re-fetched, repaired

        bad = build_web.Download("https://example.invalid/other.js", "other.js", "0" * 64)
        with pytest.raises(RuntimeError, match="does not match the pinned"):
            build_web.fetch_pinned(bad, tmp_path / "cache")
        assert not (tmp_path / "cache" / "other.js").exists()
        assert not (tmp_path / "cache" / "other.js.part").exists()


def test_lock_package_closure_follows_depends(build_web: ModuleType) -> None:
    closure = build_web.lock_package_closure(FAKE_LOCK, ("micropip", "pyyaml"))
    assert [p["name"] for p in closure] == ["micropip", "packaging", "pyyaml"]
    assert closure[0]["sha256"] == "m" * 64
    with pytest.raises(KeyError, match="nonexistent"):
        build_web.lock_package_closure(FAKE_LOCK, ("nonexistent",))


def test_pinned_pyodide_core_set_is_complete(build_web: ModuleType) -> None:
    """The five files loadPyodide() fetches from indexURL, each with a 64-hex pin."""
    assert set(build_web.PYODIDE_CORE_SHA256) == {
        "pyodide.js",
        "pyodide.asm.js",
        "pyodide.asm.wasm",
        "python_stdlib.zip",
        "pyodide-lock.json",
    }
    for name, digest in build_web.PYODIDE_CORE_SHA256.items():
        assert len(digest) == 64 and int(digest, 16) >= 0, name
    assert len(build_web.CHARTJS_SHA256) == 64
    assert build_web.PYODIDE_SOURCE.endswith("/v0.29.3/full/")


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
