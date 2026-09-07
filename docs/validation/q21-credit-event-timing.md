# Q21 — the PPM's within-month convention for credit events, prepayments and scheduled principal

Author: structured-cashflow-expert. Date: 2026-09-07. Status: **resolved — one convention
reproduces all 96 Credit Event Sensitivity cells and all 336 CER > 0 WAL cells.**

Scope: Q21 (engine 0.0.1 ties 86/96 Credit Event Sensitivity cells and 324/336 CER > 0 WAL
cells with A1–A15 as specified; Trey ruled that is not v1 done). This note determines, by an
independent scratch replication, which within-month sequence of credit events, prepayments
in full and scheduled principal the PPM tables were generated with. The engine (`src/`) was
not read for this work beyond confirming the field names quoted in §7; nothing in `src/` or
`tests/` was changed.

---

## 1. Why the Credit Event Sensitivity table is the discriminating target

The Credit Event Sensitivity Tables (PPM p146, `data/ppm_tables/credit_event_sensitivity.csv`)
print the cumulative Credit Event Amount as a percentage of the Cut-off Date Balance for 8 CER
× 6 CPR × 2 bases = 96 cells, to 0.1 %. Nothing in the hypothetical structure enters this
number: it is `100 × Σ CE[m] / CutoffBalance` over the collection months of the basis. So it
isolates the pool conventions — annual-to-monthly conversion, the balance each rate applies to,
the order of removal, whether removed loans pay the month's scheduled principal, the start
month, the horizon — from everything the waterfall does. The WAL grid at CER > 0 then tests
the same convention through the structure.

Pass criterion (03-tieout.md §3.5, Q16/A13): `round_half_up(model, 1) == printed`; the ±0.25 pp
BRIEF §7 tolerance is reported as a flag only.

## 2. Method — independent replication

Scratch scripts in the session scratchpad (not engine code, not committed):
`q21_ces_sweep.py` (pool projection and the 96-cell scorer), `q21_wal.py` (feeds the
projection into the scratch waterfall `replicate.py` written when the spec was drafted, and
scores every WAL cell), `q21_db.py` (Declining Balances round-match). None imports from
`src/crt`.

- Rep-lines: Appendix C, 31 rows, `Decimal` (precision 28 for the sweep, 40 for the
  confirmation; the two agree to the printed digit on every cell), cent rounding of every
  rep-line flow (R1), level payment on the remaining term recomputed monthly from the balance
  the payment is computed on (Modeling Assumption (c)).
- Months 1..241 (January 2026 .. January 2046); Payment Date 1 ← months 1–2 (A4), Payment
  Date n ← month n + 1. "To Scheduled Maturity Date" cumulates months 1..241. "To Early
  Redemption Date" cumulates through the earlier of Payment Date 60 and the first Payment Date
  whose end-of-Reporting-Period pool UPB ≤ 10 % of the Cut-off Date Balance (A11, Modeling
  Assumption (m)), i.e. months 1..n + 1.
- Baseline check: with the spec as written (A1–A3, `O1` below) the scratch projection
  reproduces the engine's Credit Event Sensitivity numbers cell for cell (86/96, worst
  −0.108 pp at 2.50 %/0 %) and, through the scratch waterfall, the engine's twelve failing WAL
  cells to four decimals (A-1 5.4821, M-1 13.7275, …, M-2B −0.0836). The replication is
  therefore a faithful independent instrument, and every difference below is attributable to
  the convention being varied.

### 2.1 Variables enumerated

| # | variable | values |
|---|---|---|
| 1 | annual → monthly conversion, separately for CER and CPR | `1 − (1 − x)^(1/12)` (BMA); `x / 12` |
| 2, 3, 4, 6 | within-month sequence: the balance each rate applies to, sequential vs simultaneous, whether removed loans pay the month's scheduled principal, and whether the Credit Event UPB is the balance before or after that scheduled principal | the 13 orderings `O1`–`O13` in §2.2 — every arrangement of {scheduled principal, credit events, prepayments} in which each rate applies to the beginning balance or to the beginning balance net of what precedes it |
| 5 | first month with credit events | month 1 (January 2026); month 2 (February); month 3 (after the Closing Date) |
| — | horizon of the scheduled basis | month 240, 241 (spec), 242 |
| — | clean-up test basis (early basis only) | UPB at the end of the Reporting Period (A11); UPB at the end of the previous Reporting Period |

### 2.2 The orderings

`B` = beginning-of-month balance of the rep-line, `d` = monthly credit-event rate, `p` = SMM,
`s(X)` = scheduled principal for the month computed on balance `X` (level payment on the
remaining term less 30/360 interest, both cent-rounded), `CE` = Credit Event UPB removed,
`pre` = prepayment in full. End balance is always `B − s − CE − pre`.

| id | sequence | meaning | previously tried? |
|---|---|---|---|
| `O1_sched>CE>pre` | `s = s(B)`; `CE = (B−s)·d`; `pre = (B−s−CE)·p` | **A2/A3 as specified and as built** | engine |
| `O2_sched>pre>CE` | `s = s(B)`; `pre = (B−s)·p`; `CE = (B−s−pre)·d` | prepayments before credit events | fintech-dev H7c |
| `O3_sched>{CE,pre}` | `s = s(B)`; `CE = (B−s)·d`; `pre = (B−s)·p` | simultaneous on the balance net of scheduled principal | no |
| `O4_CE>sched>pre` | `CE = B·d`; `s = s(B−CE)`; `pre = (B−CE−s)·p` | credit-event loans pay no scheduled principal; then amortize; then prepay ("Intex-style") | fintech-dev H7b |
| `O5_pre>CE>sched` | `pre = B·p`; `CE = (B−pre)·d`; `s = s(B−pre−CE)` | | no |
| `O6_{CE,pre}>sched` | `CE = B·d`; `pre = B·p`; `s = s(B−CE−pre)` | **credit events and prepayments in full both on the beginning balance, simultaneously; only survivors pay scheduled principal** | no |
| `O7_{sched,CE,pre}onB` | `s = s(B)`; `CE = B·d`; `pre = B·p` | all three on the beginning balance (removed loans also pay scheduled principal) | fintech-dev H7e |
| `O8_sched,pre>CE_onB` | `s = s(B)`; `pre = B·p`; `CE = (B−pre)·d` | | fintech-dev H7f |
| `O9_sched,CE>pre_onB` | `s = s(B)`; `CE = B·d`; `pre = (B−CE)·p` | | no |
| `O10_CE>{sched,pre}` | `CE = B·d`; `s = s(B−CE)`; `pre = (B−CE)·p` | | no |
| `O11_CE>pre>sched` | `CE = B·d`; `pre = (B−CE)·p`; `s = s(B−CE−pre)` | sequential version of O6 | no |
| `O12_pre>sched>CE` | `pre = B·p`; `s = s(B−pre)`; `CE = (B−pre−s)·d` | | no |
| `O13_pre>{sched,CE}` | `pre = B·p`; `s = s(B−pre)`; `CE = (B−pre)·d` | | no |

