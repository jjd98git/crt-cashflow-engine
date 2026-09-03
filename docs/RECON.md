# Pre-Phase-0 reconnaissance notes

**Status: UNVERIFIED. This is not the Phase 0 deliverable.**

These observations were produced during environment setup by profiling the files
positionally, without the Freddie Mac file layout document. Every field name below is an
inference from observed values, not a fact. Treat this as a head start on Phase 0 —
verify each item and produce `docs/data-inventory.md` properly.

## File structure (verified mechanically)
- Pipe-delimited, no header row, **93 fields**, 64,434 rows per month, 0 ragged rows.
- Both months contain the **same 64,434 loan IDs** — the full original reference pool is
  carried forward each month with zero-balance loans retained.

## Aggregates (computed, but field positions unconfirmed)
| Measure | 2026-07 | 2026-08 |
|---|---|---|
| Original UPB (col 13) | 23,552,092,000.00 | 23,552,092,000.00 |
| Current UPB (col 40) | 19,675,126,108.17 | 19,443,046,983.78 |
| Interest-bearing UPB (col 41) | 19,675,031,403.43 | 19,442,850,173.36 |
| col 41 − col 40 | −94,704.74 | −196,810.42 |
| Loans with UPB > 0 | 57,438 | 56,871 |
| Loans at zero | 6,996 | 7,563 |
| WAC | 6.7650% | 6.7629% |
| WALA (months) | 16.34 | 17.34 |

Jul → Aug: balance −232,079,124.39 (−1.1796%). 567 loans went to zero, carrying
189,330,649.65 of July UPB; the residual ~42.7MM is scheduled amortization plus curtailments.

Zero-balance codes present: `01` (6,974 → 7,539), `96` (19 → 21), `98` (3 → 3).
Delinquency status distribution (live loans, 2026-08): 00:56,479 01:262 02:56 03:30 04:15
05:16 06:10 07:3.

## Inferred field positions — ALL REQUIRE CONFIRMATION
1 reporting period · 2 deal id (`26DNA1`) · 3 loan id · 4 amortization type (`FRM`) ·
5 seller · 6 state · 7 postal code (3-digit) · 8 MSA · 9 first payment / origination ·
10 maturity · 11 original term · 12 original rate · 13 original UPB · 14 UPB at cutoff ·
15 loan purpose · 16 channel · 17 property type · 18 units · 19 occupancy · 20 borrowers ·
21 first-time homebuyer · 23 credit score · 24 LTV · 25 CLTV · 26 DTI · 27 MI% ·
33 servicer · 34 loan age · 35/36 remaining months · 37 delinquency status ·
38 48-char delinquency history string · 39 current rate · 40 current actual UPB ·
41 interest-bearing UPB · 42 deferred UPB · 43 zero balance code · 44 zero balance date ·
48 last paid installment date · 60/62 refreshed score-like fields · 82/93 rate-like fields.

Columns fully empty in both months: 31, 32, 51–55, 57, 58, 61, 71–81, 83, 92.
Columns with <1% fill: 45, 46, 47, 49, 50, 65–70, 87, 88.

**The sparse-but-not-empty columns matter.** They are almost certainly the credit-event and
loss fields that are unpopulated because the deal is five months old. The model needs them
even though they are nearly all blank today — do not conclude they are unused.

## Structural facts from the PPM (verified by reading, page cites still needed)
- STACR REMIC Trust 2026-DNA1, closing date **February 17, 2026**, $627,500,000 offered.
- Capital stack: **A-1 $275,900,000** (SOFR + 0.85%, 4.50786% initial, WAL 1.59, window 1–37,
  initial CE 3.525%); **M-1 $275,900,000** (SOFR + 1.00%, 4.65786%, WAL 1.75, window 1–45,
  CE 2.250%); **M-2A $37,850,000** and **M-2B $37,850,000** (SOFR + 1.30%, 4.95786%,
  WAL 4.11 / 4.79, windows 45–53 and 53–60, CE 2.075% / 1.900%).
- All classes: 0% minimum coupon rate, scheduled maturity February 2046.
- **MACR classes** (M-2, M-2R/S/T/U, M-2AR/AS/AT/AU, M-2BR/BS/BT/BU) are exchangeable
  combinations of M-2A and M-2B, **not separate cashflows**. Modeling them as independent
  tranches double-counts the structure.
- Three tie-out table families exist, not one: **Weighted Average Life tables**,
  **Declining Balances tables**, **Credit Event Sensitivity tables**.

## Immediate consequence
The single largest Phase 0 risk is Q1 (missing file layout). Resolve it before any field is
given a name in code.
