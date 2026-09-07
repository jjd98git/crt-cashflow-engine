# 01 — Reference Pool projection (rep-line engine)

Scope: the pool side of the v1 run (`00-overview.md` §1). One rep-line `i` is one row of
`data/ppm_tables/appendix_c_rep_lines.csv` (31 rows, T4). The projection produces, for
every collection month `m`, the scheduled principal, the Credit Event Amount and the
prepayment in full of each rep-line, and their pool totals; then aggregates months into
Payment Dates. Interest on the pool is defined (§7) but is not consumed by the v1 waterfall.

Notation: `m` = collection month index (`00-overview.md` §2.1), `i` = rep-line,
`round2(x)` = round half-up to the cent (R1), all quantities `Decimal`.

---

## 1. Inputs

| symbol | meaning | source |
|---|---|---|
| `B[i,0]` | outstanding principal balance at the Cut-off Date | Appendix C column `outstanding_principal_balance` (strip thousands separators; `Decimal`) |
| `N[i,0]` | remaining term to maturity in months at the Cut-off Date | Appendix C `remaining_term_months` |
| `rate[i]` | per annum interest rate as a fraction (printed `6.933` → `Decimal("0.06933")`) | Appendix C `interest_rate_pct` |
| `CPR` | constant annual prepayment rate as a fraction (`10` % → `0.10`) | scenario axis, T25 |
| `CER` | constant annual credit event rate as a fraction (`1.00` % → `0.0100`) | scenario axis, T26 |
| `CutoffBalance` | $22,781,151,551.84 | P10 |

Load-time assertions (fail loud): 31 rows; `Σ_i B[i,0] == CutoffBalance` exactly (README
verification: 22,781,151,551.84); `Σ_i original_balance == 23,552,092,000.00` (D3); every
`N[i,0] ≥ 242` (so no rep-line matures before Payment Date 240 — true for Appendix C, the
smallest is 301; if a future pool violates it, `N = 1` and `N = 0` are handled in §3);
every rate strictly positive; `0 ≤ CPR < 1`, `0 ≤ CER < 1`. `original_term_months` is not
used by the projection (Modeling Assumption (c) uses the remaining term, T7).

---

## 2. Monthly rates from annual rates (A1, A2)

```
SMM  = 1 − (1 − CPR)^(1/12)        (A1)   single monthly mortality, prepayments
MDR  = 1 − (1 − CER)^(1/12)        (A2)   monthly credit event rate
```

Both are computed once per scenario in `Decimal` at full context precision and are **not
rounded** (R5). `CPR = 0 → SMM = 0`; `CER = 0 → MDR = 0`. Reference values (40-digit
context; a 28-digit context gives the same cents everywhere):

```
CPR 10 %  → SMM = 0.00874161095469670576…
CER 1 %   → MDR = 0.00083717735912055953…
```

These are the Bond Market Association conventions; the PPM states only "converted to an
equivalent monthly rate" (`YAML: credit_events.cpr_definition`, `cer_definition`; Q11
option 1). They are registered ASSUMED. The Q21 diagnosis
(`docs/validation/q21-credit-event-timing.md` §3–§5) tested `CER / 12` and `CPR / 12`, each
rate separately, against the Credit Event Sensitivity table and rejected both by 0.8–1.9 pp;
the conversions above are the only ones that reproduce it. The engine tie-out must confirm
them.

---

## 3. One rep-line, one month — order of operations

For rep-line `i` in month `m`, starting from `B = B[i,m−1]`, `N = N[i,m−1]`,
`r = rate[i] / 12` (exact `Decimal` division; e.g. 6.933 % → `r = 0.0057775` exactly).

If `B = 0` (rep-line fully paid): all flows are zero, `N[i,m] = N − 1`, skip to the next
rep-line. If `B < 0` at any point: raise.

Reading adopted 2026-09-07 (Q21; `docs/validation/q21-credit-event-timing.md`): the loans of
a rep-line that become Credit Event Reference Obligations in the month and the loans that
prepay in full are both identified at the **beginning** of the month, on the same balance,
and make no scheduled payment in the month; only the surviving loans amortize. This
supersedes the earlier reading (scheduled principal first, credit events on the balance net
of it, prepayments on the balance net of both), which left 10 of 96 Credit Event Sensitivity
cells and 12 of 336 CER > 0 WAL cells outside tolerance; the adopted reading reproduces all
of them in the independent replication.

**Step P1 — credit events, on the beginning-of-month balance** (A2):

```
CE[i,m] = round2( B × MDR )
```

