# 03 — Tie-out: WAL definition, targets, tolerances, diagnostics, report layout

Scope: Phase 4 acceptance (BRIEF §7). The engine of `01-pool.md` and `02-waterfall.md` is
run over the PPM grid (`00-overview.md` §1) and compared with `data/ppm_tables/*`. The
comparison is a CI regression test and is regenerated as `docs/validation/tieout.md` on
every run.

---

## 1. Weighted Average Life — definition and computation

PPM definition (`YAML: modeling_assumptions.wal_definition`, p219): "the average amount of
time that will elapse from the date of issuance of such Class of Notes until its balance is
reduced to zero." The PPM gives no formula, no day count and no statement of whether
write-downs count. The spec fixes all three:

```
R[X, n]  = CPB[X] immediately prior to Payment Date n − CPB[X] after Payment Date n
           (net reduction of the Class Principal Balance on n: principal paid + Tranche
            Write-down allocated − Tranche Write-up allocated; on the Maturity Date it
            includes the 100 % payment)                                                (A10)
t[n]     = ( 30 × n + 8 ) / 360   years from the Closing Date 2026-02-17 to the 25th of the
           Payment Date month, 30/360 day count, no Business Day adjustment              (A9)
WAL[X]   = Σ_n R[X, n] × t[n]  /  Σ_n R[X, n]           over all Payment Dates up to and including the Maturity Date
```

`t[1] = 38/360 = 0.10556` (2026-02-17 → 2026-03-25 is 8 + 30 days in 30/360),
`t[12] = 368/360`, `t[60] = 1808/360 = 5.02222` (the printed 5.02 for every class that is
redeemed on the February 2031 Early Redemption Date).

Why these readings (both ASSUMED, Q12/Q13, to be confirmed by the engine tie-out):

- **Write-downs count (A10).** The printed M-2B WAL at 0 % CPR falls from 19.29 (CER 0) to
  8.75 (CER 1 %) and 1.61 (CER 5 %) "To Scheduled Maturity Date". At 0 % CPR the
  subordinate side receives ~4.8 % of ~$20 MM of scheduled principal a month, so no
  principal-only measure can retire $37.85 MM in 1.6 years; only write-downs can. The
  Cumulative Note Write-down Amount Tables being a separate family does not change this.
- **30/360 from the Closing Date (A9).** Class A-1's principal is fixed by Appendix G plus
  limb (B): 3.750 %/month for 12 months, 1.500 %/month for 24 months, the remaining
  19.000 % on Payment Date 37 at any CPR ≥ 5 %. That schedule gives Σ (weight × n) =
  18.775 months, hence WAL = 1.565 with `t = n/12`, 1.583 with actual/365 from the Closing
  Date, 1.587 with 30/360 from the Closing Date, 1.603 with actual/360. The PPM prints
  **1.59**; only 30/360 rounds to it. The spec author's scratch replication then
  reproduced all 48 CER-0 cells of the four Original Notes within ±0.01 with 30/360,
  whereas actual/365 misses six of them (A-1 at every CPR ≥ 5 %, M-2A at 0/25/35 % CPR,
  M-2B at 35 % CPR).

Rounding: `WAL` is stored unrounded and rounded half-up to 2 decimals for display only.
If `Σ R = 0` (a Note never reduced — impossible in v1) report `n/a`, never 0.

**Hand check for the unit test** (A-1, 10 % CPR, CER 0, either basis): weights 0.0375 on
n = 1..12, 0.0150 on n = 13..36, 0.1900 on n = 37; `WAL = (0.0375 × Σ_{1}^{12} t[n] +
0.0150 × Σ_{13}^{36} t[n] + 0.19 × t[37])` = 1.5868 → 1.59. The engine must reproduce
the weights from the waterfall, not take them from this paragraph.

---

## 2. First and last principal Payment Date

For each Note and scenario: `first[X]` = the smallest `n` with principal paid > 0;
`last[X]` = the largest such `n` (principal paid only — write-downs are not payments; the
Maturity Date 100 % payment counts). Month numbering: `n = 1` is March 2026 (T38).

The only printed windows are Table 1's, at 10 % CPR, CER 0, RM 0, early redemption **on**
(T2, T38, `YAML: original_notes.<X>.expected_principal_window_months_table1`):

