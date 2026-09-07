"""Writer for ``docs/validation/tieout.md`` in the layout of spec ``03-tieout.md``
section 7.  The timestamp appears only in the title line; every other line is a pure
function of the inputs, so two runs differ in that line alone."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.io.deal_terms import NOTE_CLASSES
from crt.money import round_half_up
from crt.tieout.compare import (
    CreditEventSensitivityResult,
    DecliningBalanceResult,
    DecliningBalanceWalResult,
    WalCellResult,
    WindowBandResult,
    WindowResult,
)
from crt.tieout.manifest import RunManifest

FAMILY_TABLE1 = "Table 1 windows"
FAMILY_DECLINING = "Declining Balances CER 0"
FAMILY_WAL_CER0 = "WAL CER 0"
FAMILY_WAL_CER_POSITIVE = "WAL CER>0"
FAMILY_CREDIT_EVENT = "Credit Event Sensitivity"


@dataclass(frozen=True)
class FamilySummary:
    family: str
    cells: int
    passes: int
    fails: int
    worst_abs_diff: str
    tolerance: str

    @property
    def status(self) -> str:
        return "PASS" if self.fails == 0 else "FAIL"


@dataclass(frozen=True)
class TieoutResults:
    windows: tuple[WindowResult, ...]
    declining: tuple[DecliningBalanceResult, ...]
    declining_wal_rows: tuple[DecliningBalanceWalResult, ...]
    window_bands: tuple[WindowBandResult, ...]
    wal_cer0: tuple[WalCellResult, ...]
    wal_cer_positive: tuple[WalCellResult, ...]
    credit_event_sensitivity: tuple[CreditEventSensitivityResult, ...]

    def summaries(self) -> tuple[FamilySummary, ...]:
        return (
            _summarise(
                FAMILY_TABLE1,
                [w.passes for w in self.windows],
                [
                    Decimal(abs((w.model_first or 0) - w.ppm_first)
                            + abs((w.model_last or 0) - w.ppm_last))
                    for w in self.windows
                ],
                "exact month",
                places=0,
            ),
            _summarise(
                FAMILY_DECLINING,
                [c.round_match for c in self.declining],
                [abs(c.diff) for c in self.declining],
                "round-match (A13); ±0.25 pp reported",
                places=2,
            ),
            _summarise(
                FAMILY_WAL_CER0,
                [c.within_tolerance for c in self.wal_cer0],
                [abs(c.diff) for c in self.wal_cer0 if c.diff is not None],
                "±0.02 yr",
                places=4,
            ),
            _summarise(
                FAMILY_WAL_CER_POSITIVE,
                [c.within_tolerance for c in self.wal_cer_positive],
                [abs(c.diff) for c in self.wal_cer_positive if c.diff is not None],
                "±0.02 yr",
                places=4,
            ),
            _summarise(
                FAMILY_CREDIT_EVENT,
                [c.round_match for c in self.credit_event_sensitivity],
                [abs(c.diff) for c in self.credit_event_sensitivity],
                "round-match (A13); ±0.25 pp reported",
                places=2,
            ),
        )

    def overall_pass(self) -> bool:
        return all(summary.fails == 0 for summary in self.summaries()) and all(
            band.passes for band in self.window_bands
        )


def _summarise(
    family: str, passes: list[bool], abs_diffs: list[Decimal], tolerance: str, *, places: int
) -> FamilySummary:
    worst = max(abs_diffs) if abs_diffs else Decimal(0)
    return FamilySummary(
        family=family,
        cells=len(passes),
        passes=sum(1 for p in passes if p),
        fails=sum(1 for p in passes if not p),
        worst_abs_diff=fmt(worst, places),
        tolerance=tolerance,
    )


def fmt(value: Decimal | None, places: int) -> str:
    """Half-up display rounding of a stored unrounded value; ``n/a`` for None."""
    if value is None:
        return "n/a"
    return str(round_half_up(value, places))


def fmt_signed(value: Decimal | None, places: int) -> str:
    if value is None:
        return "n/a"
    text = fmt(value, places)
    return text if text.startswith("-") else "+" + text


def _basis(early_redemption: bool) -> str:
    return "To Early Redemption Date" if early_redemption else "To Scheduled Maturity Date"


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _pass_fail(flag: bool) -> str:
    return "pass" if flag else "FAIL"


def _cpr(value: Decimal) -> str:
    """Plain positional notation (``Decimal("10")`` -> ``"10"``, never ``1E+1``)."""
    return format(value, "f")


def render_report(
    results: TieoutResults, manifest: RunManifest, *, diagnostics_log: str | None = None
) -> str:
    """Render the report.  ``diagnostics_log`` is the content of the hand-maintained
    trials file (``docs/validation/tieout-diagnostics.md``), included verbatim under
    section 7 when anything fails; it is part of the inputs, so the output stays
    deterministic."""
    lines: list[str] = []
    add = lines.append

    add(f"# Tie-out — STACR 2026-DNA1 — {manifest.timestamp_utc}")
    hashes = "; ".join(f"{name} {digest}" for name, digest in manifest.input_sha256.items())
    add(
        f"Manifest: engine version {manifest.engine_version}, git commit {manifest.git_commit}, "
        f"Decimal precision {manifest.decimal_precision}, scenario grid {manifest.scenario_grid}; "
        f"SHA-256: {hashes}; conventions in force: {' '.join(manifest.conventions_in_force)}."
    )
    add("")

    add("## 1. Summary")
    add("| family | cells | pass | fail | worst \\|diff\\| | tolerance | status |")
    add("|---|---|---|---|---|---|---|")
    for summary in results.summaries():
        add(
            f"| {summary.family} | {summary.cells} | {summary.passes} | {summary.fails} | "
            f"{summary.worst_abs_diff} | {summary.tolerance} | {summary.status} |"
        )
    band_fails = sum(1 for band in results.window_bands if not band.passes)
    add(
        f"Secondary window-band check (spec 03 section 2): {len(results.window_bands)} "
        f"(Note, CPR) pairs, {band_fails} failing."
    )
    add(f"Overall: {'PASS' if results.overall_pass() else 'FAIL'}.")
    add("")

    add("## 2. Table 1 principal windows (10 % CPR, CER 0, early redemption on)")
    add("| Note | model first | model last | PPM window | pass |")
    add("|---|---|---|---|---|")
    for window in results.windows:
        add(
            f"| {window.note} | {window.model_first if window.model_first is not None else 'n/a'} | "
            f"{window.model_last if window.model_last is not None else 'n/a'} | "
            f"{window.ppm_first}-{window.ppm_last} | {_pass_fail(window.passes)} |"
        )
    add("")

    add("## 3. Declining Balances (CER 0), one table per Note")
    for note in NOTE_CLASSES:
        add(f"### {note}")
        add("| CPR | row date | model % (2 dp) | PPM % | diff | round-match pass | \\|diff\\| ≤ 0.25 |")
        add("|---|---|---|---|---|---|---|")
        for cell in results.declining:
            if cell.note != note:
                continue
            add(
                f"| {_cpr(cell.cpr_pct)} | {cell.row_label} | {fmt(cell.model_pct, 2)} | {cell.printed} | "
                f"{fmt_signed(cell.diff, 2)} | {_pass_fail(cell.round_match)} | "
                f"{_yes_no(cell.within_brief_tolerance)} |"
            )
        add("")
        add("| CPR | basis | model WAL (4 dp) | PPM | diff | ±0.02 |")
        add("|---|---|---|---|---|---|")
        for wal_row in results.declining_wal_rows:
            if wal_row.note != note:
                continue
            add(
                f"| {_cpr(wal_row.cpr_pct)} | {_basis(wal_row.early_redemption)} | "
                f"{fmt(wal_row.model, 4)} | {wal_row.printed} | {fmt_signed(wal_row.diff, 4)} | "
                f"{_pass_fail(wal_row.within_tolerance)} |"
            )
        add("")
        add("| CPR | model last principal PD | must be after PD | must be on or before PD | pass |")
        add("|---|---|---|---|---|")
        for band in results.window_bands:
            if band.note != note:
                continue
            add(
                f"| {_cpr(band.cpr_pct)} | {band.model_last if band.model_last is not None else 'n/a'} | "
                f"{band.after_payment_date} | {band.on_or_before_payment_date} | "
                f"{_pass_fail(band.passes)} |"
            )
        add("")

    add("## 4. WAL, CER 0, RM 0")
    add("| Note | basis | CPR | model WAL (4 dp) | PPM | diff | ±0.02 | ±0.10 |")
    add("|---|---|---|---|---|---|---|---|")
    for wal_cell in results.wal_cer0:
        add(
            f"| {wal_cell.note} | {_basis(wal_cell.early_redemption)} | {_cpr(wal_cell.cpr_pct)} | "
            f"{fmt(wal_cell.model, 4)} | {wal_cell.printed} | {fmt_signed(wal_cell.diff, 4)} | "
            f"{_pass_fail(wal_cell.within_tolerance)} | {_pass_fail(wal_cell.within_milestone)} |"
        )
    add("")

    add("## 5. WAL, CER > 0, RM 0")
    add("| Note | basis | CER | CPR | model | PPM | diff | ±0.02 |")
    add("|---|---|---|---|---|---|---|---|")
    for cer_cell in results.wal_cer_positive:
        add(
            f"| {cer_cell.note} | {_basis(cer_cell.early_redemption)} | {cer_cell.cer_pct}% | "
            f"{_cpr(cer_cell.cpr_pct)} | {fmt(cer_cell.model, 4)} | {cer_cell.printed} | "
            f"{fmt_signed(cer_cell.diff, 4)} | {_pass_fail(cer_cell.within_tolerance)} |"
        )
    add("")

    add("## 6. Credit Event Sensitivity")
    add("| basis | CER | CPR | model % (2 dp) | PPM % | diff | round-match pass | \\|diff\\| ≤ 0.25 |")
    add("|---|---|---|---|---|---|---|---|")
    for ces_cell in results.credit_event_sensitivity:
        add(
            f"| {_basis(ces_cell.early_redemption)} | {ces_cell.cer_pct}% | {_cpr(ces_cell.cpr_pct)} | "
            f"{fmt(ces_cell.model_pct, 2)} | {ces_cell.printed} | {fmt_signed(ces_cell.diff, 2)} | "
            f"{_pass_fail(ces_cell.round_match)} | {_yes_no(ces_cell.within_brief_tolerance)} |"
        )
    add("")

    if not results.overall_pass():
        add("## 7. Diagnostics (only when anything fails)")
        if diagnostics_log is None or not diagnostics_log.strip():
            add("| hypothesis (§5 number) | change tried | family/cells affected | before | after | kept? |")
            add("|---|---|---|---|---|---|")
            add(
                "| — | no trial recorded: the engine implements A1-A15 as specified; trials "
                "of the spec 03 section 5 list are logged by hand in "
                "docs/validation/tieout-diagnostics.md, one at a time | — | — | — | — |"
            )
        else:
            lines.extend(diagnostics_log.rstrip("\n").splitlines())
        add("")

    return "\n".join(lines) + "\n"
