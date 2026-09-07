"""Appendix G: Class A-1 Reduction Amount schedule (register T41, T42, T43, T44, A6)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from crt.io.csv_reader import read_csv_rows
from crt.money import ZERO, parse_int, parse_money

APPENDIX_G_COLUMNS: tuple[str, ...] = (
    "payment_period",
    "class_a1_reference_tranche_portion_usd",
    "class_a1_reference_tranche_portion_pct",
    "class_a1h_reference_tranche_portion_usd",
    "class_a1h_reference_tranche_portion_pct",
    "aggregate_class_a1_reduction_amount_usd_computed",
)

# T41 / P62: limb (A) of the Class A-1 Reduction Amount runs "up to and including the
# thirty-sixth (36th) Payment Date"; limb (B) applies thereafter.
CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE = 36
EXPECTED_A1_PORTION_TOTAL = Decimal("223479000.00")  # T43
EXPECTED_A1H_PORTION_TOTAL = Decimal("11793342.48")  # T44


class AppendixGError(ValueError):
    """Appendix G failed validation."""


@dataclass(frozen=True)
class AppendixGRow:
    payment_period: int
    class_a1_portion: Decimal
    class_a1h_portion: Decimal
    aggregate: Decimal


@dataclass(frozen=True)
class AppendixG:
    rows: tuple[AppendixGRow, ...]

    def aggregate_for_payment_date(self, payment_date_number: int) -> Decimal:
        """The aggregate (A-1 + A-1H) Class A-1 Reduction Amount for Payment Date ``n``
        (limb (A), reading A6).  Raises outside Payment Dates 1..36."""
        if not 1 <= payment_date_number <= CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE:
            raise AppendixGError(
                f"Appendix G has no amount for Payment Date {payment_date_number}"
            )
        row = self.rows[payment_date_number - 1]
        if row.payment_period != payment_date_number:
            raise AppendixGError("Appendix G rows are not indexed 1..36")
        return row.aggregate


def load_appendix_g(path: Path) -> AppendixG:
    rows = read_csv_rows(path, expected_columns=APPENDIX_G_COLUMNS)
    if len(rows) != CLASS_A1_SCHEDULE_LAST_PAYMENT_DATE:  # T42: 36 Payment Periods
        raise AppendixGError(f"{path}: {len(rows)} rows, expected 36")
    parsed: list[AppendixGRow] = []
    for index, row in enumerate(rows, start=1):
        record = f"appendix G row {index}"
        period = parse_int(row["payment_period"], field="payment_period", record=record)
        if period != index:
            raise AppendixGError(f"{record}: payment_period {period} out of sequence")
        a1 = parse_money(
            row["class_a1_reference_tranche_portion_usd"],
            field="class_a1_reference_tranche_portion_usd",
            record=record,
        )
        a1h = parse_money(
            row["class_a1h_reference_tranche_portion_usd"],
            field="class_a1h_reference_tranche_portion_usd",
            record=record,
        )
        aggregate = parse_money(
            row["aggregate_class_a1_reduction_amount_usd_computed"],
            field="aggregate_class_a1_reduction_amount_usd_computed",
            record=record,
        )
        if aggregate != a1 + a1h:
            raise AppendixGError(f"{record}: aggregate {aggregate} != {a1} + {a1h}")
        parsed.append(
            AppendixGRow(
                payment_period=period,
                class_a1_portion=a1,
                class_a1h_portion=a1h,
                aggregate=aggregate,
            )
        )
    a1_total = sum((row.class_a1_portion for row in parsed), ZERO)
    if a1_total != EXPECTED_A1_PORTION_TOTAL:  # T43
        raise AppendixGError(
            f"{path}: A-1 portion total {a1_total} != {EXPECTED_A1_PORTION_TOTAL}"
        )
    a1h_total = sum((row.class_a1h_portion for row in parsed), ZERO)
    if a1h_total != EXPECTED_A1H_PORTION_TOTAL:  # T44
        raise AppendixGError(
            f"{path}: A-1H portion total {a1h_total} != {EXPECTED_A1H_PORTION_TOTAL}"
        )
    return AppendixG(rows=tuple(parsed))
