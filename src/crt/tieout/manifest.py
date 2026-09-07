"""Run manifest (BRIEF section 2: deterministic and reproducible)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import getcontext
from pathlib import Path

# Relative paths of every input the tie-out consumes (spec 03 section 7 manifest line).
TIEOUT_INPUT_FILES: tuple[str, ...] = (
    "data/ppm_tables/appendix_c_rep_lines.csv",
    "data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv",
    "data/ppm_tables/table1_classes.csv",
    "data/ppm_tables/wal_tables.csv",
    "data/ppm_tables/declining_balances.csv",
    "data/ppm_tables/credit_event_sensitivity.csv",
    "data/deal_terms/stacr_2026_dna1.yaml",
    "docs/assumptions.csv",
)
# Conventions in force for the v1 run (register A1-A15; spec 00-04).
CONVENTIONS_IN_FORCE: tuple[str, ...] = tuple(f"A{i}" for i in range(1, 16))


class ManifestError(RuntimeError):
    """The manifest could not be assembled (missing file, no git commit)."""


@dataclass(frozen=True)
class RunManifest:
    engine_version: str
    git_commit: str
    timestamp_utc: str
    decimal_precision: int
    input_sha256: dict[str, str]
    conventions_in_force: tuple[str, ...]
    scenario_grid: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True) + "\n"


def sha256_of(path: Path) -> str:
    if not path.is_file():
        raise ManifestError(f"{path}: input file not found")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def engine_version(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise ManifestError(f"{pyproject}: not found")
    with pyproject.open("rb") as handle:
        data = tomllib.load(handle)
    try:
        version = data["project"]["version"]
    except KeyError:
        raise ManifestError("pyproject.toml has no [project].version") from None
    return str(version)


def git_commit(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ManifestError(f"git rev-parse HEAD failed in {root}: {error}") from None
    return completed.stdout.strip()


def utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_manifest(root: Path, *, timestamp: str, scenario_grid: str) -> RunManifest:
    return RunManifest(
        engine_version=engine_version(root),
        git_commit=git_commit(root),
        timestamp_utc=timestamp,
        decimal_precision=getcontext().prec,
        input_sha256={name: sha256_of(root / name) for name in TIEOUT_INPUT_FILES},
        conventions_in_force=CONVENTIONS_IN_FORCE,
        scenario_grid=scenario_grid,
    )