| Note | printed window | required |
|---|---|---|
| A-1 | 1–37 | exact |
| M-1 | 1–45 | exact |
| M-2A | 45–53 | exact |
| M-2B | 53–60 | exact |

No tolerance (BRIEF §7). The scratch replication gives exactly these four windows.

Secondary window check for every Declining Balances scenario: the last principal Payment
Date must lie in the twelve-month band ending at the first "February 25" row printed as 0
for that class and CPR (and after the last row printed > 0). This is a consistency check
derived from the printed table, reported as pass/fail without tolerance.

---

## 3. Target cells and the order in which they are diagnostic

Run and report in this order; do not look at a later family until the earlier one passes,
because each family isolates one layer of convention.

### 3.1 Declining Balances Tables, CER 0, RM 0, early redemption off (`declining_balances.csv`)

Isolates the pool conventions (Q10/A4 first period, A1/A3 SMM) and the principal
allocation with **no** losses and **no** tests binding. 4 Notes × 6 CPRs × the dated rows
(A-1: 4 dates; M-1: 18; M-2A: 19; M-2B: 20) plus the "and thereafter" rows.

- Model value: `100 × CPB[X] after Payment Date 12·k / original Class Principal Balance`
  for the row "February 25, 2026 + k" (`k = 1` → Payment Date 12 → February 25, 2027).
  Unrounded; the Closing Date row is 100 by construction.
- Printed value: a whole percent (T28, "Rounded to the nearest whole percentage").
- **Pass criterion (A13, ASSUMED — Q16):** `round_half_up(model, 0) == printed`. The
  brief's ±0.25 pp is reported alongside as `within_brief_tolerance` but a correct model
  cannot be held to it against a whole-percent print (a true value of 23.47 prints as 23;
  the scratch replication has exactly that cell for M-1 at 25 % CPR, February 2027, and
  52.51 → 53 for M-1 at 15 % CPR). Trey decides which criterion is the definition of done.
- Also compare the two WAL rows printed under each Declining Balances table
  ("to Scheduled Maturity Date", "to Early Redemption Date**"); they equal the WAL-table
  cells at CER 0 (README cross-check), so they are the same targets as §3.2.

### 3.2 Weighted Average Life Tables, CER 0, RM 0, both bases (`wal_tables.csv`)

Isolates the WAL clock (A9) and the early-redemption mechanics (Modeling Assumption (m),
A11, §9 of `02-waterfall.md`). 4 Notes × 6 CPRs × 2 bases = 48 cells. Tolerance
**±0.02 years** (v1); report whether ±0.10 (milestone) and ±0.02 hold. Only the four
Original Notes are compared in v1; MACR classes are derived later (`00-overview.md` §5).

### 3.3 Table 1 windows (§2) — at 10 % CPR, early redemption on. Exact.

### 3.4 Weighted Average Life Tables, CER > 0, RM 0, both bases

