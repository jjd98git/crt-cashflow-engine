# Open questions - STACR 2026-DNA2

Format: `ID | phase | raised-by | question | why blocked | what was tried | options + recommendation`
(same format as `docs/open-questions.md`; ids `DNA2-Q1` onward). Every entry carries a
recommendation. Do not hand Trey a bare question.

---

## DNA2-Q1 | Phase 1 | ppm-analyst | OPEN — Four pages of the DNA2 text extract are column-shifted; the Original Notes' Initial Class Coupons are reconciled, not read

**Question.** In `data/raw/stacr-2026-dna2-ppm.txt` the `pdftotext -layout` output of PDF
pages 10 (Table 1), 24 (Table 3), 229 (Appendix A summary) and 264 (Appendix C) prints
one or more columns offset by one row from their labels. Examples: on p24 the A-H notional
$25,902,685,229.86 prints on the "Class M-1 and Class M-1H" line and the B-3H amount on an
unlabeled last line; on p10 the five Initial Class Coupons print as 4.87223 / 5.27223 /
5.27223 / 5.77223 / 5.77223 on the wrong rows and the margins 1.20 / 1.60 / 1.60 / 2.10 /
2.10 on the M-1, M-2B and B-1B rows plus two trailing lines; on p229 every value prints on
the line below its label (so "Aggregate Principal Balance" shows $27,524,842,000, which is
actually the Aggregate *Original* Principal Balance); on p264 the Original Balance column
is shifted up one row and the term columns down one row relative to the group numbers.

**Why it matters.** Rule 1 of the analyst brief is "no citation, no entry"; a value that
has to be re-derived from arithmetic is a medium-confidence entry. The Original Notes'
Initial Class Coupons and margins are engine inputs (register DNA2-P27 to DNA2-P36).

**What was tried.** (1) Reconciled p24 by the footnote markers (3),(5),(7),(9),(11), which
stay attached to the percentages, and by the footnoted dollar amounts (2),(4),(6),(8),(10);
the reconciled 13 notionals sum to the Cut-off Date Balance to the cent and reproduce every
printed subordination percentage. (2) Reconciled p10 by SOFR 3.67223% + margin = coupon and
by Table 2 (p12), which prints M-2 = SOFR + 1.60% at 5.27223% and B-1 = SOFR + 2.10% at
5.77223%; the exchange constraint on p111 (equal annual interest at all SOFR levels) forces
M-2A = M-2B = 1.60 and B-1A = B-1B = 2.10, leaving M-1 = 1.20 = the only margin printed on
the M-1 line. (3) Reconciled p229 by value type (count, dollar totals, ranges, percentages,
a date). The PDF itself was not opened (task rule).

**Options.**
1. **(Recommended)** Re-extract only pages 10, 24, 229 and 264 with `pdftotext -layout -f N -l N`
   at a different `-fixed` pitch (or `-raw`), save alongside the main extract, and confirm the
   reconciled values; then raise DNA2-P27..P36 to high confidence. Ten minutes of work; no
   engine impact if the values are confirmed.
2. Accept the arithmetic reconciliation as final. Every reconciled number is corroborated by at
   least one independent figure in the PPM, so the risk is low, but it is not zero for the
   coupons (a 1.20 / 1.60 swap between M-1 and M-2A would be invisible to the Table 2 check
   only if both margins moved together, which they do not - still, confirm).

---

## DNA2-Q2 | Phase 1 | ppm-analyst | OPEN — First-Payment-Date denominators: reuse DNA1's A5 or re-decide?

**Question.** As in DNA1 (Q8), the Senior Percentage divides by "the aggregate UPB of the
Reference Obligations in the Reference Pool at the end of the previous Reporting Period"
(p223) and the Delinquency Test uses "the aggregate UPB ... as of the preceding Payment
Date" (p203). For the April 2026 Payment Date there is no previous Reporting Period and no
preceding Payment Date. The wording is identical to DNA1.

**Why it matters.** With the Cut-off Date Balance as the first-period denominator the
initial Subordinate Percentage is 3.00000% = the 3.000% threshold (unrounded 3.0000037%),
the same knife-edge DNA1 had at 3.525%. Any other denominator (for instance the UPB after
the two month-ends of February and March 2026) makes SubPct[1] > 3.000% and the knife-edge
disappears - which would change Payment Date 1 behaviour at CER > 0.

**What was tried.** Read the Senior Percentage, Subordinate Percentage, Delinquency Test and
Reporting Period definitions (p203, p221, p223, p224). Nothing in the DNA2 PPM resolves it
differently from DNA1.

**Options.**
1. **(Recommended)** Carry over Trey's DNA1 decision (Q8 option 1 / register A5): Cut-off
   Date Balance on the first Payment Date, prior Reporting Period UPB thereafter. Record it
   as ASSUMED for DNA2 with a pointer to A5 and assert `SubPct[1] == Decimal("0.0300000")`
   in a unit test.
2. Re-open the question for DNA2 only if the DNA2 tie-out fails on Payment Date 1 cells.

---

## DNA2-Q3 | Phase 1 | ppm-analyst | OPEN — The first Payment Date rolls from Saturday 25 April 2026 to Monday 27 April 2026; the PPM tables assume the 25th

**Question.** "Payment Date" is the 25th or, if not a Business Day, the following Business
Day (p216). 25 April 2026 is a Saturday, so the contractual first Payment Date is
27 April 2026 and the first Accrual Period is 17 March - 26 April 2026 (41 days) rather than
17 March - 24 April (39 days). Modeling Assumption (q) (p139) and Table 1 footnote (1)
(p11) say the tables assume payment "on the 25th day of each month". DNA1 never faced this
(25 March 2026 was a Wednesday). The same roll recurs for every 25th that is a weekend or
holiday over 240 Payment Dates.

