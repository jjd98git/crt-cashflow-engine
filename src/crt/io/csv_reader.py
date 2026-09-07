"""Strict CSV reading: exact header set, no coercion, every row a ``dict[str, str]``."""

from __future__ import annotations

import csv
from pathlib import Path


class CsvLayoutError(ValueError):
    """The CSV does not have the expected layout."""


def read_csv_rows(path: Path, *, expected_columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Read ``path`` and return its rows as string dicts.

    Raises ``CsvLayoutError`` if the header is not exactly ``expected_columns`` (order
    included) or if any row has a different number of fields.
    """
    if not path.is_file():
        raise CsvLayoutError(f"{path}: file not found")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            raise CsvLayoutError(f"{path}: empty file") from None
        if tuple(header) != expected_columns:
            raise CsvLayoutError(
                f"{path}: header {header!r} does not match expected {list(expected_columns)!r}"
            )
        rows: list[dict[str, str]] = []
        for line_number, values in enumerate(reader, start=2):
            if len(values) != len(expected_columns):
                raise CsvLayoutError(
                    f"{path} line {line_number}: {len(values)} fields, expected "
                    f"{len(expected_columns)}"
                )
            rows.append(dict(zip(expected_columns, values, strict=True)))
    return rows
