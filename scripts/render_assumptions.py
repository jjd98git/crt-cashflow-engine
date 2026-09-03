"""Render docs/assumptions.md from docs/assumptions.csv.

Not engine code. Everything ASSUMED or not yet confirmed by Trey is listed first.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "assumptions.csv"
DST = ROOT / "docs" / "assumptions.md"

GROUPS = {
    "C": "Modeling conventions (brief section 6)",
    "P": "PPM-sourced deal terms and structuring assumptions",
    "T": "PPM tables and Table 1 values",
    "D": "Dataset facts",
    "U": "Decisions by Trey",
}


def esc(s: str) -> str:
    return s.replace("|", r"\|").replace("\n", " ")


def row_line(r: dict[str, str]) -> str:
    return (
        f"| {esc(r['id'])} | {esc(r['item'])} | {esc(r['value'])} | {esc(r['unit'])} | "
        f"{esc(r['source_type'])} | {esc(r['source_ref'])} | {esc(r['confidence'])} | "
        f"{esc(r['used_in'])} | {esc(r['confirmed_by_user'])} | {esc(r['notes'])} |"
    )


HEADER = (
    "| id | item | value | unit | source | source_ref | confidence | used_in | confirmed | notes |\n"
    "|---|---|---|---|---|---|---|---|---|---|"
)


def main() -> None:
    rows = list(csv.DictReader(SRC.open(newline="", encoding="utf-8")))
    open_rows = [r for r in rows if r["source_type"] == "ASSUMED" or r["confirmed_by_user"] != "Y"]
    intro = (
        f"Generated from `docs/assumptions.csv` ({len(rows)} rows). Do not edit; edit the CSV "
        "and re-run `scripts/render_assumptions.py`."
    )
    out = ["# Assumptions register (rendered)", "", intro, "",
           "## >>> UNCONFIRMED OR ASSUMED — Trey has not signed these off <<<", "",
           f"{len(open_rows)} of {len(rows)} rows.", "", HEADER]
    out += [row_line(r) for r in open_rows]
    by = defaultdict(list)
    for r in rows:
        by[r["id"][0]].append(r)
    for key, title in GROUPS.items():
        if key not in by:
            continue
        out += ["", f"## {title}", "", HEADER]
        out += [row_line(r) for r in by[key]]
    DST.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {DST} ({len(rows)} rows, {len(open_rows)} unconfirmed)")


if __name__ == "__main__":
    main()
