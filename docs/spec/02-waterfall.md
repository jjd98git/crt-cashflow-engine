# 02 — Hypothetical structure: Reference Tranches, tests, allocations, Notes

Scope: everything that happens on a Payment Date `n` given the pool aggregates of
`01-pool.md` §6. Every dollar amount is `Decimal` and rounded per `00-overview.md` §3.2
(R2, R3, R4). "Immediately prior to the Payment Date" means the state after Payment Date
`n − 1` was fully processed (at `n = 1`, the initial state of §1).

Notation: `CNA[X]` = Class Notional Amount of Reference Tranche `X`; `round2` = cent,
half-up; `round7` = 7 decimal places as a fraction (= 1/100,000 of a percentage point),
half-up; `pair(X)` = the H tranche paired with Note tranche `X` (A-1/A-1H, M-1/M-1H,
M-2A/M-2AH, M-2B/M-2BH).

---

## 1. The Reference Tranche stack (Table 3)

Initial Class Notional Amounts, `YAML: reference_tranches.<X>.initial_class_notional_amount_usd`:

| tranche | initial Class Notional Amount | register | role |
|---|---|---|---|
| A-H | 21,687,655,280.84 | P24 | retained senior |
| A-1 | 275,900,000.00 | P3 | Note |
| A-1H | 14,559,682.00 | P25 | retained, pro rata with A-1 |
| M-1 | 275,900,000.00 | P4 | Note |
| M-1H | 14,559,682.00 | P26 | retained, pro rata with M-1 |
| M-2A | 37,850,000.00 | P5 | Note |
| M-2AH | 2,017,015.00 | P27 | retained, pro rata with M-2A |
| M-2B | 37,850,000.00 | P6 | Note |
| M-2BH | 2,017,015.00 | P28 | retained, pro rata with M-2B |
| B-1H | 102,515,181.00 | P29 | retained |
| B-2H | 273,373,818.00 | P30 | retained |
| B-3H | 56,953,878.00 | P31 | retained first loss |
| **sum** | **22,781,151,551.84** | = P10 Cut-off Date Balance | verified (`YAML: reference_tranches.sum_equals_cut_off_balance`) |

Load-time assertion: the sum equals the Cut-off Date Balance exactly.

Two derived facts the dev must not get wrong:

- The **senior** tranches for the Senior Percentage are A-H, A-1 **and** A-1H
  (`YAML: principal.senior_percentage`). Their initial sum is 21,978,114,962.84, so the
  initial Senior Percentage is **96.47500 %** and the initial Subordinate Percentage is
  **3.52500 %** — exactly the Minimum Credit Enhancement threshold. (Table 3's 4.800 % is
  the subordination *below A-H*, i.e. including A-1/A-1H; the 3.525 % printed for A-1 is
  the relevant figure. The remark in Q8 and the note on register row P32 that read the
  initial Senior Percentage as 95.200 % are wrong; see `04-open-items.md`.)
- The four Original Notes correspond one-to-one to A-1, M-1, M-2A, M-2B; their Class
  Principal Balance equals the tranche's Class Notional Amount at all times
  (`00-overview.md` §3.3).

State carried from Payment Date to Payment Date: the twelve `CNA[X]`; cumulative Tranche
Write-down Amounts allocated to each tranche (for the write-up cap); cumulative Principal
Loss Amount and Principal Recovery Amount (for the Cumulative Net Loss Percentage); whether
the Class A-1 Cumulative Net Loss Test has ever failed; the Overcollateralization Amount;
`UPB_prev[n]`.

---

## 2. Senior Percentage and Subordinate Percentage

`YAML: principal.senior_percentage`, `principal.subordinate_percentage` (P95); first-period
denominator A5 (Q8 option 1):

```
SeniorPct[n] = round7( ( CNA[A-H] + CNA[A-1] + CNA[A-1H] )_{immediately prior to n} / UPB_prev[n] )
SubPct[n]    = 1 − SeniorPct[n]
```

