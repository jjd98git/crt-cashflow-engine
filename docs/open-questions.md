# Open questions

Format: `ID | phase | raised-by | question | why blocked | what was tried | options + recommendation`

Every entry must carry a recommendation. Do not hand Trey a bare question.

---

## Q1 | Phase 0 | setup | CLOSED 2026-09-03 — Trey confirmed layout v4.2

**Question.** The Freddie Mac CRT loan-level file layout / data dictionary was not in the
downloaded zip. The files have no header row and 93 positional fields.

**What was done.** Freddie Mac publishes the layout. The Manager retrieved the public
*CRT Reference Pool Disclosure File Layouts* v4.2 (effective July 2026) and the companion
*Reference Pool Glossary* v4.2 from `capitalmarkets.freddiemac.com` and saved both PDFs and
their text extracts under `data/raw/` (gitignored; hashes in `docs/data-inventory.md`).
The layout defines exactly 93 fields; every position was cross-checked against observed
values and 15 of them independently against PPM Appendix A statistics, all matching.

**Remaining ask.** Trey confirms v4.2 is the correct version for the 2026-07 and 2026-08
reporting periods (v4.2 introduced fields 92 Actual Loss and 93 Cumulative Modification
Costs in July 2026; both are present in the files, which is consistent). If a different
version applies, drop it in `data/raw/` and Phase 0 will be re-run against it.

**Recommendation.** Confirm v4.2. No field name is used in code until this is confirmed.

---

## Q2 | Phase 0 | manager | CLOSED 2026-09-03 — option 1 adopted (rep-line engine; tie-out on Appendix C)

**Question.** PPM Modeling Assumption (a) (p136) states the WAL / Declining Balances /
Credit Event Sensitivity tables were computed on "the assumed mortgage loans having the
characteristics shown in Appendix C" — 31 rep-line groups (p255). The brief (§1 done
criterion 1, §3 Phase 2, §7) reads as if the loan-level dataset were the tie-out input.

**Why it matters.** A loan-level projection will not reproduce the PPM tables to ±0.02
years WAL by construction; the PPM's own numbers came from 31 groups.

**Options.**
1. **(Recommended)** Phase 2 pool engine takes rep-line inputs as its primary interface.
   Tie-out (Phase 4) runs on the Appendix C transcription. Actual-pool projections load the
   loan-level file and either project loan-by-loan or collapse to rep-lines by a documented
   method; both are inputs to the same engine.
2. Loan-level only, and accept that the tie-out is approximate. Not acceptable under §7.
3. Rep-line only, never loan-level. Loses delinquency/modification detail for actual runs.

---

## Q3 | Phase 0 | manager | CLOSED 2026-09-03 — option 1 adopted (hard single-file validation; reconcile step with exceptions report)

**Question.** Between the July and August files, Current Actual UPB *rose* for 31 loans.
5 carry a Modification or Payment Deferral flag; 26 do not (increases from $25.00 to
$40,564.95; IDs printed by `scripts/phase0_reconcile.py`). Channel (field 16) also
changed for 8 loans and Servicer (field 33) for 332. The brief's loader rule is "balance
continuity … assert; don't warn."

**Why blocked.** These are Freddie Mac's reported values. A hard assert makes the August
file unloadable; silently accepting contradicts "fail loud"; "fixing" them is fabrication.

**What was tried.** Looked for an explaining flag (fields 46, 47, 87, 88) and for a
delinquency-status change; only 5 of 31 are explained. No further diagnosis is possible
from the data alone.

**Options.**
1. **(Recommended)** Single-file validation is hard (row count, field count, types, ID
   uniqueness, pool balance vs a stated total). Cross-month checks are a separate
   `reconcile` step that produces an exceptions report listing every loan whose balance
   rose, whose static field changed, or whose zero-balance state reversed, and that FAILS
   only on structural breaks (ID set changes, field count). Projection runs start from a
   single factor date and carry the exceptions report in the manifest.
2. Hard-fail on any balance increase without an explaining flag. August is then unusable
   until Freddie Mac corrects the data, which may never happen.
3. Treat increases as data corrections and use the later value. This is inference and is
   ruled out.

---

## Q4 | Phase 0 | manager | OPEN — 2026-09-08: Trey asked whether the 25th payment date is what is needed; it is not. Needed: the monthly Payment Date statements (class balances, factors, losses) published on Freddie Mac's CRT site after each Payment Date. Manager to attempt sourcing them directly — Trey to source the Mar–Aug 2026 payment date statements; not blocking Phases 1–4

**Question.** Six Payment Dates (March–August 2026) have occurred. The class balances,
factors, cumulative Credit Event Net Loss and test outcomes after those dates exist only
in Freddie Mac's monthly STACR 2026-DNA1 payment date statements (public, CRT site), which
are not in the download. Gap G4 in the inventory.

**Why it matters.** Any "actual pool" projection starting from the August 2026 factor date
needs the tranche state as of that date. Re-deriving it by running the waterfall from
closing on the loan file is possible but unverifiable without the statements. The
statements would also give a second, empirical tie-out of the waterfall against six
months of real payments, independent of the PPM tables.

**Recommendation.** Trey sources the March–August 2026 payment date statements (and the
at-issuance loan-level file if available) and drops them in `data/raw/`. Not blocking for
Phases 1–4, which use the PPM; needed before Phase 6 scenario runs on the actual pool.


