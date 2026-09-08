"""Build ``web/dist/``: the static site that runs the engine in the browser.

Output layout (everything the page fetches; every project file and the wheel are listed
in ``manifest.json`` with SHA-256, and the Web Worker verifies each one before writing
it into Pyodide's virtual file system under ``/project/``)::

    web/dist/
      index.html, app.js, app.css, worker.js      the page (copied from web/)
      diag.html                                   per-file fetch test page (copied from web/)
      manifest.json                               file list + hashes + wheel entries
      wheels/crt_cashflow_engine-<v>-py3-none-any.whl
      wheels/et_xmlfile-<v>-*.whl, openpyxl-<v>-*.whl   vendored pure-Python dependencies
      engine_bridge.py                            -> /project/engine_bridge.py
      build_info.json                             -> /project/build_info.json
      pyproject.toml                              -> /project/pyproject.toml (engine version)
      data/deal_terms/stacr_2026_dna1.yaml        -> /project/data/...
      data/ppm_tables/*.csv|yaml|md
      docs/assumptions.csv
      docs/validation/tieout.md, tieout-diagnostics.md
      scenarios/*.yaml

The wheel is built with ``uv build --wheel`` (falling back to ``python -m build``).  The
openpyxl and et_xmlfile wheels are downloaded once at build time with ``pip download``
(``--only-binary=:all: --no-deps``) so the page installs them from this site and never
contacts a package index.  Nothing here touches the engine; the script copies files and
hashes them.
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
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
DIST_DIR = WEB_DIR / "dist"
WHEELS_SUBDIR = "wheels"

# Static page files, copied as-is into web/dist/ (not loaded into the Pyodide FS).
PAGE_FILES: tuple[str, ...] = ("index.html", "app.js", "app.css", "worker.js", "diag.html")

# Pure-Python wheels the worker installs from this site, in dependency order (each with
# deps=False): et_xmlfile is openpyxl's only dependency; the engine wheel comes last.
VENDORED_WHEELS: tuple[str, ...] = ("et_xmlfile==2.0.0", "openpyxl==3.1.5")

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
    path: str  # relative to web/dist and to /project
    sha256: str
    bytes: int

    def to_dict(self) -> dict[str, str | int]:
        return {"path": self.path, "sha256": self.sha256, "bytes": self.bytes}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _wheel_entry(shipped: Path, requirement: str | None = None) -> dict[str, str | int]:
    entry: dict[str, str | int] = {
        "path": f"{WHEELS_SUBDIR}/{shipped.name}",
        "file_name": shipped.name,
        "sha256": sha256_of(shipped),
        "bytes": shipped.stat().st_size,
    }
    if requirement is not None:
        entry["requirement"] = requirement
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


def build(root: Path = ROOT, dist: Path = DIST_DIR, *, skip_wheel: bool = False) -> Path:
    _empty_directory(dist)

    for name in PAGE_FILES:
        source = root / "web" / name
        if not source.is_file():
            raise FileNotFoundError(f"{source}: page file missing")
        shutil.copy2(source, dist / name)

    entries: list[FileEntry] = []

    def ship(source: Path, relative: str) -> None:
        target = dist / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append(FileEntry(relative, sha256_of(target), target.stat().st_size))

    for source in collect_project_files(root):
        ship(source, source.relative_to(root).as_posix())
    ship(root / "web" / BRIDGE_FILE, BRIDGE_FILE)

    version = engine_version(root)
    commit = git_commit(root)
    built_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    build_info = {"engine_version": version, "git_commit": commit, "built_utc": built_utc}
    build_info_path = dist / BUILD_INFO_FILE
    build_info_path.write_text(
        json.dumps(build_info, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    entries.append(
        FileEntry(BUILD_INFO_FILE, sha256_of(build_info_path), build_info_path.stat().st_size)
    )

    wheels_dir = dist / WHEELS_SUBDIR
    wheels_dir.mkdir()
    vendored: list[dict[str, str | int]] = []
    with tempfile.TemporaryDirectory() as tmp:
        for requirement, wheel in zip(
            VENDORED_WHEELS, download_wheels(VENDORED_WHEELS, Path(tmp)), strict=True
        ):
            shipped = wheels_dir / wheel.name
            shutil.copy2(wheel, shipped)
            vendored.append(_wheel_entry(shipped, requirement))

    wheel_entry: dict[str, str | int] | None = None
    if not skip_wheel:
        with tempfile.TemporaryDirectory() as tmp:
            wheel = build_wheel(root, Path(tmp))
            shipped = wheels_dir / wheel.name
            shutil.copy2(wheel, shipped)
        wheel_entry = _wheel_entry(shipped)

    manifest = {
        "generated_utc": built_utc,
        "engine_version": version,
        "git_commit": commit,
        "project_root": "/project",
        "wheel": wheel_entry,
        "wheels": vendored,  # installed before the engine wheel, in this order
        "files": [entry.to_dict() for entry in entries],
    }
    (dist / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return dist


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build web/dist for GitHub Pages")
    parser.add_argument("--skip-wheel", action="store_true", help="page and data only")
    args = parser.parse_args(argv)
    dist = build(skip_wheel=args.skip_wheel)
    manifest = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    wheel = manifest["wheel"]["path"] if manifest["wheel"] else "(no wheel)"
    vendored = ", ".join(entry["file_name"] for entry in manifest["wheels"])
    print(f"{dist}: {len(manifest['files'])} project files, wheel {wheel}")
    print(f"vendored wheels: {vendored}")
    print(f"engine {manifest['engine_version']}, commit {manifest['git_commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
