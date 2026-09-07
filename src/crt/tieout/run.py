"""Run the PPM grid, compare, and regenerate ``docs/validation/tieout.md`` plus the JSON
manifest next to it (spec ``03-tieout.md``; BRIEF section 7)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from crt.io.appendix_g import AppendixG, load_appendix_g
from crt.io.deal_terms import NOTE_CLASSES, DealTerms, load_deal_terms
from crt.io.ppm_tables import (
    load_credit_event_sensitivity,
    load_declining_balances,
    load_table1,
    load_wal_table,
)
from crt.io.rep_lines import RepLine, load_rep_lines
from crt.money import ZERO
from crt.pool.projection import PoolProjection, project_pool
from crt.scenarios.grid import PPM_CER_AXIS_PCT, PPM_CPR_AXIS_PCT, ppm_grid
from crt.scenarios.scenario import Scenario
from crt.tieout.compare import (
    GridKey,
    compare_credit_event_sensitivity,
    compare_declining_balance_wal_rows,
    compare_declining_balances,
    compare_table1_windows,
    compare_wal_cells,
    compare_window_bands,
    grid_key,
)
from crt.tieout.manifest import RunManifest, build_manifest, utc_timestamp
from crt.tieout.report import TieoutResults, render_report
from crt.waterfall.engine import WaterfallResult, run_waterfall

REPORT_PATH = Path("docs/validation/tieout.md")
MANIFEST_PATH = Path("docs/validation/tieout-manifest.json")
# Hand-maintained log of spec 03 section 5 trials, included under section 7 of the report.
DIAGNOSTICS_LOG_PATH = Path("docs/validation/tieout-diagnostics.md")

# src/crt/tieout/run.py -> parents[3] is the project root (editable install).
DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class TieoutInputs:
    deal: DealTerms
    rep_lines: tuple[RepLine, ...]
    appendix_g: AppendixG


def load_inputs(root: Path) -> TieoutInputs:
    deal = load_deal_terms(root / "data/deal_terms/stacr_2026_dna1.yaml")
    rep_lines = load_rep_lines(
        root / "data/ppm_tables/appendix_c_rep_lines.csv",
        cut_off_date_balance=deal.cut_off_date_balance,
    )
    appendix_g = load_appendix_g(root / "data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv")
    return TieoutInputs(deal=deal, rep_lines=rep_lines, appendix_g=appendix_g)


class PoolCache:
    """One pool projection per (CPR, CER): both early-redemption bases share it."""

    def __init__(self, inputs: TieoutInputs) -> None:
        self._inputs = inputs
        self._cache: dict[tuple[Decimal, Decimal], PoolProjection] = {}

    def get(self, cpr: Decimal, cer: Decimal) -> PoolProjection:
        key = (cpr, cer)
        if key not in self._cache:
            self._cache[key] = project_pool(
                self._inputs.rep_lines,
                cpr=cpr,
                cer=cer,
                cut_off_date_balance=self._inputs.deal.cut_off_date_balance,
            )
        return self._cache[key]

    def __len__(self) -> int:
        return len(self._cache)


def run_scenario(inputs: TieoutInputs, scenario: Scenario, cache: PoolCache) -> WaterfallResult:
    pool = cache.get(scenario.cpr, scenario.cer)
    return run_waterfall(pool, inputs.deal, inputs.appendix_g, scenario)


def run_grid(inputs: TieoutInputs) -> dict[GridKey, WaterfallResult]:
    """All 96 PPM scenarios, keyed by (CPR %, CER %, early redemption)."""
    cache = PoolCache(inputs)
    runs: dict[GridKey, WaterfallResult] = {}
    for scenario in ppm_grid(sofr_rate=inputs.deal.sofr_rate_flat):
        result = run_scenario(inputs, scenario, cache)
        key = grid_key(scenario.cpr.scaleb(2), scenario.cer.scaleb(2), scenario.early_redemption)
        runs[key] = result
    return runs


def compare_all(root: Path, inputs: TieoutInputs, runs: dict[GridKey, WaterfallResult]) -> TieoutResults:
    tables = root / "data/ppm_tables"
    wal_cells = load_wal_table(tables / "wal_tables.csv", note_classes=NOTE_CLASSES)
    declining_cells, declining_wal_rows = load_declining_balances(
        tables / "declining_balances.csv", note_classes=NOTE_CLASSES
    )
    ces_cells = load_credit_event_sensitivity(tables / "credit_event_sensitivity.csv")
    table1 = load_table1(tables / "table1_classes.csv", note_classes=NOTE_CLASSES)

    wal_results = compare_wal_cells(runs, wal_cells)
    return TieoutResults(
        windows=compare_table1_windows(runs, table1),
        declining=compare_declining_balances(runs, declining_cells, inputs.deal),
        declining_wal_rows=compare_declining_balance_wal_rows(runs, declining_wal_rows),
        window_bands=compare_window_bands(runs, declining_cells, inputs.deal),
        wal_cer0=tuple(cell for cell in wal_results if cell.cer_pct == ZERO),
        wal_cer_positive=tuple(cell for cell in wal_results if cell.cer_pct > ZERO),
        credit_event_sensitivity=compare_credit_event_sensitivity(runs, ces_cells, inputs.deal),
    )


def scenario_grid_description() -> str:
    cprs = ", ".join(str(x) for x in PPM_CPR_AXIS_PCT)
    cers = ", ".join(str(x) for x in PPM_CER_AXIS_PCT)
    return f"CPR {{{cprs}}} % x CER {{{cers}}} % x RM 0 x early redemption {{off, on}}"


@dataclass(frozen=True)
class TieoutRun:
    results: TieoutResults
    manifest: RunManifest
    report: str
    runs: dict[GridKey, WaterfallResult]


def run_tieout(root: Path = DEFAULT_PROJECT_ROOT, *, timestamp: str | None = None) -> TieoutRun:
    """Compute everything; write nothing."""
    inputs = load_inputs(root)
    runs = run_grid(inputs)
    results = compare_all(root, inputs, runs)
    manifest = build_manifest(
        root,
        timestamp=timestamp if timestamp is not None else utc_timestamp(),
        scenario_grid=scenario_grid_description(),
    )
    log_path = root / DIAGNOSTICS_LOG_PATH
    diagnostics_log = log_path.read_text(encoding="utf-8") if log_path.is_file() else None
    return TieoutRun(
        results=results,
        manifest=manifest,
        report=render_report(results, manifest, diagnostics_log=diagnostics_log),
        runs=runs,
    )


def write_tieout(root: Path = DEFAULT_PROJECT_ROOT, *, timestamp: str | None = None) -> TieoutRun:
    """Run and regenerate ``docs/validation/tieout.md`` and ``tieout-manifest.json``."""
    run = run_tieout(root, timestamp=timestamp)
    report_path = root / REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(run.report, encoding="utf-8", newline="\n")
    (root / MANIFEST_PATH).write_text(run.manifest.to_json(), encoding="utf-8", newline="\n")
    return run