with `UPB_prev[1] = CutoffBalance` and `UPB_prev[n] = UPB_end[n − 1]` (the aggregate UPB at
the end of the previous Reporting Period). `round7` is the PPM rounding rule for
percentages (P51, A12). Worked value at `n = 1`: `21,978,114,962.84 / 22,781,151,551.84 =
0.96474995624…` → `SeniorPct[1] = 0.9647500`, `SubPct[1] = 0.0352500`.

**Knife-edge warning.** `SubPct[1]` equals the 3.525 % threshold to the fifth decimal of a
percent, and the unrounded value (3.5250044 %) exceeds it by $996.80 of subordinate
notional. The test is "greater than or equal to" and passes; any rounding other than R3
(for instance rounding to 4 places, or float arithmetic) can flip it. A unit test must
assert `SeniorPct[1] == Decimal("0.9647500")` and that the Minimum Credit Enhancement Test
passes on Payment Date 1 at CER 0.

---

## 3. Losses, recoveries, write-down and write-up amounts

### 3.1 Amounts (Modeling Assumption (d), `YAML: modeling_assumptions.d_credit_events`; P14, P78, T8)

```
PrincipalLossAmount[n]     = round2( 0.25 × CreditEventAmount[n] )        (d)(i): "Preliminary Principal
                                                                            Loss Amount = 25 % of the
                                                                            Credit Event Amount"; with no
                                                                            Modification Loss (RM = 0) the
                                                                            Preliminary and final amounts
                                                                            coincide (YAML:
                                                                            credit_events.preliminary_principal_loss_amount)
PrincipalRecoveryAmount[n] = 0                                            Modeling Assumptions (n),(o): no
                                                                            reversals, settlements, subsequent
                                                                            recoveries or Projected Recovery
                                                                            Amount (YAML:
                                                                            credit_events.principal_recovery_amount)
TrancheWriteDown[n]        = max( 0, PrincipalLossAmount[n] − PrincipalRecoveryAmount[n] )   YAML: credit_events.tranche_write_down_amount
TrancheWriteUp[n]          = max( 0, PrincipalRecoveryAmount[n] − PrincipalLossAmount[n] )   YAML: credit_events.tranche_write_up_amount
RecoveryPrincipal[n]       = ( CreditEventAmount[n] − TrancheWriteDown[n] ) + TrancheWriteUp[n]   YAML: principal.recovery_principal (P97)
```

The constant `0.25` is `YAML: modeling_assumptions.d_preliminary_principal_loss_pct_of_credit_event_amount`
(P14). Two different PPM terms must not be confused: **Principal Recovery Amount** (p209,
zero in v1) enters the write-down/write-up netting; **Recovery Principal** (p211, 75 % of
the Credit Event Amount in v1) is principal that flows to the Senior Reduction Amount in the
same Payment Date ("no lag", (d)(i)). In v1, `TrancheWriteDown[n] = 25 %` and
`RecoveryPrincipal[n] = 75 %` of the Credit Event Amount, to the cent (the 75 % is a
remainder, never a second rounding).

Engine requirement: implement the full definitions (all five clauses of Principal Loss
Amount and Principal Recovery Amount, `YAML: credit_events.principal_loss_amount`,
`principal_recovery_amount`) with the v1 inputs forcing clauses (b)–(e) to zero, so the
same code serves actual-pool runs; but the v1 unit test asserts the 25 / 75 split.

### 3.2 Cumulative Net Loss Percentage (`YAML: performance_tests.cumulative_net_loss_percentage`)

```
CNLPct[n] = round7( Σ_{k ≤ n} ( PrincipalLossAmount[k] − PrincipalRecoveryAmount[k] ) / CutoffBalance )
```