`CE[i,m]` is the Credit Event UPB of the loans that become Credit Event Reference
Obligations in month `m` (`YAML: credit_events.credit_event_upb`: "UPB as of the end of the
Reporting Period"): for a loan that has stopped paying, that is its balance at the start of
the month. Those loans pay neither scheduled principal nor interest in the month.

**Step P2 — prepayments in full, on the beginning-of-month balance** (A1, A3; Modeling
Assumption (g); no curtailments, Modeling Assumption (h), P72):

```
Prepay[i,m] = round2( B × SMM )
```

The prepaying loans pay off their whole balance, with 30 days' interest (§7), and make no
separate scheduled principal payment. `CE` and `Prepay` are both computed on the same `B`;
neither is net of the other (simultaneous, not sequential).

**Step P3 — surviving balance:**

```
Bs = B − CE[i,m] − Prepay[i,m]          assert Bs ≥ 0
```

**Step P4 — scheduled monthly payment and interest of the survivors** (Modeling Assumption
(c), `YAML: modeling_assumptions.c_level_pay_amortization`, T7: level payment from the
*outstanding* balance, the rate and the *remaining* term, recomputed every month; 30 days'
interest, Modeling Assumption (g), A15):

```
if N ≥ 2:   Pmt[i,m] = round2( Bs × r / (1 − (1 + r)^(−N)) )
if N = 1:   Pmt[i,m] = round2( Bs × (1 + r) )            (final instalment)
if N = 0:   raise (a positive balance with no remaining term is a data error)
Int[i,m] = round2( Bs × r )
```

`(1 + r)^(−N)` is an integer power in `Decimal`; no float. Because the payment is
recomputed from the outstanding survivor balance each month, a rep-line keeps amortizing on
the same schedule shape after prepayments and credit events; this is the literal reading of
(c) and, for a rep-line under proportional removals, equals scaling the original schedule.

**Step P5 — scheduled principal** (Stated Principal clause (a), `YAML:
principal.stated_principal`):

```
if N ≥ 2:   SchedPrin[i,m] = min( Bs, Pmt[i,m] − Int[i,m] )
if N = 1:   SchedPrin[i,m] = Bs
B[i,m] = Bs − SchedPrin[i,m]
N[i,m] = N − 1
```

The `min` guards the last few cents when rounding would otherwise overshoot; assert
`SchedPrin ≥ 0`.

**Identity (assert):** `B[i,m] = B[i,m−1] − CE[i,m] − Prepay[i,m] − SchedPrin[i,m]`
exactly.

**Sequence within the month, restated:** credit events and prepayments in full, both on the
beginning balance → survivors → scheduled payment and interest on the survivors → scheduled
principal → roll the remaining term. Never reorder. At `CER = 0` this sequence gives the
same pool UPB and Stated Principal as the superseded one to within cents (only the split
between `SchedPrin` and `Prepay` moves, by about `SchedPrin × SMM`), which is why the CER 0
tables tied under either reading and why the CER > 0 tables are the only test of it.

---

## 4. Pool totals per month

```
SchedPrin[m] = Σ_i SchedPrin[i,m]     Int[m]  = Σ_i Int[i,m]
CE[m]        = Σ_i CE[i,m]            UPB[m]  = Σ_i B[i,m]
Prepay[m]    = Σ_i Prepay[i,m]        UPB[0]  = CutoffBalance
```

Sums of cent-rounded amounts; no further rounding.

---

## 5. What flows into the waterfall: Stated Principal and Credit Event Amount

Stated Principal (`YAML: principal.stated_principal`, P96) has five clauses. Under the
Modeling Assumptions, per month:

| clause | PPM content | v1 value |
|---|---|---|
| (a) | scheduled principal due and collected | `SchedPrin[m]` (every payment is timely, Modeling Assumption (f)) |
| (b) | partial prepayments | 0 (Modeling Assumption (h)) |
| (c) | UPB of Reference Pool Removals other than Credit Events — a payment in full is a Reference Pool Removal (`YAML: reference_pool_removal.definition` (ii), `cashflow_treatment`) | `Prepay[m]` |
| (d) | negative UPB adjustments (modifications, data corrections) | 0 (Modeling Assumptions (k)(i)/(l); RM = 0) |
| (e) | positive UPB adjustments | 0 (Modeling Assumption (l)) |

Hence, per collection month, `StatedPrincipal[m] = SchedPrin[m] + Prepay[m]`, and the
clause (e) floor (excess of (e) over (a)–(d) added to A-H) is zero. The engine must still
implement the floor as written for later phases; assert it is zero in v1.

Credit Event Amount per month (`YAML: credit_events.credit_event_amount`):
`CreditEventAmount[m] = CE[m]`. Credit Event loans leave the pool through the loss
definitions in `02-waterfall.md` §3, not through Stated Principal.

The terms "scheduled principal" and "unscheduled principal" are not PPM terms
(`YAML: principal.scheduled_vs_unscheduled_note`); in this spec they mean `SchedPrin[m]` and
`Prepay[m]` respectively, and both are reported separately by the engine.

---

## 6. Aggregation into Payment Dates (the two-month first period)

Using `M(n)` from `00-overview.md` §2.1 (`M(1) = {1, 2}`, `M(n) = {n + 1}` for `n ≥ 2`;
A4, P67, P68):

```
StatedPrincipal[n]   = Σ_{m ∈ M(n)} ( SchedPrin[m] + Prepay[m] )
CreditEventAmount[n] = Σ_{m ∈ M(n)} CE[m]
UPB_end[n]           = UPB[ max M(n) ]        pool UPB at the end of the Reporting Period for n
UPB_prev[n]          = CutoffBalance  if n = 1,  else UPB_end[n − 1]        (A5)
```

The first Payment Date therefore carries **two** month-ends of scheduled amortization,
credit events and prepayments (January 31 and February 28, 2026), one Appendix G Class A-1
Reduction Amount (the schedule is indexed by Payment Period, T42), and one Accrual Period
of Note interest (36 days). Payment Date 240 (February 2046) carries collection month 241
(January 2046). Months are projected through `m = 241` only; the pool is not fully
amortized at the Scheduled Termination Date and does not need to be.

If the run ends early (Maturity Date before `n = 240`, `00-overview.md` §2.2), months
after `max M(n_maturity)` are not needed; it is acceptable to project all 241 months and
ignore the tail.

---

## 7. Pool interest (defined; not consumed by the v1 tie-out)

`Int[m] = Σ_i Int[i,m]` (§3 P4, §4) is the survivors' scheduled interest for the month,
30/360 on their beginning balance (A15). Modeling Assumption (g) adds "30 days' interest" on
prepayments in full, received on the last day of the month: under §3 the prepaying loans
have made no scheduled payment, so that interest is additional:

```
PoolInterest[m] = Int[m] + Σ_i round2( Prepay[i,m] × r[i] )
```

Credit Event Reference Obligations contribute no interest in the month they are removed (a
loan reported as a Credit Event has stopped paying). None of this is tied out by a PPM
table — the Notes' interest does not depend on pool interest (`YAML: interest.*`; no
available-funds mechanism, P107) — so pool interest appears in the pool output for the
Excel export and for later actual-pool use only. Register row A15 still carries the
superseded wording ("prepayments in full carry no additional interest because they occur
after the month's scheduled payment") and must be revised to this definition before pool
interest is consumed anywhere (Q21 resolution, item for the manager).

---

## 8. Edge cases

| case | required behaviour |
|---|---|
| `B[i,m−1] = 0` | all flows 0; do not divide; still decrement `N` |
| `N = 1` | final instalment: scheduled principal = whole surviving balance (§3 P4/P5) |
| `N = 0` with `B > 0` | raise, naming the rep-line and month |
| `Pmt − Int > Bs` after rounding | capped by the `min` in P5 |
| `CPR = 0` / `CER = 0` | `SMM = 0` / `MDR = 0`; steps still executed, amounts 0, `Bs = B` |
| `CPR` or `CER` ≥ 1 or < 0 | reject at scenario load |
| first Payment Date | two months per §6; nothing else special on the pool side |
| final Payment Date (240) | month 241 only; leftover pool balance is simply the end state |
| early redemption | pool projection unaffected; the waterfall stops (`02-waterfall.md` §9) |
| pool UPB reaches 0 | possible only at CPR ≥ 100 % or a maturing rep-line; the waterfall then terminates (`02-waterfall.md` §9) |
| negative balance / negative flow anywhere | raise |

---

## 9. Worked example — rep-line group 17, first two months, 10 % CPR, 0 % CER

Inputs (Appendix C row 17): `B[17,0] = 5,703,897,138.22`, `N[17,0] = 350`,
`rate = 6.933 %`, so `r = 0.06933 / 12 = 0.0057775` exactly. `SMM =
0.00874161095469670576…` (§2). `MDR = 0`. (Numbers revised 2026-09-07 for the §3 reading
adopted under Q21; the month-end balances are unchanged from the superseded reading.)

**Month 1 (January 2026, month-end 2026-01-31)**

| step | computation | result |
|---|---|---|
| P1 | `5,703,897,138.22 × 0` | `CE = 0.00` |
| P2 | `5,703,897,138.22 × 0.0087416109546967…` → round2 | `Prepay = 49,861,249.71` |
| P3 | `5,703,897,138.22 − 0 − 49,861,249.71` | `Bs = 5,654,035,888.51` |
| P4 | `5,654,035,888.51 × 0.0057775 / (1 − 1.0057775^(−350))` → round2 | `Pmt = 37,683,632.42` |
| | `5,654,035,888.51 × 0.0057775 = 32,666,192.3458…` → round2 | `Int = 32,666,192.35` |
| P5 | `37,683,632.42 − 32,666,192.35` | `SchedPrin = 5,017,440.07` |
| | `B[17,1] = 5,654,035,888.51 − 5,017,440.07` | `5,649,018,448.44`; `N[17,1] = 349` |

**Month 2 (February 2026, month-end 2026-02-28)**

| step | computation | result |
|---|---|---|
| P1 | | `CE = 0.00` |
| P2 | `5,649,018,448.44 × SMM` → round2 | `Prepay = 49,381,521.55` |
| P3 | `5,649,018,448.44 − 49,381,521.55` | `Bs = 5,599,636,926.89` |
| P4 | `5,599,636,926.89 × 0.0057775 / (1 − 1.0057775^(−349))` → round2 | `Pmt = 37,354,216.77` |
| | `5,599,636,926.89 × 0.0057775` → round2 | `Int = 32,351,902.35` |
| P5 | `37,354,216.77 − 32,351,902.35` | `SchedPrin = 5,002,314.42` |
| | | `B[17,2] = 5,594,634,612.47`; `N[17,2] = 348` |

Rep-line 17's contribution to Payment Date 1 Stated Principal:
`5,017,440.07 + 49,861,249.71 + 5,002,314.42 + 49,381,521.55 = 109,262,525.75`.

**Credit-event hand case — same rep-line, month 1, 10 % CPR, 1 % CER** (`MDR =
0.00083717735912055953…`, §2): `CE = round2(5,703,897,138.22 × MDR) = 4,775,173.54`;
`Prepay = 49,861,249.71` (unchanged: same `B`, same `SMM`); `Bs = 5,649,260,714.97`;
`Pmt = 37,651,806.33`; `Int = 32,638,603.78`; `SchedPrin = 5,013,202.55`;
`B[17,1] = 5,644,247,512.42`. Pool month 1 for this scenario: `SchedPrin[1] =
20,714,216.91`, `Prepay[1] = 199,143,963.97`, `CE[1] = 19,071,864.30`, `UPB[1] =
22,542,221,506.66`.

**Pool totals at 10 % CPR, 0 % CER** (all 31 rep-lines, same method), which the
`02-waterfall.md` example consumes:

| month | `SchedPrin[m]` | `Prepay[m]` | `CE[m]` | `UPB[m]` |
|---|---|---|---|---|
| 1 (Jan 2026) | 20,731,726.12 | 199,143,963.97 | 0.00 | 22,561,275,861.75 |
| 2 (Feb 2026) | 20,666,043.58 | 197,221,896.21 | 0.00 | 22,343,387,921.96 |
| 3 (Mar 2026) | 20,600,572.48 | 195,317,204.65 | 0.00 | 22,127,470,144.83 |

Payment Date aggregates: `StatedPrincipal[1] = 437,763,629.88`, `UPB_end[1] =
22,343,387,921.96`, `UPB_prev[1] = 22,781,151,551.84`; `StatedPrincipal[2] =
215,917,777.13`, `UPB_end[2] = 22,127,470,144.83`, `UPB_prev[2] = 22,343,387,921.96`.
(Under the superseded reading month 3 ended at 22,127,470,144.88 and `StatedPrincipal[2]`
was 215,917,777.08 — five cents, the rounding of 31 rep-lines; Payment Date 1 is identical
to the cent.)

A unit test should reproduce the group-17 tables above to the cent from the six inputs
(both the CER 0 months and the 1 % CER hand case), and a second test should reproduce the
three pool rows from the full Appendix C file. A third test at `CPR = 0, CER = 0` should
show `Prepay = 0`, `CE = 0` and, for group 17, that the scheduled payment `38,015,953.09` is
unchanged in month 2 (level-pay identity: with no removals the recomputed payment equals the
original one to the cent, or differs by at most one cent from rounding — the test must
assert the exact engine value, not "about").
