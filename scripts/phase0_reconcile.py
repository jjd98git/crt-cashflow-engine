"""Phase 0 reconciliation: loan-level file vs PPM Appendix A, and cross-month consistency.

Not engine code. Field positions are taken from the Freddie Mac CRT Reference Pool
Disclosure File Layouts v4.2 (data/raw/crt-reference-pool-disclosure-file-layouts-v4.2.txt).
PPM comparison values are typed here from Appendix A (PPM p220-221) and are labelled.
"""
from __future__ import annotations

from collections import Counter
from decimal import Decimal
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
JUL = RAW / "26DNA1_20260701_lld.txt"
AUG = RAW / "26DNA1_20260801_lld.txt"

# 1-based field positions per file layout v4.2
F_LOAN_ID = 3
F_STATE = 6
F_ZIP3 = 7
F_FIRST_PAY = 9
F_MATURITY = 10
F_ORIG_TERM = 11
F_ORIG_RATE = 12
F_ORIG_UPB = 13
F_UPB_ISSUANCE = 14
F_PURPOSE = 15
F_PROP_TYPE = 17
F_FICO = 23
F_LTV = 24
F_CLTV = 25
F_DTI = 26
F_LOAN_AGE = 34
F_RMLM = 35
F_DQ_STATUS = 37
F_CUR_UPB = 40
F_CUR_IB_UPB = 41
F_ZB_CODE = 43
F_MOD_FLAG = 46
F_PMT_DEFERRAL = 88
F_BUYDOWN = 90

# PPM Appendix A, "Selected Reference Obligation Data as of the Cut-off Date" (p220)
PPM = {
    "loan_count": 64434,
    "aggregate_original_upb": Decimal(23552092000),
    "cutoff_balance": Decimal("22781151551.84"),  # Glossary p194: "Cut-off Date Balance"
    "wa_rate_pct": Decimal("6.793"),
    "wa_orig_term": 360,
    "wa_rem_term": 349,
    "wa_loan_age": 10,
    "wa_ltv": 76,
    "wa_cltv": 76,
    "wa_dti": 38,
    "wa_fico": 759,
    "top_states": {"CA": "11.11", "FL": "9.41", "TX": "9.16", "NY": "5.98", "NJ": "3.69"},
    "max_zip3_pct": "1.66",
    "cash_out_pct": "10.90",  # p38
    "condo_pct": "8.62",  # p61
    "coop_pct": "0.35",
    "mh_pct": "0.55",
    "buydown_pct": "4.74",  # p62
}


