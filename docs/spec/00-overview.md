# 00 — Overview: scope, time line, units and rounding for the v1 run

Author: structured-cashflow-expert, 2026-09-03. Status: authoritative for Phases 2–4.
The `fintech-dev` implements this specification without making modeling decisions. Where
this spec says ASSUMED, the reading is registered in `docs/assumptions.csv` (id given) and
is to be implemented exactly as written; if the tie-out disproves it, the diagnosis goes to
`docs/open-questions.md`, never into a tuning constant (BRIEF §2 "No plugging").

Sources used by this spec, in order of authority:

1. `data/deal_terms/stacr_2026_dna1.yaml` — cited as `YAML: <path>`; every quote there is
   verbatim PPM text with a PDF page.
2. `data/ppm_tables/*` — the tie-out targets (Appendix C, Appendix G, Table 1, WAL,
   Declining Balances, Credit Event Sensitivity, Modeling Assumptions (a)–(s)).
3. `docs/assumptions.csv` — register ids `C*`, `P*`, `T*`, `U*` (PPM/dataset/user facts)
   and `A*` (ASSUMED conventions). Every constant in this spec carries one of these ids or a
   YAML path.

The PDF itself was not re-read for this spec. No term needed by the v1 run was missing from
the YAML, so nothing was added to it.

---

## 1. What the v1 run is

The v1 run is **the PPM tie-out on the 31 Appendix C representative lines** (register T4 /
U1; Q2 option 1). It projects the Reference Pool defined by
`data/ppm_tables/appendix_c_rep_lines.csv` under the PPM's own Modeling Assumptions
(a)–(s) (`YAML: modeling_assumptions.*`), runs the hypothetical Reference Tranche structure
of Table 3 (`YAML: reference_tranches.*`), and derives from it the principal cashflows and
write-downs of the four Original Notes (A-1, M-1, M-2A, M-2B). Its outputs are compared with
the PPM's Weighted Average Life Tables, Declining Balances Tables and Credit Event
Sensitivity Tables in `docs/validation/tieout.md` (spec `03-tieout.md`).

The engine is a **rep-line engine** (U1). A rep-line is one row of Appendix C: an
outstanding balance, a remaining term, an original term and a per-annum interest rate. The
loan-level disclosure file is not an input to the v1 run.

Scenario axes of the v1 run, all taken from the PPM grids (register T25, T26):

| axis | values | source |
|---|---|---|
| CPR | 0, 5, 10, 15, 25, 35 % | T25 |
| CER | 0.00, 0.25, 0.50, 1.00, 1.50, 2.50, 3.00, 5.00 % | T26 (RM = 0 rows only) |
| RM | 0 % only (see §5) | T26, T16 |
| SOFR Rate | 3.65786 % flat | P12 / `YAML: modeling_assumptions.r_sofr_flat_pct` |
| early redemption | off ("To Scheduled Maturity Date") and on ("To Early Redemption Date") | T18 / `YAML: modeling_assumptions.m_early_redemption` |
| Delinquency Test | satisfied on every Payment Date | T10 / `YAML: modeling_assumptions.e_delinquency_test` |

---

## 2. Time line

All dates below are calendar facts from the YAML unless marked ASSUMED.

| item | value | source |
|---|---|---|
| Cut-off Date | 2025-12-31 (close of business) | `YAML: deal.cut_off_date` (P9) |
| Cut-off Date Balance | $22,781,151,551.84 | `YAML: deal.cut_off_date_balance_usd` (P10) |
| Closing Date / issue date | 2026-02-17 | `YAML: deal.closing_date` (P1), `modeling_assumptions.p_issue_date` (P70) |
| first collection month-end | 2026-01-31 | Modeling Assumptions (f),(g): "beginning in January 2026" (T11, T12) |
| first Payment Date | 2026-03-25 | `YAML: deal.first_payment_date` (P19, P71) |
| Payment Dates | 25th of each calendar month | `YAML: coupon.payment_date`; Modeling Assumption (q) |
| Scheduled Maturity / Termination Date | Payment Date in February 2046 | `YAML: deal.scheduled_maturity_date`, `deal.scheduled_termination_date` (P8, P21) |
| Earliest Time-Based Call Option Date | Payment Date in February 2031 | `YAML: termination.earliest_time_based_call_option_date` (P64) |
| clean-up threshold | aggregate UPB ≤ 10 % of Cut-off Date Balance | `YAML: termination.clean_up_threshold_pct_of_cut_off_balance` (P63) |

### 2.1 Indexing used throughout the spec

- **Collection month** `m = 1, 2, …, 241`: `m = 1` is January 2026 (month-end
  2026-01-31), `m = 241` is January 2046. Under Modeling Assumptions (f) and (g) every
  scheduled payment and every prepayment in full of month `m` is received on the last
  calendar day of that month. `m = 0` denotes the Cut-off Date state.
