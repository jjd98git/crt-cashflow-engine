"""VALUES workbook of one run: the hypothetical structure Payment Date by Payment Date,
with charts of the tranche stack over time (BRIEF section 9, first Phase 5 deliverable).

Every cell is an engine value read off a ``crt.api.RunResult``.  There are no formulas:
the live-formula workbook with the recalculation test of BRIEF section 9 is a later
deliverable, and this module says so on its README sheet rather than pretending
otherwise.

Arithmetic policy: none.  The exporter adds nothing, subtracts nothing and sums nothing;
the cumulative write-downs and the per-tranche lifetime totals it shows were summed in
``Decimal`` by ``crt.api``.  ``Decimal`` becomes ``float`` in exactly one place,
``_cell_value``, at the moment a value is written to a cell (openpyxl has no Decimal
cell type).  Every engine amount is cents with at most 11 integer digits, so the float
written is the nearest double to the exact cents and Excel displays it exactly with the
``#,##0.00`` format; percentages are 7-decimal fractions, likewise exactly displayed by
``0.00000%``.  Nothing is ever read back from the workbook into a calculation.

Determinism: ``wb.properties.created`` / ``modified`` are pinned to the run's manifest
timestamp and the zip container is rewritten with fixed entry timestamps, so the same
``RunResult`` always produces the same bytes, and two runs of the same scenario differ
only in the README timestamp cell.
"""

from __future__ import annotations

import io
import re
import zipfile
from collections.abc import Iterable, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.chart import AreaChart, BarChart, LineChart, Reference
from openpyxl.chart.axis import TextAxis
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from crt.api import RunResult, StructureRow
from crt.io.appendix_g import EXPECTED_A1_PORTION_TOTAL, EXPECTED_A1H_PORTION_TOTAL
from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER
from crt.presentation import STACK_ORDER_BOTTOM_UP, STACK_ORDER_TOP_DOWN, TRANCHE_COLOURS

# Sheet names, in workbook order.
SHEET_NAMES: tuple[str, ...] = (
    "README",
    "Inputs",
    "Structure",
    "Tranche principal",
    "Tranche write-downs",
    "Cumulative write-downs",
    "Notes",
    "Pool",
    "Summary",
    "Charts",
)
VALUES_ONLY_SENTENCE = (
    "All cells are engine values exported from crt.api; the live-formula workbook "
    "(BRIEF §9) is a later deliverable"
)

# Tranches bottom-up: first loss at the bottom of every stack, each Note directly under
# its H tranche, A-H on top (crt.presentation; shared with the GUI and the browser page).
BOTTOM_UP_ORDER: tuple[str, ...] = STACK_ORDER_BOTTOM_UP
# Roles per spec 02 section 1 (Table 3).
TRANCHE_ROLES: dict[str, str] = {
    "A-H": "retained senior",
    "A-1": "Note",
    "A-1H": "retained, pro rata with A-1",
    "M-1": "Note",
    "M-1H": "retained, pro rata with M-1",
    "M-2A": "Note",
    "M-2AH": "retained, pro rata with M-2A",
    "M-2B": "Note",
    "M-2BH": "retained, pro rata with M-2B",
    "B-1H": "retained",
    "B-2H": "retained",
    "B-3H": "retained first loss",
}
# One palette for every chart (crt.presentation.TRANCHE_COLOURS, re-exported): a Note's H
# tranche is a lighter tint of the Note's own hue.
INTEREST_COLOUR = "7F7F7F"
WRITE_DOWN_COLOUR = "C00000"
THRESHOLD_COLOUR = "C00000"
POOL_COLOUR = "1F3864"

MONEY_FORMAT = "#,##0.00"
PERCENT_FORMAT = "0.00000%"
DATE_FORMAT = "yyyy-mm-dd"
INTEGER_FORMAT = "0"
WAL_FORMAT = "0.0000"  # display; the stored WAL is unrounded (R6)
CHART_MONEY_AXIS_FORMAT = "#,##0"
CHART_PERCENT_AXIS_FORMAT = "0.00%"
CHART_DATE_AXIS_FORMAT = "yyyy-mm"

CHART_WIDTH_CM = 32  # int: openpyxl types ChartBase.width as int
CHART_HEIGHT_CM = 15.0
CHART_ROW_STEP = 32  # rows between chart anchors (15 cm at the default row height)
X_AXIS_LABEL_EVERY = 12  # one Payment Date label per year

# Fixed zip entry timestamp (DOS epoch) so the container bytes depend on content only.
_ZIP_ENTRY_DATETIME = (1980, 1, 1, 0, 0, 0)

_HEADER_FONT = Font(bold=True)
_HEADER_FILL = PatternFill("solid", fgColor="D9D9D9")
_HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=True)
_HEADER_BORDER = Border(bottom=Side(style="thin"))
_TITLE_FONT = Font(bold=True, size=13)


class StructureWorkbookError(ValueError):
    """The workbook could not be assembled from the run."""


# --------------------------------------------------------------------------------------
# Cell writing (the Decimal -> float boundary)
# --------------------------------------------------------------------------------------