**2026-09-08 sourcing attempt (Manager).** Freddie Mac's STACR deal-documents page lists only the offering and trust documents for 2026-DNA1 and names U.S. Bank as Indenture Trustee; the monthly Payment Date statements are published on the U.S. Bank trust gateway (login required) and deal-level monthly data on Clarity (registration required). Neither is reachable from this session. Trey holds the credentials; the statements for the March to August 2026 Payment Dates are what actual-pool mode and Q20 need.

---

## Q5 | Phase 0 | manager | CLOSED 2026-09-03 — recommendation adopted; ppm-analyst checks for an assumed ANY in Phase 1

**Question.** Original and Current Accrual Rate are "the lesser of Accounting Net Yield
and the mortgage rate minus 0.35%" (PPM p194, p207). They drive Modification Loss/Gain
Amounts and the delinquent-interest term of Credit Event Net Loss. Accounting Net Yield is
not a field in the loan-level file (gap G5).

**Recommendation.** Phase 1 ppm-analyst checks whether the PPM states an assumed ANY (or
an assumed accrual-rate haircut) in the Modeling Assumptions for its RM tables. If it does,
use it for the tie-out and expose it as a scenario input for actual runs. If it does not,
escalate immediately: RM>0 WAL tables cannot be tied without it.

---

## Q6 | Phase 0 | manager | CLOSED 2026-09-03 — recommendation adopted; Reporting Period transcribed in Phase 1, mapping stated in spec before Phase 2

**Question.** The inventory infers that the `202607` file (paid through June 2026) feeds
the July 2026 Payment Date. The PPM's "Reporting Period" definition (p212) has a two-part
structure (collections vs prepayments vs delinquency status, with different windows).

**Recommendation.** Phase 1 ppm-analyst transcribes the Reporting Period definition
verbatim and the structured-cashflow-expert states the file→Payment Date mapping in the
spec before Phase 2. Trey can short-circuit this if he knows the convention.

---

## Q7 | Phase 1 | ppm-analyst | CLOSED 2026-09-03 — option 1 adopted by Trey (ANY: none for tie-out; required servicing-fee input for actual runs) — Accounting Net Yield is not in the PPM (closes Q5; needs a decision for actual-pool runs)

**Question.** Q5 asked whether the PPM states an assumed Accounting Net Yield (ANY). It does
not. The only definition is p187: "'Accounting Net Yield' with respect to each Payment Date
and any Reference Obligation, means the related mortgage rate less the related servicing fee
rate." Modeling Assumptions (a)–(s) (p136–137) and Appendix C are silent on ANY and on any
servicing fee. Appendix E (p268) says only that Freddie Mac "generally require[s] that
servicers retain a minimum servicing fee of at least 0.25% per annum" — a Guide statement,
not a modeling assumption and not loan-level data.