The sum **includes** Payment Date `n` ("for such Payment Date and all prior Payment
Dates"). The denominator is the Cut-off Date Balance (P10), never the current UPB.

### 3.3 The four tests

| test | passes when | source |
|---|---|---|
| Minimum Credit Enhancement Test | `SubPct[n] ≥ 0.03525` | `YAML: performance_tests.minimum_credit_enhancement_test`, threshold P15 |
| Cumulative Net Loss Test | `CNLPct[n] ≤ Threshold(n)` | `YAML: performance_tests.cumulative_net_loss_test_schedule_pct`, P52 |
| Delinquency Test | `AvgDPB[n] < 0.50 × ( SubPct[n] × UPB_prev[n] − PrincipalLossAmount[n] )` | `YAML: performance_tests.delinquency_test`, P53, P54; denominator per A5 |
| Class A-1 Cumulative Net Loss Test | `CNLPct[k] ≤ 0.0100` for **every** `k ≤ n` | `YAML: performance_tests.class_a1_cumulative_net_loss_test`, P16 |

`Threshold(n)` by Payment Date number (March 2026 = 1; each band is 12 Payment Dates):

| Payment Dates | period | threshold |
|---|---|---|
| 1–12 | Mar 2026 – Feb 2027 | 0.10 % |
| 13–24 | Mar 2027 – Feb 2028 | 0.20 % |
| 25–36 | Mar 2028 – Feb 2029 | 0.30 % |
| 37–48 | Mar 2029 – Feb 2030 | 0.40 % |
| 49–60 | Mar 2030 – Feb 2031 | 0.50 % |
| 61–72 | Mar 2031 – Feb 2032 | 0.60 % |
| 73–84 | Mar 2032 – Feb 2033 | 0.70 % |
| 85–96 | Mar 2033 – Feb 2034 | 0.80 % |
| 97–108 | Mar 2034 – Feb 2035 | 0.90 % |
| 109–120 | Mar 2035 – Feb 2036 | 1.00 % |
| 121–132 | Mar 2036 – Feb 2037 | 1.10 % |
| 133–144 | Mar 2037 – Feb 2038 | 1.20 % |
| 145 onward | Mar 2038 and thereafter | 1.30 % |

Delinquency Test: `AvgDPB[n]` is the average Distressed Principal Balance over Payment
Dates `max(1, n − 5) … n` (six, or all since the Closing Date before the sixth). In v1 the
scenario carries `delinquency_test_satisfied = true` (Modeling Assumption (e), T10/P73)
and the Distressed Principal Balance input is absent; the engine must evaluate the formula
only when the flag is false and raise if the input is then missing — never default the
Distressed Principal Balance to zero silently. The tests are evaluated **every** Payment
Date on the "immediately prior" state; they have no memory, except the Class A-1 test's
clause (2), which fails permanently once it has failed.

Consequence the dev should expect, not "fix": at any CER > 0 the first credit event writes
down B-3H on Payment Date 1, `SubPct` falls below 3.525 % on Payment Date 2, the Minimum
Credit Enhancement Test fails, 100 % of Stated Principal goes to the senior side, the
senior notional then shrinks faster than the pool, `SubPct` recovers above 3.525 % and the
test passes again — the tests toggle. This toggling is what the PPM's WAL cells at CER > 0
encode (`03-tieout.md` §6).

---

## 4. Allocation primitives

**Pro rata to a Note/H pair** (every "pro rata based on their Class Notional Amounts
immediately prior to such Payment Date" in the PPM; A8):

```
allocate_pair(X, amount):
    total = CNA[X] + CNA[pair(X)]                 (values immediately prior to the Payment Date)
    if total = 0 or amount = 0: return 0
    used   = min(amount, total)
    to_X   = round2( used × CNA[X] / total )       exact Decimal ratio, then one cent rounding
    to_H   = used − to_X
    CNA[X] −= to_X ;  CNA[pair(X)] −= to_H
    return used
```

`to_X` is capped by `CNA[X]` and `to_H` by `CNA[pair(X)]` — with the ratio above neither
cap can bind unless a balance is already zero, in which case the whole `used` goes to the
other member. The ratio is taken from the balances immediately prior to the Payment Date
even when an earlier priority on the same Payment Date has already reduced them (that is
the PPM's wording in every priority). Check: `allocate_pair(A-1, 10,892,238.08)` on
Payment Date 1 gives A-1 `10,346,250.00`, A-1H `545,988.08` — the two Appendix G columns
(T42), which is why A8 is the reading adopted.

**Single tranche**: `allocate_one(X, amount)`: `used = min(amount, CNA[X])`;
`CNA[X] −= used`; return `used`.

Every priority list below is applied "in each case until its Class Notional Amount is
reduced to zero": run the priorities in order, passing the remaining amount down; stop when
it is zero. Assert at the end of each list that the amount allocated equals the amount
available, except where the PPM allows a remainder (write-down beyond all tranches, §5).

---

## 5. Step 1 — Tranche Write-down Amount and Tranche Write-up Amount

Applied first on every Payment Date on or prior to the Maturity Date (`YAML:
credit_events.tranche_write_down_allocation_order`, P88, C6):

1. reduce the Overcollateralization Amount to zero (`YAML:
   credit_events.overcollateralization_amount`; zero in v1 because there is never a
   Write-up Excess);
2. B-3H; 3. B-2H; 4. B-1H; 5. `allocate_pair(M-2B)`; 6. `allocate_pair(M-2A)`;
   7. `allocate_pair(M-1)`; 8. `allocate_pair(A-1)`;
9. A-H, but only the excess of the remaining unallocated amount over the Principal Loss
   Amount attributable to clause (d) (Modification Loss principal steps). Clause (d) is zero
   in v1, so any remainder goes to A-H.

Record the amount allocated to each tranche (cumulative, for the write-up cap and for the
WAL). The Class Principal Balance of the Note corresponding to A-1/M-1/M-2A/M-2B is reduced
by the amount allocated to its tranche **without any payment** (`YAML:
credit_events.note_write_down_no_payment`); the Return Amount to Freddie Mac equals the sum
of those Note write-downs (`YAML: credit_events.return_amount`; reported, not a tie-out
target).

Also on every Payment Date: `CNA[A-H] += max(0, TrancheWriteDown[n] − CreditEventAmount[n])`
(`YAML: credit_events.a_h_increase_on_write_down`). Zero in v1 (25 % < 100 %); assert.

Tranche Write-up Amount (`YAML: credit_events.tranche_write_up_allocation_order`, P89, C7),
zero in v1 but specified: A-H; `allocate_pair(A-1)`; `allocate_pair(M-1)`;
`allocate_pair(M-2A)`; `allocate_pair(M-2B)`; B-1H; B-2H; B-3H — each **increase** capped
so that cumulative write-ups to that tranche do not exceed its cumulative prior
write-downs; the pair split of a write-up uses the ratio of the pair's cumulative
unreimbursed write-downs is NOT what the PPM says — it says pro rata by Class Notional
Amounts immediately prior, so use `allocate_pair` logic with the sign reversed and the cap
applied per member. Any remainder is the Write-up Excess and increases the
Overcollateralization Amount (`YAML: credit_events.write_up_excess`,
`write_up_excess_use`).

---

## 6. Step 2 — Senior Reduction Amount

`YAML: principal.senior_reduction_amount` (P95, C5):

```
if MCE and CNL and Delinquency tests all pass:
    SeniorReduction[n] = round2( SeniorPct[n] × StatedPrincipal[n] ) + RecoveryPrincipal[n]
else:
    SeniorReduction[n] = StatedPrincipal[n] + RecoveryPrincipal[n]
```

Class A-1 Reduction Amount (`YAML: principal.class_a1_reduction_amount`,
`appendix_g_schedule`; P60, P61, P62, T41, T42; reading A6 = Q9 option 1):

```
if the Class A-1 Cumulative Net Loss Test fails:   ClassA1Reduction[n] = 0      (deemed zero, YAML: performance_tests.gating_summary)
elif n ≤ 36:   ClassA1Reduction[n] = AppendixG_aggregate[n]                   10,892,238.08 for n = 1..12; 4,356,895.23 for n = 13..36
else:          ClassA1Reduction[n] = SeniorReduction[n] − RecoveryPrincipal[n]   limb (B): 100 % of the Senior Reduction Amount excluding Recovery Principal
```

`AppendixG_aggregate[n]` is the `aggregate_class_a1_reduction_amount_usd_computed` column
of `data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv` for `payment_period = n`,
the sum of the printed A-1 and A-1H columns. It is a per-Payment-Date amount with no
carry-forward of any shortfall (A6). Payment Date 1 uses the period-1 amount once, although
it carries two collection months (the schedule is indexed by Payment Period, T42).

Allocation of the Senior Reduction Amount (`YAML: principal.senior_reduction_allocation_order`,
P90), applied after Step 1, "in each case until its Class Notional Amount is reduced to
zero":

1. **if and only if** the Class A-1 Cumulative Net Loss Test is satisfied:
   `allocate_pair(A-1, min(remaining, ClassA1Reduction[n]))`;
2. `allocate_one(A-H)`;
3. `allocate_pair(A-1)`;
4. `allocate_pair(M-1)`;
5. `allocate_pair(M-2A)`;
6. `allocate_pair(M-2B)`;
7. `allocate_one(B-1H)`; 8. `allocate_one(B-2H)`; 9. `allocate_one(B-3H)`.

Note that A-1 receives its scheduled amount *ahead of* A-H in priority 1 and the rest of
the senior share goes to A-H in priority 2; priority 3 reaches A-1 again only after A-H is
exhausted, which cannot happen before the pool itself is exhausted (A-H is always
`SeniorPct × UPB − CNA[A-1] − CNA[A-1H]` in a no-loss scenario).

---

## 7. Step 3 — Subordinate Reduction Amount

`YAML: principal.subordinate_reduction_amount` (P91):

```
SubordinateReduction[n] = StatedPrincipal[n] + RecoveryPrincipal[n] − SeniorReduction[n]
```

which is `(1 − SeniorPct[n]) × StatedPrincipal[n]` up to the cent when the tests pass and
exactly zero when any of the three fails (`YAML: performance_tests.gating_summary`).
Allocation order (`YAML: principal.subordinate_reduction_allocation_order`):

1. `allocate_pair(M-1)`; 2. `allocate_pair(M-2A)`; 3. `allocate_pair(M-2B)`;
4. `allocate_one(B-1H)`; 5. `allocate_one(B-2H)`; 6. `allocate_one(B-3H)`;
7. `allocate_pair(A-1)`; 8. `allocate_one(A-H)`.

---

## 8. Step 4 — Supplemental Reduction Amount and Supplemental Senior Increase Amount

`YAML: principal.class_a1_additional_reduction_amount`, `supplemental_reduction_amount`,
`offered_reference_tranche_percentage`, `supplemental_reduction_allocation_order`,
`supplemental_senior_increase_amount` (P58, P59, P92, P103). Computed **after** Steps 1–3
on the balances as then reduced:

```
ClassA1Additional[n] = ( CNA[A-1] + CNA[A-1H] )   if n ≥ 39 and the Class A-1 Cumulative Net Loss Test passes on n
                     = 0                          otherwise
Offered[n]           = CNA[A-1] + CNA[A-1H] + CNA[M-1] + CNA[M-1H] + CNA[M-2A] + CNA[M-2AH] + CNA[M-2B] + CNA[M-2BH]
ORTP[n]              = round7( ( Offered[n] − ClassA1Additional[n] ) / UPB_end[n] )      (0 if UPB_end[n] = 0)
SupplementalReduction[n] = round2( UPB_end[n] × max( 0, ORTP[n] − 0.0550 ) ) + ClassA1Additional[n]
```

Constants: `39` (P59), `0.0550` (P58, `YAML: principal.supplemental_reduction_threshold_pct`).
`UPB_end[n]` is the UPB at the end of the **related** (current) Reporting Period.

Allocation, "in each case until its Class Notional Amount is reduced to zero":

1. `allocate_pair(A-1, min(remaining, ClassA1Additional[n]))`;
2. `allocate_pair(M-1)`; 3. `allocate_pair(M-2A)`; 4. `allocate_pair(M-2B)`;
5. `allocate_pair(A-1)`.

Simultaneously `CNA[A-H] += SupplementalReduction[n]` (the Supplemental Senior Increase
Amount, `YAML: principal.supplemental_senior_increase_allocation`). This is the one place
where A-H grows; it keeps the §3.3 identity of `00-overview.md` intact because the offered
tranches shrink by the same amount.

Expected v1 behaviour: `ORTP` starts at 2.9 % and falls, so the 5.50 % limb is never
positive in the PPM grid; the Class A-1 Additional Reduction Amount does bind (at 0 % CPR
it retires A-1 on Payment Date 39, which is why the printed A-1 WAL is 1.60 at 0 % CPR and
1.59 at every other CPR). Both limbs must be implemented and unit-tested with synthetic
inputs.

---

## 9. Maturity Date, early redemption, pool exhaustion

Scenario switch `early_redemption ∈ {off, on}` (T18). Payment Date `n` is the **Maturity
Date** if any of:

- `n = 240` (Scheduled Maturity Date, P8/P21);
- `early_redemption = on` and `n = 60` (the Payment Date in February 2031, P64,
  Modeling Assumption (m)(i));
- `early_redemption = on` and `UPB_end[n] ≤ 0.10 × CutoffBalance` (Modeling Assumption
  (m)(ii), P63; the UPB tested is the end of the related Reporting Period — **A11,
  ASSUMED**), on the first such `n`;
- `UPB_end[n] = 0` (Early Termination Date clauses (iii)/(iv), `YAML:
  termination.early_termination_date`), regardless of the switch.

On the Maturity Date (`YAML: termination.maturity_date_principal`, P106; P108):

1. Steps 1 of §5 are applied (write-down/write-up are "on or prior to the Maturity
   Date");
2. Steps 2–4 are **not** applied (they are "prior to the Maturity Date");
3. each Original Note is paid 100 % of its Class Principal Balance as then standing; for
   the WAL this is a principal payment on Payment Date `n` equal to the whole remaining
   balance;
4. the run stops; nothing after the final Reporting Period is computed (`YAML:
   termination.final_period_performance_disregarded`).

With `early_redemption = off` the run always reaches `n = 240`, where any Note still
outstanding is paid in full (at 0 % CPR the offered Notes are in fact retired earlier
through the subordinate allocations, but the engine must not assume that).

---

## 10. Note cashflows

**Principal paid** on Payment Date `n` to Note `X ∈ {A-1, M-1, M-2A, M-2B}` = the sum of
the amounts allocated to tranche `X` in Steps 2, 3 and 4 (`YAML:
principal.principal_payment_rule`), or 100 % of the Class Principal Balance on the Maturity
Date. **Write-down** = the amount allocated to `X` in Step 1. **Class Principal Balance**
after `n` = before − principal paid − write-down + write-up
(`YAML: principal.class_principal_balance_definition`) = `CNA[X]`.

**Interest** (`YAML: coupon.*`, `interest.*`; C4, C11, P36–P48, P50; not a tie-out target):

```
Coupon[X, n]  = max( 0, SOFR[n] + margin[X] )          margins: A-1 0.85 %, M-1 1.00 %, M-2A 1.30 %, M-2B 1.30 %
                                                       SOFR[n] = 3.65786 % flat (P12); first-period coupons are Table 1's
                                                       Initial Class Coupons, which equal the same sums (P42–P45);
                                                       the floor is the Class Coupon minimum rate 0 % (P7)
Days[n]       = calendar days from Payment Date n − 1 (Closing Date 2026-02-17 for n = 1)
                to the day before Payment Date n, inclusive = PD[n] − PD[n − 1] in days     (Accrual Period, P50)
InterestAccrual[X, n] = round2( CPB[X] immediately prior to n × Coupon[X, n] × Days[n] / 360 )   (actual/360, P20)
InterestPayment[X, n] = InterestAccrual[X, n] − Modification Loss allocated to interest + Modification Gain allocated   (both 0 in v1)
```

First Accrual Period: 2026-02-17 through 2026-03-24 = 36 days. With the unadjusted 25th
(`00-overview.md` §2.1) later periods are 28–31 days. Interest accrues on the balance
before that Payment Date's write-down and principal.

---

## 11. Edge cases

| case | required behaviour |
|---|---|
| Payment Date 1 | `UPB_prev = CutoffBalance` (A5); two collection months in the aggregates; one Appendix G amount; 36-day Accrual Period |
| a test fails | Senior Reduction = 100 % of Stated Principal + Recovery Principal; Subordinate = 0; re-evaluated next Payment Date from the then state |
| Class A-1 CNL Test fails once | `ClassA1Reduction = 0` and `ClassA1Additional = 0` on that and **every later** Payment Date (clause (2)) |
| Senior Reduction Amount smaller than the Appendix G amount | priority 1 is "up to": A-1/A-1H get the whole Senior Reduction Amount, nothing carries forward (A6) |
| `n > 36` | limb (B): priority 1 amount = Senior Reduction − Recovery Principal, so A-1/A-1H are paid ahead of A-H until retired |
| a tranche is at zero | skipped by the `min(…)` in the primitives; a pair with one zero member sends everything to the other |
| write-down larger than all subordinate tranches | continues into A-1/A-1H and then A-H (§5 priority 9); the Notes' balances fall without payment |
| Recovery Principal with tests failing | still 100 % senior (both limbs of the Senior Reduction Amount include it) |
| Maturity Date | §9: write-down, then 100 % payment, no Steps 2–4 |
| `UPB_end[n] = 0` | Maturity Date by clause (iii)/(iv); `ORTP` defined as 0 |
| Supplemental Reduction with `UPB_end` small | the 5.50 % limb is a dollar amount on the current UPB; the A-1 Additional limb is the whole remaining A-1/A-1H |
| negative SOFR | coupon floored at 0 % per class (P7); no negative interest |
| identity of `00-overview.md` §3.3 broken | raise, naming the Payment Date and the difference |

---

## 12. Worked example — Payment Date 1 at 10 % CPR, 0 % CER, early redemption off

Pool inputs from `01-pool.md` §9: `StatedPrincipal[1] = 437,763,629.88`,
`CreditEventAmount[1] = 0.00`, `UPB_end[1] = 22,343,387,921.96`,
`UPB_prev[1] = 22,781,151,551.84`.

| step | computation | result |
|---|---|---|
| §2 | `(21,687,655,280.84 + 275,900,000 + 14,559,682) / 22,781,151,551.84 = 0.964749956…` → round7 | `SeniorPct = 0.9647500`; `SubPct = 0.0352500` |
| §3.1 | `0.25 × 0` | `PrincipalLossAmount = 0`; `TrancheWriteDown = 0`; `TrancheWriteUp = 0`; `RecoveryPrincipal = 0` |
| §3.2 | | `CNLPct = 0.0000000` |
| §3.3 | `0.0352500 ≥ 0.03525` ✔; `0 ≤ 0.0010` ✔; Delinquency flag ✔; A-1 CNL `0 ≤ 0.0100` ✔ | all four tests pass |
| §5 | nothing to allocate | balances unchanged |
| §6 | `round2(0.9647500 × 437,763,629.88) = round2(422,332,461.926…)` | `SeniorReduction = 422,332,461.93` |
| §6 | `n = 1 ≤ 36` | `ClassA1Reduction = 10,892,238.08` |
| §6 priority 1 | `allocate_pair(A-1, 10,892,238.08)`: `round2(10,892,238.08 × 275,900,000 / 290,459,682)` | A-1 `10,346,250.00`; A-1H `545,988.08` |
| §6 priority 2 | `422,332,461.93 − 10,892,238.08` | A-H `411,440,223.85`; remaining 0 |
| §7 | `437,763,629.88 + 0 − 422,332,461.93` | `SubordinateReduction = 15,431,167.95` |
| §7 priority 1 | `allocate_pair(M-1, 15,431,167.95)`: `round2(15,431,167.95 × 275,900,000 / 290,459,682)` | M-1 `14,657,659.91`; M-1H `773,508.04`; remaining 0 |
| §8 | `n < 39` → `ClassA1Additional = 0`; `Offered = 265,553,750.00 + 14,013,693.92 + 261,242,340.09 + 13,786,173.96 + 37,850,000 + 2,017,015 + 37,850,000 + 2,017,015 = 634,329,987.97`; `634,329,987.97 / 22,343,387,921.96 = 0.02839009…` → round7 | `ORTP = 0.0283901` < 0.0550 → `SupplementalReduction = 0` |

Class Notional Amounts after Payment Date 1:

| tranche | before | reduction | after |
|---|---|---|---|
| A-H | 21,687,655,280.84 | 411,440,223.85 | 21,276,215,056.99 |
| A-1 | 275,900,000.00 | 10,346,250.00 | 265,553,750.00 |
| A-1H | 14,559,682.00 | 545,988.08 | 14,013,693.92 |
| M-1 | 275,900,000.00 | 14,657,659.91 | 261,242,340.09 |
| M-1H | 14,559,682.00 | 773,508.04 | 13,786,173.96 |
| M-2A, M-2AH, M-2B, M-2BH, B-1H, B-2H, B-3H | unchanged | 0 | unchanged |
| **sum** | 22,781,151,551.84 | 437,763,629.88 | **22,343,387,921.96** = `UPB_end[1]` ✔ |

Note cashflows on 2026-03-25:

| Note | principal paid | write-down | Class Principal Balance after | coupon | interest (36 days) |
|---|---|---|---|---|---|
| A-1 | 10,346,250.00 | 0 | 265,553,750.00 | 4.50786 % | `round2(275,900,000 × 0.0450786 × 36/360)` = 1,243,718.57 |
| M-1 | 14,657,659.91 | 0 | 261,242,340.09 | 4.65786 % | 1,285,103.57 |
| M-2A | 0 | 0 | 37,850,000.00 | 4.95786 % | 187,655.00 |
| M-2B | 0 | 0 | 37,850,000.00 | 4.95786 % | 187,655.00 |

**Payment Date 2** (same scenario; `StatedPrincipal[2] = 215,917,777.08`, `UPB_prev[2] =
22,343,387,921.96`): `SeniorPct[2] = round7(21,555,782,500.91 / 22,343,387,921.96) =
0.9647500`; `SeniorReduction = round2(0.96475 × 215,917,777.08) = 208,306,675.44`;
A-1 `10,346,250.00`, A-1H `545,988.08`, A-H `197,414,437.36`; `SubordinateReduction =
7,611,101.64` → M-1 `7,229,584.94`, M-1H `381,516.70`; `ORTP = 0.0278309`; balances after:
A-H 21,078,800,619.63, A-1 255,207,500.00, A-1H 13,467,705.84, M-1 254,012,755.15, M-1H
13,404,657.26; sum 22,127,470,144.88 = `UPB_end[2]` ✔.

These two Payment Dates are the hand-computable unit test for the waterfall. A third test
should take a synthetic `CreditEventAmount[1] = 1,000,000.00` with the same pool numbers
and assert: `PrincipalLossAmount = 250,000.00`, `TrancheWriteDown = 250,000.00` allocated
entirely to B-3H, `RecoveryPrincipal = 750,000.00`, `SeniorReduction = 422,332,461.93 +
750,000.00`, and that the sum of Class Notional Amounts after the Payment Date equals
`UPB_end[1] − 1,000,000.00` (the pool would have lost the Credit Event UPB).
