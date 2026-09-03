"""Phase 0 profiler for the Freddie Mac CRT loan-level disclosure files.

Not engine code. Reads the pipe-delimited, header-less monthly files positionally and
emits a per-column profile plus cross-month consistency checks. Column numbers are
1-based positions; NO names are assigned here (see open question Q1).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
FILES = {"2026-07": RAW / "26DNA1_20260701_lld.txt", "2026-08": RAW / "26DNA1_20260801_lld.txt"}
NCOL = 93
MAX_DISTINCT_LISTED = 12


def load(path: Path) -> list[list[str]]:
    rows = []
    with path.open("r", encoding="ascii", newline="") as fh:
        for i, line in enumerate(fh, 1):
            parts = line.rstrip("\n").split("|")
            if len(parts) != NCOL:
                raise ValueError(f"{path.name} line {i}: {len(parts)} fields, expected {NCOL}")
            rows.append(parts)
    return rows


def is_decimal(s: str) -> Decimal | None:
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def profile(rows: list[list[str]]) -> list[dict]:
    n = len(rows)
    out = []
    for c in range(NCOL):
        vals = [r[c] for r in rows]
        nonempty = [v for v in vals if v != ""]
        cnt = Counter(nonempty)
        numeric = True
        dsum = Decimal(0)
        dmin = dmax = None
        has_dot = False
        for v in cnt:  # iterate distinct values only
            d = is_decimal(v)
            if d is None:
                numeric = False
                break
        if numeric and nonempty:
            for v, k in cnt.items():
                d = Decimal(v)
                if "." in v:
                    has_dot = True
                dsum += d * k
                dmin = d if dmin is None or d < dmin else dmin
                dmax = d if dmax is None or d > dmax else dmax
        rec = {
            "col": c + 1,
            "fill": len(nonempty),
            "fill_pct": round(100 * len(nonempty) / n, 2),
            "distinct": len(cnt),
            "maxlen": max((len(v) for v in nonempty), default=0),
            "numeric": bool(numeric and nonempty),
            "has_decimal_point": has_dot,
            "min": str(dmin) if dmin is not None else None,
            "max": str(dmax) if dmax is not None else None,
            "sum": str(dsum) if numeric and nonempty and has_dot else None,
            "top": cnt.most_common(MAX_DISTINCT_LISTED),
        }
        out.append(rec)
    return out


def cross_month(a: list[list[str]], b: list[list[str]]) -> dict:
    ia = {r[2]: r for r in a}
    ib = {r[2]: r for r in b}
    res: dict = {"ids_only_in_jul": len(set(ia) - set(ib)), "ids_only_in_aug": len(set(ib) - set(ia)),
                 "common": len(set(ia) & set(ib))}
    # Static columns: identical value for every loan across months
    static = []
    for c in range(NCOL):
        if all(ia[k][c] == ib[k][c] for k in ia if k in ib):
            static.append(c + 1)
    res["static_columns"] = static
    # Columns that changed by exactly +1 / -1 for every live loan (age / remaining term)
    plus1, minus1 = [], []
    for c in range(NCOL):
        try:
            diffs = {int(ib[k][c]) - int(ia[k][c]) for k in ia if k in ib and ia[k][c] != "" and ib[k][c] != ""}
        except ValueError:
            continue
        if diffs == {1}:
            plus1.append(c + 1)
        if diffs == {-1}:
            minus1.append(c + 1)
    res["always_plus_one"] = plus1
    res["always_minus_one"] = minus1
    # Balance movement on col 40 (inferred current UPB)
    inc = dec = same = 0
    to_zero = 0
    to_zero_bal = Decimal(0)
    for k in ia:
        x, y = Decimal(ia[k][39]), Decimal(ib[k][39])
        if y > x:
            inc += 1
        elif y < x:
            dec += 1
        else:
            same += 1
        if x > 0 and y == 0:
            to_zero += 1
            to_zero_bal += x
    res["col40_increase"] = inc
    res["col40_decrease"] = dec
    res["col40_same"] = same
    res["col40_to_zero_loans"] = to_zero
    res["col40_to_zero_jul_balance"] = str(to_zero_bal)
    return res


def main() -> None:
    data = {k: load(p) for k, p in FILES.items()}
    report = {k: profile(v) for k, v in data.items()}
    report["cross_month"] = cross_month(data["2026-07"], data["2026-08"])
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("profile.json")
    out.write_text(json.dumps(report, indent=1))
    # Compact console view
    for k in FILES:
        print(f"\n=== {k}  rows={len(data[k])}")
        print("col fill%  distinct maxlen num  min .. max  | sum | top")
        for r in report[k]:
            top = ", ".join(f"{v!r}:{n}" for v, n in r["top"][:5])
            print(f"{r['col']:>3} {r['fill_pct']:>6} {r['distinct']:>8} {r['maxlen']:>3} "
                  f"{'Y' if r['numeric'] else '-'}  {r['min']}..{r['max']} | {r['sum']} | {top}")
    print("\n=== cross-month")
    print(json.dumps(report["cross_month"], indent=1))


if __name__ == "__main__":
    main()
