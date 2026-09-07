"""Read the summary (section 1) of ``docs/validation/tieout.md`` for the sidebar.

The report is written by ``crt.tieout.report``; this module only parses its section 1
table back into rows.  A missing or unparseable report yields ``None`` -- the GUI then says
so instead of inventing a status."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

TIEOUT_REPORT_PATH = Path("docs/validation/tieout.md")
_TITLE = re.compile(r"^# Tie-out — .* — (?P<timestamp>\S+)\s*$")
_SECTION_1 = "## 1. Summary"
_NEXT_SECTION = re.compile(r"^## \d")
_OVERALL = re.compile(r"^Overall:\s*(?P<status>[A-Za-z]+)\.?\s*$")


@dataclass(frozen=True)
class TieoutFamilyRow:
    family: str
    cells: str
    passed: str
    failed: str
    worst_abs_diff: str
    tolerance: str
    status: str


@dataclass(frozen=True)
class TieoutStatus:
    timestamp_utc: str | None
    rows: tuple[TieoutFamilyRow, ...]
    overall: str | None
    secondary_check: str | None


def _split_table_row(line: str) -> list[str]:
    inner = line.strip().strip("|")
    # Cells may contain escaped pipes ("\|diff\|"); split on unescaped pipes only.
    cells = re.split(r"(?<!\\)\|", inner)
    return [cell.replace("\\|", "|").strip() for cell in cells]


def parse_tieout_status(report_text: str) -> TieoutStatus | None:
    lines = report_text.splitlines()
    if not lines:
        return None
    title = _TITLE.match(lines[0])
    timestamp = title.group("timestamp") if title else None
    try:
        start = lines.index(_SECTION_1)
    except ValueError:
        return None
    rows: list[TieoutFamilyRow] = []
    overall: str | None = None
    secondary: str | None = None
    for line in lines[start + 1 :]:
        if _NEXT_SECTION.match(line):
            break
        if line.startswith("|"):
            cells = _split_table_row(line)
            if len(cells) != 7 or cells[0] == "family" or set(cells[0]) <= {"-"}:
                continue
            rows.append(TieoutFamilyRow(*cells))
            continue
        match = _OVERALL.match(line)
        if match:
            overall = match.group("status")
        elif line.startswith("Secondary window-band check"):
            secondary = line.strip()
    if not rows:
        return None
    return TieoutStatus(
        timestamp_utc=timestamp, rows=tuple(rows), overall=overall, secondary_check=secondary
    )


def load_tieout_status(project_root: Path) -> TieoutStatus | None:
    path = project_root / TIEOUT_REPORT_PATH
    if not path.is_file():
        return None
    return parse_tieout_status(path.read_text(encoding="utf-8"))