At 0 % CPR the prepayment terms vanish, so the 0 % CPR column separates the orderings into
three classes — credit events on `B − s` (`O1`, `O2`, `O3`, `O12`); on `B` with only the
survivors amortizing (`O4`, `O5`, `O6`, `O10`, `O11`); on `B` with the removed loans also
paying scheduled principal (`O7`, `O8`, `O9`, `O13`) — and is used first.

## 3. Stage A — the 0 % CPR column (16 cells), one variable at a time from the spec baseline

Signed differences (model − PPM, pp) are for the eight "To Scheduled Maturity Date" cells at
CER 0.00 / 0.25 / 0.50 / 1.00 / 1.50 / 2.50 / 3.00 / 5.00 %.

| trial | 0 % CPR round-match | worst (pp) | sched-basis diffs |
|---|---|---|---|
| baseline `O1` (A1–A3 as built) | 13/16 | 0.108 | +0.00 +0.01 −0.05 −0.04 −0.03 −0.11 −0.11 −0.10 |
| CER conversion `x/12` | 6/16 | 0.884 | +0.00 +0.01 −0.06 −0.10 −0.16 −0.41 −0.51 −0.88 |
| `O2`, `O3`, `O12` (CE on `B − s`) | 13/16 | 0.108 | identical to baseline (prepayment terms vanish) |
| `O4`, `O5`, `O6`, `O10`, `O11` (CE on `B`, survivors amortize) | **16/16** | 0.039 | +0.00 +0.02 −0.03 −0.01 +0.02 −0.03 −0.02 +0.02 |
| `O7`, `O8`, `O9`, `O13` (CE on `B`, removed loans also amortize) | 16/16 | 0.047 | +0.00 +0.02 −0.03 −0.01 +0.01 −0.05 −0.04 −0.02 |
| credit events start month 2 | 5/16 | 0.381 | +0.00 −0.01 −0.08 −0.11 −0.13 −0.25 −0.26 −0.29 |
| credit events start month 3 | 5/16 | 0.714 | +0.00 −0.03 −0.12 −0.18 −0.23 −0.39 −0.42 −0.48 |
| scheduled horizon month 240 | 10/16 | 0.181 | +0.00 +0.00 −0.07 −0.08 −0.08 −0.18 −0.18 −0.18 |
| scheduled horizon month 242 | 16/16 | 0.048 | +0.00 +0.02 −0.03 −0.01 +0.02 −0.04 −0.04 −0.01 |

Reading: the 0 % CPR column rules out the `x/12` conversion, any later start month, and a
shorter horizon, and shows that the Credit Event UPB is the balance **before** the month's
scheduled principal, with the survivors — not the credit-event loans — making the scheduled
payment (`O4`/`O5`/`O6`/`O10`/`O11` are indistinguishable here; the variants where credit-event
loans also amortize are slightly worse but still pass). Horizon 242 also passes this column but
is not a date the PPM defines (it would be a February 2046 collection month feeding a Payment
Date that does not exist) and it fails elsewhere (§5); it is recorded, not adopted.

## 4. Stage B — full factorial over all 96 cells

13 orderings × 2 CER conversions × 2 CPR conversions × 2 start months = 104 combinations,
each scored on all 96 cells. The complete table is in Appendix A. Ranked summary of every
combination with the BMA conversions and credit events from January 2026 (every other
conversion/start combination is at or below 53/96):

| rank | ordering | round-match | within ±0.25 pp | worst miss (pp) | worst cell |
|---|---|---|---|---|---|
| 1 | **`O6_{CE,pre}>sched`** | **96/96** | 96/96 | 0.050 | sched 1.00 % / 25 % |
| 2 | `O7_{sched,CE,pre}onB` (H7e) | 92/96 | 96/96 | 0.072 | sched 5.00 % / 5 % |
| 3 | `O9_sched,CE>pre_onB` | 89/96 | 96/96 | 0.080 | sched 5.00 % / 25 % |
| 3 | `O10_CE>{sched,pre}` | 89/96 | 96/96 | 0.083 | sched 5.00 % / 25 % |
| 5 | `O4_CE>sched>pre` (H7b) | 86/96 | 96/96 | 0.097 | sched 5.00 % / 25 % |
| 5 | `O11_CE>pre>sched` | 86/96 | 96/96 | 0.097 | sched 5.00 % / 25 % |
| 5 | `O1_sched>CE>pre` (as built) | 86/96 | 96/96 | 0.108 | sched 2.50 % / 0 % |
| 8 | `O3_sched>{CE,pre}` | 85/96 | 96/96 | 0.108 | sched 2.50 % / 0 % |
| 9 | `O5_pre>CE>sched` | 51/96 | 92/96 | 0.321 | sched 5.00 % / 35 % |
| 9 | `O8_sched,pre>CE_onB` (H7f) | 51/96 | 92/96 | 0.332 | sched 5.00 % / 35 % |
| 9 | `O13_pre>{sched,CE}` | 51/96 | 92/96 | 0.323 | sched 5.00 % / 35 % |
| 12 | `O2_sched>pre>CE` (H7c) | 47/96 | 91/96 | 0.333 | sched 5.00 % / 35 % |
| 12 | `O12_pre>sched>CE` | 47/96 | 91/96 | 0.333 | sched 5.00 % / 35 % |

The 25 %/35 % CPR columns discriminate what the 0 % column could not: the credit-event rate and
the SMM must apply to the **same** balance, the beginning balance, with neither net of the
other (`O6`). Making prepayments net of credit events (`O11`, `O4`) leaves the 25 % CPR cells
0.08–0.10 pp long; making credit events net of prepayments (`O5`, `O13`, `O2`, `O12`) leaves
the 35 % CPR cells 0.3 pp short; letting removed loans also pay scheduled principal (`O7`,
`O9`) overshoots at 5 % CER.

## 5. The neighbourhood of `O6`, one variable at a time

| trial | round-match | within ±0.25 pp | worst (pp) | worst cell |
|---|---|---|---|---|
| **`O6` as found** (BMA, BMA, start month 1, horizon 241, clean-up on end-of-period UPB) | **96/96** | 96/96 | 0.050 | sched 1.00 % / 25 % |
| horizon month 240 | 90/96 | 96/96 | 0.103 | sched 2.50 % / 0 % |
| horizon month 242 | 92/96 | 96/96 | 0.097 | sched 5.00 % / 0 % |
| clean-up tested on the previous Reporting Period's UPB | 95/96 | 96/96 | 0.070 | early 2.50 % / 35 % |
| credit events start month 2 | 31/96 | 83/96 | 0.397 | early 5.00 % / 25 % |
| CER conversion `x/12` | 50/96 | 84/96 | 0.774 | sched 5.00 % / 0 % |
| CPR conversion `x/12` | 38/96 | 66/96 | 1.852 | sched 5.00 % / 35 % |
| `Decimal` precision 40 instead of 28 | 96/96 | 96/96 | 0.050 | no cell moves at the printed digit |