- **Payment Date** `n = 1, 2, …, 240`: `n = 1` is 2026-03-25, `n = 240` is 2046-02-25
  (the Scheduled Maturity Date). Payment Date `n` falls on the 25th of month `n + 2`
  counted from January 2026.
- **Reporting Period → Payment Date mapping** (`YAML: reporting_period.*`, P67, P68, and
  A4 for the first period):

  | Payment Date `n` | collection months feeding it, `M(n)` |
  |---|---|
  | 1 (March 2026) | {1, 2} = January and February 2026 |
  | n ≥ 2 | {n + 1} = the calendar month immediately preceding the Payment Date month |

  So PD 2 (April 2026) receives March 2026, and PD 240 (February 2046) receives January
  2046. This is the file-to-Payment-Date convention asked for in Q6: the Reporting Period
  for principal collections is the calendar month before the Payment Date month, and the
  disclosure file for period `YYYYMM` carries the collections that feed the Payment Date in
  month `YYYYMM + 1`.
- The 25th is used **without Business Day adjustment** in the v1 run, for the WAL clock
  and for the Accrual Period day count. This is Modeling Assumption (q) (P71) read
  literally; the actual-deal Business Day rule (`YAML: coupon.business_day`) is out of scope
  for v1 (§5).

### 2.2 Termination

The run ends on the **Maturity Date**, the earliest of (`YAML: termination.maturity_date`,
P106):

1. the Scheduled Maturity Date, Payment Date `n = 240`;
2. the Early Redemption Date, only when the scenario's early-redemption switch is on: the
   earlier of Payment Date `n = 60` (February 2031) and the first Payment Date `n` on which
   the aggregate pool UPB at the end of its Reporting Period is ≤ 10 % of the Cut-off Date
   Balance (Modeling Assumption (m); basis of the UPB test is **A11, ASSUMED**);
3. the Payment Date on which the pool UPB at the end of its Reporting Period is zero
   (Early Termination Date clause (iii)/(iv), `YAML: termination.early_termination_date`) —
   not reachable in the PPM grid but must be handled (see `02-waterfall.md` §9).

On the Maturity Date the Trust pays 100 % of each Class Principal Balance
(`YAML: termination.maturity_date_principal`, P106/P108). Nothing after the Maturity Date
is computed.

---

## 3. Units, precision and rounding policy

### 3.1 Types

- **Money is `Decimal`**: balances, principal, interest, losses, write-downs, all
  Reduction Amounts and all allocations. Never `float` (CLAUDE.md rule 3).
- **Rates and factors** (CPR, CER, SMM, monthly credit-event rate, coupons, Senior
  Percentage, day-count fractions) are computed in `Decimal` too in this engine, because
  Python does not multiply `Decimal` by `float` and because deterministic, byte-identical
  runs are required. The Decimal context precision must be at least 28 significant digits
  (Python's default) for every unrounded intermediate; 40 was used for the worked examples
  and the results are identical to the cent.

### 3.2 Rounding points — the complete list

Rounding is `ROUND_HALF_UP` everywhere (the PPM's "one-half cent being rounded up",
"five millionths of a percentage point rounded up"; `YAML: deal.rounding_convention`, P51).
No other rounding exists. The engine must not round anywhere not listed here.

| # | quantity | rounded to | rule source | spec section |
|---|---|---|---|---|
| R1 | rep-line scheduled payment, interest, scheduled principal, Credit Event Amount, prepayment in full (each month, each rep-line) | cent | **A7 (ASSUMED)** — the PPM's rounding rule is for Note calculations; the rep-line pool is a model construct | `01-pool.md` |
| R2 | every dollar amount of the hypothetical structure: Stated Principal, Credit Event Amount, Principal Loss Amount, Tranche Write-down/Write-up Amounts, Recovery Principal, Senior/Subordinate/Supplemental Reduction Amounts, Class A-1 Reduction Amount, every per-tranche allocation, Interest Accrual Amount | cent | P51 as applied by **A12 (ASSUMED)** | `02-waterfall.md` |
| R3 | percentages of the hypothetical structure: Senior Percentage, Subordinate Percentage, Offered Reference Tranche Percentage, Cumulative Net Loss Percentage | 1/100,000 of a percentage point, i.e. 7 decimal places as a fraction (`0.9647500`) | P51 as applied by **A12 (ASSUMED)** | `02-waterfall.md` |
| R4 | pro rata split of an amount between a Note tranche and its H tranche | Note leg to the cent using the exact Decimal ratio; H leg = amount − Note leg | **A8 (ASSUMED)** | `02-waterfall.md` §4 |
| R5 | SMM, monthly credit-event rate, coupons, WAL time fractions | **not rounded** (full Decimal precision) | A1, A2, A9 | `01-pool.md`, `03-tieout.md` |
| R6 | WAL for reporting | 2 decimal places, for comparison with the printed cell only; the unrounded value is stored | T28 analogue; `03-tieout.md` | `03-tieout.md` |
| R7 | Declining Balance percentage for reporting | unrounded stored; printed target is a whole percent | T28 | `03-tieout.md` |

Where the PPM's rounding rule applies (R2, R3) and where this spec specifies its own (R1,
R4) is stated in each equation in `01-pool.md` and `02-waterfall.md`.