def _cell_value(value: Any) -> Any:
    """The one Decimal -> float conversion of the exporter (see the module docstring)."""
    if isinstance(value, Decimal):
        return float(value)
    return value


def _header_row(ws: Worksheet, row: int, headers: Sequence[str], first_col: int = 1) -> None:
    for offset, header in enumerate(headers):
        cell = ws.cell(row=row, column=first_col + offset, value=header)
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        cell.alignment = _HEADER_ALIGNMENT
        cell.border = _HEADER_BORDER


def _write_rows(
    ws: Worksheet,
    first_row: int,
    rows: Iterable[Sequence[Any]],
    formats: Sequence[str | None],
    first_col: int = 1,
) -> int:
    """Write ``rows`` from ``first_row``; return the last row written."""
    row = first_row - 1
    for row_offset, values in enumerate(rows):
        row = first_row + row_offset
        if len(values) != len(formats):
            raise StructureWorkbookError(
                f"{ws.title}: row {row} has {len(values)} values for {len(formats)} columns"
            )
        for offset, (value, number_format) in enumerate(zip(values, formats, strict=True)):
            cell = ws.cell(row=row, column=first_col + offset, value=_cell_value(value))
            if number_format is not None:
                cell.number_format = number_format
    return row


def _set_widths(ws: Worksheet, widths: Sequence[float], first_col: int = 1) -> None:
    for offset, width in enumerate(widths):
        ws.column_dimensions[get_column_letter(first_col + offset)].width = width


def _table_sheet(
    ws: Worksheet,
    headers: Sequence[str],
    rows: Iterable[Sequence[Any]],
    formats: Sequence[str | None],
    widths: Sequence[float],
    *,
    freeze: str,
) -> int:
    """Header in row 1, data from row 2, frozen panes and widths; returns the last row."""
    _header_row(ws, 1, headers)
    last_row = _write_rows(ws, 2, rows, formats)
    _set_widths(ws, widths)
    ws.freeze_panes = freeze
    return last_row


# --------------------------------------------------------------------------------------
# Data sheets
# --------------------------------------------------------------------------------------


def _readme_sheet(ws: Worksheet, result: RunResult) -> None:
    manifest = result.manifest
    scenario = result.scenario
    ws["A1"] = "CRT Cashflow Engine — structure workbook (engine values)"
    ws["A1"].font = _TITLE_FONT
    facts: list[tuple[str, Any, str | None]] = [
        ("Deal", result.deal.name, None),
        ("Scenario", manifest.scenario_name, None),
        ("Scenario label", scenario.label(), None),
        ("Scenario source", manifest.scenario_source or "(built from values, no file)", None),
        ("Run id", manifest.run_id, None),
        ("Engine version", manifest.engine_version, None),
        ("Git commit", manifest.git_commit or "(not a git checkout)", None),
        ("Timestamp (UTC)", manifest.timestamp_utc, None),
        ("Decimal precision", manifest.decimal_precision, INTEGER_FORMAT),
        ("Conventions in force", ", ".join(manifest.conventions_in_force), None),
        (
            "Maturity Date",
            f"Payment Date {manifest.maturity_payment_date_number}: {manifest.maturity_reason}",
            None,
        ),
        ("Contents", VALUES_ONLY_SENTENCE, None),
    ]
    row = 3
    for label, value, number_format in facts:
        ws.cell(row=row, column=1, value=label).font = _HEADER_FONT
        cell = ws.cell(row=row, column=2, value=_cell_value(value))
        if number_format is not None:
            cell.number_format = number_format
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="Reference Tranche legend (top of the stack first)").font = (
        _TITLE_FONT
    )
    row += 1
    _header_row(
        ws, row, ("Tranche", "Role", "Initial Class Notional Amount", "% of pool", "Chart colour")
    )
    row += 1
    for tranche in STACK_ORDER_TOP_DOWN:
        summary = result.tranche_summary_for(tranche)
        values = (
            tranche,
            TRANCHE_ROLES[tranche],
            summary.initial_class_notional_amount,
            summary.initial_pct_of_pool,
            "",
        )
        _write_rows(ws, row, [values], (None, None, MONEY_FORMAT, PERCENT_FORMAT, None))
        ws.cell(row=row, column=5).fill = PatternFill("solid", fgColor=TRANCHE_COLOURS[tranche])
        row += 1
    row += 1
    ws.cell(row=row, column=1, value="Sheets").font = _TITLE_FONT
    descriptions = (
        ("Inputs", "scenario fields and the deal constants used, with register ids"),
        ("Structure", "one row per Payment Date; tranche balances after, bottom-up"),
        ("Tranche principal", "principal allocated per tranche per Payment Date (Steps 2-4 and the Maturity Date payment)"),
        ("Tranche write-downs", "Step 1 Tranche Write-down Amount allocated per tranche"),
        ("Cumulative write-downs", "running sum of the write-downs (summed in Decimal by crt.api)"),
        ("Notes", "the four Original Notes' cashflows side by side"),
        ("Pool", "pool totals per collection month"),
        ("Summary", "per-Note WAL / windows / totals and per-tranche totals"),
        ("Charts", "stacked tranche balances, write-downs, Note cashflows, pool UPB and Subordinate %"),
    )
    for name, text in descriptions:
        row += 1
        ws.cell(row=row, column=1, value=name).font = _HEADER_FONT
        ws.cell(row=row, column=2, value=text)
    _set_widths(ws, (28, 110, 30, 12, 12))