Every neighbour is worse; the found convention is a strict local optimum on every axis, and
the horizon, start month, conversion and clean-up basis are each confirmed independently
(the early basis at 35 % CPR is where A11 bites: the clean-up occurs at Payment Date 58 for
2.50 %, 58 for 3.00 % and 55 for 5.00 % CER (collection months 59/59/56); testing the previous period's UPB moves those
by a month and breaks the 2.50 %/35 % cell).

## 6. Per-cell result under the new reading (all 96 cells)

Appendix B lists every cell with the as-built and new-reading model values. Summary: 96/96
round-match, 96/96 within ±0.25 pp, mean |diff| 0.027 pp over the 84 CER > 0 cells, worst 0.0499 pp. Six cells sit
within 0.003 pp of a rounding boundary (1.00 %/25 % sched at 3.2499 → 3.2 is the tightest at
0.0001 pp). That is expected when 96 numbers printed to 0.1 are matched — roughly one cell in
twenty will land within 0.0025 of a boundary — and the signed residuals are centred (46
positive, 38 negative among the 84 CER > 0 cells), so there is no bias to explain. Had the
underlying convention been wrong, the WAL check in §7 would not have collapsed as it did.

## 7. Confirmation through the structure — WAL, Declining Balances

The same projection was fed to the scratch waterfall (`replicate.py`, unchanged since
2026-09-03) and every Note/basis/CER/CPR cell of `wal_tables.csv` scored against ±0.02 (BRIEF
§7), with the 30/360 clock from the Closing Date (A9) and write-downs in the numerator (A10).

| family | as built (`O1`) | new reading (`O6`) |
|---|---|---|
| WAL, CER > 0, RM 0 (336 cells) within ±0.02 | 324/336, worst +0.084 (M-2B sched 1.00 %/15 %) | **336/336, worst +0.0050** (M-1 sched 3.00 %/10 %) |
| … within ±0.01 | 295/336 | **336/336** |
| … exact to the printed two decimals | — | 335/336 |
| WAL, CER 0, RM 0 (48 cells) within ±0.02 | 48/48, worst −0.0048 | 48/48, worst −0.0048 (identical) |
| Declining Balances, CER 0, four Notes (390 cells), whole-percent round-match | 390/390 | 390/390 (identical) |
| Credit Event Sensitivity (96 cells) round-match | 86/96, worst 0.108 pp | **96/96, worst 0.050 pp** |

The twelve cells Q21 lists:

| Note | basis | CER | CPR | PPM | as built | diff | new reading | diff |
|---|---|---|---|---|---|---|---|---|
| A-1 | sched | 5.00 % | 25 | 5.46 | 5.4821 | +0.0221 | 5.4640 | +0.0040 |
| M-1 | sched | 1.00 % | 0 | 13.70 | 13.7275 | +0.0275 | 13.6965 | −0.0035 |
| M-1 | sched | 1.50 % | 5 | 11.78 | 11.8025 | +0.0225 | 11.7754 | −0.0046 |
| M-2A | sched | 0.50 % | 5 | 16.00 | 15.9707 | −0.0293 | 15.9963 | −0.0037 |
| M-2A | sched | 1.00 % | 5 | 14.12 | 14.1612 | +0.0412 | 14.1242 | +0.0042 |
| M-2A | sched | 1.00 % | 15 | 13.39 | 13.3101 | −0.0799 | 13.3908 | +0.0008 |
| M-2A | sched | 1.50 % | 10 | 10.86 | 10.8803 | +0.0203 | 10.8601 | +0.0001 |
| M-2A | sched | 3.00 % | 25 | 6.17 | 6.1939 | +0.0239 | 6.1672 | −0.0028 |
| M-2B | sched | 0.50 % | 0 | 19.83 | 19.8514 | +0.0214 | 19.8264 | −0.0036 |
| M-2B | sched | 0.50 % | 5 | 18.71 | 18.6817 | −0.0283 | 18.7084 | −0.0016 |
| M-2B | sched | 1.00 % | 5 | 12.10 | 12.1247 | +0.0247 | 12.0984 | −0.0016 |
| M-2B | sched | 1.00 % | 15 | 14.46 | 14.3764 | −0.0836 | 14.4577 | −0.0023 |

Full CER > 0 grid by Note and basis under the new reading:

| Note | basis | cells | within ±0.02 | within ±0.01 | exact to the printed 2 dp | max abs diff (years) |
|---|---|---|---|---|---|---|
| A-1 | early | 42 | 42/42 | 42/42 | 42/42 | 0.0050 |
| A-1 | sched | 42 | 42/42 | 42/42 | 42/42 | 0.0046 |
| M-1 | early | 42 | 42/42 | 42/42 | 42/42 | 0.0049 |
| M-1 | sched | 42 | 42/42 | 42/42 | 41/42 | 0.0050 |
| M-2A | early | 42 | 42/42 | 42/42 | 42/42 | 0.0049 |
| M-2A | sched | 42 | 42/42 | 42/42 | 42/42 | 0.0049 |
| M-2B | early | 42 | 42/42 | 42/42 | 42/42 | 0.0044 |
| M-2B | sched | 42 | 42/42 | 42/42 | 42/42 | 0.0047 |
| **all** | | **336** | **336/336** | **336/336** | **335/336** | **0.0050** |

Every one of the 336 CER > 0 WALs is now within half a printed digit of the PPM; the one cell
that is not exact to the printed two decimals (M-1 sched 3.00 %/10 %, model 5.6150 vs 5.61)
sits on the rounding boundary by 0.0050. This is the
same residual profile as the CER 0 grid, which has always tied. Q17's "+0.01 to +0.03, model
longer" pattern is gone: it was this convention.

The CER 0 families are unchanged to the printed digit because at `d = 0` the two sequences
differ only in how the month's principal is split between scheduled and prepaid — the survivor
of `pre = B·p` then amortizes to exactly the balance that `s(B)` followed by
`(B − s)·p` reaches, up to cents (the level payment is linear in the balance). Stated Principal,
the pool UPB and hence every CER 0 test are identical; §8 gives the cents.

## 8. The convention the PPM uses — statement and evidence

**For each rep-line and collection month, starting from the beginning-of-month balance `B`:**

1. `CE = round2(B × MDR)`, `MDR = 1 − (1 − CER)^(1/12)`. The Credit Event UPB is the
   beginning-of-month balance of the loans becoming Credit Event Reference Obligations; they
   make no scheduled payment in the month.
