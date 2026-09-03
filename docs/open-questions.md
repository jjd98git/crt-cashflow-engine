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

## Q4 | Phase 0 | manager | ACCEPTED 2026-09-03 — Trey to source the Mar–Aug 2026 payment date statements; not blocking Phases 1–4

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

## Q7 | Phase 1 | ppm-analyst | OPEN 2026-09-03 — Accounting Net Yield is not in the PPM (closes Q5; needs a decision for actual-pool runs)

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

## Q8 | Phase 1 | ppm-analyst | OPEN 2026-09-03 — First-Payment-Date denominators for Senior Percentage and the Delinquency Test

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

## Q9 | Phase 1 | ppm-analyst | OPEN 2026-09-03 — Class A-1 Reduction Amount: "aggregate" reading and shortfall carry-forward

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

## Q10 | Phase 1 | ppm-analyst | OPEN 2026-09-03 — When do prepayments start in the PPM tables: January 2026 or the Closing Date?

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

## Q11 | Phase 1 | ppm-analyst | OPEN 2026-09-03 — CPR and CER monthly conversion and balance basis are not stated

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