def _inputs_sheet(ws: Worksheet, result: RunResult) -> None:
    deal = result.deal
    scenario = result.scenario
    headers = ("Item", "Value", "Unit", "Register id", "Source")
    distressed = scenario.distressed_principal_balance_by_payment_date
    rows: list[tuple[Any, ...]] = [
        ("Scenario name", result.manifest.scenario_name, "", "", "run manifest"),
        ("CPR", scenario.cpr, "fraction (annual)", "T25", "scenario"),
        ("CER", scenario.cer, "fraction (annual)", "T26", "scenario"),
        ("RM", scenario.rm, "fraction (annual)", "T26", "scenario (v1: 0 only)"),
        ("SOFR Rate (flat)", scenario.sofr_rate, "fraction", "P12", "scenario"),
        ("Early redemption", scenario.early_redemption, "bool", "T18", "scenario"),
        ("Delinquency Test satisfied", scenario.delinquency_test_satisfied, "bool", "T10 / P73", "scenario"),
        (
            "Distressed Principal Balance vector",
            "not supplied" if distressed is None else f"{len(distressed)} Payment Dates",
            "",
            "",
            "scenario",
        ),
        ("Deal", deal.name, "", "", "deal terms (deal.name)"),
        ("Closing Date", deal.closing_date, "date", "P1", "deal terms"),
        ("Cut-off Date", deal.cut_off_date, "date", "P9", "deal terms"),
        ("Cut-off Date Balance", deal.cut_off_date_balance, "USD", "P10", "deal terms"),
        ("First Payment Date", deal.first_payment_date, "date", "P19 / P71", "deal terms"),
        ("Scheduled Maturity Payment Date #", deal.scheduled_maturity_payment_date_number, "Payment Date", "P8 / P21", "deal terms"),
        ("Earliest Early Redemption Payment Date #", deal.earliest_early_redemption_payment_date_number, "Payment Date", "P64", "deal terms"),
        ("Clean-up threshold", deal.clean_up_threshold, "fraction of Cut-off Date Balance", "P63", "deal terms"),
        ("Minimum Credit Enhancement threshold", deal.minimum_credit_enhancement_threshold, "fraction", "P15", "deal terms"),
        ("Class A-1 Cumulative Net Loss threshold", deal.class_a1_cumulative_net_loss_threshold, "fraction", "P16", "deal terms"),
        ("Delinquency Test factor", deal.delinquency_test_factor, "fraction", "P53", "deal terms"),
        ("Delinquency Test averaging window", deal.delinquency_test_averaging_payment_dates, "Payment Dates", "P54", "deal terms"),
        ("Supplemental Reduction threshold (ORTP)", deal.supplemental_reduction_threshold, "fraction", "P58", "deal terms"),
        ("Preliminary Principal Loss share of Credit Event Amount", deal.preliminary_principal_loss_share_of_credit_event_amount, "fraction", "P14", "deal terms"),
        ("Appendix G aggregate Class A-1 Reduction Amount, Payment Dates 1-12", deal.appendix_g_aggregate_payment_dates_1_to_12, "USD", "P60", "deal terms"),
        ("Appendix G aggregate Class A-1 Reduction Amount, Payment Dates 13-36", deal.appendix_g_aggregate_payment_dates_13_to_36, "USD", "P61", "deal terms"),
        ("Appendix G total, A-1 portion", EXPECTED_A1_PORTION_TOTAL, "USD", "T43", "crt.io.appendix_g"),
        ("Appendix G total, A-1H portion", EXPECTED_A1H_PORTION_TOTAL, "USD", "T44", "crt.io.appendix_g"),
    ]
    for index, threshold in enumerate(deal.cumulative_net_loss_test_schedule, start=1):
        rows.append(
            (f"Cumulative Net Loss Test threshold, band {index}", threshold, "fraction", "P52", "deal terms")
        )
    note_register = {"A-1": ("P3", "P36"), "M-1": ("P4", "P37"), "M-2A": ("P5", "P38"), "M-2B": ("P6", "P39")}
    for note in NOTE_CLASSES:
        terms = deal.notes[note]
        balance_id, margin_id = note_register[note]
        rows.append((f"{note} original Class Principal Balance", terms.original_class_principal_balance, "USD", balance_id, "deal terms"))
        rows.append((f"{note} margin over SOFR Rate", terms.margin, "fraction", margin_id, "deal terms"))
        rows.append((f"{note} Class Coupon minimum rate", terms.class_coupon_minimum_rate, "fraction", "P7", "deal terms"))
        rows.append((f"{note} Table 1 expected WAL", terms.expected_wal_years_table1, "years", "T39", "deal terms"))
        first, last = terms.expected_principal_window_table1
        rows.append((f"{note} Table 1 expected principal window", f"{first}-{last}", "Payment Dates", "T38", "deal terms"))
    tranche_register = {
        "A-H": "P24", "A-1": "P3", "A-1H": "P25", "M-1": "P4", "M-1H": "P26", "M-2A": "P5",
        "M-2AH": "P27", "M-2B": "P6", "M-2BH": "P28", "B-1H": "P29", "B-2H": "P30", "B-3H": "P31",
    }
    for tranche in TRANCHE_ORDER:
        rows.append(
            (f"{tranche} initial Class Notional Amount", deal.initial_class_notional_amounts[tranche], "USD", tranche_register[tranche], "deal terms")
        )
    _header_row(ws, 1, headers)
    for row_index, values in enumerate(rows, start=2):
        value = values[1]
        unit = values[2]
        if isinstance(value, Decimal):
            number_format = PERCENT_FORMAT if unit.startswith("fraction") else (
                WAL_FORMAT if unit == "years" else MONEY_FORMAT
            )
        elif isinstance(value, date):
            number_format = DATE_FORMAT
        elif isinstance(value, int) and not isinstance(value, bool):
            number_format = INTEGER_FORMAT
        else:
            number_format = None
        _write_rows(ws, row_index, [values], (None, number_format, None, None, None))
    _set_widths(ws, (62, 26, 30, 12, 24))
    ws.freeze_panes = "A2"


