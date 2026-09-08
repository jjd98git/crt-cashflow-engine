# STACR 2026-DNA2 vs 2026-DNA1 - engine-relevant differences

Source for DNA2: `data/raw/stacr-2026-dna2-ppm.txt` (PPM dated March 13, 2026; Closing Date
March 17, 2026), extracted into `data/deals/stacr_2026_dna2/deal_terms.yaml` (same schema as
`data/deal_terms/stacr_2026_dna1.yaml`). Page numbers are PDF pages of the text extract
(printed folio + 22 in the body). DNA1 values are taken from the DNA1 YAML and
`docs/spec/02-waterfall.md`.

Legend: **SAME** = identical rule and value; **DIFFERENT** = same mechanic, different value or
wording (both values given); **NEW** = present in DNA2, absent in DNA1; **ABSENT** = present
in DNA1, absent in DNA2.

The one-sentence summary: DNA2 is a **five-Note, thirteen-tranche** deal with **no Class A-1
layer**. Everything that DNA1 needed for A-1 (the Class A-1 Cumulative Net Loss Test, the
Class A-1 Reduction Amount, the Appendix G schedule, the Class A-1 Additional Reduction
Amount, the A-1-first priorities in the Senior and Supplemental allocations) is absent. In
its place the B-1 layer is split into two Note/H pairs (B-1A/B-1AH, B-1B/B-1BH) that enter
every allocation order. The arithmetic of the tests, the loss definitions, the rounding, the
day count and the SOFR mechanics are unchanged.

## 1. Deal facts

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Memorandum date | DIFFERENT | 2026-02-12 | 2026-03-13 | p1 |
| Closing Date | DIFFERENT | 2026-02-17 | 2026-03-17 | p200 |
| Cut-off Date | DIFFERENT | 2025-12-31 | 2026-01-31 | p203 |
| Cut-off Date Balance | DIFFERENT | 22,781,151,551.84 | 26,703,800,234.86 | p203 |
| Total offered | DIFFERENT | 627,500,000 | 507,200,000 | p1 |
| First Payment Date | DIFFERENT | 2026-03-25 (Wed) | 2026-04-27 (25 Apr 2026 is a Saturday; PPM tables assume the 25th) | p216, p139 (q) |
| Scheduled Maturity Date | DIFFERENT (calendar) / SAME (240 Payment Dates) | Payment Date in Feb 2046 | Payment Date in Mar 2046 | p222 |
| Rounding convention | SAME | 1/100,000 of a pct point; cents half-up | same | p101 |
| Minimum denomination | SAME | 10,000 | 10,000 | p96 |

## 2. Tranche stack and pairs (`reference_tranches`)

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Number of Reference Tranches | DIFFERENT | 12 | 13 | p220 |
| A-H initial notional | DIFFERENT | 21,687,655,280.84 (95.200%) | 25,902,685,229.86 (97.00000%) | p24 |
| A-1 / A-1H | ABSENT | 275,900,000 / 14,559,682 | none; the string "Class A-1" does not occur in the PPM | p220 |
| M-1 / M-1H | DIFFERENT | 275,900,000 / 14,559,682 | 253,600,000 / 13,438,002 | p24 fn (2) |
| M-2A / M-2AH | DIFFERENT | 37,850,000 / 2,017,015 | 57,050,000 / 3,033,550 | p24 fn (4) |
| M-2B / M-2BH | DIFFERENT | 37,850,000 / 2,017,015 | 57,050,000 / 3,033,550 | p24 fn (6) |
| B-1A / B-1AH | NEW | - | 69,750,000 / 3,685,450 (Note/H pair) | p24 fn (8) |
| B-1B / B-1BH | NEW | - | 69,750,000 / 3,685,450 (Note/H pair) | p24 fn (10) |
| B-1H (single retained, SOFR + 1.80%) | ABSENT | 102,515,181 | none; "B-1H" in the diagram is B-1AH + B-1BH drawn together (p23) | p23 |
| B-2H | DIFFERENT | 273,373,818, SOFR + 4.75% | 200,278,501, SOFR + 5.00% | p24, p10 |
| B-3H | DIFFERENT | 56,953,878 | 66,760,502 | p24 |
| Sum of initial notionals = Cut-off Date Balance | SAME (verified) | 22,781,151,551.84 | 26,703,800,234.86, difference 0.00 | p25 |
| Note/H pairs (`allocate_pair`) | DIFFERENT | 4: A-1, M-1, M-2A, M-2B | 5: M-1, M-2A, M-2B, B-1A, B-1B | p105-111 |
| Retained H minimum share of each pair | SAME (5%) | 4 pairs | 5 pairs (5.0322 / 5.0489 / 5.0489 / 5.0186 / 5.0186%) | p26 |
| "Senior Reference Tranche" / "Mezzanine" / "Junior" defined terms | NEW | - | A-H / M-1..M-2BH / B-1A..B-3H | p223, p211, p210 |
| Original Notes | DIFFERENT | A-1, M-1, M-2A, M-2B | M-1, M-2A, M-2B, B-1A, B-1B | p215 |
| Initial subordination (Table 3) | DIFFERENT | A-H 4.800; A-1 3.525; M-1 2.250; M-2A 2.075; M-2B 1.900; B-1H 1.450; B-2H 0.250; B-3H 0 | A-H 3.000; M-1 2.000; M-2A 1.775; M-2B 1.550; B-1A 1.275; B-1B 1.000; B-2H 0.250; B-3H 0 | p24 |

