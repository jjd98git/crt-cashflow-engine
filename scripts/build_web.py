"""Build ``web/dist/``: the static site that runs the engine in the browser.

The page contacts ONE origin at runtime (the site itself).  Everything it needs is copied
into ``web/dist/`` at build time, hashed, and listed in the manifest, which the Web Worker
checks (SHA-256, byte count) before using any file::

    web/dist/
      index.html, app.js, app.css, worker.js      the page (copied from web/)
      diag.html                                   per-file fetch test page (copied from web/)
      manifest.bin                                the manifest the worker fetches
      manifest.json                               byte-identical copy, for people and diag.html
      pyodide/                                    the Pyodide runtime, self-hosted, ORIGINAL names
        pyodide.js, pyodide.asm.js, pyodide.asm.wasm, python_stdlib.zip, pyodide-lock.json
        micropip-*.whl, pyyaml-*.whl              what loadPackage(["micropip", "pyyaml"]) fetches
      vendor/chart.umd.min.js                     Chart.js, self-hosted
      files/<sha256 prefix>.bin                   every project file and every wheel

Neutral names: project files (``.yaml``, ``.csv``, ``.json``, ``.md``, ``.py``, ``.toml``) and
wheels (``.whl``) are served as ``files/<first 16 hex of sha256>.bin`` so no extension a
corporate proxy might filter appears in a fetched URL; the manifest keeps the logical path
(``path``) next to the served one (``served``) and the worker writes each file under its
logical path in Pyodide's file system.  The Pyodide runtime is the one exception: Pyodide
fetches its own files by name from ``indexURL``, so ``pyodide/`` keeps ``.wasm``, ``.zip``,
``.json`` and two ``.whl`` names (README and diag.html say so).

Downloads (the Pyodide runtime from its release CDN, Chart.js from cdnjs, the openpyxl and
et_xmlfile wheels with ``pip download``) happen at build time only.  Each runtime and vendor
file is pinned by SHA-256 here and cached under ``web/.cache/``; a cached file with the
right hash is not fetched again, a file that hashes differently is refused.  CI has no cache
and downloads fresh.  The engine wheel is built with ``uv build --wheel`` (falling back to
``python -m build``).  Nothing here touches the engine; the script copies files and hashes
them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
DIST_DIR = WEB_DIR / "dist"
CACHE_DIR = WEB_DIR / ".cache"  # gitignored; verified downloads, reused across builds

FILES_SUBDIR = "files"  # project files and wheels, as <sha256[:16]>.bin
PYODIDE_SUBDIR = "pyodide"  # the runtime, original file names (Pyodide fetches them itself)
VENDOR_SUBDIR = "vendor"
MANIFEST_JSON = "manifest.json"  # readable copy
MANIFEST_SERVED = "manifest.bin"  # what the worker fetches; identical bytes

# Static page files, copied as-is into web/dist/ (not loaded into the Pyodide FS).
PAGE_FILES: tuple[str, ...] = ("index.html", "app.js", "app.css", "worker.js", "diag.html")

# Pure-Python wheels the worker installs from this site, in dependency order (each with
# deps=False): et_xmlfile is openpyxl's only dependency; the engine wheel comes last.
VENDORED_WHEELS: tuple[str, ...] = ("et_xmlfile==2.0.0", "openpyxl==3.1.5")

# Pyodide release the worker runs (CPython 3.13.2, C _decimal built in).  The five core
# files are what loadPyodide() fetches from indexURL; each is pinned to the SHA-256 of the
# published release so a build never ships a file that differs from it.
PYODIDE_VERSION = "0.29.3"
PYODIDE_SOURCE = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"
PYODIDE_LOCK_FILE = "pyodide-lock.json"
PYODIDE_CORE_SHA256: dict[str, str] = {
    "pyodide.js": "718d40f1c015dd25ec724cc8fc4e2325d6a45a92ae225121ff6953f224a16f72",
    "pyodide.asm.js": "1263f02b5b26099b96112378156f242dd98b39a8201ba7765e5fe3d455c5ce91",
    "pyodide.asm.wasm": "e2f4ee75b325e35eb31bfb8c613d4dd5098f5502c156a97847686875b5025480",
    "python_stdlib.zip": "4298b6ee445cb724c3973437da47789752b9e6ff4e26619026b283ec801fc46b",
    PYODIDE_LOCK_FILE: "3256ffc76388de0e37f4b34d42ab484268d1afc675179ff97b2a5bb14f84ccac",
}
# Packages the worker loads with pyodide.loadPackage(); their files, dependencies and
# hashes come from the pinned lock file above, never from a guess.
PYODIDE_PACKAGES: tuple[str, ...] = ("micropip", "pyyaml")

CHARTJS_VERSION = "4.5.1"
CHARTJS_FILE = "chart.umd.min.js"
CHARTJS_SOURCE = f"https://cdnjs.cloudflare.com/ajax/libs/Chart.js/{CHARTJS_VERSION}/{CHARTJS_FILE}"
CHARTJS_SHA256 = "48444a82d4edcb5bec0f1965faacdde18d9c17db3063d042abada2f705c9f54a"

# Files written to /project/<path> in the browser; globs are relative to the repo root.
PROJECT_FILE_GLOBS: tuple[str, ...] = (
    "pyproject.toml",
    "data/deal_terms/stacr_2026_dna1.yaml",
    "data/ppm_tables/*.csv",
    "data/ppm_tables/*.yaml",
    "data/ppm_tables/*.md",
    "docs/assumptions.csv",
    "docs/validation/tieout.md",
    "docs/validation/tieout-diagnostics.md",
    "scenarios/*.yaml",
)
BRIDGE_FILE = "engine_bridge.py"  # from web/, shipped to /project/engine_bridge.py
BUILD_INFO_FILE = "build_info.json"


@dataclass(frozen=True)
class FileEntry:
    path: str  # logical path: relative to /project in the browser
    served: str  # relative to web/dist: files/<sha256[:16]>.bin
    sha256: str
    bytes: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "path": self.path,
            "served": self.served,
            "sha256": self.sha256,
            "bytes": self.bytes,
        }


@dataclass(frozen=True)
class Download:
    """One pinned build-time download: ``url`` must hash to ``sha256``."""

    url: str
    file_name: str
    sha256: str


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def served_name(sha256: str) -> str:
    """The neutral, content-addressed name a project file or wheel is served under."""
    return f"{FILES_SUBDIR}/{sha256[:16]}.bin"


def collect_project_files(root: Path = ROOT) -> list[Path]:
    """Every repo file the page loads into /project, resolved from the globs.  A glob
    that matches nothing is an error: a missing input is never silently dropped."""
    files: list[Path] = []
    for pattern in PROJECT_FILE_GLOBS:
        matches = sorted(p for p in root.glob(pattern) if p.is_file())
        if not matches:
            raise FileNotFoundError(f"{pattern}: no file matches under {root}")
        files.extend(matches)
    return files


def git_commit(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip() or None


def engine_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def build_wheel(root: Path, out_dir: Path) -> Path:
    """Build the pure-Python wheel into ``out_dir`` and return its path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    commands = (
        ["uv", "build", "--wheel", "--out-dir", str(out_dir), str(root)],
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(out_dir), str(root)],
    )
    errors: list[str] = []
    for command in commands:
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, cwd=root)
            break
        except (OSError, subprocess.CalledProcessError) as error:
            detail = str(getattr(error, "stderr", "") or error)
            errors.append(f"{' '.join(command[:3])}: {detail.strip()[-400:]}")
    else:
        raise RuntimeError("could not build the wheel:\n" + "\n".join(errors))
    wheels = sorted(out_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected exactly one wheel in {out_dir}, found {wheels}")
    return wheels[0]


def download_wheels(requirements: tuple[str, ...], out_dir: Path) -> list[Path]:
    """``pip download`` each pinned requirement as a wheel into ``out_dir`` (no
    dependencies, binaries only) and return the wheel paths in ``requirements`` order.

    Tries ``sys.executable -m pip`` first, then ``pip`` on PATH (the uv-created venv has
    no pip; CI installs uv with the runner's pip), then ``uv run --with pip``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pip_args = ["download", "--only-binary=:all:", "--no-deps", "--dest", str(out_dir)]
    commands = (
        [sys.executable, "-m", "pip", *pip_args, *requirements],
        ["pip", *pip_args, *requirements],
        ["uv", "run", "--no-project", "--with", "pip", "python", "-m", "pip", *pip_args]
        + list(requirements),
    )
    errors: list[str] = []
    for command in commands:
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            break
        except (OSError, subprocess.CalledProcessError) as error:
            detail = str(getattr(error, "stderr", "") or error)
            errors.append(f"{' '.join(command[:3])}: {detail.strip()[-400:]}")
    else:
        raise RuntimeError("could not download the vendored wheels:\n" + "\n".join(errors))

    wheels: list[Path] = []
    for requirement in requirements:
        name = requirement.split("==", 1)[0].replace("-", "_").lower()
        matches = sorted(p for p in out_dir.glob("*.whl") if p.name.lower().startswith(f"{name}-"))
        if len(matches) != 1:
            raise RuntimeError(
                f"{requirement}: expected exactly one wheel in {out_dir}, found {matches}"
            )
        wheels.append(matches[0])
    return wheels


# ----------------------------------------------------------------- pinned downloads


def fetch_pinned(download: Download, cache_dir: Path) -> Path:
    """Return ``cache_dir/<file_name>`` holding bytes that hash to ``download.sha256``:
    reuse the cached copy when it already matches, otherwise fetch ``download.url``
    into a temporary file, verify, and move it into place.  A mismatch is an error
    naming the URL and both digests; nothing unverified is ever left under the name."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / download.file_name
    if target.is_file() and sha256_of(target) == download.sha256:
        return target
    partial = target.with_name(target.name + ".part")
    try:
        with (
            urllib.request.urlopen(download.url, timeout=120) as response,
            partial.open("wb") as handle,
        ):
            shutil.copyfileobj(response, handle, 1 << 20)
    except OSError as error:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"GET {download.url} failed: {error}") from error
    actual = sha256_of(partial)
    if actual != download.sha256:
        partial.unlink()
        raise RuntimeError(
            f"{download.url}: SHA-256 {actual} does not match the pinned {download.sha256}; "
            "refusing to ship it (a new release needs a new pin in scripts/build_web.py)"
        )
    partial.replace(target)
    return target