# Structure sheet columns: (header, attribute or None, number format).  Balances after
# are appended bottom-up.
_STRUCTURE_COLUMNS: tuple[tuple[str, str, str | None], ...] = (
    ("Payment Date #", "payment_date_number", INTEGER_FORMAT),
    ("Payment Date", "payment_date", DATE_FORMAT),
    ("Maturity Date?", "is_maturity_date", None),
    ("Maturity reason", "maturity_reason", None),
    ("Stated Principal", "stated_principal", MONEY_FORMAT),
    ("Credit Event Amount", "credit_event_amount", MONEY_FORMAT),
    ("Principal Loss Amount", "principal_loss_amount", MONEY_FORMAT),
    ("Principal Recovery Amount", "principal_recovery_amount", MONEY_FORMAT),
    ("Tranche Write-down Amount", "tranche_write_down", MONEY_FORMAT),
    ("Tranche Write-up Amount", "tranche_write_up", MONEY_FORMAT),
    ("Recovery Principal", "recovery_principal", MONEY_FORMAT),
    ("Senior %", "senior_pct", PERCENT_FORMAT),
    ("Subordinate %", "subordinate_pct", PERCENT_FORMAT),
    ("MCE threshold (P15)", "", PERCENT_FORMAT),
    ("Cumulative Net Loss %", "cumulative_net_loss_pct", PERCENT_FORMAT),
    ("CNL threshold (P52)", "cumulative_net_loss_threshold", PERCENT_FORMAT),
    ("MCE Test", "test_minimum_credit_enhancement", None),
    ("CNL Test", "test_cumulative_net_loss", None),
    ("Delinquency Test", "test_delinquency", None),
    ("Class A-1 CNL Test", "test_class_a1_cumulative_net_loss", None),
    ("Senior Reduction Amount", "senior_reduction", MONEY_FORMAT),
    ("Class A-1 Reduction Amount", "class_a1_reduction", MONEY_FORMAT),
    ("Subordinate Reduction Amount", "subordinate_reduction", MONEY_FORMAT),
    ("Class A-1 Additional Reduction Amount", "class_a1_additional_reduction", MONEY_FORMAT),
    ("Offered Reference Tranche %", "offered_reference_tranche_pct", PERCENT_FORMAT),
    ("Supplemental Reduction Amount", "supplemental_reduction", MONEY_FORMAT),
    ("Pool UPB end", "pool_upb_end", MONEY_FORMAT),
)
STRUCTURE_HEADERS: tuple[str, ...] = tuple(h for h, _, _ in _STRUCTURE_COLUMNS) + tuple(
    f"{t} after" for t in BOTTOM_UP_ORDER
)


def _structure_values(row: StructureRow, mce_threshold: Decimal) -> tuple[Any, ...]:
    values: list[Any] = []
    for header, attribute, _ in _STRUCTURE_COLUMNS:
        if header == "MCE threshold (P15)":
            values.append(mce_threshold)
        else:
            values.append(getattr(row, attribute))
    values.extend(row.balances_after[t] for t in BOTTOM_UP_ORDER)
    return tuple(values)


def _structure_sheet(ws: Worksheet, result: RunResult) -> int:
    threshold = result.deal.minimum_credit_enhancement_threshold  # P15
    formats = tuple(f for _, _, f in _STRUCTURE_COLUMNS) + (MONEY_FORMAT,) * len(BOTTOM_UP_ORDER)
    widths = (9, 12, 9, 34) + (18,) * (len(_STRUCTURE_COLUMNS) - 4) + (20,) * len(BOTTOM_UP_ORDER)
    return _table_sheet(
        ws,
        STRUCTURE_HEADERS,
        (_structure_values(row, threshold) for row in result.structure),
        formats,
        widths,
        freeze="C2",
    )