def load(path: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with path.open(encoding="ascii") as fh:
        for line in fh:
            r = line.rstrip("\n").split("|")
            out[r[F_LOAN_ID - 1]] = r
    return out


def col(r: list[str], f: int) -> str:
    return r[f - 1]


def ym(s: str) -> int:
    return int(s[:4]) * 12 + int(s[4:6])


def wavg(rows: list[list[str]], f: int, skip: set[str] = frozenset()) -> Decimal:
    num = den = Decimal(0)
    for r in rows:
        v = col(r, f)
        if v == "" or v in skip:
            continue
        w = Decimal(col(r, F_UPB_ISSUANCE))
        num += Decimal(v) * w
        den += w
    return num / den


def share(rows: list[list[str]], f: int, values: set[str], total: Decimal) -> Decimal:
    return sum((Decimal(col(r, F_UPB_ISSUANCE)) for r in rows if col(r, f) in values), Decimal(0)) / total * 100


def main() -> None:
    jul, aug = load(JUL), load(AUG)
    rows = list(jul.values())
    total = sum(Decimal(col(r, F_UPB_ISSUANCE)) for r in rows)
    print("== Loan-level (2026-07 file, cut-off fields) vs PPM Appendix A")
    print(f"loan count           file={len(rows)}  ppm={PPM['loan_count']}")
    print(f"sum Original UPB     file={sum(Decimal(col(r, F_ORIG_UPB)) for r in rows)}  ppm={PPM['aggregate_original_upb']}")
    print(f"sum UPB at Issuance  file={total}  ppm={PPM['cutoff_balance']}  diff={total - PPM['cutoff_balance']}")
    print(f"WA orig rate         file={wavg(rows, F_ORIG_RATE):.4f}  ppm={PPM['wa_rate_pct']}")
    print(f"WA orig term         file={wavg(rows, F_ORIG_TERM):.1f}  ppm={PPM['wa_orig_term']}")
    rem = [(ym(col(r, F_MATURITY)) - ym('202512') + 1, Decimal(col(r, F_UPB_ISSUANCE))) for r in rows]
    print(f"WA rem term (mat-Dec25+1) file={sum(a * b for a, b in rem) / total:.1f}  ppm={PPM['wa_rem_term']}  (orig term - age: {wavg(rows, F_ORIG_TERM) - (sum((ym('202512') - ym(col(r, F_FIRST_PAY)) + 1) * Decimal(col(r, F_UPB_ISSUANCE)) for r in rows) / total):.1f})")
    age = [(ym('202512') - ym(col(r, F_FIRST_PAY)) + 1, Decimal(col(r, F_UPB_ISSUANCE))) for r in rows]
    print(f"WA loan age at cutoff file={sum(a * b for a, b in age) / total:.2f} range {min(a for a, _ in age)}-{max(a for a, _ in age)}  ppm={PPM['wa_loan_age']} (8-17)")
    print(f"WA LTV               file={wavg(rows, F_LTV):.2f}  ppm={PPM['wa_ltv']}")
    print(f"WA CLTV              file={wavg(rows, F_CLTV):.2f}  ppm={PPM['wa_cltv']}")
    print(f"WA DTI (non-999)     file={wavg(rows, F_DTI, {'999'}):.2f}  ppm={PPM['wa_dti']}")
    print(f"WA FICO (non-9999)   file={wavg(rows, F_FICO, {'9999'}):.1f}  ppm={PPM['wa_fico']}")
    st: Counter[str] = Counter()
    for r in rows:
        st[col(r, F_STATE)] += Decimal(col(r, F_UPB_ISSUANCE))
    print("top states           file=" + ", ".join(f"{k} {v / total * 100:.2f}" for k, v in st.most_common(5)) + f"  ppm={PPM['top_states']}")
    z: Counter[str] = Counter()
    for r in rows:
        z[col(r, F_ZIP3)] += Decimal(col(r, F_UPB_ISSUANCE))
    print(f"max zip3 conc        file={max(z.values()) / total * 100:.2f}  ppm={PPM['max_zip3_pct']}")
    print(f"cash-out (purpose C) file={share(rows, F_PURPOSE, {'C'}, total):.2f}  ppm={PPM['cash_out_pct']}")
    print(f"condo/coop/MH        file={share(rows, F_PROP_TYPE, {'CO'}, total):.2f}/{share(rows, F_PROP_TYPE, {'CP'}, total):.2f}/{share(rows, F_PROP_TYPE, {'MH'}, total):.2f}  ppm={PPM['condo_pct']}/{PPM['coop_pct']}/{PPM['mh_pct']}")
    print(f"buydown (90 in 1,2,3) file={share(rows, F_BUYDOWN, {'1', '2', '3'}, total):.2f}  ppm={PPM['buydown_pct']}")

    print("\n== Cross-month 2026-07 -> 2026-08")
    print(f"id sets identical: {set(jul) == set(aug)}")
    changed = Counter()
    for k in jul:
        for f in range(1, 94):
            if col(jul[k], f) != col(aug[k], f):
                changed[f] += 1
    print("fields that changed for >=1 loan (field: loans):", dict(sorted(changed.items())))
    cur_j = sum(Decimal(col(r, F_CUR_UPB)) for r in rows)
    cur_a = sum(Decimal(col(r, F_CUR_UPB)) for r in aug.values())
    print(f"sum Current Actual UPB  jul={cur_j}  aug={cur_a}  change={cur_a - cur_j}")
    to_zero = [k for k in jul if Decimal(col(jul[k], F_CUR_UPB)) > 0 and Decimal(col(aug[k], F_CUR_UPB)) == 0]
    print(f"loans to zero: {len(to_zero)}  jul balance {sum(Decimal(col(jul[k], F_CUR_UPB)) for k in to_zero)}  zb codes {Counter(col(aug[k], F_ZB_CODE) for k in to_zero)}")
    up = [k for k in jul if Decimal(col(aug[k], F_CUR_UPB)) > Decimal(col(jul[k], F_CUR_UPB))]
    explained = [k for k in up if col(aug[k], F_PMT_DEFERRAL) != "" or col(aug[k], F_MOD_FLAG) != ""]
    print(f"loans whose Current Actual UPB increased: {len(up)}; with deferral/mod flag: {len(explained)}; unexplained: {len(up) - len(explained)}")
    print("unexplained:", [(k, col(jul[k], F_CUR_UPB), col(aug[k], F_CUR_UPB)) for k in up if k not in explained])
    print(f"ZB code distribution jul={Counter(col(r, F_ZB_CODE) for r in rows if col(r, F_ZB_CODE))}  aug={Counter(col(r, F_ZB_CODE) for r in aug.values() if col(r, F_ZB_CODE))}")
    print(f"DQ status (live loans) aug={dict(sorted(Counter(col(r, F_DQ_STATUS) for r in aug.values() if Decimal(col(r, F_CUR_UPB)) > 0).items()))}")
    ib = [k for k in aug if col(aug[k], F_CUR_UPB) != col(aug[k], F_CUR_IB_UPB)]
    print(f"loans with Current Actual UPB != Interest Bearing UPB (aug): {len(ib)}; deferred total {sum(Decimal(col(aug[k], F_CUR_UPB)) - Decimal(col(aug[k], F_CUR_IB_UPB)) for k in ib)}")


if __name__ == "__main__":
    main()
