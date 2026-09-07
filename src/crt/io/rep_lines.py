"""Appendix C representative lines (spec ``01-pool.md`` section 1; register T4, U1)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from crt.io.csv_reader import read_csv_rows
from crt.money import ZERO, parse_int, parse_money, parse_percent, percent_to_fraction

REP_LINE_COLUMNS: tuple[str, ...] = (
    "group",
    "original_balance",
    "outstanding_principal_balance",
    "remaining_term_months",
    "original_term_months",
    "interest_rate_pct",
)

EXPECTED_REP_LINE_COUNT = 31  # T4: Appendix C has 31 assumed loan groups
# D3: aggregate original balance of the reference pool, 23,552,092,000.00.
EXPECTED_ORIGINAL_BALANCE_TOTAL = Decimal("23552092000.00")
# Spec 01 section 1: every remaining term must reach past Payment Date 240 (month 241).
MINIMUM_REMAINING_TERM_MONTHS = 242


class RepLineError(ValueError):
    """Appendix C failed validation."""


@dataclass(frozen=True)
class RepLine:
    """One row of Appendix C.  ``interest_rate`` is the per-annum rate as a fraction."""

    group: int
    original_balance: Decimal
    outstanding_principal_balance: Decimal
    remaining_term_months: int
    original_term_months: int
    interest_rate: Decimal


def load_rep_lines(path: Path, *, cut_off_date_balance: Decimal) -> tuple[RepLine, ...]:
    """Load and validate Appendix C.  ``cut_off_date_balance`` is P10 from the deal terms."""
    rows = read_csv_rows(path, expected_columns=REP_LINE_COLUMNS)
    if len(rows) != EXPECTED_REP_LINE_COUNT:  # T4
        raise RepLineError(f"{path}: {len(rows)} rows, expected {EXPECTED_REP_LINE_COUNT}")

    rep_lines: list[RepLine] = []
    for index, row in enumerate(rows, start=1):
        record = f"appendix C row {index}"
        group = parse_int(row["group"], field="group", record=record)
        if group != index:
            raise RepLineError(f"{record}: group {group} is out of sequence")
        rate_pct = parse_percent(row["interest_rate_pct"], field="interest_rate_pct", record=record)
        rep_line = RepLine(
            group=group,
            original_balance=parse_money(
                row["original_balance"], field="original_balance", record=record
            ),
            outstanding_principal_balance=parse_money(
                row["outstanding_principal_balance"],
                field="outstanding_principal_balance",
                record=record,
            ),
            remaining_term_months=parse_int(
                row["remaining_term_months"], field="remaining_term_months", record=record
            ),
            original_term_months=parse_int(
                row["original_term_months"], field="original_term_months", record=record
            ),
            interest_rate=percent_to_fraction(rate_pct),
        )
        if rep_line.interest_rate <= ZERO:
            raise RepLineError(f"{record}: interest rate {rate_pct}% is not strictly positive")
        if rep_line.outstanding_principal_balance <= ZERO:
            raise RepLineError(f"{record}: outstanding balance is not strictly positive")
        if rep_line.remaining_term_months < MINIMUM_REMAINING_TERM_MONTHS:
            raise RepLineError(
                f"{record}: remaining term {rep_line.remaining_term_months} < "
                f"{MINIMUM_REMAINING_TERM_MONTHS}"
            )
        if rep_line.original_term_months < rep_line.remaining_term_months:
            raise RepLineError(f"{record}: original term shorter than remaining term")
        rep_lines.append(rep_line)

    outstanding_total = sum((line.outstanding_principal_balance for line in rep_lines), ZERO)
    if outstanding_total != cut_off_date_balance:  # P10
        raise RepLineError(
            f"{path}: sum of outstanding_principal_balance {outstanding_total} != Cut-off Date "
            f"Balance {cut_off_date_balance}"
        )
    original_total = sum((line.original_balance for line in rep_lines), ZERO)
    if original_total != EXPECTED_ORIGINAL_BALANCE_TOTAL:  # D3
        raise RepLineError(
            f"{path}: sum of original_balance {original_total} != "
            f"{EXPECTED_ORIGINAL_BALANCE_TOTAL}"
        )
    return tuple(rep_lines)