def _matrix_sheet(ws: Worksheet, result: RunResult, attribute: str) -> int:
    """Payment Date x 12 tranches (bottom-up) of one StructureRow dict attribute."""
    headers = ("Payment Date #", "Payment Date") + BOTTOM_UP_ORDER
    formats = (INTEGER_FORMAT, DATE_FORMAT) + (MONEY_FORMAT,) * len(BOTTOM_UP_ORDER)
    rows = (
        (row.payment_date_number, row.payment_date)
        + tuple(getattr(row, attribute)[t] for t in BOTTOM_UP_ORDER)
        for row in result.structure
    )
    return _table_sheet(ws, headers, rows, formats, (9, 12) + (18,) * len(BOTTOM_UP_ORDER), freeze="C2")


NOTE_BLOCK_HEADERS: tuple[str, ...] = (
    "Beginning balance",
    "Interest",
    "Principal",
    "Write-down",
    "Ending balance",
)
NOTE_BLOCK_WIDTH = len(NOTE_BLOCK_HEADERS)
NOTES_FIRST_DATA_ROW = 3


def _note_block_first_col(index: int) -> int:
    return 3 + index * NOTE_BLOCK_WIDTH


def _notes_sheet(ws: Worksheet, result: RunResult) -> int:
    by_key = {(r.note, r.payment_date_number): r for r in result.note_cashflows}
    _header_row(ws, 2, ("Payment Date #", "Payment Date"))
    for index, note in enumerate(NOTE_CLASSES):
        first_col = _note_block_first_col(index)
        ws.merge_cells(
            start_row=1, start_column=first_col, end_row=1, end_column=first_col + NOTE_BLOCK_WIDTH - 1
        )
        title = ws.cell(row=1, column=first_col, value=f"Class {note}")
        title.font = _HEADER_FONT
        title.alignment = _HEADER_ALIGNMENT
        _header_row(ws, 2, NOTE_BLOCK_HEADERS, first_col)
    last_row = NOTES_FIRST_DATA_ROW - 1
    for offset, structure_row in enumerate(result.structure):
        row = NOTES_FIRST_DATA_ROW + offset
        n = structure_row.payment_date_number
        _write_rows(ws, row, [(n, structure_row.payment_date)], (INTEGER_FORMAT, DATE_FORMAT))
        for index, note in enumerate(NOTE_CLASSES):
            cashflow = by_key[(note, n)]
            values = (
                cashflow.balance_before,
                cashflow.interest,
                cashflow.principal_paid,
                cashflow.write_down,
                cashflow.balance_after,
            )
            _write_rows(ws, row, [values], (MONEY_FORMAT,) * NOTE_BLOCK_WIDTH, _note_block_first_col(index))
        last_row = row
    _set_widths(ws, (9, 12) + (18,) * (NOTE_BLOCK_WIDTH * len(NOTE_CLASSES)))
    ws.freeze_panes = "C3"
    return last_row


def _pool_sheet(ws: Worksheet, result: RunResult) -> int:
    headers = (
        "Collection month",
        "Month end",
        "Feeds Payment Date #",
        "Balance begin",
        "Scheduled principal",
        "Prepayment",
        "Credit Event Amount",
        "Interest",
        "Balance end",
    )
    formats = (INTEGER_FORMAT, DATE_FORMAT, INTEGER_FORMAT) + (MONEY_FORMAT,) * 6
    rows = (
        (
            m.month,
            m.month_end,
            m.payment_date_number,
            m.balance_begin,
            m.scheduled_principal,
            m.prepayment,
            m.credit_event_amount,
            m.interest,
            m.balance_end,
        )
        for m in result.pool_months
    )
    return _table_sheet(ws, headers, rows, formats, (10, 12, 12) + (20,) * 6, freeze="D2")


