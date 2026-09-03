# Data inventory — Phase 0 deliverable

Status: **complete, awaiting gate review.** Every field name below comes from the published
Freddie Mac *CRT Reference Pool Disclosure File Layouts*, Version 4.2 (effective July 2026),
retrieved from `https://capitalmarkets.freddiemac.com/crt/docs/pdfs/crt-reference-pool-disclosure-file-layouts.pdf`
and saved (gitignored) as `data/raw/crt-reference-pool-disclosure-file-layouts-v4.2.pdf`
with a `pdftotext -layout` extract beside it. Code enumerations come from the companion
*Reference Pool Glossary* v4.2 (`data/raw/crt-reference-pool-glossary.pdf`). Both are
public. Trey should confirm these are the authoritative versions (open question Q1).

`docs/RECON.md` (the unverified setup notes) was checked line by line against the layout.
Every positional guess it made that is repeated here was confirmed; the ones it got wrong
are listed in §9.

Reproduce every number in this document with:

```bash
.venv/Scripts/python scripts/phase0_profile.py profile.json
.venv/Scripts/python scripts/phase0_reconcile.py
```

The first prints a per-column profile of both months; the second prints the PPM
Appendix A reconciliation and the cross-month checks.

---

## 1. Files

| File | SHA-256 (prefix) | Bytes | Rows | Fields | Encoding |
|---|---|---|---|---|---|
| `data/raw/26DNA1_20260701_lld.txt` | `555c1f34bcec896c` | 22,746,429 | 64,434 | 93 | ASCII, LF, no header |
| `data/raw/26DNA1_20260801_lld.txt` | `80955e2d45b7d474` | 22,743,333 | 64,434 | 93 | ASCII, LF, no header |
| `data/raw/stacr-2026-dna1-ppm.pdf` | `0cd0dea897822b43` | 1,222,025 | 285 pages | — | — |
| `data/raw/stacr-2026-dna1-ppm.txt` | `66594ac4a59a41be` | 1,497,085 | 14,527 lines | — | `pdftotext -layout` |
| `data/raw/crt-reference-pool-disclosure-file-layouts-v4.2.pdf` | `83c424389a915b09` | 429,378 | 8 pages | — | public, Freddie Mac |
| `data/raw/crt-reference-pool-glossary.pdf` | `2281a05850fb360d` | 347,091 | 33 pages | — | public, Freddie Mac |

Full hashes come from `sha256sum data/raw/*` and belong in every run manifest.

File naming follows the layout document's "Loan Level Monthly Disclosure File
(DealName_YYYYMMDD_lld.txt)". Both files are the **monthly** file, not the at-issuance
file; the at-issuance file (same layout, cut-off date values) is not in the download.

Mechanically verified: pipe-delimited, exactly 93 fields on every one of the 128,868
lines, zero ragged rows, no carriage returns, no quoting, no embedded pipes.

## 2. What one row represents

One row is **one Reference Obligation (one mortgage loan in the STACR 2026-DNA1 reference
pool) as of one reporting period (factor date)**. The file is a full snapshot: all 64,434
loans that were in the pool at the Cut-off Date appear in every monthly file, including
loans that have since paid off or been removed. A removed loan keeps its row with
`Current Actual UPB = 0.00`, a Zero Balance Code, a Zero Balance Effective Date, and its
terminal values frozen (the glossary says most fields "remain constant beginning in the
month in which the loan is removed from the Reference Pool"; verified for Loan Age,
Remaining Months, Payment History and Delinquency Status across the two months).