def lock_package_closure(lock: dict[str, object], names: tuple[str, ...]) -> list[dict[str, str]]:
    """The packages ``pyodide.loadPackage(names)`` fetches: ``names`` plus every package
    reachable through the lock file's ``depends`` lists, each as
    ``{"name", "file_name", "sha256", "version"}`` sorted by name.  An unknown package
    name is an error, never skipped."""
    packages = lock["packages"]
    assert isinstance(packages, dict)
    closure: dict[str, dict[str, str]] = {}
    pending = list(names)
    while pending:
        name = pending.pop()
        if name in closure:
            continue
        if name not in packages:
            raise KeyError(f"{name}: not in {PYODIDE_LOCK_FILE} (Pyodide {PYODIDE_VERSION})")
        entry = packages[name]
        closure[name] = {
            "name": name,
            "file_name": str(entry["file_name"]),
            "sha256": str(entry["sha256"]),
            "version": str(entry["version"]),
        }
        pending.extend(str(dep) for dep in entry.get("depends", []))
    return [closure[name] for name in sorted(closure)]


def runtime_downloads(cache_dir: Path) -> list[Download]:
    """Everything ``loadPyodide()`` and ``loadPackage(PYODIDE_PACKAGES)`` fetch from
    indexURL, in a fixed order: the five core files, then the package wheels the pinned
    lock file names (read from the cached, verified lock file)."""
    downloads = [
        Download(f"{PYODIDE_SOURCE}{name}", name, sha) for name, sha in PYODIDE_CORE_SHA256.items()
    ]
    lock_path = fetch_pinned(
        Download(
            f"{PYODIDE_SOURCE}{PYODIDE_LOCK_FILE}",
            PYODIDE_LOCK_FILE,
            PYODIDE_CORE_SHA256[PYODIDE_LOCK_FILE],
        ),
        cache_dir,
    )
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for package in lock_package_closure(lock, PYODIDE_PACKAGES):
        downloads.append(
            Download(
                f"{PYODIDE_SOURCE}{package['file_name']}", package["file_name"], package["sha256"]
            )
        )
    return downloads