Engine consequence: the tranche list, the pair map and every priority list must be data
(loaded from the YAML), not code. Any code path that names `A-1`, `A-1H` or `B-1H` cannot
run DNA2.

## 3. Senior Percentage and Minimum Credit Enhancement

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Tranches in the Senior Percentage numerator | DIFFERENT | A-H + A-1 + A-1H | **A-H only** ("Senior Reference Tranche" means the Class A-H Reference Tranche) | p223 |
| Denominator | SAME | aggregate UPB at end of previous Reporting Period | same | p223 |
| Initial Senior / Subordinate Percentage | DIFFERENT | 96.47500 / 3.52500 | 97.00000 / 3.00000 (unrounded 3.0000037%) | derived |
| Minimum Credit Enhancement threshold | DIFFERENT | 3.525% | **3.000%** | p211 |
| Knife-edge on Payment Date 1 | SAME (recurs) | SubPct[1] = threshold to 5 decimals | SubPct[1] = 3.00000% = threshold; passes only under the PPM rounding rule (R3); unit test required | derived |
| Test comparison | SAME | >= | >= | p211 |

## 4. Cumulative Net Loss Test schedule

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Percentages by 12-Payment-Date band | SAME | 0.10, 0.20, ... 1.20, then 1.30 | 0.10, 0.20, ... 1.20, then 1.30 | p202 |
| Band calendar | DIFFERENT | Mar 2026-Feb 2027 = band 1 | Apr 2026-Mar 2027 = band 1 | p202 |
| Band by Payment Date number (PD 1 = first Payment Date) | SAME | 1-12, 13-24, ... 145+ | 1-12, 13-24, ... 145+ | derived |
| Denominator | SAME | Cut-off Date Balance | Cut-off Date Balance | p202 |
| Delinquency Test (50%, 6-PD average, Distressed Principal Balance) | SAME | same | same wording | p203 |

## 5. Class A-1 mechanics - all ABSENT

| item | status | DNA1 | DNA2 | evidence |
|---|---|---|---|---|
| Class A-1 Cumulative Net Loss Test (1.00%, permanent fail) | ABSENT | present, gates A-1 principal | not in the PPM; no test gates the Senior Reduction allocation | "Class A-1" absent from all 17,456 lines; p202 defines only the Cumulative Net Loss Test |
| Class A-1 Reduction Amount (scheduled, 36 Payment Dates) | ABSENT | present | not in the PPM; Senior Reduction goes first to A-H with no carve-out | p109 |
| Appendix G schedule | ABSENT | present | Appendices A-F only | p9 TOC; "Appendix G" absent |
| Class A-1 Additional Reduction Amount (from PD 39) | ABSENT | present | not in the PPM; Supplemental Reduction Amount has a single 5.50% limb | p225 |
| Scheduled amortization of any tranche | ABSENT | A-1 only | none | - |

Engine consequence: the A-1 block in `02-waterfall.md` section 6 (priority 1 of the Senior
allocation), section 8 (`ClassA1Additional`) and section 3.3 (the fourth test) must be
switchable off by data - e.g. absent `class_a1_*` keys (value null) mean "no scheduled tranche,
no fourth test, no additional term". The state variable "whether the Class A-1 test has ever
failed" is unused for DNA2.