**Why it matters.** (a) Interest: actual/360 on 41 vs 39 days for the first period changes
every Note's first coupon by ~5%. (b) WAL clock: DNA1 adopted 30/360 from the Closing Date
to the unadjusted 25th (A9). (c) The engine needs a Business Day calendar if it follows the
contract, or an explicit "unadjusted" switch if it follows the tables.

**What was tried.** Searched the PPM for any statement that the tables use adjusted dates
(none; (q) says the 25th) and for a holiday calendar (none beyond the Business Day
definition, p198).

**Options.**
1. **(Recommended)** Two switches in the scenario: `payment_dates = unadjusted` for tie-out
   runs (matches (q) and A9 exactly; interest accrues 25th-to-25th) and
   `payment_dates = business_day_adjusted` for actual-pool runs, with a weekend-only roll
   until Trey supplies (or approves) a holiday calendar. Register the choice as ASSUMED.
2. Always roll (contractual) and accept that PPM interest/yield tables will not tie on rolled
   months. Not acceptable for the tie-out.
3. Never roll. Wrong for actual payment date statements.

---

## DNA2-Q4 | Phase 1 | ppm-analyst | OPEN — When do prepayments start in the DNA2 tables: February 2026 or the Closing Date?

**Question.** Same tension as DNA1 Q10, shifted one month. Modeling Assumptions (f) and (g)
(p138) put scheduled payments and full prepayments "on the last day of each month beginning
in February 2026", i.e. two month-ends (28 Feb and 31 Mar 2026) inside the first Reporting
Period (1 Feb - 31 Mar 2026, p221), while Table 1 footnote (1) (p11) says "10% CPR,
calculated from the Closing Date" (17 March 2026).

**Why it matters.** One versus two months of amortization and prepayment before the first
Payment Date moves every WAL by roughly 0.04 years and the Declining Balances first column
by roughly 0.8%.

**What was tried.** Read (f), (g), (k)(z) and the Reporting Period definition. (k)(z)
explicitly computes the first Modification Loss Amount as two monthly calculations
(1 Feb on the Cut-off UPB, 1 Mar on the 28 Feb UPB), which is consistent with two months of
pool activity before the April 2026 Payment Date.

**Options.**
1. **(Recommended)** Carry over Trey's DNA1 decision (Q10 option 1): two month-ends of
   amortization and prepayment in the first Reporting Period; "calculated from the Closing
   Date" describes the CPR convention, not the start of prepayments. Record as ASSUMED.
2. Start prepayments at the Closing Date (one month-end, 31 Mar 2026). Test only if the DNA2
   tie-out fails at 10% CPR with option 1.

---

## DNA2-Q5 | Phase 1 | ppm-analyst | OPEN — Appendix C (38 rep-line groups) is misaligned in the extract and a quick sum of the Outstanding Principal Balance column does not equal the Cut-off Date Balance

**Question.** Appendix C (PDF p264) prints 38 groups. In the extract the Original Balance
column is shifted up one row (the header row carries "412,000.00", group 38 has no original
balance) and the Remaining Term / Original Term columns are shifted down one row (group 1
is blank, a trailing "351 360" belongs to group 38); the Outstanding Principal Balance and
rate columns appear aligned. A regex parse of the outstanding column summed to
26,703,800,475.22 versus the Cut-off Date Balance 26,703,800,234.86 (difference +240.36),
and the parse itself double-counted (76 matches for 38 rows), so the sum is not yet
trustworthy.

**Why it matters.** Modeling Assumption (a) makes Appendix C the tie-out pool (DNA1 Q2
option 1). `01-pool.md` asserts that the rep-line balances sum to the Cut-off Date Balance
at load time; a $240 discrepancy would fail that assertion or, worse, be "fixed".

**What was tried.** One regex pass over lines 15771-15812 of the page-prefixed scratch copy;
not a careful transcription (the Appendix C transcription is a separate deliverable under
`data/ppm_tables/`, not part of this extraction).

**Options.**
1. **(Recommended)** When Appendix C is transcribed for DNA2, do it from a re-extracted p264
   (DNA2-Q1 option 1), transcribe all 38 rows by hand, and compute the sum. If it differs from
   the Cut-off Date Balance by more than rounding (38 groups x $0.005), record the printed
   figures as-is, flag the difference in the register, and let the tie-out use the printed
   groups (the PPM tables were computed from them). Never scale the groups to the Cut-off
   Date Balance.
2. Accept the Cut-off Date Balance as the pool total and ignore Appendix C's sum. Rejected:
   the tables were computed from Appendix C.

---

## DNA2-Q6 | Phase 1 | ppm-analyst | OPEN — Memorandum date: the task brief says 17 March 2026; the PPM front page says 13 March 2026

**Question.** The brief that commissioned this extraction described the PPM as "memorandum
dated 2026-03-17". Page 1 reads "The date of this Private Placement Memorandum is March 13,
2026"; 17 March 2026 is the Closing Date (p1, p200).

**Why it matters.** Only for provenance (the `meta.source_file` citation and the data
inventory). No engine input depends on the memorandum date.

**What was tried.** Grepped the extract for "date of this Private Placement Memorandum"
(one hit, p1) and "Closing Date" (p1, p200).

**Options.**
1. **(Recommended)** Record 2026-03-13 as the memorandum date and 2026-03-17 as the Closing
   Date (done in the YAML). Confirm the file in `data/raw/` is the final PPM and not a
   preliminary one (a final PPM dated four days before closing is normal; a red-herring
   preliminary would usually be dated earlier and carry "PRELIMINARY" on its cover, which
   this extract does not).