def _shipped_entry(shipped: Path, extra: dict[str, str] | None = None) -> dict[str, str | int]:
    entry: dict[str, str | int] = {
        "path": shipped.name,
        "bytes": shipped.stat().st_size,
        "sha256": sha256_of(shipped),
    }
    if extra:
        entry.update(extra)
    return entry


def _empty_directory(directory: Path) -> None:
    """Remove the contents, not the directory itself: a local ``http.server`` started
    inside ``web/dist`` holds it open on Windows, and keeping the directory lets a rebuild
    land under a running server."""
    directory.mkdir(parents=True, exist_ok=True)
    for child in directory.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def build(
    root: Path = ROOT,
    dist: Path = DIST_DIR,
    *,
    skip_wheel: bool = False,
    cache_dir: Path = CACHE_DIR,
) -> Path:
    _empty_directory(dist)

    for name in PAGE_FILES:
        source = root / "web" / name
        if not source.is_file():
            raise FileNotFoundError(f"{source}: page file missing")
        shutil.copy2(source, dist / name)

    files_dir = dist / FILES_SUBDIR
    files_dir.mkdir()

    def ship(source: Path) -> dict[str, str | int]:
        """Copy ``source`` to files/<hash>.bin; return served path, hash and size."""
        digest = sha256_of(source)
        served = served_name(digest)
        target = dist / served
        if not target.exists():
            shutil.copy2(source, target)
        return {"served": served, "sha256": digest, "bytes": source.stat().st_size}

    entries: list[FileEntry] = []

    def ship_project_file(source: Path, logical: str) -> None:
        shipped = ship(source)
        entries.append(
            FileEntry(
                logical, str(shipped["served"]), str(shipped["sha256"]), int(shipped["bytes"])
            )
        )

    for source in collect_project_files(root):
        ship_project_file(source, source.relative_to(root).as_posix())
    ship_project_file(root / "web" / BRIDGE_FILE, BRIDGE_FILE)

    version = engine_version(root)
    commit = git_commit(root)
    built_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    build_info = {"engine_version": version, "git_commit": commit, "built_utc": built_utc}
    with tempfile.TemporaryDirectory() as tmp:
        build_info_path = Path(tmp) / BUILD_INFO_FILE
        build_info_path.write_text(
            json.dumps(build_info, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        ship_project_file(build_info_path, BUILD_INFO_FILE)

    def ship_wheel(wheel: Path, requirement: str | None = None) -> dict[str, str | int]:
        entry: dict[str, str | int] = {"path": f"wheels/{wheel.name}", "file_name": wheel.name}
        if requirement is not None:
            entry["requirement"] = requirement
        entry.update(ship(wheel))
        return entry

    vendored: list[dict[str, str | int]] = []
    with tempfile.TemporaryDirectory() as tmp:
        for requirement, wheel in zip(
            VENDORED_WHEELS, download_wheels(VENDORED_WHEELS, Path(tmp)), strict=True
        ):
            vendored.append(ship_wheel(wheel, requirement))

    wheel_entry: dict[str, str | int] | None = None
    if not skip_wheel:
        with tempfile.TemporaryDirectory() as tmp:
            wheel_entry = ship_wheel(build_wheel(root, Path(tmp)))

    # The Pyodide runtime, original names, under pyodide/ (this is the worker's indexURL).
    pyodide_dir = dist / PYODIDE_SUBDIR
    pyodide_dir.mkdir()
    runtime_files: list[dict[str, str | int]] = []
    for download in runtime_downloads(cache_dir):
        shipped = pyodide_dir / download.file_name
        shutil.copy2(fetch_pinned(download, cache_dir), shipped)
        runtime_files.append(
            _shipped_entry(
                shipped,
                {
                    "path": f"{PYODIDE_SUBDIR}/{download.file_name}",
                    "file_name": download.file_name,
                    "source": download.url,
                },
            )
        )

    vendor_dir = dist / VENDOR_SUBDIR
    vendor_dir.mkdir()
    chart_download = Download(CHARTJS_SOURCE, CHARTJS_FILE, CHARTJS_SHA256)
    chart_shipped = vendor_dir / CHARTJS_FILE
    shutil.copy2(fetch_pinned(chart_download, cache_dir), chart_shipped)
    vendor = [
        _shipped_entry(
            chart_shipped,
            {
                "name": "Chart.js",
                "version": CHARTJS_VERSION,
                "path": f"{VENDOR_SUBDIR}/{CHARTJS_FILE}",
                "source": CHARTJS_SOURCE,
            },
        )
    ]

    manifest = {
        "generated_utc": built_utc,
        "engine_version": version,
        "git_commit": commit,
        "project_root": "/project",
        "served_manifest": MANIFEST_SERVED,
        "runtime": {
            "pyodide_version": PYODIDE_VERSION,
            "index_url": f"{PYODIDE_SUBDIR}/",  # relative to the site; original file names
            "packages": list(PYODIDE_PACKAGES),
            "source": PYODIDE_SOURCE,
            "files": runtime_files,
        },
        "vendor": vendor,
        "wheel": wheel_entry,
        "wheels": vendored,  # installed before the engine wheel, in this order
        "files": [entry.to_dict() for entry in entries],
    }
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (dist / MANIFEST_JSON).write_text(text, encoding="utf-8")
    (dist / MANIFEST_SERVED).write_text(text, encoding="utf-8")
    return dist


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build web/dist for GitHub Pages")
    parser.add_argument("--skip-wheel", action="store_true", help="page and data only")
    args = parser.parse_args(argv)
    dist = build(skip_wheel=args.skip_wheel)
    manifest = json.loads((dist / MANIFEST_JSON).read_text(encoding="utf-8"))
    wheel = manifest["wheel"]["file_name"] if manifest["wheel"] else "(no wheel)"
    vendored = ", ".join(entry["file_name"] for entry in manifest["wheels"])
    runtime_bytes = sum(int(entry["bytes"]) for entry in manifest["runtime"]["files"])
    total_bytes = sum(p.stat().st_size for p in dist.rglob("*") if p.is_file())
    print(f"{dist}: {len(manifest['files'])} project files, wheel {wheel}")
    print(f"vendored wheels: {vendored}")
    print(
        f"Pyodide {PYODIDE_VERSION} runtime: {len(manifest['runtime']['files'])} files, "
        f"{runtime_bytes / 1e6:.1f} MB; Chart.js {CHARTJS_VERSION}; site total {total_bytes / 1e6:.1f} MB"
    )
    print(f"engine {manifest['engine_version']}, commit {manifest['git_commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