## 6. Supplemental Reduction Amount

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Threshold | SAME | 5.50% | 5.50% | p225 |
| Offered Reference Tranche Percentage numerator | DIFFERENT | A-1, A-1H, M-1, M-1H, M-2A, M-2AH, M-2B, M-2BH minus Class A-1 Additional Reduction Amount | M-1, M-1H, M-2A, M-2AH, M-2B, M-2BH, B-1A, B-1AH, B-1B, B-1BH (no subtraction) | p214 |
| Denominator | SAME | UPB at end of the related Reporting Period | same | p214 |
| Formula | DIFFERENT | UPB x max(0, ORTP - 5.50%) + Class A-1 Additional Reduction Amount | UPB x max(0, ORTP - 5.50%) | p225 |
| Initial ORTP | DIFFERENT | 2.9% | 2.00000% | derived |
| Allocation order | DIFFERENT | A-1 pair (up to the additional amount); M-1; M-2A; M-2B; A-1 pair | M-1; M-2A; M-2B; B-1A; B-1B; B-2H; B-3H; A-H (identical to the Subordinate order) | p110-111 |
| Supplemental Senior Increase Amount to A-H, simultaneous | SAME | same | same | p111, p225 |

Note on priorities sixth-eighth (B-2H, B-3H, A-H): by construction the Supplemental Reduction
Amount is at most the offered tranches' notional in excess of 5.50% of UPB, so it cannot reach
B-2H, B-3H or A-H unless the five pairs are exhausted; the engine should carry the full
eight-priority list as data and assert (not assume) that the last three are never reached.

## 7. Allocation orders

| list | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Senior Reduction | DIFFERENT | [A-1 pair, min(remaining, ClassA1Reduction) if A-1 test passes]; A-H; A-1 pair; M-1; M-2A; M-2B; B-1H; B-2H; B-3H (9) | A-H; M-1; M-2A; M-2B; B-1A; B-1B; B-2H; B-3H (8) | p109 |
| Subordinate Reduction | DIFFERENT | M-1; M-2A; M-2B; B-1H; B-2H; B-3H; A-1 pair; A-H (8) | M-1; M-2A; M-2B; B-1A; B-1B; B-2H; B-3H; A-H (8) | p110 |
| Tranche Write-down | DIFFERENT | OC; B-3H; B-2H; B-1H; M-2B; M-2A; M-1; A-1 pair; A-H (excess over clause (d)) | OC; B-3H; B-2H; B-1B pair; B-1A pair; M-2B; M-2A; M-1; A-H (excess over clause (d)) | p105-106 |
| Tranche Write-up | DIFFERENT | A-H; A-1 pair; M-1; M-2A; M-2B; B-1H; B-2H; B-3H | A-H; M-1; M-2A; M-2B; B-1A pair; B-1B pair; B-2H; B-3H | p106 |
| Write-up cap / Write-up Excess / Overcollateralization | SAME | clauses first-eighth | clauses first-eighth | p228, p216 |
| A-H increase by (write-down - Credit Event Amount) | SAME | same | same | p106 |
| Modification Loss (13 priorities) | DIFFERENT | 1 B-3H prin; 2 B-2H int; 3 B-2H prin; 4 B-1H int; 5 B-1H prin; 6 M-2B int; 7 M-2A int; 8 M-2B prin; 9 M-2A prin; 10 M-1 int; 11 M-1 prin; 12 A-1 int; 13 A-1 prin | 1 B-3H prin; 2 B-2H int; 3 B-2H prin; 4 B-1B pair int; 5 B-1A pair int; 6 B-1B pair prin; 7 B-1A pair prin; 8 M-2B int; 9 M-2A int; 10 M-2B prin; 11 M-2A prin; 12 M-1 int; 13 M-1 prin | p107-108 |
| Modification Loss principal priorities (Principal Loss Amount clause (d); A-H increase) | DIFFERENT | 1,3,5,8,9,11,13 | 1,3,6,7,10,11,13 | p108, p218 |
| Modification Loss interest priorities | DIFFERENT | 2,4,6,7,10,12 (A-1 12th, M-1 10th, M-2A 7th, M-2B 6th) | 2,4,5,8,9,12 (M-1 12th, M-2A 9th, M-2B 8th, B-1A 5th, B-1B 4th) | p108 |
| Modification Gain (7 priorities) | DIFFERENT | A-1; M-1; M-2A; M-2B; B-1H; B-2H; most subordinate | M-1; M-2A; M-2B; B-1A; B-1B; B-2H; most subordinate | p108-109 |
| Tranches bearing a deemed coupon for modification allocations | DIFFERENT | B-1H (SOFR + 1.80%) and B-2H (SOFR + 4.75%) | B-2H only (SOFR + 5.00%); B-1A/B-1B use their Note coupons | p10, p11 fn (10) |
| Pro-rata basis inside a pair | SAME | Class Notional Amounts immediately prior (Preliminary CNA in the principal steps of Modification Loss) | same wording | p105-111 |