Isolates the loss conventions (A2 credit-event basis and timing, the 25 % / 75 % split,
write-down allocation, test toggling, the Class A-1 test's permanence). 4 Notes × 6 CPRs ×
7 CERs × 2 bases = 336 cells, ±0.02.

### 3.5 Credit Event Sensitivity Tables (`credit_event_sensitivity.csv`)

Cumulative Credit Event Amount as a percentage of the Cut-off Date Balance, to the Maturity
Date of each basis: `100 × Σ_{n ≤ Maturity} CreditEventAmount[n] / CutoffBalance`. 8 CERs ×
6 CPRs × 2 bases = 96 cells, printed to one decimal. Pass criterion: `round_half_up(model,
1) == printed`; also report `|model − printed| ≤ 0.25 pp`. This family checks the pool's
credit-event mechanics independently of the waterfall and should be run alongside §3.4 to
separate pool-side from structure-side causes.

Out of scope (T40): Cumulative Note Write-down Amount Tables, Yield Tables, RM > 0 rows,
MACR rows.

---

## 4. Tolerances (BRIEF §7) — summary

| target | tolerance | notes |
|---|---|---|
| first / last principal Payment Date | exact month | Table 1 windows only |
| WAL | ±0.02 years (report ±0.10 milestone too) | printed to 2 decimals |
| Declining Balances % | printed whole percent; A13 criterion plus the ±0.25 pp flag | see §3.1 |
| Credit Event Sensitivity % | printed 0.1 %; A13-style criterion plus ±0.25 pp flag | see §3.5 |

---

## 5. Ranked hypothesis list for a mismatch

Test one at a time, in this order, reverting each before the next; record every trial in
`docs/validation/tieout.md` §7 whether or not it helped. Never combine a change with a
scaling factor (BRIEF §2).

1. **First-period timing (Q10 / A4).** Symptom: every Declining Balances cell for M-1 is
   too high by about one month of subordinate principal (≈2–3 pp in the first year) and
   every WAL is long by ~0.08. Alternatives: one month of prepayment but two of
   amortization; one month of everything.
2. **WAL clock (A9).** Symptom: Declining Balances tie, WALs are uniformly off by
   0.01–0.04 with no CPR pattern. Alternatives in order: actual/365 from the Closing Date;
   `n/12`; actual/360; Business-Day-adjusted 25ths.
3. **Termination / early redemption (Modeling Assumption (m), A11, P108).** Symptom: only
   the "To Early Redemption Date" cells or only the 0 %/5 % CPR long-dated cells miss;
   M-2A/M-2B at 0–5 % CPR should read exactly 5.02 (Payment Date 60). Alternatives: UPB
   tested at the end of the previous Reporting Period; Steps 2–4 applied on the Maturity
   Date before the 100 % payment.
4. **Test thresholds and evaluation timing (`02-waterfall.md` §3).** Symptom: CER-0 cells
   tie, CER > 0 cells miss with the miss growing in CER; or M-1 lengthens at small CER
   more/less than printed (2.10 at 0.25 % CER / 10 % CPR). Alternatives: Cumulative Net
   Loss Percentage excluding the current Payment Date; MCE test on balances after the
   write-down; the Class A-1 test without permanence.
5. **Allocation order and the Class A-1 Reduction Amount (A6, P90–P92).** Symptom: A-1's
   Declining Balances differ from 55/37/19 at any CPR (they are fixed by Appendix G) or
   A-1's WAL at 0 % CPR is not 1.60 (Payment Date 39 Supplemental limb). Alternatives:
   Appendix G read as the A-1 column only; carry-forward of shortfalls; A-1 Additional
   Reduction not applied.
6. **Rounding (A7, A8, A12).** Symptom: differences at the fifth significant figure only,
   or the Minimum Credit Enhancement Test failing on Payment Date 1 at CER 0 (the
   knife-edge in `02-waterfall.md` §2). Alternatives: no rounding of percentages; cent
   rounding of pool amounts removed.
7. **SMM / credit-event convention (A1, A2, A3).** Symptom: CER-0 Declining Balances drift
   with horizon (SMM); or CER > 0 cells are consistently long or short by 0.01–0.03 (credit
   events). Alternatives in order: monthly rate = annual/12; credit events on the balance
   before scheduled principal; prepayments before credit events; credit-event loans not
   paying scheduled principal in the month. The scratch replication with the adopted
   conventions is within ±0.01 on most CER > 0 cells and +0.01 to +0.03 (model longer) on
   the rest (Q17), so a residual of that size is expected and is **not** a failure of the
   ±0.02 tolerance except on a handful of long-dated 0 % CPR cells; if the engine shows the
   same pattern, escalate with the per-cell table rather than changing A2.
   *Superseded 2026-09-07 (Q21): the engine showed exactly that pattern (12/336 WAL CER > 0 and 10/96 Credit Event Sensitivity cells outside tolerance); the diagnosis in `docs/validation/q21-credit-event-timing.md` adopted the fourth alternative combined with the second — credit events and prepayments in full both on the beginning-of-month balance, simultaneous, only the survivors amortize (A2/A3 revised; `01-pool.md` §3) — and the engine now ties 336/336 and 96/96, so the residual described here is no longer expected.*

A mismatch surviving the list is escalated immediately (BRIEF §11) with the table of
trials.

---

## 6. Independent replication already on file (informational)

While writing this spec the author built a scratch replication (Python `Decimal`, outside
the repository, not engine code) of `01-pool.md` and `02-waterfall.md` exactly as written
and compared it with the transcribed tables. Results, all with A1–A13 as specified:

- Table 1 windows: 1–37, 1–45, 45–53, 53–60 — exact.
- WAL, CER 0, RM 0, 48 cells: all within ±0.01 with the 30/360 clock (A-1 1.60/1.59; M-1
  10.31, 4.59, 3.20, 1.75, 1.18, 0.68, 0.46; M-2A 18.00, 7.35, 4.11, 2.78, 1.62, 1.09;
  M-2B 19.29, 8.51/8.52, 4.81/4.79, 3.26, 1.89/1.90, 1.28).
- Declining Balances, CER 0: every cell checked rounds to the printed whole percent
  (M-1 at 0 % CPR 96.6/93.2/89.6/85.7/81.6/77.2/72.4/67.4 → 97/93/90/86/82/77/72/67;
  M-1 10 % 67.1/40.1/15.8; M-2A 10 % 56.7 → 57; M-2B 10 % 14.8 → 15; M-2B 5 % 87.85/4.41
  → 88/4; M-2A 0 % 2044 45.85 → 46; M-2B 0 % 2045 68.26 → 68).
- WAL, CER > 0, 96 cells checked (CER 0.25/1.00/2.50/5.00 % × CPR 0/10/35 % × 2 bases):
  60 exact to the printed 2 decimals, 33 within ±0.01, 2 at +0.02, 1 at +0.03 (M-1, 1 %
  CER, 0 % CPR, to Scheduled Maturity: 13.73 vs 13.70). Sign is almost always model
  longer.

This is evidence that the conventions are the PPM's, not a substitute for the engine
tie-out: the engine must reproduce these independently, and `docs/validation/` will then
carry the spec author's replication of a Payment Date against the engine's numbers.

*Superseded 2026-09-07 (Q21): the replication above used the pre-Q21 A2/A3 reading; under `01-pool.md` §3 as amended the engine ties WAL CER > 0 336/336 (worst 0.0050 yr) and Credit Event Sensitivity 96/96 (worst 0.05 pp), with the CER 0 results above unchanged (`docs/validation/tieout.md`, `docs/validation/q21-credit-event-timing.md`).*

---

## 7. `docs/validation/tieout.md` — required layout

Regenerated on every run (BRIEF §7); the file is the artifact, the CI test asserts its
pass/fail cells.

```
# Tie-out — STACR 2026-DNA1 — <UTC timestamp>
Manifest: engine version, git commit, SHA-256 of appendix_c_rep_lines.csv, appendix_g_…csv,
wal_tables.csv, declining_balances.csv, credit_event_sensitivity.csv, stacr_2026_dna1.yaml,
assumptions.csv; conventions in force: A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13.

## 1. Summary
| family | cells | pass | fail | worst |diff| | tolerance | status |
(rows: Table 1 windows; Declining Balances CER 0; WAL CER 0; WAL CER>0; Credit Event Sensitivity)
Overall: PASS / FAIL.

## 2. Table 1 principal windows (10 % CPR, CER 0, early redemption on)
| Note | model first | model last | PPM window | pass |

## 3. Declining Balances (CER 0), one table per Note
| CPR | row date | model % (2 dp) | PPM % | diff | round-match pass | |diff| ≤ 0.25 |
plus the two WAL rows per CPR.

## 4. WAL, CER 0, RM 0
| Note | basis | CPR | model WAL (4 dp) | PPM | diff | ±0.02 | ±0.10 |

## 5. WAL, CER > 0, RM 0
| Note | basis | CER | CPR | model | PPM | diff | ±0.02 |

## 6. Credit Event Sensitivity
| basis | CER | CPR | model % (2 dp) | PPM % | diff | round-match pass | |diff| ≤ 0.25 |

## 7. Diagnostics (only when anything fails)
| hypothesis (§5 number) | change tried | family/cells affected | before | after | kept? |
```

Every model number is written from the engine's stored unrounded value; every PPM number
is the transcribed string. A `diff` is model − PPM. Nothing is omitted when it fails.