Timing of a row (inferred from the data, to be confirmed against the PPM's "Reporting
Period" definition, PPM p212, in Phase 1 — open question Q6):

- `Period = 202607` contains balances **paid through June 2026**: for 45,607 of the 57,438
  live loans, Due Date of Last Paid Installment is `202606`; the 10,836 current loans
  showing `202607` or later are paid ahead.
- Field 35 (Remaining Months to Legal Maturity) equals `Maturity − Period + 1` for all
  live loans, and field 34 (Loan Age) equals `(Period − 1) − First Payment Date + 1`, both
  exactly as the glossary formulas define them with `Period` as the "current factor date".
- So the July 2026 file is the servicer-reported June activity that feeds the **July 2026
  Payment Date** (the 25th or the next Business Day, PPM p208). This mapping is what the
  waterfall will rely on and must be confirmed in Phase 1.

## 3. Field list (all 93 positions)

Type/length per the layout document. "Fill" is the share of non-empty values,
July / August. Ranges and code sets are what was actually observed, not what the
glossary permits. Money fields are listed to the cent.

| # | Attribute (layout v4.2) | Type | Fill Jul/Aug % | Observed | Notes |
|---|---|---|---|---|---|
| 1 | Period | CCYYMM | 100/100 | 202607 / 202608 | one value per file |
| 2 | Reference Pool Number | AN 6 | 100/100 | `26DNA1` | constant |
| 3 | Loan Identifier | AN 12 | 100/100 | `26DNA1000001` … | unique; identical ID set both months |
| 4 | Amortization Type | A 3 | 100/100 | `FRM` | all fixed-rate |
| 5 | Seller Name | AN 100 | 100/100 | 20 distinct; `OTHER` 16,814 | sellers under 1% of issuance UPB are aggregated as OTHER (glossary) |
| 6 | Property State | A 2 | 100/100 | 54 distinct | |
| 7 | Postal Code (3-Digit) | N 3 | 100/100 | 6–999, 873 distinct | leading zeros dropped (e.g. `6`) |
| 8 | MSA or Metropolitan Division | N 5 | 90.6/90.6 | 10180–49740 | null = non-MSA or unknown (glossary) |
| 9 | First Payment Date | CCYYMM | 100/100 | 202408–202505 | |
| 10 | Maturity Date | CCYYMM | 100/100 | 204602–206606 | 206606 is the one modified loan (term extended); unmodified max 205504 = PPM "April 2055" |
| 11 | Original Loan Term | N 3 | 100/100 | 252–480; 360 for 63,843 | 480 is the modified loan (glossary: updated on modification) |
| 12 | Original Interest Rate | N 2.3 | 100/100 | 4.875–8.625 | |
| 13 | Original UPB | N 9.2 | 100/100 | 24,000–1,944,000; sum 23,552,092,000.00 | rounded to nearest $1,000 (glossary) |
| 14 | UPB at Issuance | N 9.2 | 100/100 | 0.01–1,917,992.96; sum **22,781,151,551.84** | equals the PPM Cut-off Date Balance to the cent |
| 15 | Loan Purpose | AN 1 | 100/100 | P 50,408 / C 8,419 / N 5,607 | |
| 16 | Channel | AN 1 | 100/100 | R / C / B | **changed for 8 loans** Jul→Aug; not immutable |
| 17 | Property Type | AN 2 | 100/100 | SF / PU / CO / MH / CP | |
| 18 | Number of Units | N 2 | 100/100 | 1–4 | |
| 19 | Occupancy Status | AN 1 | 100/100 | P / I / S | |
| 20 | Number of Borrowers | N 2 | 100/100 | 1–5 | |
| 21 | First Time Homebuyer Indicator | AN 1 | 100/100 | Y / N | |
| 22 | Prepayment Penalty Indicator | AN 1 | 100/100 | N | all |
| 23 | Classic FICO | N 4 | 100/100 | 600–832; `9999` ×42 | 9999 = Not Available |
| 24 | Original LTV | N 3 | 100/100 | 61–80 | DNA band |
| 25 | Original CLTV | N 3 | 100/100 | 61–105 | |
| 26 | Original DTI | N 3 | 100/100 | 1–62 | no 999 |
| 27 | MI % | N 3 | 100/100 | 0 | no MI in pool (LTV ≤ 80) |
| 28 | Updated Credit Score at Issuance | N 4 | 100/100 | 9999 | Not Available for all |
| 29 | Special Eligibility Program | A 26 | 10.2/10.2 | H 6,010 / F 556 / R 7 | null = none |
| 30 | Mortgage Insurance Type | N 1 | 100/100 | 7 | Not Applicable |
| 31 | Filler | — | 0/0 | | |
| 32 | Disaster Grace Period | N 2 | 0/0 | | Fixed-Severity pools only |
| 33 | Servicer Name | AN 100 | 100/100 | 24 distinct; `OTHER` ≈10,000 | changed for 332 loans Jul→Aug (transfers; the OTHER threshold is recomputed monthly) |
| 34 | Loan Age | N 3 | 100/100 | 0–22 / 1–23 | +1 for every live loan; frozen at zero balance; one loan reset to 0 by modification |
| 35 | Remaining Months to Legal Maturity | N 3 | 100/100 | 236–480 / 235–479 | = Maturity − Period + 1, verified for all live loans |
| 36 | Adjusted Remaining Months to Maturity | N 3 | 100/100 | 1–479 | curtailment-adjusted; moves irregularly |
| 37 | Current Loan Delinquency Status | AN 2 | 100/100 | 00–06 / 00–07 | 0 = current, 1 = 30–59 days, and so on; no `RA` yet |
| 38 | Payment History | AN 48 | 100/100 | 243 / 327 distinct strings | **24 months × 2 chars, most recent on the right**; `XX` = month before the loan was observed; last 2 chars = field 37 (verified for all delinquent loans) |
| 39 | Current Interest Rate | N 2.3 | 100/100 | 4.875–8.625 | = field 12 except the modified loan (6.500 → 6.125) |
| 40 | Current Actual UPB | N 9.2 | 100/100 | sum **19,675,126,108.17 / 19,443,046,983.78**; 0.00 for 6,996 / 7,563 loans | |
| 41 | Current Interest Bearing UPB | N 9.2 | 100/100 | sum 19,675,031,403.43 / 19,442,850,173.36 | below field 40 for 10 / 15 loans (payment deferral or modification); the gap is the non-interest-bearing deferred UPB |
| 42 | UPB at Time of Removal from the Reference Pool | N 9.2 | 100/100 | nonzero for exactly the zero-balance loans; sum 2,824,391,781.92 / 3,013,722,431.57 | 0.00 for live loans |
| 43 | Zero Balance Code | N 2 | 10.9/11.7 | 01 ×6,974→7,539; 96 ×19→21; 98 ×3→3 | 01 prepaid/matured; 96 confirmed underwriting/major servicing defect before credit event; 98 other. **No credit-event codes (02/03/09/15/16) yet** |
| 44 | Zero Balance Effective Date | CCYYMM | 10.9/11.7 | 202601–202608 | |
| 45 | Underwriting Defect and Major Servicing Defect Settlement Date | CCYYMM | 0.03/0.04 | 202601–202608 | populated on all 19 ZB-96 loans and 3 ZB-01 loans (July) |
| 46 | Modification Flag | A 1 | <0.01 | Y (Jul) → P (Aug), 1 loan | Y current period, P prior |
| 47 | Delinquency Due to Disaster | A 1 | <0.01 | Y ×3 / ×2 | |
| 48 | Due Date of Last Paid Installment | CCYYMM | 100/100 | 202511–202712 | future = paid ahead |
| 49 | Bankruptcy Flag | A 1 | 0.02/0.02 | Y ×12 / ×16 | |
| 50 | Date Referred to Foreclosure | CCYYMM | <0.01 | 202606–202607, 3 / 4 loans | |
| 51 | Net Sales Proceeds | N 9.2 | 0/0 | | loss fields 51–55, 57, 58, 81, 92 populate after a ZB code 02/03/09/15; none yet |
| 52 | MI Credit | N 9.2 | 0/0 | | |
| 53 | Taxes and Insurance | N 9.2 | 0/0 | | |
| 54 | Legal Costs | N 9.2 | 0/0 | | |
| 55 | Maintenance and Preservation Costs | N 9.2 | 0/0 | | |
| 56 | Bankruptcy Cramdown Costs | N 9.2 | 100/100 | 0.00 | |
| 57 | Miscellaneous Expenses | N 9.2 | 0/0 | | |
| 58 | Miscellaneous Credits | N 9.2 | 0/0 | | |
| 59 | Mortgage Insurance Cancellation Indicator | AN 1 | 100/100 | 7 | Not Applicable |
| 60 | Estimated LTV (monthly) | N 3 | 100/100 | 1–999; 999 ×4,538 / 4,585 | updated monthly from July 2026 |
| 61 | Filler | — | 0/0 | | |
| 62 | Updated Credit Score #1 (quarterly) | N 4 | 100/100 | 426–850; 9999 ×1,161 | special Terms of Use apply (glossary) |
| 63 | Updated Credit Score #2 (quarterly) | N 4 | 100/100 | 9999 | discontinued Mar-2024 |
| 64 | Number of Modifications | N 2 | 100/100 | 0 ×64,433; 1 ×1 | |
| 65 | Modification Program | AN 1 | <0.01 | F (Flex), 1 loan | |
| 66 | Modification Type | A 1 | <0.01 | F = Rate, Term & Deferred Amount | |
| 67 | Modification First Payment Date | CCYYMM | <0.01 | 202607 | |
| 68 | Modification DTI | N 3 | <0.01 | 999 | |
| 69 | Total Capitalized Amount | N 9.2 | <0.01 | 5,738.21 | |
| 70 | Interest Rate Step Indicator | A 1 | <0.01 | N | |
| 71–80 | First … Fifth Step Rate Adjustment Date / Step Rate | CCYYMM / N 2.3 | 0/0 | | no step-rate modifications |
| 81 | Delinquent Accrued Interest | N 9.2 | 0/0 | | credit-event field |
| 82 | Current Period Modification Costs | N 9.2 | 0.02/0.02 | 10 / 15 loans; sum 537.82 / 1,101.62 | exactly the loans with deferred UPB (fields 40 ≠ 41) |
| 83 | Updated Credit Score #3 | N 4 | 0/0 | | reserved |
| 84 | Property Valuation Method | N 1 | 100/100 | 2 ×48,950; 1 ×14,791; 4 ×693 | 1 ACE, 2 appraisal, 4 ACE+PDR |
| 85 | Group Number | N 10 | 100/100 | 1 | single group |
| 86 | Enhanced Relief Refi Indicator | N 1 | 100/100 | 7 | Not Applicable |
| 87 | Borrower Assistance Plan | A 1 | 0.08/0.12 | F ×44→55, R ×6→6, T ×2→14 | forbearance / repayment / trial |
| 88 | Payment Deferral Flag | A 1 | 0.01/0.02 | C ×5→5, P ×4→9 | current / prior period |
| 89 | Distressed Principal Balance Flag | A 1 | 100/100 | Y ×131 / ×146 | feeds the Delinquency Test directly |
| 90 | Temporary Subsidy Buydown Plan Type | N 1 | 100/100 | 9 ×61,921; 2 ×1,467; 1 ×829; 3 ×217 | 4.74% of cut-off UPB on buydowns = PPM p62 |
| 91 | VantageScore 4.0 | N 4 | 100/100 | 9999 | not yet populated for any CRT |
| 92 | Actual Loss | N 9.2 | 0/0 | | new in v4.2; credit-event field |
| 93 | Cumulative Modification Costs | N 9.2 | 100/100 | 0.00 except 10 / 15 loans; sum 724.31 / 1,825.93 | new in v4.2 |

Empty-in-both-months columns: 31, 32, 51–55, 57, 58, 61, 71–81, 83, 92. All are either
fillers, Fixed-Severity-only, step-rate-modification, or credit-event loss fields. None is
"unused"; 51–58, 81 and 92 are the loss components the model consumes once credit events
occur.

## 4. Reconciliation to the deal-level disclosure

The only deal-level disclosure in hand is the PPM. Its Appendix A ("Selected Reference
Obligation Data as of the Cut-off Date", p220) and Glossary (p194) were reconciled to the
July file using the cut-off-date fields (13, 14 and the static origination fields). All of
this is printed by `scripts/phase0_reconcile.py`.

| Statistic | Loan-level file | PPM | Source page | Result |
|---|---|---|---|---|
| Number of Reference Obligations | 64,434 | 64,434 | p220 | exact |
| Aggregate Original Principal Balance | 23,552,092,000.00 | 23,552,092,000 | p220 | exact |
| Cut-off Date Balance (sum field 14) | 22,781,151,551.84 | 22,781,151,551.84 | p194 | **exact to the cent** |
| Average original balance | 365,522.74 | 365,522.74 | p236 | exact |
| Average cut-off balance | 353,557.93 | 353,557.93 | p236 | exact |
| WA original mortgage rate | 6.7934% | 6.793% | p220 | match |
| WA original term | 359.7 | 360 | p220 | match |
| WA remaining term at cut-off | 349.4 (orig term − age) | 349 | p220 | match; the PPM uses term − age, not maturity − date (350.4) |
| WA loan age at cut-off | 10.31, range 8–17 | 10, range 8–17 | p220 | match |
| WA original LTV / CLTV | 75.52 / 75.74 | 76 / 76 | p220 | match |
| WA DTI (non-zero) | 38.49 | 38 | p220 | match |
| WA credit score (non-9999) | 759.2, max 832 | 759, range 600–832 | p220 | match |
| Top 5 states | CA 11.11, FL 9.41, TX 9.16, NY 5.98, NJ 3.69 | same | p220 | exact |
| Max 3-digit zip concentration | 1.66% | 1.66% | p220 | exact |
| Cash-out refinance share | 10.90% | 10.90% | p38 | exact |
| Condo / co-op / manufactured | 8.62 / 0.35 / 0.55% | 8.62 / 0.35 / 0.55% | p61 | exact |
| Temporary buydown share | 4.74% | 4.74% | p62 | exact |
| Latest maturity (unmodified) | April 2055 | April 2055 | p220 | exact |

Conclusion: fields 6, 7, 9, 10, 11, 12, 13, 14, 15, 17, 23, 24, 25, 26 and 90 are
confirmed by two independent sources (the layout document and the PPM statistics). The
files are the complete cut-off pool with no loans missing.

The monthly **deal-level payment date statements** (class balances, factors, cumulative
losses, test results) are *not* in the dataset. See gap G4 and open question Q4.

## 5. Cross-month movement, July → August 2026

| Measure | Value |
|---|---|
| Loan ID set | identical, 64,434 both months |
| Current Actual UPB | 19,675,126,108.17 → 19,443,046,983.78 (−232,079,124.39, −1.180%) |
| Loans going to zero | 567; July UPB 189,330,649.65; ZB codes 01 ×565, 96 ×2 |
| Loans whose UPB fell | 55,920 (scheduled amortization and curtailments) |
| Loans whose UPB was unchanged | 8,483 (7,563 already at zero + 920 live, mostly 30+ days delinquent) |
| Loans whose UPB **rose** | **31**; 5 explained by a Modification or Payment Deferral flag; **26 unexplained**, increases from $25.00 to $40,564.95 |
| Live loans 30+ days delinquent | 369 (Jul) → 392 (Aug) |
| Distressed Principal Balance Flag = Y | 131 → 146 (all live loans) |
| Deferred (non-interest-bearing) UPB | 94,704.74 (10 loans) → 196,810.42 (15 loans) |

Fields that change between months for at least one loan: 1, 16, 33, 34, 35, 36, 37, 38,
40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 60, 82, 87, 88, 89, 93. Everything else was
byte-identical for all 64,434 loans. Field 16 (Channel) changing for 8 loans and field 33
(Servicer) for 332 means a loader cannot treat every origination field as immutable; this
is open question Q3.

The 26 unexplained balance increases matter for the brief's "balance continuity — assert,
don't warn" rule. They are Freddie Mac's reported values; the engine cannot correct them
and must not silently accept or silently drop them. Q3 asks Trey how the loader should
treat them.

## 6. Payoff and delinquency experience so far (informational only)

Voluntary payoffs (ZB code 01) by Zero Balance Effective Date, as reported in the July file:

| 202601 | 202602 | 202603 | 202604 | 202605 | 202606 | 202607 |
|---|---|---|---|---|---|---|
| 1,072 | 1,518 | 1,856 | 1,124 | 722 | 636 | 46 |

The August file adds 567 removals, 532 of them dated 202607 and 35 dated 202608, so a
month's payoffs are mostly reported in the following file. A month-by-month realized CPR
can be computed from these, but seven observations on a ten-month-old pool are not a
prepayment model. The brief is right: **scenario inputs carry all the behavioral
assumptions.**

Credit experience: **zero credit events** (no ZB codes 02/03/09/15/16), zero Actual Loss,
zero liquidation proceeds. Loss severity cannot be estimated from this dataset at all.
The delinquency pipeline is 392 loans 30+ days (0.69% of live loans) in August, 13 of
them 150+ days (status 05–07). Delinquency transitions July→August are printed by the
reconcile script; with one transition observed, no roll-rate matrix can be estimated.

## 7. What the PPM's tables were actually computed on

This is the most important Phase 0 finding for the tie-out.

PPM p136, "Assumptions Relating to Weighted Average Life Tables, Declining Balances
Tables, Credit Event Sensitivity Tables…", Modeling Assumption (a):

> "The Reference Obligations consist of the assumed mortgage loans having the
> characteristics shown in Appendix C"

Appendix C (p255) is a table of **31 assumed loan groups** with Original Balance,
Outstanding Principal Balance, Remaining Term, Original Term and Per Annum Interest Rate.
The PPM's WAL, Declining Balances and Credit Event Sensitivity tables were run on those 31
rep-lines, **not on the 64,434-loan file**. Other assumptions that bind the tie-out
(p136–137): (c) level-pay amortization from balance, rate and remaining term; (d) the
WAL and Credit Event Sensitivity tables *do* include credit events at the stated CER with
a Preliminary Principal Loss Amount of 25% of the Credit Event Amount, while the Declining
Balances tables assume none; (e) the Delinquency Test is always satisfied; (f)/(g)
payments and full prepayments on the last day of each month starting January 2026;
(h) no curtailments; (m) no early redemption except where a table says so, in which case
on the earlier of the February 2031 Payment Date and the 10% clean-up; (r) SOFR flat at
3.65786%.

Consequences:

1. The tie-out input is Appendix C, transcribed in Phase 1, not this dataset. The pool
   engine must accept rep-line inputs. That also answers the brief's "loan-level and/or
   representative-line" question for Phase 2: rep-line for the tie-out, loan-level (or
   loan-level collapsed to rep-lines by the same method) for actual-pool projections.
   Open question Q2.
2. The brief's statement that PPM tables assume "default and severity (often zero)" is
   true only for the Declining Balances tables. The WAL tables carry a CER and a 25%
   preliminary loss. The ppm-analyst must transcribe each table's own CER/RM/CPR grid.
3. The dataset is still needed for everything the PPM does not do: projecting the
   *actual* pool from a factor date, with actual delinquencies, modifications and
   removals.

## 8. Gap list — what the cashflow model needs that the dataset does not contain

| ID | Needed for | Present? | Where it must come from | Severity |
|---|---|---|---|---|
| G1 | Tie-out pool (Appendix C, 31 groups) | No | PPM p255, Phase 1 transcription | Blocking for Phase 4 |
| G2 | Deal structure: class balances, coupons, margins, test thresholds, allocation rules | No | PPM, Phase 1 YAML | Blocking for Phase 3 |
| G3 | Index path (30-day Average SOFR) | No | Scenario input; PPM assumes 3.65786% flat | Scenario input, not a data gap |
| G4 | Current deal state at the projection start: class balances after the Mar–Aug 2026 Payment Dates, cumulative Credit Event Net Loss, test outcomes, Senior/Subordinate percentages | No | Freddie Mac monthly payment date statements for STACR 2026-DNA1 (public, CRT site). Without them an "actual pool" run must re-run the waterfall from closing using only the loan file, and cannot be checked against what actually paid | High; needed before any actual-pool projection is trustworthy |
| G5 | Accounting Net Yield per loan (Original/Current Accrual Rate = min(ANY, note rate − 0.35%), PPM p194/p207) | No | Not disclosed. Needed for Modification Loss/Gain Amounts and the delinquent-interest term of Credit Event Net Loss. Phase 1 must check whether the PPM states an assumed ANY for its RM tables | Medium; affects modification scenarios and RM>0 tables |
| G6 | Scheduled monthly P&I payment | No | Derived from balance, rate and remaining term (the PPM's own assumption (c)); the glossary's RMM formula references a "Monthly P&I Payment" that is not disclosed | Low; the derivation is standard and matches the PPM method |
| G7 | Loss severity / recovery experience | No (zero credit events) | Scenario input only | Structural; state plainly in every output |
| G8 | Prepayment experience adequate to fit a model | No (7 monthly observations) | Scenario input only | Structural |
| G9 | Delinquency roll rates | No (one observed transition) | Scenario input only | Structural |
| G10 | Reporting Period ↔ Payment Date mapping (which file feeds which Payment Date) | Inferred (§2) | PPM p212 "Reporting Period", Phase 1 | Must be confirmed before Phase 2 |
| G11 | At-issuance (cut-off) loan file | No, but reconstructible: field 14 plus the static fields equal the cut-off pool exactly (§4) | Loan-level monthly file | Not a gap in practice |

Needed and **present** (so the model can use them directly): loan identifier; original,
issuance, current and interest-bearing UPB; original and current rate; original term,
remaining term, maturity, first payment date; delinquency status and 24-month history;
Zero Balance Code and date; UPB at removal; Distressed Principal Balance Flag; bankruptcy
flag; foreclosure referral date; modification program/type/first payment date/capitalized
amount; payment deferral flag; borrower assistance plan; and the full set of loss
component fields (51–58, 81, 82, 92, 93), which are empty today only because nothing
has liquidated.

## 9. Corrections to `docs/RECON.md`

| RECON said | Layout v4.2 says | Impact |
|---|---|---|
| field 9 "first payment / origination" | First Payment Date | fine |
| field 14 "UPB at cutoff" | UPB at Issuance | same thing; confirmed by the cut-off balance match |
| field 38 "48-char delinquency history string" | Payment History: 24 months × 2 characters, most recent on the right | RECON implied 48 monthly characters; wrong granularity |
| field 42 "deferred UPB" | **UPB at Time of Removal from the Reference Pool** | wrong; the deferred UPB is field 40 − field 41 |
| fields 60/62 "refreshed score-like" | 60 = Estimated LTV (monthly), 62 = Updated Credit Score #1 | 60 is not a score |
| fields 82/93 "rate-like" | 82 = Current Period Modification Costs, 93 = Cumulative Modification Costs (dollars) | wrong; these are modification-loss dollars for the 15 deferral/mod loans |
| "columns fully empty: … 92" | 92 = Actual Loss (new in v4.2) | correct that it is empty; it is a credit-event field, not unused |
| WAC 6.7650% (current, by current UPB) | consistent; the PPM's 6.793% is the cut-off WA original rate by issuance UPB | different weighting, both right |

Everything else in RECON was confirmed.

## 10. Environment facts recorded during Phase 0

- Python 3.13.12 via `uv 0.10.6`; venv at `.venv`; `pytest -q` runs clean on the empty suite (exit 5 = no tests collected).
- `pdftotext` (poppler) is available in Git Bash at `/mingw64/bin/pdftotext`.
- Microsoft Excel is installed (`C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE`); LibreOffice is not. Relevant to the Phase 5 requirement that a test recalculates the exported workbook.
- The project lives inside OneDrive (`C:\Users\jjdeg\OneDrive\Desktop\crt-cashflow-engine`); `data/raw` is 48 MB and syncs.
