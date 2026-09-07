"""Tie-out target tables transcribed from the PPM (``data/ppm_tables/README.md``).

Every printed value is kept as the transcribed string *and* parsed to ``Decimal`` so that
the report can print the PPM number verbatim and the comparison can use exact arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from crt.io.csv_reader import read_csv_rows
from crt.money import parse_percent

WAL_TABLE_COLUMNS: tuple[str, ...] = (
    "table_name",
    "page",
    "class_group_as_printed",
    "class",
    "class_footnote",
    "basis",
    "early_redemption",
    "cpr_pct",
    "cer_pct",
    "rm_pct",
    "wal_years",
)
DECLINING_BALANCES_COLUMNS: tuple[str, ...] = (
    "table_name",
    "page",
    "class_group_as_printed",
    "class",
    "class_footnote",
    "cpr_pct",
    "date_or_month",
    "pct_of_original_balance",
    "wal_years",
)
CREDIT_EVENT_SENSITIVITY_COLUMNS: tuple[str, ...] = (
    "table_name",
    "page",
    "table_title",
    "basis",
    "early_redemption",
    "cpr_pct",
    "cer_pct",
    "cumulative_credit_event_amount_pct_of_cutoff_balance",
)
TABLE1_COLUMNS: tuple[str, ...] = (
    "note_type",
    "class",
    "class_footnote",
    "original_class_principal_balance",
    "balance_footnote",
    "initial_class_coupon",
    "coupon_footnote",
    "class_coupon_formula",
    "class_coupon_minimum_rate",
    "cusip_number",
    "scheduled_maturity_date",
    "expected_ratings_sp_morningstar_dbrs",
    "expected_wal_years",
    "expected_principal_window_months",
    "expected_initial_credit_enhancement",
)

EXPECTED_WAL_ROWS = 3168  # README: 3,168 cells
EXPECTED_DECLINING_BALANCES_ROWS = 3168  # README
EXPECTED_CREDIT_EVENT_SENSITIVITY_ROWS = 96  # README: 8 CER x 6 CPR x 2 bases
EXPECTED_TABLE1_ROWS = 27  # README

BASIS_TO_SCHEDULED_MATURITY = "To Scheduled Maturity Date"
BASIS_TO_EARLY_REDEMPTION = "To Early Redemption Date"
DECLINING_BALANCES_WAL_ROW_SCHEDULED = "Weighted Average Life (years) to Scheduled Maturity Date"
DECLINING_BALANCES_WAL_ROW_EARLY = "Weighted Average Life (years) to Early Redemption Date**"


class PpmTableError(ValueError):
    """A PPM table transcription failed validation."""


@dataclass(frozen=True)
class WalCell:
    note_class: str
    early_redemption: bool
    cpr_pct: Decimal
    cer_pct: Decimal
    rm_pct: Decimal
    printed: str
    wal_years: Decimal


@dataclass(frozen=True)
class DecliningBalanceCell:
    note_class: str
    cpr_pct: Decimal
    row_label: str
    printed: str
    pct_of_original_balance: Decimal


@dataclass(frozen=True)
class DecliningBalanceWalRow:
    note_class: str
    cpr_pct: Decimal
    early_redemption: bool
    printed: str
    wal_years: Decimal


@dataclass(frozen=True)
class CreditEventSensitivityCell:
    early_redemption: bool
    cpr_pct: Decimal
    cer_pct: Decimal
    printed: str
    cumulative_credit_event_pct: Decimal


@dataclass(frozen=True)
class Table1Row:
    note_class: str
    expected_wal_years: Decimal
    expected_principal_window: tuple[int, int]


def _early_redemption_flag(basis: str, flag: str, *, record: str) -> bool:
    if basis == BASIS_TO_SCHEDULED_MATURITY and flag == "no":
        return False
    if basis == BASIS_TO_EARLY_REDEMPTION and flag == "yes":
        return True
    raise PpmTableError(f"{record}: basis {basis!r} / early_redemption {flag!r} inconsistent")


def load_wal_table(path: Path, *, note_classes: tuple[str, ...]) -> tuple[WalCell, ...]:
    """WAL cells for the given classes (RM = 0 rows are selected by the caller)."""
    rows = read_csv_rows(path, expected_columns=WAL_TABLE_COLUMNS)
    if len(rows) != EXPECTED_WAL_ROWS:
        raise PpmTableError(f"{path}: {len(rows)} rows, expected {EXPECTED_WAL_ROWS}")
    cells: list[WalCell] = []
    for index, row in enumerate(rows, start=2):
        record = f"{path.name} line {index}"
        if row["class"] not in note_classes:
            continue
        cells.append(
            WalCell(
                note_class=row["class"],
                early_redemption=_early_redemption_flag(
                    row["basis"].strip(), row["early_redemption"].strip(), record=record
                ),
                cpr_pct=parse_percent(row["cpr_pct"], field="cpr_pct", record=record),
                cer_pct=parse_percent(row["cer_pct"], field="cer_pct", record=record),
                rm_pct=parse_percent(row["rm_pct"], field="rm_pct", record=record),
                printed=row["wal_years"].strip(),
                wal_years=parse_percent(row["wal_years"], field="wal_years", record=record),
            )
        )
    return tuple(cells)


def load_declining_balances(
    path: Path, *, note_classes: tuple[str, ...]
) -> tuple[tuple[DecliningBalanceCell, ...], tuple[DecliningBalanceWalRow, ...]]:
    """Balance rows and the two WAL rows per CPR for the given classes."""
    rows = read_csv_rows(path, expected_columns=DECLINING_BALANCES_COLUMNS)
    if len(rows) != EXPECTED_DECLINING_BALANCES_ROWS:
        raise PpmTableError(
            f"{path}: {len(rows)} rows, expected {EXPECTED_DECLINING_BALANCES_ROWS}"
        )
    balances: list[DecliningBalanceCell] = []
    wal_rows: list[DecliningBalanceWalRow] = []
    for index, row in enumerate(rows, start=2):
        record = f"{path.name} line {index}"
        if row["class"] not in note_classes:
            continue
        cpr = parse_percent(row["cpr_pct"], field="cpr_pct", record=record)
        label = row["date_or_month"].strip()
        if label in (DECLINING_BALANCES_WAL_ROW_SCHEDULED, DECLINING_BALANCES_WAL_ROW_EARLY):
            if row["pct_of_original_balance"].strip():
                raise PpmTableError(f"{record}: WAL row carries a balance percentage")
            wal_rows.append(
                DecliningBalanceWalRow(
                    note_class=row["class"],
                    cpr_pct=cpr,
                    early_redemption=(label == DECLINING_BALANCES_WAL_ROW_EARLY),
                    printed=row["wal_years"].strip(),
                    wal_years=parse_percent(row["wal_years"], field="wal_years", record=record),
                )
            )
            continue
        if row["wal_years"].strip():
            raise PpmTableError(f"{record}: balance row carries a WAL")
        balances.append(
            DecliningBalanceCell(
                note_class=row["class"],
                cpr_pct=cpr,
                row_label=label,
                printed=row["pct_of_original_balance"].strip(),
                pct_of_original_balance=parse_percent(
                    row["pct_of_original_balance"],
                    field="pct_of_original_balance",
                    record=record,
                ),
            )
        )
    return tuple(balances), tuple(wal_rows)


def load_credit_event_sensitivity(path: Path) -> tuple[CreditEventSensitivityCell, ...]:
    rows = read_csv_rows(path, expected_columns=CREDIT_EVENT_SENSITIVITY_COLUMNS)
    if len(rows) != EXPECTED_CREDIT_EVENT_SENSITIVITY_ROWS:
        raise PpmTableError(
            f"{path}: {len(rows)} rows, expected {EXPECTED_CREDIT_EVENT_SENSITIVITY_ROWS}"
        )
    cells: list[CreditEventSensitivityCell] = []
    for index, row in enumerate(rows, start=2):
        record = f"{path.name} line {index}"
        basis = row["basis"].strip()
        # This table prints the basis in lower case ("to Scheduled Maturity Date").
        normalised = basis[:1].upper() + basis[1:]
        cells.append(
            CreditEventSensitivityCell(
                early_redemption=_early_redemption_flag(
                    normalised, row["early_redemption"].strip(), record=record
                ),
                cpr_pct=parse_percent(row["cpr_pct"], field="cpr_pct", record=record),
                cer_pct=parse_percent(row["cer_pct"], field="cer_pct", record=record),
                printed=row["cumulative_credit_event_amount_pct_of_cutoff_balance"].strip(),
                cumulative_credit_event_pct=parse_percent(
                    row["cumulative_credit_event_amount_pct_of_cutoff_balance"],
                    field="cumulative_credit_event_amount_pct_of_cutoff_balance",
                    record=record,
                ),
            )
        )
    return tuple(cells)


def load_table1(path: Path, *, note_classes: tuple[str, ...]) -> dict[str, Table1Row]:
    rows = read_csv_rows(path, expected_columns=TABLE1_COLUMNS)
    if len(rows) != EXPECTED_TABLE1_ROWS:
        raise PpmTableError(f"{path}: {len(rows)} rows, expected {EXPECTED_TABLE1_ROWS}")
    result: dict[str, Table1Row] = {}
    for index, row in enumerate(rows, start=2):
        record = f"{path.name} line {index}"
        if row["class"] not in note_classes:
            continue
        window_text = row["expected_principal_window_months"].strip()
        first_text, sep, last_text = window_text.partition("-")
        if not sep or not first_text.isdigit() or not last_text.isdigit():
            raise PpmTableError(f"{record}: window {window_text!r} is not 'first-last'")
        result[row["class"]] = Table1Row(
            note_class=row["class"],
            expected_wal_years=parse_percent(
                row["expected_wal_years"], field="expected_wal_years", record=record
            ),
            expected_principal_window=(int(first_text), int(last_text)),
        )
    missing = [note for note in note_classes if note not in result]
    if missing:
        raise PpmTableError(f"{path}: Table 1 rows missing for {missing}")
    return result