def _summary_sheet(ws: Worksheet, result: RunResult) -> None:
    ws["A1"] = "Original Notes"
    ws["A1"].font = _TITLE_FONT
    note_headers = (
        "Note",
        "Original balance",
        "WAL (years, unrounded)",
        "First principal PD #",
        "First principal date",
        "Last principal PD #",
        "Last principal date",
        "Total principal",
        "Total interest",
        "Total write-downs",
        "Total write-ups",
        "Final balance",
    )
    note_formats = (
        None, MONEY_FORMAT, WAL_FORMAT, INTEGER_FORMAT, DATE_FORMAT, INTEGER_FORMAT, DATE_FORMAT,
        MONEY_FORMAT, MONEY_FORMAT, MONEY_FORMAT, MONEY_FORMAT, MONEY_FORMAT,
    )
    _header_row(ws, 2, note_headers)
    note_rows = (
        (
            s.note,
            s.original_balance,
            s.wal_years,
            s.first_principal_payment_date_number,
            s.first_principal_payment_date,
            s.last_principal_payment_date_number,
            s.last_principal_payment_date,
            s.total_principal,
            s.total_interest,
            s.total_write_downs,
            s.total_write_ups,
            s.final_balance,
        )
        for s in result.note_summaries
    )
    row = _write_rows(ws, 3, note_rows, note_formats) + 2

    ws.cell(row=row, column=1, value="Reference Tranches").font = _TITLE_FONT
    row += 1
    tranche_headers = (
        "Tranche",
        "Initial Class Notional Amount",
        "% of pool",
        "Total principal",
        "Total write-downs",
        "Total write-ups",
        "Total increases (A-H only)",
        "Final balance",
    )
    tranche_formats = (
        None, MONEY_FORMAT, PERCENT_FORMAT, MONEY_FORMAT, MONEY_FORMAT, MONEY_FORMAT, MONEY_FORMAT,
        MONEY_FORMAT,
    )
    _header_row(ws, row, tranche_headers)
    tranche_rows = (
        (
            s.tranche,
            s.initial_class_notional_amount,
            s.initial_pct_of_pool,
            s.total_principal,
            s.total_write_downs,
            s.total_write_ups,
            s.total_increases,
            s.final_balance,
        )
        for s in result.tranche_summaries
    )
    row = _write_rows(ws, row + 1, tranche_rows, tranche_formats) + 2

    ws.cell(row=row, column=1, value="Pool").font = _TITLE_FONT
    totals = result.pool_totals
    pool_rows: tuple[tuple[str, Any, str | None], ...] = (
        ("Cut-off Date Balance", totals.cut_off_date_balance, MONEY_FORMAT),
        ("First collection month", totals.first_month, INTEGER_FORMAT),
        ("Last collection month", totals.last_month, INTEGER_FORMAT),
        ("Last month end", totals.last_month_end, DATE_FORMAT),
        ("Total scheduled principal", totals.total_scheduled_principal, MONEY_FORMAT),
        ("Total prepayment", totals.total_prepayment, MONEY_FORMAT),
        ("Total Credit Event Amount", totals.total_credit_event_amount, MONEY_FORMAT),
        ("Total interest", totals.total_interest, MONEY_FORMAT),
        ("Ending balance", totals.ending_balance, MONEY_FORMAT),
        ("Maturity Payment Date #", totals.maturity_payment_date_number, INTEGER_FORMAT),
        ("Maturity Payment Date", totals.maturity_payment_date, DATE_FORMAT),
        ("Maturity reason", totals.maturity_reason, None),
    )
    for label, value, number_format in pool_rows:
        row += 1
        ws.cell(row=row, column=1, value=label).font = _HEADER_FONT
        _write_rows(ws, row, [(value,)], (number_format,), first_col=2)
    _set_widths(ws, (30, 24, 22, 18, 18, 18, 18, 20, 20, 20, 20, 20))


# --------------------------------------------------------------------------------------
# Charts
# --------------------------------------------------------------------------------------


def _style_chart(
    chart: AreaChart | BarChart | LineChart,
    *,
    title: str,
    x_title: str,
    y_title: str,
    y_format: str,
) -> None:
    chart.title = title
    chart.width = CHART_WIDTH_CM
    chart.height = CHART_HEIGHT_CM
    chart.x_axis.title = x_title
    chart.y_axis.title = y_title
    chart.y_axis.number_format = y_format
    chart.y_axis.majorGridlines = None
    # openpyxl leaves ``delete`` unset, which current Excel builds read as hidden axes.
    chart.x_axis.delete = False
    chart.y_axis.delete = False
    if isinstance(chart.x_axis, TextAxis):
        chart.x_axis.number_format = CHART_DATE_AXIS_FORMAT
        chart.x_axis.tickLblSkip = X_AXIS_LABEL_EVERY
        chart.x_axis.tickMarkSkip = X_AXIS_LABEL_EVERY
    if chart.legend is None:
        raise StructureWorkbookError(f"chart {title!r} has no legend to position")
    chart.legend.position = "r"


def _add_series(
    chart: AreaChart | BarChart | LineChart,
    ws: Worksheet,
    columns: Sequence[int],
    header_row: int,
    last_row: int,
) -> None:
    """One series per column, named from its header cell (columns need not be adjacent)."""
    for column in columns:
        chart.add_data(
            Reference(ws, min_col=column, min_row=header_row, max_row=last_row),
            titles_from_data=True,
        )


def _colour_fill(chart: AreaChart | BarChart, colours: Sequence[str]) -> None:
    for series, colour in zip(chart.series, colours, strict=True):
        series.graphicalProperties.solidFill = colour
        series.graphicalProperties.line.solidFill = colour


def _colour_lines(chart: LineChart, colours: Sequence[str], *, dashed: Sequence[bool]) -> None:
    for series, colour, dash in zip(chart.series, colours, dashed, strict=True):
        series.graphicalProperties.line.solidFill = colour
        series.graphicalProperties.line.width = 22000  # EMU (about 1.75 pt)
        if dash:
            series.graphicalProperties.line.dashStyle = "dash"
        series.marker.symbol = "none"
        series.smooth = False


def _categories(ws: Worksheet, column: int, first_row: int, last_row: int) -> Reference:
    return Reference(ws, min_col=column, min_row=first_row, max_row=last_row)