Engine consequence: the Modification Loss table in `02-waterfall.md` cannot be hard-coded by
priority number; the priority list (tranche, pair-or-single, cap type interest/principal,
pro-rata basis) must be data, and the "which priorities are principal" set must be derived
from that data (or loaded from `modification_loss_principal_priorities`) rather than written
as `{1,3,5,8,9,11,13}`.

## 8. Coupons and interest

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Index, adjustment date, determination time, fallbacks | SAME | 30-Day Average SOFR, 2 USGS business days before, 3 pm NY | same | p224 |
| First Accrual Period SOFR Rate | DIFFERENT | 3.65786% | 3.67223% | p103 |
| Margins (Original Notes) | DIFFERENT | A-1 0.85; M-1 1.00; M-2A 1.30; M-2B 1.30 | M-1 1.20; M-2A 1.60; M-2B 1.60; B-1A 2.10; B-1B 2.10 | p10 (column-shifted; reconciled via Table 2 and SOFR + margin) |
| Initial Class Coupons (Original Notes) | DIFFERENT | 4.50786 / 4.65786 / 4.95786 / 4.95786 | M-1 4.87223; M-2A 5.27223; M-2B 5.27223; B-1A 5.77223; B-1B 5.77223 | p10 (medium confidence, DNA2-Q1) |
| Coupon floor | SAME | 0% on the Class Coupon | 0% | p10 |
| Day count, arrears, Accrual Period, Record Date | SAME | actual/360 | actual/360 | p203, p103, p196, p219 |
| Priority of payments (Return Amount first) | SAME | same | same | p103 |
| Notes cease to bear interest after the Early Redemption Date | SAME | same | same | p103 |

## 9. Early redemption and termination

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Time-based early redemption assumed in the tables | DIFFERENT (calendar) / SAME (PD 60) | Payment Date in Feb 2031 = PD 60 | Payment Date in Mar 2031 = PD 60 | p139 (m), p203 |
| Earliest Time-Based Call Option Date | DIFFERENT | Feb 2031 | Mar 2031 | p203 |
| Optional Termination Event 7 wording | DIFFERENT | "on or after the Payment Date in the calendar month prior to February 2031" | "... prior to March 2031" | p215 |
| Clean-up threshold | SAME | 10% of Cut-off Date Balance | 10% | p215 (6), p139 (m)(ii) |
| Redemption is optional (Freddie Mac designation) | SAME | same | same | p204 (ii) |
| Notice timing (first / second Payment Date; 5 Business Days) | SAME | same | same | p115 |
| Early Termination Date clauses (i)-(vi), Termination Date, Maturity Date | SAME | same | same | p204, p225, p211 |
| Maturity Date pays 100% of Class Principal Balance; final-period performance disregarded | SAME | same | same | p104, p115 |

## 10. First Payment Date and Reporting Period

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Payment Dates commence | DIFFERENT | March 2026 | April 2026 | p216 |
| First Payment Date calendar day | DIFFERENT | 2026-03-25 (a Wednesday) | 2026-04-27 (the 25th is a Saturday; rolls forward) - DNA2-Q3 | p216 |
| First Reporting Period, collections and modifications | DIFFERENT | 2026-01-01 to 2026-02-28 | 2026-02-01 to 2026-03-31 | p221 (a)(1) |
| First Reporting Period, full prepayments / defects / Credit Events | DIFFERENT | 2026-01-06 to 2026-03-03 | 2026-02-04 to 2026-04-02 | p221 (a)(2) |
| First Reporting Period delinquency as-of | DIFFERENT | 2026-02-28 | 2026-03-31 | p221 (a)(3) |
| Subsequent Reporting Periods | SAME | preceding month / 2nd Business Day to 2nd Business Day / month-end | same | p221 (b) |
| Two month-ends in the first period (Modeling Assumptions (f),(g)) | SAME (structure) | Jan 31 + Feb 28, 2026 | Feb 28 + Mar 31, 2026 | p138 |
| YAML key names | DIFFERENT | `march_2026_payment_date`, `april_2026_onward_payment_dates` | `april_2026_payment_date`, `may_2026_onward_payment_dates` | - |