### 3.3 Required accounting identities (assert, do not warn)

- Pool: for every rep-line and month, `balance_end = balance_begin − scheduled principal −
  Credit Event Amount − prepayment`, exactly, in cents.
- Structure: after every Payment Date `n` that is not the Maturity Date, the sum of the
  twelve Class Notional Amounts equals the pool UPB at the end of the Reporting Period for
  `n`, exactly. This holds in every v1 scenario because the pool loses exactly Stated
  Principal + Credit Event Amount and the tranches lose exactly Stated Principal + Recovery
  Principal + Tranche Write-down Amount, and Recovery Principal + Tranche Write-down Amount =
  Credit Event Amount under Modeling Assumption (d). (It would break only through the
  Stated Principal clause (e) floor, the Supplemental Senior Increase Amount, or the A-H
  increase on write-down, none of which is non-zero in v1; the engine must still compute
  those terms and assert the identity.)
- Notes: the Class Principal Balance of each Original Note equals the Class Notional
  Amount of its Corresponding Reference Tranche after every Payment Date (`YAML:
  original_notes.correspondence`, `principal.principal_payment_rule`,
  `credit_events.note_write_down_no_payment`).

---

## 4. Order of operations for one Payment Date (summary; detail in `02-waterfall.md`)

For each Payment Date `n = 1, 2, …` until the Maturity Date:

1. Aggregate the pool months `M(n)` into Stated Principal, Credit Event Amount, and the UPB
   at the end of the Reporting Period (`01-pool.md` §6).
2. Compute Senior Percentage and Subordinate Percentage from the Class Notional Amounts
   **immediately prior** to the Payment Date and the UPB at the end of the **previous**
   Reporting Period (first period: Cut-off Date Balance, A5).
3. Compute the Principal Loss Amount, Principal Recovery Amount, Tranche Write-down Amount,
   Tranche Write-up Amount, Recovery Principal, and the Cumulative Net Loss Percentage
   **including this Payment Date's loss**.
4. Evaluate the four tests (Minimum Credit Enhancement, Cumulative Net Loss, Delinquency,
   Class A-1 Cumulative Net Loss).
5. If this Payment Date is the Maturity Date: allocate the Tranche Write-down/Write-up
   Amount, then pay 100 % of each Class Principal Balance, and stop.
6. Otherwise, in this order and never any other (`YAML:
   principal.sequencing_within_payment_date`, P90–P92): allocate the Tranche Write-down
   Amount (or Write-up Amount); then the Senior Reduction Amount; then the Subordinate
   Reduction Amount; then the Supplemental Reduction Amount with the simultaneous
   Supplemental Senior Increase Amount to A-H.
7. Derive Note principal paid, Note write-down, Note interest, and the balances after the
   Payment Date; assert the identities of §3.3.

---

## 5. Deliberately out of scope for the v1 run

| item | why | where it comes back |
|---|---|---|
| MACR classes (M-2, M-2R/S/T/U/I, M-2AR/…, M-2BR/…, M-2RB/SB/TB/UB) | they are exchange combinations of M-2A and M-2B (`YAML: macr.*`, agent notes); modelling them as tranches double-counts | derive from M-2A/M-2B by exchange proportions after the four Original Notes tie |
| RM > 0 rows of the WAL tables | require the Modification Loss machinery (`YAML: modification_events.*`, P93/P101) | after the RM = 0 tie-out; Q7 governs the servicing-fee input |
| Cumulative Note Write-down Amount Tables and Yield Tables | not transcribed (T40) | later phase |
| actual-pool mode (loan-level file, real delinquencies, modifications, removals, Business Day calendar, SOFR path, payment date statements) | U1/U2/U3, Q4 | Phase 6 |
| interest cashflows as a tie-out target | no PPM interest table exists; the coupon and Accrual Period are specified in `02-waterfall.md` §10 for completeness and for the Excel export, and are computed, but nothing is compared | Yield Tables, later |
| the Delinquency Test's Distressed Principal Balance input | Modeling Assumption (e) makes the test pass; the formula is specified in `02-waterfall.md` §3.3 with a scenario flag | actual-pool mode |
| Overcollateralization Amount / Write-up Excess dynamics | zero in every v1 scenario (no Principal Recovery Amount, Modeling Assumptions (n),(o)); specified anyway | actual-pool mode |
| Business Day adjustment of the 25th | Modeling Assumption (q) read literally (§2.1) | actual-pool mode |