def _stacked_area(
    ws: Worksheet,
    *,
    tranches: Sequence[str],
    first_tranche_col: int,
    all_tranches: Sequence[str],
    header_row: int,
    last_row: int,
    title: str,
    y_title: str,
) -> AreaChart:
    """Stacked area of the ``tranches`` columns of a bottom-up matrix block, series
    added in the given order so the first tranche sits at the bottom of the stack."""
    chart = AreaChart()
    chart.grouping = "stacked"
    columns = [first_tranche_col + all_tranches.index(t) for t in tranches]
    _add_series(chart, ws, columns, header_row, last_row)
    chart.set_categories(_categories(ws, 2, header_row + 1, last_row))
    _colour_fill(chart, [TRANCHE_COLOURS[t] for t in tranches])
    _style_chart(chart, title=title, x_title="Payment Date", y_title=y_title, y_format=CHART_MONEY_AXIS_FORMAT)
    return chart


def _charts_sheet(
    ws: Worksheet,
    result: RunResult,
    *,
    structure: Worksheet,
    structure_last_row: int,
    principal: Worksheet,
    write_downs: Worksheet,
    cumulative: Worksheet,
    matrix_last_row: int,
    notes: Worksheet,
    notes_last_row: int,
) -> int:
    """Build every chart; return how many were placed."""
    label = result.manifest.scenario_name
    charts: list[AreaChart | BarChart | LineChart] = []
    balances_first_col = STRUCTURE_HEADERS.index(f"{BOTTOM_UP_ORDER[0]} after") + 1

    # (a) all twelve tranche balances, stacked bottom-up.
    charts.append(
        _stacked_area(
            structure,
            tranches=BOTTOM_UP_ORDER,
            first_tranche_col=balances_first_col,
            all_tranches=BOTTOM_UP_ORDER,
            header_row=1,
            last_row=structure_last_row,
            title=f"Reference Tranche stack after each Payment Date — {label}",
            y_title="Class Notional Amount (USD)",
        )
    )
    # (b) the same without A-H so the subordinate stack is legible.
    charts.append(
        _stacked_area(
            structure,
            tranches=tuple(t for t in BOTTOM_UP_ORDER if t != "A-H"),
            first_tranche_col=balances_first_col,
            all_tranches=BOTTOM_UP_ORDER,
            header_row=1,
            last_row=structure_last_row,
            title=f"Subordinate stack after each Payment Date, A-H excluded — {label}",
            y_title="Class Notional Amount (USD)",
        )
    )
    # (c) write-downs allocated per tranche per Payment Date, stacked columns.
    bar = BarChart()
    bar.type = "col"
    bar.grouping = "stacked"
    bar.overlap = 100
    bar.gapWidth = 30
    _add_series(bar, write_downs, [3 + i for i in range(len(BOTTOM_UP_ORDER))], 1, matrix_last_row)
    bar.set_categories(_categories(write_downs, 2, 2, matrix_last_row))
    _colour_fill(bar, [TRANCHE_COLOURS[t] for t in BOTTOM_UP_ORDER])
    _style_chart(
        bar,
        title=f"Tranche Write-down Amount allocated per Payment Date — {label}",
        x_title="Payment Date",
        y_title="Write-down (USD)",
        y_format=CHART_MONEY_AXIS_FORMAT,
    )
    charts.append(bar)
    # (d) cumulative write-downs per tranche, stacked area.
    charts.append(
        _stacked_area(
            cumulative,
            tranches=BOTTOM_UP_ORDER,
            first_tranche_col=3,
            all_tranches=BOTTOM_UP_ORDER,
            header_row=1,
            last_row=matrix_last_row,
            title=f"Cumulative write-downs per tranche — {label}",
            y_title="Cumulative write-down (USD)",
        )
    )
    # (e) one clustered column chart per Note: principal, interest, write-down.  One
    # chart per Note rather than the four Notes stacked because A-1/M-1 (275.9 MM) and
    # M-2A/M-2B (37.85 MM) differ by 7x and interest is an order of magnitude below
    # principal; a single stacked chart would hide M-2A/M-2B and the interest entirely.
    for index, note in enumerate(NOTE_CLASSES):
        first_col = _note_block_first_col(index)
        interest_col = first_col + NOTE_BLOCK_HEADERS.index("Interest")
        principal_col = first_col + NOTE_BLOCK_HEADERS.index("Principal")
        write_down_col = first_col + NOTE_BLOCK_HEADERS.index("Write-down")
        note_chart = BarChart()
        note_chart.type = "col"
        note_chart.grouping = "clustered"
        note_chart.gapWidth = 60
        _add_series(note_chart, notes, (principal_col, interest_col, write_down_col), 2, notes_last_row)
        note_chart.set_categories(_categories(notes, 2, NOTES_FIRST_DATA_ROW, notes_last_row))
        _colour_fill(note_chart, (TRANCHE_COLOURS[note], INTEREST_COLOUR, WRITE_DOWN_COLOUR))
        _style_chart(
            note_chart,
            title=f"Class {note}: principal, interest and write-down per Payment Date — {label}",
            x_title="Payment Date",
            y_title="USD",
            y_format=CHART_MONEY_AXIS_FORMAT,
        )
        charts.append(note_chart)
    # (f) pool UPB and Subordinate % against the MCE threshold.
    upb = LineChart()
    _add_series(upb, structure, (STRUCTURE_HEADERS.index("Pool UPB end") + 1,), 1, structure_last_row)
    upb.set_categories(_categories(structure, 2, 2, structure_last_row))
    _colour_lines(upb, (POOL_COLOUR,), dashed=(False,))
    _style_chart(
        upb,
        title=f"Pool UPB at the end of each Reporting Period — {label}",
        x_title="Payment Date",
        y_title="Pool UPB (USD)",
        y_format=CHART_MONEY_AXIS_FORMAT,
    )
    charts.append(upb)
    subordinate = LineChart()
    _add_series(
        subordinate,
        structure,
        (STRUCTURE_HEADERS.index("Subordinate %") + 1, STRUCTURE_HEADERS.index("MCE threshold (P15)") + 1),
        1,
        structure_last_row,
    )
    subordinate.set_categories(_categories(structure, 2, 2, structure_last_row))
    _colour_lines(subordinate, (TRANCHE_COLOURS["M-1"], THRESHOLD_COLOUR), dashed=(False, True))
    _style_chart(
        subordinate,
        title=f"Subordinate % against the Minimum Credit Enhancement threshold — {label}",
        x_title="Payment Date",
        y_title="Subordinate %",
        y_format=CHART_PERCENT_AXIS_FORMAT,
    )
    charts.append(subordinate)

    for index, chart in enumerate(charts):
        ws.add_chart(chart, f"A{1 + index * CHART_ROW_STEP}")
    ws["A1"] = f"Charts — {label} (engine values; see README)"
    return len(charts)