Engine consequence: the loader should read the Reporting Period block generically (first
period / subsequent periods) rather than by the calendar-named key.

## 11. Modeling Assumptions (a)-(s)

| assumption | status | DNA1 | DNA2 |
|---|---|---|---|
| (a) Appendix C rep-lines | DIFFERENT (data) | 31 groups | 38 groups (p264; columns shifted in the extract, DNA2-Q5) |
| (b) Table 1 balances/coupons | DIFFERENT (wording) | "the Class B-1H Reference Tranche and the Class B-2H Reference Tranche" | "the Class B-2H Reference Tranche" only |
| (c) level-pay amortization | SAME | | |
| (d) CER, no recovery lag, Preliminary PLA = 25% of Credit Event Amount | SAME | 25% | 25% |
| (e) Delinquency Test satisfied | SAME | | |
| (f) scheduled P&I on the last day of each month beginning | DIFFERENT | January 2026 | February 2026 |
| (g) full prepayments on the last day of each month beginning | DIFFERENT | January 2026 | February 2026 |
| (h) no curtailments | SAME | | |
| (i) CPR | SAME | | |
| (j) no removals | SAME | | |
| (k) RM mechanics; first-PD Modification Loss = two monthly calcs | DIFFERENT (dates) | March 2026 PD: Jan 1 on Cut-off UPB + Feb 1 on Jan 31 UPB | April 2026 PD: Feb 1 on Cut-off UPB + Mar 1 on Feb 28 UPB |
| (l) no data corrections | SAME | | |
| (m) early redemption earlier of time-based PD and 10% clean-up | DIFFERENT (calendar) | Feb 2031 | Mar 2031 (both PD 60) |
| (n) no reversals / gains / settlements | SAME | | |
| (o) Projected Recovery Amount = 0 | SAME | | |
| (p) issue date | DIFFERENT | 2026-02-17 | 2026-03-17 |
| (q) Note payments on the 25th beginning | DIFFERENT | March 2026 | April 2026 |
| (r) SOFR flat | DIFFERENT | 3.65786% | 3.67223% |
| (s) no exchanges, no retirement | SAME | | |
| Pricing Speed | SAME | 10% CPR | 10% CPR |
| CPR/CER monthly conversion stated? | SAME (not stated) | | DNA1 Q11 convention carries over |
| Assumed Accounting Net Yield / servicing fee | SAME (none stated) | | DNA1 Q5/Q7 resolution carries over |
| Table set covered | SAME | WAL, Declining Balances, Credit Event Sensitivity, Cumulative Note Write-down, Yield | same five |

## 12. Table 1 tie-out targets (10% CPR, redemption March 2031)

| class | status | DNA1 WAL / window / CE | DNA2 WAL / window / CE |
|---|---|---|---|
| A-1 | ABSENT | 1.59 / 1-37 / 3.525% | - |
| M-1 | DIFFERENT | 1.75 / 1-45 / 2.250% | 1.59 / 1-41 / 2.000% |
| M-2A | DIFFERENT | 4.11 / 45-53 / 2.075% | 3.90 / 41-53 / 1.775% |
| M-2B | DIFFERENT | 4.79 / 53-60 / 1.900% | 4.85 / 53-60 / 1.550% |
| B-1A | NEW | - | 5.02 / 60-60 / 1.275% |
| B-1B | NEW | - | 5.02 / 60-60 / 1.000% |
| M-2 (MACR) | DIFFERENT | 4.45 (DNA1 Table 1) | 4.38 / 41-60 / 1.550% |
| B-1 (MACR) | NEW | - | 5.02 / 60-60 / 1.000% |

B-1A and B-1B have a 60-60 window: in the Table 1 scenario they receive no principal before
the March 2031 redemption. That is a useful sanity check on the DNA2 Subordinate allocation
(the pairs above them absorb everything through Payment Date 60 at 10% CPR).

## 13. MACR