**Why it matters.** ANY enters the Original and Current Accrual Rates (p207, p194: "the lesser
of (i) the related ... Accounting Net Yield and (ii) the related ... mortgage rate ... minus
0.35%"), which drive Modification Shortfall/Excess (p203) and the delinquent-interest term of
Credit Event Net Loss (p193).

**What was tried.** (1) Full-text search of the extract for "Accounting Net Yield", "servicing
fee", "accrual rate": hits only at p187, p193, p194, p203, p207, p266–268. (2) Algebra on the
definitions. For a pure rate modification (the only kind the RM tables assume, (k)(y)), the
interest-bearing UPB equals the UPB, so Shortfall = UPB/12 × (Original Accrual Rate − Current
Accrual Rate). With servicing fee f and rate r, Original = r − max(f, 0.35%) and Current =
(r − RM) − max(f, 0.35%), so Shortfall = UPB × RM / 12 for every f. ANY cancels. For Credit
Events the tables stipulate the loss directly ((d): "the Preliminary Principal Loss Amount is
equal to 25% of the Credit Event Amount"), so the delinquent-interest term is never computed.
Conclusion: the RM>0 WAL tables CAN be tied without an ANY input.

**Options.**
1. **(Recommended)** Tie-out: no ANY input; the engine's modification-loss unit test asserts
   the cancellation above. Actual-pool runs: `servicing_fee_rate` (or ANY) is a required
   scenario input with no default; a run that needs it and lacks it fails loud. It is needed
   for Credit Event Net Loss delinquent interest and for forbearance / Payment Deferral
   modifications (interest-bearing UPB < UPB), where the cancellation does not hold.
2. Default every loan to the 0.25% Guide minimum (p268). That is an inference about the pool,
   not a fact; it also makes Accrual Rate = rate − 0.35% for every loan, which is the same
   result as option 1 for rate mods but silently wrong for loans with fees above 0.35%.
3. Source servicing fee from Freddie Mac's payment date statements or loan-level file if any
   later version carries it (v4.2 does not; gap G5).

---

## Q8 | Phase 1 | ppm-analyst | CLOSED 2026-09-03 — option 1 adopted by Trey (Cut-off Date Balance on first Payment Date, prior Reporting Period UPB thereafter) — First-Payment-Date denominators for Senior Percentage and the Delinquency Test

**Question.** Senior Percentage (p214) divides by "the aggregate UPB of the Reference
Obligations in the Reference Pool at the end of the previous Reporting Period". The
Delinquency Test (p194) uses "the aggregate UPB of the Reference Obligations as of the
preceding Payment Date". For the March 2026 Payment Date there is no previous Reporting Period
and no preceding Payment Date, and "as of the preceding Payment Date" is not itself a defined
quantity for later dates either (UPB is a Reporting-Period-end figure).

**Why it matters.** Senior Percentage sets the senior/subordinate split of every Stated
Principal dollar from the first period; a wrong first-period denominator shifts the M-1
window. The Delinquency Test never binds in the PPM tables (assumption (e)) but must be
implemented for actual runs.

**What was tried.** Searched the Description of the Notes and Glossary for a first-period
carve-out (none). Checked p24: "the aggregate of the initial Class Notional Amounts of all
Classes of Reference Tranches will equal the Cut-off Date Balance", so on the first Payment
Date (A-H + A-1 + A-1H) / Cut-off Date Balance = 95.200% = 100% − 4.800% initial
subordination (Table 3), which is internally consistent.

**Options.**
1. **(Recommended)** First Payment Date: denominator = Cut-off Date Balance ($22,781,151,551.84)
   for both definitions. Later Payment Dates: Senior Percentage uses the UPB at the end of the
   Reporting Period related to the preceding Payment Date; "UPB as of the preceding Payment
   Date" in the Delinquency Test is read as the same figure. Record as a spec convention and
   verify against the first months of the Declining Balances tables.
2. Use the UPB at the end of the *current* Reporting Period. Contradicts "previous" and would
   make the Senior Percentage depend on the same period's prepayments.

---

## Q9 | Phase 1 | ppm-analyst | CLOSED 2026-09-03 — option 1 adopted by Trey (aggregate of both Appendix G columns, per Payment Date, no carry-forward) — Class A-1 Reduction Amount: "aggregate" reading and shortfall carry-forward

**Question.** p190: "'Class A-1 Reduction Amount' with respect to any Payment Date is an
amount equal to: (A) up to and including the thirty-sixth (36th) Payment Date, the aggregate
amount specified for such Payment Date on Appendix G to this Memorandum; and (B) thereafter,
100% of the Senior Reduction Amount (excluding any Recovery Principal)". Appendix G (p285)
shows two dollar columns (A-1 portion $10,346,250.00 / A-1H portion $545,988.08 for periods
1–12; $4,138,500.00 / $218,395.23 for 13–36) and marks the percentages "for illustrative
purposes only". The Senior Reduction Amount first priority (p107) allocates "an amount up to
the Class A-1 Reduction Amount to the Class A-1 and Class A-1H Reference Tranches, pro rata".
Two things are unstated: (i) whether "aggregate amount" is the sum of the two columns
($10,892,238.08 / $4,356,895.23) — the YAML and register use that reading because the amount
is then split pro rata between A-1 and A-1H, which reproduces the two columns exactly; (ii)
whether any shortfall (Senior Reduction Amount smaller than the scheduled amount, or a period
in which the Class A-1 Cumulative Net Loss Test fails) carries forward.

**Why it matters.** Under the PPM scenarios Stated Principal is far larger than the schedule
(roughly $200MM+/month at 10% CPR on $22.8bn), so the cap binds and the reading does not
affect the tie-out. It does affect stress scenarios and any period in which the A-1 CNL test
fails and then passes again.

**What was tried.** Searched for "cumulative", "carry", "shortfall" near the definition and in
the Senior Reduction Amount allocation text: no carry-forward language.

**Options.**
1. **(Recommended)** Per-Payment-Date amount, no carry-forward: the definition is "with respect
   to any Payment Date" with no cumulative term, and (B) is also a per-date quantity. Aggregate
   = both Appendix G columns. Confirm with Trey; implement as a register-cited constant.
2. Cumulative target (unpaid schedule accrues and is paid when available). Requires language
   the PPM does not contain.

---

## Q10 | Phase 1 | ppm-analyst | CLOSED 2026-09-03 — option 1 adopted by Trey (two month-ends of amortization and prepayment in the March 2026 period) — When do prepayments start in the PPM tables: January 2026 or the Closing Date?

**Question.** Two statements pull in different directions. Table 1 footnote (1) (p11):
"prepayments occur at the Pricing Speed of 10% CPR, calculated from the Closing Date".
Modeling Assumption (g) (p136): "principal prepayments in full on the Reference Obligations
are received, together with 30 days' interest thereon, on the last day of each month
beginning in January 2026" — and (f) says the same for scheduled payments. The Closing Date is
February 17, 2026, so (f)/(g) put two month-ends (January 31 and February 28, 2026) before the
first Payment Date, which matches the March 2026 Reporting Period ("from and including
January 1, 2026 through and including February 28, 2026" for collections; "January 6, 2026
through and including March 3, 2026" for full prepayments, p212) and (k)(z), which sums
modification losses "calculated as of January 1, 2026" and "as of February 1, 2026".

**Why it matters.** Whether the first Payment Date carries one or two months of CPR
prepayment changes every first-period balance in the Declining Balances tables and shifts
WALs by roughly a month's worth of principal. "First and last principal payment date: exact
month match" (brief §7) is sensitive to this.

**What was tried.** Read both passages and the Reporting Period definition twice; looked for
a reconciling sentence (none). The WAL definition (p219) measures "from the date of issuance",
which is a plausible referent for "calculated from the Closing Date" that does not conflict
with (g).

**Options.**
1. **(Recommended)** Follow (f)/(g)/(k)(z) and the Reporting Period literally: two months of
   scheduled amortization and two month-end CPR prepayments (Jan 31, Feb 28, 2026) in the
   March 2026 Payment Date; read "calculated from the Closing Date" as the WAL clock, not the
   prepayment start. Three independent passages support it.
2. Prepayments begin only after the Closing Date (one month of prepayment, two of
   amortization, in the first period).
3. One month of everything in the first period (ignores the two-month Reporting Period).
The Declining Balances tables' first rows will discriminate between the options; the tie-out
diagnostic list should test this before the accrual convention.

---

## Q11 | Phase 1 | ppm-analyst | CLOSED 2026-09-03 — option 1 adopted by Trey (SMM convention on beginning balance net of scheduled principal, credit events before prepayments; ASSUMED until tie-out proves it) — CPR and CER monthly conversion and balance basis are not stated

**Question.** The PPM defines CPR as "a specified constant annual rate" that "is converted to
an equivalent monthly rate" (p137, p192) and CER as "a constant rate of Reference Obligations
become Credit Event Reference Obligations each month relative to the then-outstanding
aggregate principal balance" with "A Credit Event Rate of 1% assumes Reference Obligations
become Credit Event Reference Obligations at an annual rate of 1%" (p138, p190). It does not
state (i) the conversion formula (1 − (1 − annual)^(1/12) versus annual/12), (ii) whether the
monthly rate applies to the balance before or after that month's scheduled principal, or
(iii) the order of credit events and prepayments within a month. Brief convention C12 assumed
"CPR on beginning-of-period scheduled balance; CDR on the same basis"; the PPM neither
confirms nor contradicts the basis and replaces CDR with CER.

**Why it matters.** Each choice moves decrement-table percentages by more than the ±0.25pp
tolerance over long horizons and moves the last principal payment month.

**What was tried.** Searched the extract for "SMM", "single monthly", "beginning of", "after
scheduled", "equivalent monthly": no further specification.

**Options.**
1. **(Recommended)** Implement the standard Bond Market Association convention as the
   starting point — SMM = 1 − (1 − CPR)^(1/12) and monthly CE rate = 1 − (1 − CER)^(1/12),
   both applied to the beginning-of-month balance net of that month's scheduled principal,
   credit events removed before prepayments — and register it as ASSUMED until the tie-out
   proves it. The Declining Balances tables (CER = 0) isolate the CPR convention first; the
   WAL tables then isolate CER. Any mismatch is diagnosed by switching conventions one at a
   time, never by tuning.
2. Simple annual/12 conversion. Non-standard; test only if option 1 fails.
3. Apply rates to the balance before scheduled principal. Test only if option 1 fails.

---

## Q12 | Phase 2 | structured-cashflow-expert | CLOSED 2026-09-07 — A10 confirmed by Trey — Do Tranche Write-down Amounts count in the WAL?

**Question.** The PPM (p219) defines WAL as the time "until its balance is reduced to zero"
and gives no formula. **Reading adopted (A10, ASSUMED):** yes, the WAL weight on a Payment
Date is the net reduction of the Class Principal Balance (principal paid + write-downs −
write-ups). **Evidence:** M-2B WAL at 0% CPR is 19.29 / 8.75 / 1.61 at CER 0 / 1% / 5% to
Scheduled Maturity (p140); principal alone cannot retire $37.85MM in 1.6 years.
**Recommendation.** Confirm A10; the engine tie-out at CER > 0 is the test.

---

## Q13 | Phase 2 | structured-cashflow-expert | CLOSED 2026-09-07 — A9 confirmed by Trey — WAL day count and origin

**Question.** No day count is stated. **Reading adopted (A9, ASSUMED):** 30/360 from the
Closing Date 2026-02-17 to the unadjusted 25th, t[n] = (30n + 8)/360. **Evidence:** A-1's
schedule is fixed by Appendix G; 30/360 gives 1.587 → printed 1.59, actual/365 gives 1.583
→ 1.58; 48/48 CER-0 cells tie with 30/360, 42/48 with actual/365.
**Recommendation.** Confirm A9.

---

## Q14 | Phase 3 | structured-cashflow-expert | CLOSED 2026-09-07 — A11 confirmed by Trey — UPB basis of the 10% clean-up in Modeling Assumption (m)

**Reading adopted (A11, ASSUMED):** the aggregate UPB at the end of the Reporting Period
related to the Payment Date. Not exercised in the PPM grid before Payment Date 60 at CPR
≤ 35%; matters for actual-pool and high-CPR runs. **Recommendation.** Confirm A11.

---

## Q15 | Phase 3 | structured-cashflow-expert | CLOSED 2026-09-07 — A7, A8, A12 confirmed by Trey — Rounding of the hypothetical structure and of rep-line amounts

**Reading adopted (A12, A8, A7, ASSUMED):** the PPM's p99 rounding rule (cent; 1/100,000 of
a percentage point) applied to every structure amount and percentage; Note/H pair splits by
exact ratio with the Note leg rounded and the H leg the remainder; rep-line amounts rounded
to the cent at each step. **Evidence:** A8 reproduces both Appendix G columns exactly; A12
makes the Payment Date 1 Subordinate Percentage exactly 3.52500%, a knife-edge against the
3.525% Minimum Credit Enhancement threshold. **Recommendation.** Confirm.

---

## Q16 | Phase 4 | structured-cashflow-expert | CLOSED 2026-09-07 — Trey: round-match (A13) is the pass criterion; ±0.25 pp stays a reported flag — Decrement-table pass criterion vs whole-percent printing

**Question.** The brief's ±0.25pp tolerance is tighter than the PPM's whole-percent print
(p141 dagger). A correct model gives 23.47 where the PPM prints 23 (M-1, 25% CPR, Feb 2027).
**Reading adopted (A13, ASSUMED):** primary pass = model rounded half-up to the printed
precision equals the printed value; the ±0.25pp result is reported as a flag.
**Recommendation.** Trey confirms which criterion is the definition of done.

---

## Q17 | Phase 4 | structured-cashflow-expert | SUPERSEDED 2026-09-07 by Q21 (the residual was the pre-Q21 A2/A3 convention; engine now 336/336 and 96/96) — was OPEN 2026-09-03 — Residual +0.01 to +0.03 on some CER > 0 WAL cells

**Question.** The spec author's scratch replication with A2 gives, over 96 CER > 0 cells,
60 exact, 33 within ±0.01, 2 at +0.02 and 1 at +0.03 (model longer). **Reading adopted:**
keep A2; escalate with the per-cell table if the engine shows any cell outside ±0.02, and
only then test the 03-tieout.md §5 item-7 alternatives one at a time.
**Recommendation.** Accept for now; revisit with engine numbers.

---

**Correction to Q8 (2026-09-03, structured-cashflow-expert).** The narrative in Q8 said
the initial Senior Percentage is 95.200%. It is 96.47500%: A-1 and A-1H are senior for the
Senior Percentage (YAML principal.senior_percentage). Table 3's 4.800% is subordination
below A-H. The adopted option is unchanged.

---

## Q18 | Phase 3 | fintech-dev | CLOSED 2026-09-08 — option 1 adopted by Trey (split by cumulative unreimbursed write-downs) — Tranche Write-up split for a Note/H pair whose prior balances are both zero

**Question.** Spec 02 section 5 requires the Tranche Write-up Amount to be split between a
Note tranche and its H tranche "pro rata by Class Notional Amounts immediately prior" with the
cap applied per member. A pair that has been fully written down has both prior balances at
zero, so the ratio is 0/0. The PPM text quoted in the YAML (`credit_events.tranche_write_up_allocation_order`)
does not say what ratio applies then.

**Why it matters.** Zero in every v1 scenario (no Principal Recovery Amount, Modeling
Assumptions (n), (o)); it decides which Note is written back up first in an actual-pool run
with subsequent recoveries after a full write-down of M-2B/M-2BH.

**What was implemented.** `crt.waterfall.allocation.split_pair` raises `AllocationError`
(marked `# Q18`) when both prior balances are zero, so the engine cannot silently guess.

**Options.**
1. **(Recommended)** Split by the pair's cumulative unreimbursed write-downs when both prior
   balances are zero (the only quantity that still distinguishes the members; gives the same
   Note/H shares as the original notionals when both were written down pro rata).
2. Split by the initial Class Notional Amounts.
3. Keep raising (blocks actual-pool runs with write-ups after a full write-down).
Numeric implication in v1: none. Options 1 and 2 coincide whenever the pair was written down
pro rata, which is always the case under the PPM's write-down order.

---

## Q19 | Phase 3 | fintech-dev | CLOSED 2026-09-08 — option 1 adopted by Trey (with Step 1, before the Reduction Amounts) — Timing of the Stated Principal clause (e) floor excess added to A-H

**Question.** Stated Principal is floored at zero and the excess of clause (e) over (a)–(d)
is added to A-H (`principal.stated_principal`, P96). Spec 01 section 5 says to implement the
floor "as written" and assert it is zero in v1, but neither the spec nor the YAML says at
which point in the Payment Date order (before Step 1, after Step 4) A-H is increased.

**What was implemented.** The engine computes the excess in the pool aggregation
(`PaymentPeriod.stated_principal_floor_excess_to_a_h`, zero in v1) and adds it to A-H
together with the Step 1 A-H adjustments, before Steps 2–4 (marked `# Q19`).

**Options.**
1. **(Recommended)** With Step 1, before the Reduction Amounts (matches the PPM's grouping of
   the A-H increase on write-down, which is also a "Class Notional Amount ... increased by"
   clause outside the priority lists).
2. After Step 4, with the Supplemental Senior Increase Amount.
Numeric implication in v1: none (the excess is zero). In actual-pool runs the choice moves the
Senior Percentage of the following Payment Date by the excess / UPB, i.e. by less than one
hundred-thousandth of a percent for any plausible data correction.

---

## Q20 | Phase 3 | fintech-dev | CLOSED 2026-09-08 — option 1 adopted by Trey (keep A8; verify against payment date statements when available) — A8 pair split drifts from the printed Appendix G columns by one cent on five Payment Dates

**Question.** A8 takes the Note/H ratio from the Class Notional Amounts "immediately prior to
the Payment Date". Appendix G prints a constant 10,346,250.00 / 545,988.08 split for Payment
Dates 1–12 (3.750 % of each *initial* notional) and 4,138,500.00 / 218,395.23 for 13–36. The
engine reproduces both columns on Payment Date 1 (spec 02 section 4 check) but, because the
H leg was rounded up by 0.0013 cents on Payment Date 1, the prior-balance ratio on later dates
is fractionally larger for A-1 and the cent rounding flips on Payment Dates 3, 5, 7, 9 and 11:
A-1 receives 10,346,250.01 and A-1H 545,988.07. Cumulative effect: A-1 is paid $0.05 more than
Appendix G by Payment Date 12 and its balance after Payment Date 36 is 52,420,999.95, not
52,421,000.00; the A-1 WAL moves by 4.5e-10 years. Payment Dates 13–36 match Appendix G exactly.

**Why it matters.** No tie-out cell is affected (WAL identical to 9 decimals, Declining
Balances identical to 8 decimals). It matters for penny-level agreement with Freddie Mac's
payment date statements (Q4) and for the Excel export "to the penny" criterion, where the
convention must be the PPM's.

**Options.**
1. **(Recommended for now)** Keep A8 as specified; verify against the March–August 2026
   payment date statements when Trey supplies them (Q4): the actual A-1 factor after the
   third Payment Date decides between the two readings.
2. For the Class A-1 Reduction Amount only, allocate the printed Appendix G columns directly
   (the PPM says the percentages are "illustrative", so this is a reading, not a fact).
3. Take every pair ratio from the initial Class Notional Amounts.
Numeric implication: ≤ $0.05 on A-1 and ≤ $0.05 on A-1H through Payment Date 36; nothing else.

**Related observation (not a question).** Spec 02 section 8 says the Class A-1 Additional
Reduction Amount "does bind (at 0 % CPR it retires A-1 on Payment Date 39)". In the engine
A-1 is retired on Payment Date 39 at 0 % CPR by Step 2 priority 1 under limb (B) (from
Payment Date 37 the Class A-1 Reduction Amount equals the whole Senior Reduction Amount and
A-1/A-1H are paid ahead of A-H), so Step 4 finds nothing left and the Additional limb is
zero. The outcome (Payment Date 39, WAL 1.5971 → 1.60) is as printed; only the narrative
mechanism differs. `tests/unit/test_waterfall.py::test_zero_cpr_retires_a1_on_payment_date_39`
asserts the actual mechanism.

---

## Q21 | Phase 4 | fintech-dev | CLOSED 2026-09-08 — A2/A3/A15 confirmed by Trey; engine change deployed, tie-out PASS — diagnosed 2026-09-07 by structured-cashflow-expert (convention found; resolution and code change below; awaiting Trey's confirmation of revised A2/A3) — Trey 2026-09-07: 324/336 is NOT v1 done; diagnose before deciding — ESCALATION: 12 of 336 CER > 0 WAL cells outside ±0.02 and 10 of 96 Credit Event Sensitivity cells outside the A13 round-match, with A1–A15 implemented exactly as specified (supersedes Q17 with engine numbers)

**Status of the tie-out (`docs/validation/tieout.md`, engine 0.0.1).** Table 1 windows 4/4
exact; Declining Balances CER 0: 366/366 round-match (A13); WAL CER 0: 48/48 within ±0.02
(worst 0.0048); WAL CER > 0: 324/336 within ±0.02, **336/336 within the ±0.10 milestone**
(worst 0.0836); Credit Event Sensitivity: 86/96 round-match, **96/96 within ±0.25 pp** (worst
0.11 pp). Every miss is on the "To Scheduled Maturity Date" basis except one CES cell.

**The failing WAL cells (model − PPM, years).**

| Note | basis | CER | CPR | model | PPM | diff |
|---|---|---|---|---|---|---|
| A-1 | sched | 5.00 % | 25 | 5.4821 | 5.46 | +0.0221 |
| M-1 | sched | 1.00 % | 0 | 13.7275 | 13.70 | +0.0275 |
| M-1 | sched | 1.50 % | 5 | 11.8025 | 11.78 | +0.0225 |
| M-2A | sched | 0.50 % | 5 | 15.9707 | 16.00 | −0.0293 |
| M-2A | sched | 1.00 % | 5 | 14.1612 | 14.12 | +0.0412 |
| M-2A | sched | 1.00 % | 15 | 13.3101 | 13.39 | −0.0799 |
| M-2A | sched | 1.50 % | 10 | 10.8803 | 10.86 | +0.0203 |
| M-2A | sched | 3.00 % | 25 | 6.1939 | 6.17 | +0.0239 |
| M-2B | sched | 0.50 % | 0 | 19.8514 | 19.83 | +0.0214 |
| M-2B | sched | 0.50 % | 5 | 18.6817 | 18.71 | −0.0283 |
| M-2B | sched | 1.00 % | 5 | 12.1247 | 12.10 | +0.0247 |
| M-2B | sched | 1.00 % | 15 | 14.3764 | 14.46 | −0.0836 |

**The failing Credit Event Sensitivity cells (model − PPM, percentage points).**

| basis | CER | CPR | model | PPM | diff |
|---|---|---|---|---|---|
| sched | 0.25 % | 15 | 1.349 | 1.4 | −0.051 |
| sched | 1.00 % | 10 | 7.044 | 7.1 | −0.056 |
| sched | 2.50 % | 0 | 33.292 | 33.4 | −0.108 |
| sched | 2.50 % | 5 | 22.643 | 22.7 | −0.057 |
| sched | 3.00 % | 0 | 38.392 | 38.5 | −0.108 |
| sched | 3.00 % | 25 | 9.253 | 9.2 | +0.053 |
| sched | 5.00 % | 0 | 54.905 | 55.0 | −0.095 |
| sched | 5.00 % | 5 | 38.749 | 38.8 | −0.051 |
| sched | 5.00 % | 25 | 14.679 | 14.6 | +0.079 |
| early | 2.50 % | 35 | 4.951 | 4.9 | +0.051 |

**Pattern.** The Credit Event Sensitivity table depends on the pool alone (no waterfall). The
model is 0.10–0.11 pp *short* of the PPM at 0 % CPR for CER ≥ 2.5 % and *long* at 25 % CPR;
this CPR-dependent sign is the signature of a different basis or ordering of credit events
versus prepayments within the month (spec 03 section 5 item 7), not of the annual-to-monthly
conversion (which moves every cell the same way). The WAL misses cluster on long-dated
cells (5.5–20 year WALs) where a one-month shift in credit-event timing moves the WAL by
several hundredths; the largest (M-2A/M-2B at CER 1.00 %, CPR 15 %, −0.08) are on a CPR
column the spec author's scratch replication (Q17) did not check.

**What was tried (scratch scripts only; engine unchanged; every trial in
`docs/validation/tieout-diagnostics.md`, section 7 of the report).** No single item-7
alternative reproduces both tables: "credit events on the beginning-of-month balance before
scheduled principal" (H7b) brings the WAL to 330/336 (worst 0.038) but leaves the CES at
39/48 sched cells with the opposite sign pattern; "credit events and prepayments both on the
beginning balance" (H7e) brings the CES to 44/48 but worsens the worst WAL miss to −0.10;
CER/12, prepay-before-CE and the other orderings are much worse.

**Options.**
1. **(Recommended)** Keep A1–A3 as specified (the engine as built). Record the v1 tie-out as:
   windows exact, Declining Balances 100 %, WAL CER 0 100 % at ±0.02, WAL CER > 0 96.4 % at
   ±0.02 and 100 % at ±0.10, CES 100 % at ±0.25 pp. Ask the structured-cashflow-expert for an
   independent first-principles determination of the PPM's within-month credit-event timing
   (whether Credit Event Reference Obligations pay their scheduled principal in the month, and
   whether the CE rate applies before or after that month's scheduled principal and
   prepayments) — the pool-only CES table is the discriminating target and should be tied
   first, as spec 03 section 3.5 intends. Trey decides whether 324/336 meets the v1 definition
   of done or the tie-out stays open.
2. Adopt H7b now. Numeric implication: every CER > 0 cell changes; WAL worst miss 0.084 →
   0.038 (6 cells still outside ±0.02); CES sched cells 39/48 → 39/48 with different cells
   failing (0 % CPR cells fixed, CER ≥ 3 % / CPR ≥ 10 % cells overshoot by up to 0.21 pp).
   Rejected by fintech-dev because it does not tie the pool-only table.
3. Adopt H7e now. Numeric implication: CES 39/48 → 44/48; WAL 324 → 327/336 but worst miss
   −0.10. Rejected for the same reason.
Never a scaling factor (BRIEF section 2).

**Resolution 2026-09-07 — structured-cashflow-expert; recommendation for Trey and fintech-dev.**
Method, every trial (104 combinations) and every cell: `docs/validation/q21-credit-event-timing.md`.

**Finding.** An independent scratch replication (no engine code; it reproduces the engine's
86/96 and its twelve failing WAL cells to four decimals with A1–A3 as built) enumerated the
within-month conventions one variable at a time against the pool-only Credit Event Sensitivity
table. Exactly one reproduces all 96 cells: **credit events and prepayments in full are both
taken on the beginning-of-month balance, simultaneously (neither net of the other), and only
the surviving loans make the month's scheduled payment.** Per rep-line and month:
`CE = round2(B × MDR)`; `Prepay = round2(B × SMM)`; `Bs = B − CE − Prepay`; level payment,
interest and scheduled principal computed on `Bs`; `B_end = Bs − SchedPrin`. Conversions stay
`1 − (1 − x)^(1/12)` for both rates (`x/12` rejected by 0.8–1.9 pp); credit events start in
January 2026; horizon month 241; clean-up on end-of-period UPB (A11) — each confirmed
separately, every neighbour of the found convention is worse.

| family | as built | new reading |
|---|---|---|
| Credit Event Sensitivity, 96 cells, round-match | 86/96, worst 0.108 pp | **96/96**, worst 0.050 pp |
| WAL CER > 0, 336 cells, ±0.02 | 324/336, worst +0.084 | **336/336**, worst +0.005 (336/336 within ±0.01; 335 exact to the printed 2 dp) |
| WAL CER 0, 48 cells | 48/48 | 48/48, identical |
| Declining Balances CER 0, 390 Note cells | 390/390 | 390/390, identical |

The CER 0 families cannot see the change (at `MDR = 0` the two sequences reach the same
month-end balance to within cents), which is why they tied under the old reading and why the
old reading survived until the CER > 0 tables were run. Q17's "+0.01 to +0.03, model longer"
was this convention; it closes with Q21.

**Recommendation — option 4: adopt the new reading.** Done in this pass: `docs/spec/01-pool.md`
§2/§3/§7/§8/§9 restated (new P1–P5 order, revised worked example, new 1 % CER hand case);
`docs/spec/02-waterfall.md` §12 Payment Date 2 moved by five cents (`StatedPrincipal[2] =
215,917,777.13`, `UPB_end[2] = 22,127,470,144.83`; Payment Date 1 unchanged to the cent);
register A2/A3 revised (ASSUMED, `confirmed_by_user = N`, "revised 2026-09-07 per q21
diagnosis"); `docs/assumptions.md` re-rendered. No scaling factor or offset anywhere.
Trey: confirm A2/A3 as revised. fintech-dev: implement the change below, update the tests,
regenerate `docs/validation/tieout.md`; the expected result is 96/96 and 336/336 with every
CER 0 family unchanged — if the engine does not reproduce that, the difference is in the
implementation, not the convention, and `q21-credit-event-timing.md` §9 gives the cents to
diff against.

**Code-level change (only file: `src/crt/pool/rep_line.py`, `project_rep_line_month`).**
Replace the P1–P5 block (from `# P1 - scheduled monthly payment.` through
`balance_end = balance_after_credit_events - prepayment`) with:

```python
    # P1 - credit events on the beginning-of-month balance (A2, revised 2026-09-07 per Q21):
    # the Credit Event UPB is the balance before the month's scheduled principal.
    credit_event = round2(balance * mdr)

    # P2 - prepayments in full on the beginning-of-month balance (A1, A3 revised per Q21;
    # Modeling Assumption (g); no curtailments, P72).  Not net of credit events.
    prepayment = round2(balance * smm)

    # P3 - the surviving loans are the only ones that amortize this month.
    survivor = balance - credit_event - prepayment
    if survivor < ZERO:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: removals {credit_event + prepayment} exceed balance {balance}"
        )

    # P4 - scheduled payment and interest of the survivors (Modeling Assumption (c), A15).
    payment = scheduled_payment(survivor, rate, remaining_term)
    interest = round2(survivor * rate)

    # P5 - scheduled principal (Stated Principal clause (a)).
    if remaining_term >= 2:
        sched_principal = min(survivor, payment - interest)
    else:
        sched_principal = survivor
    if sched_principal < ZERO:
        raise RepLineProjectionError(
            f"rep-line {group} month {month}: negative scheduled principal {sched_principal}"
        )
    balance_end = survivor - sched_principal
```

The `RepLineMonth` fields, the `balance_end < ZERO` guard and the identity assertion
(`balance − sched_principal − credit_event − prepayment`) are unchanged and still hold;
`scheduled_payment(...)` for `survivor == ZERO` returns 0 and needs no special case. Update
the module docstring's order sentence to "credit events and prepayments on the beginning
balance → survivors → scheduled payment → interest → scheduled principal → roll the term"
and the two inline citations. `rates.py`, `projection.py`, the scenarios, the waterfall and
the tie-out code do not change. Tests (`tests/unit/test_pool.py`): group-17 month 1/2
intermediates become `scheduled_payment 37,683,632.42 / 37,354,216.77`, `interest
32,666,192.35 / 32,351,902.35`, `scheduled_principal 5,017,440.07 / 5,002,314.42`,
`prepayment 49,861,249.71 / 49,381,521.55` (month-end balances unchanged); pool rows months
1–3 and `pd2.stated_principal = 215,917,777.13`, `pd2.upb_end = 22,127,470,144.83` per
`01-pool.md` §9; add the 1 % CER hand case from §9 (`credit_event_amount 4,775,173.54`,
`balance_end 5,644,247,512.42`; pool `CE[1] = 19,071,864.30`). The CPR 0 / CER 0 level-pay
identity test is unaffected. Waterfall test for Payment Date 2: `SeniorReduction
208,306,675.49`, A-H share `197,414,437.41`, A-H balance `21,078,800,619.58`.

**Housekeeping for the manager once the engine re-runs:** register A15's note ("prepayments in
full carry no additional interest because they occur after the month's scheduled payment") is
stale — pool interest is not consumed by v1 and `01-pool.md` §7 now states the reading
consistent with the new order; `03-tieout.md` §5 item 7 and §6, `04-open-items.md` row 6 and
Q17 describe the old residual as expected and should be marked superseded by Q21;
`docs/validation/tieout-diagnostics.md` should gain the row "7 (A2 + A3 basis, simultaneous
on the beginning balance, survivors amortize) — CES 86/96 → 96/96, WAL 324 → 336/336 — kept".

---

## Q22 | Phase 5 | fintech-dev via manager | CLOSED 2026-09-08 — option 1 adopted by Trey (expose scheduled_interest and pool_interest columns) — Pool interest exposed by the run API

**Question.** After the Q21 change the pool projection carries two interest figures: survivors'
scheduled interest `Int[m]` (spec 01 §4) and `PoolInterest[m] = Int[m] + Σ Prepay × r` (spec
01 §7, A15). `RunResult.pool_months.interest`, the CSV export and the GUI "Total interest" line
expose `Int[m]` only. Pool interest is not a tie-out target and is not consumed by the v1
waterfall.

**Options.**
1. **(Recommended)** Expose both columns (`scheduled_interest`, `pool_interest`) in the API,
   CSV and GUI, labelled per the spec, before the Excel export (Phase 5) freezes the layout.
2. Expose `PoolInterest[m]` only. Loses the split the spec defines.
3. Leave as is. Understates pool interest by roughly `Prepay × r` per month.
