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
option 1). They are registered ASSUMED and were shown by the spec author's independent
scratch replication to reproduce the PPM tables (`03-tieout.md` §6); the engine tie-out
must confirm them.

---

## 3. One rep-line, one month — order of operations

For rep-line `i` in month `m`, starting from `B = B[i,m−1]`, `N = N[i,m−1]`,
`r = rate[i] / 12` (exact `Decimal` division; e.g. 6.933 % → `r = 0.0057775` exactly).

If `B = 0` (rep-line fully paid): all flows are zero, `N[i,m] = N − 1`, skip to the next
rep-line. If `B < 0` at any point: raise.

**Step P1 — scheduled monthly payment** (Modeling Assumption (c), `YAML:
modeling_assumptions.c_level_pay_amortization`, T7: level payment from the *outstanding*
balance, the rate and the *remaining* term, recomputed every month):

```
if N ≥ 2:   Pmt[i,m] = round2( B × r / (1 − (1 + r)^(−N)) )
if N = 1:   Pmt[i,m] = round2( B × (1 + r) )            (final instalment)
if N = 0:   raise (a positive balance with no remaining term is a data error)
```

`(1 + r)^(−N)` is an integer power in `Decimal`; no float. Because the balance is
recomputed from the outstanding amount each month, a rep-line that has prepaid keeps
amortizing on the same schedule shape; this is the literal reading of (c) and is
equivalent, for a rep-line under proportional prepayments, to scaling the original
schedule.