| item | status | DNA1 | DNA2 | DNA2 cite |
|---|---|---|---|---|
| Exchangeable Notes | DIFFERENT | M-2A, M-2B | M-2A, M-2B, B-1A, B-1B | p206 |
| MACR classes | DIFFERENT | 20 | 28 (B-1, B-1R/S/T/U, B-1I, B-1AR, B-1AI added; no B-1B-only classes) | p210 |
| Combinations | DIFFERENT | 17 | 23 (18-23 NEW) | p12 |
| M-2 family strip margins (R/S/T/U) | DIFFERENT | 0.55 / 0.70 / 0.85 / 1.00 | 0.85 / 1.00 / 1.15 / 1.30 | p12 |
| B-1 family strip margins (R/S/T/U) | NEW | - | 1.10 / 1.30 / 1.50 / 1.70 | p12 |
| IO coupon | DIFFERENT | 0.75% (M-2 family) | 0.75% (M-2 family), 1.00% (B-1 family) | p10 |
| M-2RB family initial coupons | DIFFERENT | 5.70786 / 5.55786 / 5.40786 / 5.25786 | 6.02223 / 5.87223 / 5.72223 / 5.57223 | p10 |
| Deemed exchange at closing | DIFFERENT | M-2A + M-2B -> M-2 | M-2A + M-2B -> M-2 (Comb. 1) and B-1A + B-1B -> B-1 (Comb. 18) | p1 fn (4),(5) |
| Exchange constraints, proportions basis, fee | SAME | | | p111, p113 |

## 14. Reference Pool (Appendix A)

| item | status | DNA1 | DNA2 |
|---|---|---|---|
| Loans | DIFFERENT | 64,434 | 73,437 |
| Aggregate Original Principal Balance | DIFFERENT | 23,552,092,000 | 27,524,842,000 (this is the figure the task brief called "Aggregate Principal Balance"; the extract's row labels are shifted) |
| Aggregate Principal Balance | DIFFERENT | 22,781,151,551 | 26,703,800,234 |
| WA rate / remaining term / loan age | DIFFERENT | 6.793% / 349 / 10 | 6.720% / 352 / 8 |
| Selection window | DIFFERENT | securitized Jan-Mar 2025, originated on/after 2024-01-01 | securitized Apr-Jun 2025, originated on/after 2024-04-01 |
| Minimum current Principal Balance | NEW (observation) | - | $0 printed; do not assert UPB > 0 at Cut-off in the loader |
| Latest maturity | DIFFERENT | Apr 2055 | Jul 2055 |

## 15. Unchanged mechanics (SAME) - for completeness

Credit Event definition (five triggers, one per loan plus one per reversal); Credit Event
Amount / UPB / Net Loss / Net Gain; Principal Loss Amount clauses (a)-(e) and Principal
Recovery Amount clauses (a)-(e) (only the priority numbers inside clause (d) differ, section
7); Tranche Write-down / Write-up Amount; Recovery Principal; Stated Principal clauses (a)-(e)
with the zero floor and A-H increase; Senior / Subordinate Reduction Amount formulas and the
three-test gate; Subordinate Percentage = 100% - Senior Percentage; Delinquency Test and
Distressed Principal Balance; Reference Pool Removal clauses (i)-(viii) and timing;
Modification Event / Excess / Shortfall / Loss / Gain, Original and Current Accrual Rate with
the 0.35% haircut; Preliminary amounts computed before modification allocations; Class
Notional Amount and Class Principal Balance definitions; Return Amount; write-downs without
payment; Notes Retirement Amount treatment; Benchmark Replacement waterfall; 30-day SOFR
correction window.

## 16. Engine code vs engine data - checklist for the dev

1. Tranche list and Note/H pair map: data. DNA2 has 13 tranches, 5 pairs, no A-1, no B-1H.
2. Senior-numerator set: data (`principal.senior_percentage`). DNA2 = {A-H}.
3. Minimum Credit Enhancement threshold: data (3.000%).
4. Every priority list (Senior, Subordinate, Supplemental, Write-down, Write-up, Modification
   Loss, Modification Gain): data, including whether a step is a pair or a single tranche,
   its cap type and its pro-rata basis.
5. Class A-1 block (fourth test, scheduled reduction, additional reduction, the A-1-first
   priority in Senior and Supplemental allocations): must be absent-able. With the DNA2 YAML
   all four keys are null.
6. Supplemental Reduction Amount: formula limb list is data; DNA2 has the 5.50% limb only and
   an eight-step allocation.
7. CNL schedule: index by Payment Date number (identical for both deals); calendar labels are
   informational.
8. First Payment Date: derive from "25th, roll forward" and the calendar; DNA2 rolls to
   2026-04-27 while the PPM tables assume the 25th (DNA2-Q3).
9. Reporting Period block: read generically (first period / subsequent), not by the
   calendar-named key.
10. The first-period Senior Percentage denominator (DNA1 A5 = Cut-off Date Balance) and the
    CPR/CER conversion (A2/A3) carry over as ASSUMED unless Trey says otherwise (DNA2-Q2).