# --------------------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------------------


def build_structure_workbook(result: RunResult) -> Workbook:
    """The openpyxl ``Workbook`` for ``result`` (not yet serialised)."""
    if not result.structure:
        raise StructureWorkbookError("the run has no Payment Dates to export")
    wb = Workbook()
    sheets = {name: wb.create_sheet(name) for name in SHEET_NAMES}
    del wb["Sheet"]  # the default sheet openpyxl creates

    _readme_sheet(sheets["README"], result)
    _inputs_sheet(sheets["Inputs"], result)
    structure_last_row = _structure_sheet(sheets["Structure"], result)
    principal_last = _matrix_sheet(sheets["Tranche principal"], result, "principal_allocated")
    write_down_last = _matrix_sheet(sheets["Tranche write-downs"], result, "write_down_allocated")
    cumulative_last = _matrix_sheet(sheets["Cumulative write-downs"], result, "cumulative_write_down")
    if not principal_last == write_down_last == cumulative_last == structure_last_row:
        raise StructureWorkbookError("the matrix sheets and the Structure sheet disagree on row count")
    notes_last_row = _notes_sheet(sheets["Notes"], result)
    _pool_sheet(sheets["Pool"], result)
    _summary_sheet(sheets["Summary"], result)
    _charts_sheet(
        sheets["Charts"],
        result,
        structure=sheets["Structure"],
        structure_last_row=structure_last_row,
        principal=sheets["Tranche principal"],
        write_downs=sheets["Tranche write-downs"],
        cumulative=sheets["Cumulative write-downs"],
        matrix_last_row=structure_last_row,
        notes=sheets["Notes"],
        notes_last_row=notes_last_row,
    )

    stamp = datetime.strptime(result.manifest.timestamp_utc, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=UTC
    )
    wb.properties.creator = "crt.api"
    wb.properties.lastModifiedBy = "crt.api"
    wb.properties.created = stamp
    wb.properties.modified = stamp
    wb.properties.title = f"{result.deal.name} — {result.manifest.scenario_name}"
    wb.properties.description = f"run {result.manifest.run_id}; {VALUES_ONLY_SENTENCE}"
    return wb


def structure_workbook_bytes(result: RunResult) -> bytes:
    """Serialise the workbook with content-only zip bytes (fixed entry timestamps).

    openpyxl overwrites ``docProps/core.xml``'s ``dcterms:modified`` with the wall-clock
    time at save (``openpyxl.writer.excel.save_workbook``), so that one value is re-pinned
    to the run's manifest timestamp here; otherwise two saves a second apart differ.
    """
    raw = io.BytesIO()
    build_structure_workbook(result).save(raw)
    pinned_modified = (
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{result.manifest.timestamp_utc}'
        "</dcterms:modified>"
    )
    out = io.BytesIO()
    with (
        zipfile.ZipFile(raw) as source,
        zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as target,
    ):
        for info in source.infolist():
            payload = source.read(info.filename)
            if info.filename == "docProps/core.xml":
                payload = re.sub(
                    rb"<dcterms:modified[^>]*>[^<]*</dcterms:modified>",
                    pinned_modified.encode("utf-8"),
                    payload,
                    count=1,
                )
            entry = zipfile.ZipInfo(info.filename, date_time=_ZIP_ENTRY_DATETIME)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = info.external_attr
            target.writestr(entry, payload)
    return out.getvalue()


def export_structure_workbook(result: RunResult, path: Path) -> None:
    """Write the values workbook for ``result`` to ``path`` (parents created)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(structure_workbook_bytes(result))


def workbook_file_name(result: RunResult) -> str:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in result.manifest.scenario_name)
    return f"crt_structure_{safe}_{result.manifest.run_id}.xlsx"