2. `Prepay = round2(B × SMM)`, `SMM = 1 − (1 − CPR)^(1/12)`. Prepayments in full are the
   beginning-of-month balance of the prepaying loans; they make no separate scheduled principal
   payment (a payoff is the whole balance, with 30 days' interest — Modeling Assumption (g)).
3. `B_s = B − CE − Prepay` — the surviving loans.
4. `Pmt = round2(B_s × r / (1 − (1 + r)^(−N)))`, `Int = round2(B_s × r)`,
   `SchedPrin = min(B_s, Pmt − Int)` — the level payment on the remaining term, computed on
   the survivors' balance (Modeling Assumption (c)).
5. `B_end = B_s − SchedPrin`; `N → N − 1`.

Credit events begin in January 2026 with the first collection month (as prepayments do under
Modeling Assumption (g)); Payment Date 1 carries months 1–2 (A4); Payment Date 240 carries
month 241; the early-redemption basis stops at the earlier of Payment Date 60 and the first
Payment Date whose end-of-Reporting-Period UPB ≤ 10 % of the Cut-off Date Balance (A11).

Textual support, for the record (none of it is decisive on its own; the tables are):

- CER definition (PPM p138): "a constant rate of Reference Obligations becoming Credit Event
  Reference Obligations each month relative to the then-outstanding aggregate principal
  balance" — the balance outstanding when the month begins, not a balance net of the month's
  own scheduled principal.
- CPR definition (p137): "the outstanding principal balance of a pool of mortgage loans prepays
  at a specified constant annual rate" — likewise the outstanding balance, and there is no text
  making either rate net of the other.
- Modeling Assumption (g): prepayments in full are received "together with 30 days' interest
  thereon" on the last day of the month — a payoff of the full balance plus a month's interest,
  which is what step 2 produces; a prepaying loan that had first made its scheduled payment
  would owe 30 days' interest on a smaller balance and the PPM would not need the phrase.
- Credit Event UPB (p193): "the UPB thereof as of the end of the Reporting Period" — for a
  loan that has stopped paying, that is its balance at the start of the month in which the
  Credit Event is reported; the spec's earlier reading ("after that month's scheduled
  principal") assumed the loan amortized in the month it defaulted, which the tables reject.

What the diagnosis rules out, each by more than the printing tolerance: the `x/12` conversion
for either rate; credit events on the balance net of scheduled principal (the as-built A2);
prepayments net of credit events (A3 as built, and its mirror); any sequential ordering of the
two removals; credit-event loans paying scheduled principal in the month; a start after
January 2026; a horizon other than month 241.

## 9. Consequences

1. **Spec.** `docs/spec/01-pool.md` §3 restated as the five steps above; §2, §5 and §7 wording
   aligned; §9 worked example recomputed (below). `02-waterfall.md` §12 Payment Date 1 is
   unchanged to the cent (`StatedPrincipal[1] = 437,763,629.88`, `UPB_end[1] =
   22,343,387,921.96`); Payment Date 2 moves by five cents (`StatedPrincipal[2] =
   215,917,777.13`, `UPB_end[2] = 22,127,470,144.83`, `SeniorReduction = 208,306,675.49`, A-H
   share 197,414,437.41, A-H balance after 21,078,800,619.58) and has been updated.
2. **Register.** A2 and A3 revised (still ASSUMED, `confirmed_by_user = N`, "revised 2026-09-07
   per q21 diagnosis"); `docs/assumptions.md` re-rendered. A15's note ("prepayments in full
   carry no additional interest because they occur after the month's scheduled payment") is now
   stale; its formula is not consumed by the v1 tie-out and is left for the manager (see §10).
3. **Engine change** (for fintech-dev; exact wording in `docs/open-questions.md` Q21): in
   `src/crt/pool/rep_line.py::project_rep_line_month`, compute `credit_event` and `prepayment`
   from `balance` before P1, take `survivor = balance − credit_event − prepayment`, and compute
   `scheduled_payment`, `interest` and `sched_principal` on `survivor`. Field names, the
   identity assertion, `rates.py`, `projection.py` and the waterfall are untouched.
4. **Tests to update** (`tests/unit/test_pool.py`): the group-17 intermediates
   (`scheduled_payment`, `scheduled_principal`, `prepayment`), the pool rows for months 1–3 and
   the Payment Date 2 aggregates, per the new §9 numbers; the CPR 0/CER 0 level-pay identity
   test is unaffected. A new hand case at 10 % CPR / 1 % CER is given in §9 for the credit-event
   path, which the current tests exercise only at CER 0.
5. **Other documents referring to the old reading**: `03-tieout.md` §5 item 7 and §6, and
   `04-open-items.md` row 6 / Q17, describe the +0.01 to +0.03 residual as expected; they should
   be marked superseded by this note once the engine re-runs.

New §9 numbers (10 % CPR, 0 % CER, `SMM = 0.00874161095469670576…`):

| | month 1 (Jan 2026) | month 2 (Feb 2026) |
|---|---|---|
| `B` | 5,703,897,138.22 (N 350) | 5,649,018,448.44 (N 349) |
| `CE` | 0.00 | 0.00 |
| `Prepay = round2(B × SMM)` | 49,861,249.71 | 49,381,521.55 |
| `B_s` | 5,654,035,888.51 | 5,599,636,926.89 |
| `Pmt` on `B_s` | 37,683,632.42 | 37,354,216.77 |
| `Int = round2(B_s × r)` | 32,666,192.35 | 32,351,902.35 |
| `SchedPrin` | 5,017,440.07 | 5,002,314.42 |
| `B_end` | 5,649,018,448.44 | 5,594,634,612.47 |

Rep-line 17's contribution to Payment Date 1 Stated Principal is unchanged at
109,262,525.75. Pool totals: month 1 `SchedPrin 20,731,726.12 / Prepay 199,143,963.97 / CE 0 /
UPB 22,561,275,861.75`; month 2 `20,666,043.58 / 197,221,896.21 / 0 / 22,343,387,921.96`;
month 3 `20,600,572.48 / 195,317,204.65 / 0 / 22,127,470,144.83`.

Credit-event hand case, group 17, month 1, 10 % CPR / 1 % CER (`MDR =
0.00083717735912055953…`): `CE = 4,775,173.54`, `Prepay = 49,861,249.71`, `B_s =
5,649,260,714.97`, `Pmt = 37,651,806.33`, `Int = 32,638,603.78`, `SchedPrin = 5,013,202.55`,
`B_end = 5,644,247,512.42`. Pool month 1: `SchedPrin 20,714,216.91 / Prepay 199,143,963.97 /
CE 19,071,864.30 / UPB 22,542,221,506.66`.

## 10. What I am not certain of

- **Pool interest (01-pool.md §7, A15)** is not tied out by any PPM table. Under the new
  order the natural reading is: survivors pay `B_s × r`, prepaying loans pay 30 days' interest
  on their balance (Modeling Assumption (g)), credit-event loans pay nothing in the month. I
  have written §7 that way and left the A15 register row's formula alone; whether credit-event
  loans are assumed to pay a final month's interest matters only for the Excel export and for
  actual-pool runs, and should be settled when interest is first consumed.
- **The 1.00 %/25 % cell** rounds correctly by 0.0001 pp. If the PPM's own model rounded
  rep-line flows differently (or not at all) that cell could print either way; nothing else in
  the grid is sensitive at that level, and the WAL grid does not depend on the printing.
- **The clean-up basis at 35 % CPR** is confirmed only through the three early-basis cells where
  it binds (2.50 %, 3.00 %, 5.00 % CER); A11 as adopted is the reading that ties.
- I did not test conventions that vary by rep-line or by month (none is suggested by the PPM
  text), or partial-month (day-count-weighted) removals; the residuals leave no room for them.

---

## Appendix A — every combination of Stage B (104 rows)

Score on all 96 cells; horizon 241, clean-up on end-of-period UPB throughout.

| # | order (within-month sequence) | CER conv. | CPR conv. | CE start month | round-match | within ±0.25 pp | worst miss (pp) | worst cell |
|---|---|---|---|---|---|---|---|---|
| 1 | `O1_sched>CE>pre` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 86/96 | 96/96 | 0.108 | sched CER 2.50% CPR 0 |
| 2 | `O1_sched>CE>pre` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 29/96 | 81/96 | 0.395 | early CER 5.00% CPR 10 |
| 3 | `O1_sched>CE>pre` | 1−(1−x)^(1/12) | x/12 | 1 | 35/96 | 67/96 | 1.882 | sched CER 5.00% CPR 35 |
| 4 | `O1_sched>CE>pre` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 70/96 | 1.508 | sched CER 5.00% CPR 35 |
| 5 | `O1_sched>CE>pre` | x/12 | 1−(1−x)^(1/12) | 1 | 47/96 | 83/96 | 0.884 | sched CER 5.00% CPR 0 |
| 6 | `O1_sched>CE>pre` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 60/96 | 1.076 | sched CER 5.00% CPR 0 |
| 7 | `O1_sched>CE>pre` | x/12 | x/12 | 1 | 33/96 | 63/96 | 1.630 | sched CER 5.00% CPR 35 |
| 8 | `O1_sched>CE>pre` | x/12 | x/12 | 2 | 27/96 | 64/96 | 1.262 | sched CER 5.00% CPR 35 |
| 9 | `O2_sched>pre>CE` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 47/96 | 91/96 | 0.333 | sched CER 5.00% CPR 35 |
| 10 | `O2_sched>pre>CE` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 23/96 | 63/96 | 0.702 | sched CER 5.00% CPR 35 |
| 11 | `O2_sched>pre>CE` | 1−(1−x)^(1/12) | x/12 | 1 | 42/96 | 71/96 | 1.521 | sched CER 5.00% CPR 35 |
| 12 | `O2_sched>pre>CE` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 76/96 | 1.157 | sched CER 5.00% CPR 35 |
| 13 | `O2_sched>pre>CE` | x/12 | 1−(1−x)^(1/12) | 1 | 33/96 | 68/96 | 0.884 | sched CER 5.00% CPR 0 |
| 14 | `O2_sched>pre>CE` | x/12 | 1−(1−x)^(1/12) | 2 | 23/96 | 54/96 | 1.089 | sched CER 5.00% CPR 5 |
| 15 | `O2_sched>pre>CE` | x/12 | x/12 | 1 | 33/96 | 71/96 | 1.276 | sched CER 5.00% CPR 35 |
| 16 | `O2_sched>pre>CE` | x/12 | x/12 | 2 | 36/96 | 65/96 | 1.076 | sched CER 5.00% CPR 0 |
| 17 | `O3_sched>{CE,pre}` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 85/96 | 96/96 | 0.108 | sched CER 2.50% CPR 0 |
| 18 | `O3_sched>{CE,pre}` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 28/96 | 81/96 | 0.412 | early CER 5.00% CPR 10 |
| 19 | `O3_sched>{CE,pre}` | 1−(1−x)^(1/12) | x/12 | 1 | 36/96 | 67/96 | 1.838 | sched CER 5.00% CPR 35 |
| 20 | `O3_sched>{CE,pre}` | 1−(1−x)^(1/12) | x/12 | 2 | 31/96 | 70/96 | 1.465 | sched CER 5.00% CPR 35 |
| 21 | `O3_sched>{CE,pre}` | x/12 | 1−(1−x)^(1/12) | 1 | 47/96 | 82/96 | 0.884 | sched CER 5.00% CPR 0 |
| 22 | `O3_sched>{CE,pre}` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 60/96 | 1.076 | sched CER 5.00% CPR 0 |
| 23 | `O3_sched>{CE,pre}` | x/12 | x/12 | 1 | 34/96 | 65/96 | 1.587 | sched CER 5.00% CPR 35 |
| 24 | `O3_sched>{CE,pre}` | x/12 | x/12 | 2 | 26/96 | 64/96 | 1.221 | sched CER 5.00% CPR 35 |
| 25 | `O4_CE>sched>pre` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 86/96 | 96/96 | 0.097 | sched CER 5.00% CPR 25 |
| 26 | `O4_CE>sched>pre` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 34/96 | 86/96 | 0.376 | early CER 5.00% CPR 10 |
| 27 | `O4_CE>sched>pre` | 1−(1−x)^(1/12) | x/12 | 1 | 38/96 | 64/96 | 1.897 | sched CER 5.00% CPR 35 |
| 28 | `O4_CE>sched>pre` | 1−(1−x)^(1/12) | x/12 | 2 | 32/96 | 70/96 | 1.521 | sched CER 5.00% CPR 35 |
| 29 | `O4_CE>sched>pre` | x/12 | 1−(1−x)^(1/12) | 1 | 53/96 | 85/96 | 0.774 | sched CER 5.00% CPR 0 |
| 30 | `O4_CE>sched>pre` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 62/96 | 0.965 | sched CER 5.00% CPR 0 |
| 31 | `O4_CE>sched>pre` | x/12 | x/12 | 1 | 34/96 | 63/96 | 1.643 | sched CER 5.00% CPR 35 |
| 32 | `O4_CE>sched>pre` | x/12 | x/12 | 2 | 27/96 | 67/96 | 1.276 | sched CER 5.00% CPR 35 |
| 33 | `O5_pre>CE>sched` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 51/96 | 92/96 | 0.321 | sched CER 5.00% CPR 35 |
| 34 | `O5_pre>CE>sched` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 24/96 | 67/96 | 0.691 | early CER 5.00% CPR 35 |
| 35 | `O5_pre>CE>sched` | 1−(1−x)^(1/12) | x/12 | 1 | 44/96 | 71/96 | 1.535 | sched CER 5.00% CPR 35 |
| 36 | `O5_pre>CE>sched` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 77/96 | 1.171 | sched CER 5.00% CPR 35 |
| 37 | `O5_pre>CE>sched` | x/12 | 1−(1−x)^(1/12) | 1 | 36/96 | 70/96 | 0.774 | sched CER 5.00% CPR 0 |
| 38 | `O5_pre>CE>sched` | x/12 | 1−(1−x)^(1/12) | 2 | 23/96 | 56/96 | 1.023 | sched CER 5.00% CPR 5 |
| 39 | `O5_pre>CE>sched` | x/12 | x/12 | 1 | 33/96 | 70/96 | 1.289 | sched CER 5.00% CPR 35 |
| 40 | `O5_pre>CE>sched` | x/12 | x/12 | 2 | 37/96 | 67/96 | 0.965 | sched CER 5.00% CPR 0 |
| 41 | `O6_{CE,pre}>sched` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 96/96 | 96/96 | 0.050 | sched CER 1.00% CPR 25 |
| 42 | `O6_{CE,pre}>sched` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 31/96 | 83/96 | 0.397 | early CER 5.00% CPR 25 |
| 43 | `O6_{CE,pre}>sched` | 1−(1−x)^(1/12) | x/12 | 1 | 38/96 | 66/96 | 1.852 | sched CER 5.00% CPR 35 |
| 44 | `O6_{CE,pre}>sched` | 1−(1−x)^(1/12) | x/12 | 2 | 32/96 | 72/96 | 1.478 | sched CER 5.00% CPR 35 |
| 45 | `O6_{CE,pre}>sched` | x/12 | 1−(1−x)^(1/12) | 1 | 50/96 | 84/96 | 0.774 | sched CER 5.00% CPR 0 |
| 46 | `O6_{CE,pre}>sched` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 61/96 | 0.965 | sched CER 5.00% CPR 0 |
| 47 | `O6_{CE,pre}>sched` | x/12 | x/12 | 1 | 34/96 | 64/96 | 1.601 | sched CER 5.00% CPR 35 |
| 48 | `O6_{CE,pre}>sched` | x/12 | x/12 | 2 | 26/96 | 67/96 | 1.235 | sched CER 5.00% CPR 35 |
| 49 | `O7_{sched,CE,pre}onB` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 92/96 | 96/96 | 0.072 | sched CER 5.00% CPR 5 |
| 50 | `O7_{sched,CE,pre}onB` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 29/96 | 83/96 | 0.404 | early CER 5.00% CPR 25 |
| 51 | `O7_{sched,CE,pre}onB` | 1−(1−x)^(1/12) | x/12 | 1 | 38/96 | 67/96 | 1.839 | sched CER 5.00% CPR 35 |
| 52 | `O7_{sched,CE,pre}onB` | 1−(1−x)^(1/12) | x/12 | 2 | 34/96 | 72/96 | 1.465 | sched CER 5.00% CPR 35 |
| 53 | `O7_{sched,CE,pre}onB` | x/12 | 1−(1−x)^(1/12) | 1 | 50/96 | 82/96 | 0.807 | sched CER 5.00% CPR 0 |
| 54 | `O7_{sched,CE,pre}onB` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 61/96 | 0.998 | sched CER 5.00% CPR 0 |
| 55 | `O7_{sched,CE,pre}onB` | x/12 | x/12 | 1 | 33/96 | 65/96 | 1.588 | sched CER 5.00% CPR 35 |
| 56 | `O7_{sched,CE,pre}onB` | x/12 | x/12 | 2 | 27/96 | 66/96 | 1.221 | sched CER 5.00% CPR 35 |
| 57 | `O8_sched,pre>CE_onB` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 51/96 | 92/96 | 0.332 | sched CER 5.00% CPR 35 |
| 58 | `O8_sched,pre>CE_onB` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 24/96 | 66/96 | 0.702 | sched CER 5.00% CPR 35 |
| 59 | `O8_sched,pre>CE_onB` | 1−(1−x)^(1/12) | x/12 | 1 | 44/96 | 71/96 | 1.522 | sched CER 5.00% CPR 35 |
| 60 | `O8_sched,pre>CE_onB` | 1−(1−x)^(1/12) | x/12 | 2 | 34/96 | 78/96 | 1.158 | sched CER 5.00% CPR 35 |
| 61 | `O8_sched,pre>CE_onB` | x/12 | 1−(1−x)^(1/12) | 1 | 35/96 | 68/96 | 0.807 | sched CER 5.00% CPR 0 |
| 62 | `O8_sched,pre>CE_onB` | x/12 | 1−(1−x)^(1/12) | 2 | 23/96 | 55/96 | 1.059 | sched CER 5.00% CPR 5 |
| 63 | `O8_sched,pre>CE_onB` | x/12 | x/12 | 1 | 34/96 | 70/96 | 1.276 | sched CER 5.00% CPR 35 |
| 64 | `O8_sched,pre>CE_onB` | x/12 | x/12 | 2 | 36/96 | 66/96 | 0.998 | sched CER 5.00% CPR 0 |
| 65 | `O9_sched,CE>pre_onB` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 89/96 | 96/96 | 0.080 | sched CER 5.00% CPR 25 |
| 66 | `O9_sched,CE>pre_onB` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 30/96 | 84/96 | 0.383 | early CER 5.00% CPR 10 |
| 67 | `O9_sched,CE>pre_onB` | 1−(1−x)^(1/12) | x/12 | 1 | 38/96 | 66/96 | 1.883 | sched CER 5.00% CPR 35 |
| 68 | `O9_sched,CE>pre_onB` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 71/96 | 1.508 | sched CER 5.00% CPR 35 |
| 69 | `O9_sched,CE>pre_onB` | x/12 | 1−(1−x)^(1/12) | 1 | 50/96 | 84/96 | 0.807 | sched CER 5.00% CPR 0 |
| 70 | `O9_sched,CE>pre_onB` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 61/96 | 0.998 | sched CER 5.00% CPR 0 |
| 71 | `O9_sched,CE>pre_onB` | x/12 | x/12 | 1 | 34/96 | 63/96 | 1.630 | sched CER 5.00% CPR 35 |
| 72 | `O9_sched,CE>pre_onB` | x/12 | x/12 | 2 | 28/96 | 67/96 | 1.263 | sched CER 5.00% CPR 35 |
| 73 | `O10_CE>{sched,pre}` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 89/96 | 96/96 | 0.083 | sched CER 5.00% CPR 25 |
| 74 | `O10_CE>{sched,pre}` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 30/96 | 85/96 | 0.381 | early CER 5.00% CPR 10 |
| 75 | `O10_CE>{sched,pre}` | 1−(1−x)^(1/12) | x/12 | 1 | 38/96 | 65/96 | 1.885 | sched CER 5.00% CPR 35 |
| 76 | `O10_CE>{sched,pre}` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 71/96 | 1.510 | sched CER 5.00% CPR 35 |
| 77 | `O10_CE>{sched,pre}` | x/12 | 1−(1−x)^(1/12) | 1 | 50/96 | 85/96 | 0.774 | sched CER 5.00% CPR 0 |
| 78 | `O10_CE>{sched,pre}` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 61/96 | 0.965 | sched CER 5.00% CPR 0 |
| 79 | `O10_CE>{sched,pre}` | x/12 | x/12 | 1 | 34/96 | 63/96 | 1.632 | sched CER 5.00% CPR 35 |
| 80 | `O10_CE>{sched,pre}` | x/12 | x/12 | 2 | 28/96 | 67/96 | 1.264 | sched CER 5.00% CPR 35 |
| 81 | `O11_CE>pre>sched` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 86/96 | 96/96 | 0.097 | sched CER 5.00% CPR 25 |
| 82 | `O11_CE>pre>sched` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 34/96 | 86/96 | 0.376 | early CER 5.00% CPR 10 |
| 83 | `O11_CE>pre>sched` | 1−(1−x)^(1/12) | x/12 | 1 | 38/96 | 64/96 | 1.897 | sched CER 5.00% CPR 35 |
| 84 | `O11_CE>pre>sched` | 1−(1−x)^(1/12) | x/12 | 2 | 32/96 | 70/96 | 1.521 | sched CER 5.00% CPR 35 |
| 85 | `O11_CE>pre>sched` | x/12 | 1−(1−x)^(1/12) | 1 | 53/96 | 85/96 | 0.774 | sched CER 5.00% CPR 0 |
| 86 | `O11_CE>pre>sched` | x/12 | 1−(1−x)^(1/12) | 2 | 28/96 | 62/96 | 0.965 | sched CER 5.00% CPR 0 |
| 87 | `O11_CE>pre>sched` | x/12 | x/12 | 1 | 34/96 | 63/96 | 1.643 | sched CER 5.00% CPR 35 |
| 88 | `O11_CE>pre>sched` | x/12 | x/12 | 2 | 27/96 | 67/96 | 1.276 | sched CER 5.00% CPR 35 |
| 89 | `O12_pre>sched>CE` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 47/96 | 91/96 | 0.333 | sched CER 5.00% CPR 35 |
| 90 | `O12_pre>sched>CE` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 23/96 | 63/96 | 0.702 | sched CER 5.00% CPR 35 |
| 91 | `O12_pre>sched>CE` | 1−(1−x)^(1/12) | x/12 | 1 | 42/96 | 71/96 | 1.521 | sched CER 5.00% CPR 35 |
| 92 | `O12_pre>sched>CE` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 76/96 | 1.157 | sched CER 5.00% CPR 35 |
| 93 | `O12_pre>sched>CE` | x/12 | 1−(1−x)^(1/12) | 1 | 33/96 | 68/96 | 0.884 | sched CER 5.00% CPR 0 |
| 94 | `O12_pre>sched>CE` | x/12 | 1−(1−x)^(1/12) | 2 | 23/96 | 54/96 | 1.089 | sched CER 5.00% CPR 5 |
| 95 | `O12_pre>sched>CE` | x/12 | x/12 | 1 | 33/96 | 71/96 | 1.276 | sched CER 5.00% CPR 35 |
| 96 | `O12_pre>sched>CE` | x/12 | x/12 | 2 | 36/96 | 65/96 | 1.076 | sched CER 5.00% CPR 0 |
| 97 | `O13_pre>{sched,CE}` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 1 | 51/96 | 92/96 | 0.323 | sched CER 5.00% CPR 35 |
| 98 | `O13_pre>{sched,CE}` | 1−(1−x)^(1/12) | 1−(1−x)^(1/12) | 2 | 24/96 | 67/96 | 0.692 | sched CER 5.00% CPR 35 |
| 99 | `O13_pre>{sched,CE}` | 1−(1−x)^(1/12) | x/12 | 1 | 44/96 | 71/96 | 1.533 | sched CER 5.00% CPR 35 |
| 100 | `O13_pre>{sched,CE}` | 1−(1−x)^(1/12) | x/12 | 2 | 33/96 | 78/96 | 1.169 | sched CER 5.00% CPR 35 |
| 101 | `O13_pre>{sched,CE}` | x/12 | 1−(1−x)^(1/12) | 1 | 36/96 | 70/96 | 0.807 | sched CER 5.00% CPR 0 |
| 102 | `O13_pre>{sched,CE}` | x/12 | 1−(1−x)^(1/12) | 2 | 23/96 | 56/96 | 1.040 | sched CER 5.00% CPR 5 |
| 103 | `O13_pre>{sched,CE}` | x/12 | x/12 | 1 | 34/96 | 70/96 | 1.288 | sched CER 5.00% CPR 35 |
| 104 | `O13_pre>{sched,CE}` | x/12 | x/12 | 2 | 37/96 | 67/96 | 0.998 | sched CER 5.00% CPR 0 |

## Appendix B — every Credit Event Sensitivity cell, as built vs the new reading

| basis | CER | CPR | PPM % | A2/A3 as built: model % | diff | new reading: model % | diff | round-match |
|---|---|---|---|---|---|---|---|---|
| sched | 0.00% | 0 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| sched | 0.00% | 5 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| sched | 0.00% | 10 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| sched | 0.00% | 15 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| sched | 0.00% | 25 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| sched | 0.00% | 35 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| sched | 0.25% | 0 | 4.0 | 4.011 | +0.011 | 4.021 | +0.021 | pass |
| sched | 0.25% | 5 | 2.6 | 2.635 | +0.035 | 2.640 | +0.040 | pass |
| sched | 0.25% | 10 | 1.8 | 1.835 | +0.035 | 1.838 | +0.038 | pass |
| sched | 0.25% | 15 | 1.4 | 1.349 | -0.051 FAIL | 1.351 | -0.049 | pass |
| sched | 0.25% | 25 | 0.8 | 0.829 | +0.029 | 0.829 | +0.029 | pass |
| sched | 0.25% | 35 | 0.6 | 0.570 | -0.030 | 0.571 | -0.029 | pass |
| sched | 0.50% | 0 | 7.9 | 7.853 | -0.047 | 7.872 | -0.028 | pass |
| sched | 0.50% | 5 | 5.2 | 5.179 | -0.021 | 5.189 | -0.011 | pass |
| sched | 0.50% | 10 | 3.6 | 3.620 | +0.020 | 3.625 | +0.025 | pass |
| sched | 0.50% | 15 | 2.7 | 2.669 | -0.031 | 2.672 | -0.028 | pass |
| sched | 0.50% | 25 | 1.6 | 1.646 | +0.046 | 1.647 | +0.047 | pass |
| sched | 0.50% | 35 | 1.1 | 1.135 | +0.035 | 1.136 | +0.036 | pass |
| sched | 1.00% | 0 | 15.1 | 15.059 | -0.041 | 15.093 | -0.007 | pass |
| sched | 1.00% | 5 | 10.0 | 10.009 | +0.009 | 10.025 | +0.025 | pass |
| sched | 1.00% | 10 | 7.1 | 7.044 | -0.056 FAIL | 7.052 | -0.048 | pass |
| sched | 1.00% | 15 | 5.2 | 5.224 | +0.024 | 5.228 | +0.028 | pass |
| sched | 1.00% | 25 | 3.2 | 3.248 | +0.048 | 3.250 | +0.050 | pass |
| sched | 1.00% | 35 | 2.3 | 2.251 | -0.049 | 2.252 | -0.048 | pass |
| sched | 1.50% | 0 | 21.7 | 21.668 | -0.032 | 21.717 | +0.017 | pass |
| sched | 1.50% | 5 | 14.5 | 14.514 | +0.014 | 14.535 | +0.035 | pass |
| sched | 1.50% | 10 | 10.3 | 10.286 | -0.014 | 10.295 | -0.005 | pass |
| sched | 1.50% | 15 | 7.7 | 7.671 | -0.029 | 7.675 | -0.025 | pass |
| sched | 1.50% | 25 | 4.8 | 4.809 | +0.009 | 4.809 | +0.009 | pass |
| sched | 1.50% | 35 | 3.3 | 3.348 | +0.048 | 3.348 | +0.048 | pass |
| sched | 2.50% | 0 | 33.4 | 33.292 | -0.108 FAIL | 33.365 | -0.035 | pass |
| sched | 2.50% | 5 | 22.7 | 22.643 | -0.057 FAIL | 22.669 | -0.031 | pass |
| sched | 2.50% | 10 | 16.3 | 16.265 | -0.035 | 16.272 | -0.028 | pass |
| sched | 2.50% | 15 | 12.3 | 12.268 | -0.032 | 12.267 | -0.033 | pass |
| sched | 2.50% | 25 | 7.8 | 7.810 | +0.010 | 7.805 | +0.005 | pass |
| sched | 2.50% | 35 | 5.5 | 5.488 | -0.012 | 5.484 | -0.016 | pass |
| sched | 3.00% | 0 | 38.5 | 38.392 | -0.108 FAIL | 38.475 | -0.025 | pass |
| sched | 3.00% | 5 | 26.3 | 26.310 | +0.010 | 26.336 | +0.036 | pass |
| sched | 3.00% | 10 | 19.0 | 19.025 | +0.025 | 19.028 | +0.028 | pass |
| sched | 3.00% | 15 | 14.4 | 14.427 | +0.027 | 14.421 | +0.021 | pass |
| sched | 3.00% | 25 | 9.2 | 9.253 | +0.053 FAIL | 9.245 | +0.045 | pass |
| sched | 3.00% | 35 | 6.5 | 6.532 | +0.032 | 6.524 | +0.024 | pass |
| sched | 5.00% | 0 | 55.0 | 54.905 | -0.095 FAIL | 55.016 | +0.016 | pass |
| sched | 5.00% | 5 | 38.8 | 38.749 | -0.051 FAIL | 38.765 | -0.035 | pass |
| sched | 5.00% | 10 | 28.7 | 28.739 | +0.039 | 28.718 | +0.018 | pass |
| sched | 5.00% | 15 | 22.2 | 22.246 | +0.046 | 22.213 | +0.013 | pass |
| sched | 5.00% | 25 | 14.6 | 14.679 | +0.079 FAIL | 14.647 | +0.047 | pass |
| sched | 5.00% | 35 | 10.5 | 10.539 | +0.039 | 10.512 | +0.012 | pass |
| early | 0.00% | 0 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| early | 0.00% | 5 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| early | 0.00% | 10 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| early | 0.00% | 15 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| early | 0.00% | 25 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| early | 0.00% | 35 | 0.0 | 0.000 | +0.000 | 0.000 | +0.000 | pass |
| early | 0.25% | 0 | 1.2 | 1.224 | +0.024 | 1.225 | +0.025 | pass |
| early | 0.25% | 5 | 1.1 | 1.082 | -0.018 | 1.083 | -0.017 | pass |
| early | 0.25% | 10 | 1.0 | 0.955 | -0.045 | 0.956 | -0.044 | pass |
| early | 0.25% | 15 | 0.8 | 0.843 | +0.043 | 0.844 | +0.044 | pass |
| early | 0.25% | 25 | 0.7 | 0.657 | -0.043 | 0.658 | -0.042 | pass |
| early | 0.25% | 35 | 0.5 | 0.512 | +0.012 | 0.513 | +0.013 | pass |
| early | 0.50% | 0 | 2.4 | 2.436 | +0.036 | 2.439 | +0.039 | pass |
| early | 0.50% | 5 | 2.2 | 2.153 | -0.047 | 2.155 | -0.045 | pass |
| early | 0.50% | 10 | 1.9 | 1.902 | +0.002 | 1.904 | +0.004 | pass |
| early | 0.50% | 15 | 1.7 | 1.680 | -0.020 | 1.681 | -0.019 | pass |
| early | 0.50% | 25 | 1.3 | 1.309 | +0.009 | 1.311 | +0.011 | pass |
| early | 0.50% | 35 | 1.0 | 1.022 | +0.022 | 1.022 | +0.022 | pass |
| early | 1.00% | 0 | 4.8 | 4.823 | +0.023 | 4.828 | +0.028 | pass |
| early | 1.00% | 5 | 4.3 | 4.266 | -0.034 | 4.270 | -0.030 | pass |
| early | 1.00% | 10 | 3.8 | 3.770 | -0.030 | 3.774 | -0.026 | pass |
| early | 1.00% | 15 | 3.3 | 3.332 | +0.032 | 3.334 | +0.034 | pass |
| early | 1.00% | 25 | 2.6 | 2.600 | +0.000 | 2.602 | +0.002 | pass |
| early | 1.00% | 35 | 2.0 | 2.031 | +0.031 | 2.032 | +0.032 | pass |
| early | 1.50% | 0 | 7.2 | 7.162 | -0.038 | 7.170 | -0.030 | pass |
| early | 1.50% | 5 | 6.3 | 6.338 | +0.038 | 6.344 | +0.044 | pass |
| early | 1.50% | 10 | 5.6 | 5.605 | +0.005 | 5.610 | +0.010 | pass |
| early | 1.50% | 15 | 5.0 | 4.956 | -0.044 | 4.959 | -0.041 | pass |
| early | 1.50% | 25 | 3.9 | 3.873 | -0.027 | 3.875 | -0.025 | pass |
| early | 1.50% | 35 | 3.0 | 3.030 | +0.030 | 3.030 | +0.030 | pass |
| early | 2.50% | 0 | 11.7 | 11.699 | -0.001 | 11.712 | +0.012 | pass |
| early | 2.50% | 5 | 10.4 | 10.364 | -0.036 | 10.373 | -0.027 | pass |
| early | 2.50% | 10 | 9.2 | 9.177 | -0.023 | 9.183 | -0.017 | pass |
| early | 2.50% | 15 | 8.1 | 8.124 | +0.024 | 8.127 | +0.027 | pass |
| early | 2.50% | 25 | 6.4 | 6.365 | -0.035 | 6.365 | -0.035 | pass |
| early | 2.50% | 35 | 4.9 | 4.951 | +0.051 FAIL | 4.949 | +0.049 | pass |
| early | 3.00% | 0 | 13.9 | 13.898 | -0.002 | 13.914 | +0.014 | pass |
| early | 3.00% | 5 | 12.3 | 12.320 | +0.020 | 12.330 | +0.030 | pass |
| early | 3.00% | 10 | 10.9 | 10.915 | +0.015 | 10.921 | +0.021 | pass |
| early | 3.00% | 15 | 9.7 | 9.668 | -0.032 | 9.671 | -0.029 | pass |
| early | 3.00% | 25 | 7.6 | 7.585 | -0.015 | 7.583 | -0.017 | pass |
| early | 3.00% | 35 | 5.9 | 5.908 | +0.008 | 5.904 | +0.004 | pass |
| early | 5.00% | 0 | 22.3 | 22.252 | -0.048 | 22.277 | -0.023 | pass |
| early | 5.00% | 5 | 19.8 | 19.769 | -0.031 | 19.782 | -0.018 | pass |
| early | 5.00% | 10 | 17.6 | 17.557 | -0.043 | 17.560 | -0.040 | pass |
| early | 5.00% | 15 | 15.6 | 15.590 | -0.010 | 15.584 | -0.016 | pass |
| early | 5.00% | 25 | 12.3 | 12.292 | -0.008 | 12.278 | -0.022 | pass |
| early | 5.00% | 35 | 9.5 | 9.508 | +0.008 | 9.492 | -0.008 | pass |