**Step P2 — interest for the month** (30 days' interest, Modeling Assumption (g); A15):

```
Int[i,m] = round2( B × r )
```

**Step P3 — scheduled principal** (Stated Principal clause (a), `YAML:
principal.stated_principal`):

```
if N ≥ 2:   SchedPrin[i,m] = min( B, Pmt[i,m] − Int[i,m] )
if N = 1:   SchedPrin[i,m] = B
B1 = B − SchedPrin[i,m]
```

The `min` guards the last few cents when rounding would otherwise overshoot; assert
`SchedPrin ≥ 0`.

**Step P4 — credit events, removed before prepayments, on the balance net of scheduled
principal** (A2, A3):

```
CE[i,m] = round2( B1 × MDR )
B2 = B1 − CE[i,m]
```

`CE[i,m]` is the Credit Event UPB of the loans that become Credit Event Reference
Obligations in month `m` (`YAML: credit_events.credit_event_upb`: "UPB as of the end of
the Reporting Period" — the balance after that month's scheduled principal). Under the
adopted convention those loans pay their scheduled principal for the month (it is computed
on `B` before removal); this is part of A2/A3, not a separate choice.

**Step P5 — prepayments in full, on the balance net of scheduled principal and credit
events** (A1, A3; Modeling Assumption (g); no curtailments, Modeling Assumption (h), P72):

```
Prepay[i,m] = round2( B2 × SMM )
B[i,m] = B2 − Prepay[i,m]
N[i,m] = N − 1
```

**Identity (assert):** `B[i,m] = B[i,m−1] − SchedPrin[i,m] − CE[i,m] − Prepay[i,m]`
exactly.

**Sequence within the month, restated:** scheduled payment → interest → scheduled
principal → credit events → prepayments → roll the remaining term. Never reorder.

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

`Int[m]` in §4 is the pool's gross scheduled interest for the month, 30/360 on the
beginning balance (A15). Modeling Assumption (g) adds "30 days' interest" on prepayments in
full; since prepayments occur on the last day of the month after that month's scheduled
payment, the prepaid loans have already paid their month's interest in `Int[m]` and no
extra interest is due. The Notes' interest does not depend on pool interest (`YAML:
interest.*`; no available-funds mechanism, P107), so pool interest appears in the pool
output for the Excel export and for later actual-pool use only.

---

## 8. Edge cases

| case | required behaviour |
|---|---|
| `B[i,m−1] = 0` | all flows 0; do not divide; still decrement `N` |
| `N = 1` | final instalment: scheduled principal = whole balance (§3 P1/P3) |
| `N = 0` with `B > 0` | raise, naming the rep-line and month |
| `Pmt − Int > B` after rounding | capped by the `min` in P3 |
| `CPR = 0` / `CER = 0` | `SMM = 0` / `MDR = 0`; steps still executed, amounts 0 |
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
0.00874161095469670576…` (§2). `MDR = 0`.

**Month 1 (January 2026, month-end 2026-01-31)**

| step | computation | result |
|---|---|---|
| P1 | `5,703,897,138.22 × 0.0057775 / (1 − 1.0057775^(−350))` → round2 | `Pmt = 38,015,953.09` |
| P2 | `5,703,897,138.22 × 0.0057775 = 32,954,265.7157…` → round2 | `Int = 32,954,265.72` |
| P3 | `38,015,953.09 − 32,954,265.72` | `SchedPrin = 5,061,687.37` |
| | `B1 = 5,703,897,138.22 − 5,061,687.37` | `B1 = 5,698,835,450.85` |
| P4 | `B1 × 0` | `CE = 0.00`; `B2 = 5,698,835,450.85` |
| P5 | `5,698,835,450.85 × 0.0087416109546967…` → round2 | `Prepay = 49,817,002.41` |
| | `B[17,1] = 5,698,835,450.85 − 49,817,002.41` | `5,649,018,448.44`; `N[17,1] = 349` |

**Month 2 (February 2026, month-end 2026-02-28)**

| step | computation | result |
|---|---|---|
| P1 | `5,649,018,448.44 × 0.0057775 / (1 − 1.0057775^(−349))` → round2 | `Pmt = 37,683,632.42` |
| P2 | `5,649,018,448.44 × 0.0057775` → round2 | `Int = 32,637,204.09` |
| P3 | `37,683,632.42 − 32,637,204.09` | `SchedPrin = 5,046,428.33`; `B1 = 5,643,972,020.11` |
| P4 | | `CE = 0.00`; `B2 = 5,643,972,020.11` |
| P5 | `5,643,972,020.11 × SMM` → round2 | `Prepay = 49,337,407.64` |
| | | `B[17,2] = 5,594,634,612.47`; `N[17,2] = 348` |

Rep-line 17's contribution to Payment Date 1 Stated Principal:
`5,061,687.37 + 49,817,002.41 + 5,046,428.33 + 49,337,407.64 = 109,262,525.75`.

**Pool totals for the same scenario** (all 31 rep-lines, same method), which the
`02-waterfall.md` example consumes:

| month | `SchedPrin[m]` | `Prepay[m]` | `CE[m]` | `UPB[m]` |
|---|---|---|---|---|
| 1 (Jan 2026) | 20,914,552.99 | 198,961,137.10 | 0.00 | 22,561,275,861.75 |
| 2 (Feb 2026) | 20,848,291.20 | 197,039,648.59 | 0.00 | 22,343,387,921.96 |
| 3 (Mar 2026) | 20,782,242.77 | 195,135,534.31 | 0.00 | 22,127,470,144.88 |

Payment Date aggregates: `StatedPrincipal[1] = 437,763,629.88`, `UPB_end[1] =
22,343,387,921.96`, `UPB_prev[1] = 22,781,151,551.84`; `StatedPrincipal[2] =
215,917,777.08`, `UPB_end[2] = 22,127,470,144.88`, `UPB_prev[2] = 22,343,387,921.96`.

A unit test should reproduce the group-17 table above to the cent from the six inputs, and
a second test should reproduce the three pool rows from the full Appendix C file. A third
test at `CPR = 0, CER = 0` should show `Prepay = 0`, `CE = 0` and, for group 17, that the
scheduled payment `38,015,953.09` is unchanged in month 2 (level-pay identity: with no
prepayment the recomputed payment equals the original one to the cent, or differs by at
most one cent from rounding — the test must assert the exact engine value, not "about").
