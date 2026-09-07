# 04 — Open items: what the PPM leaves ambiguous, and the reading the dev implements

None of these blocks the build. Each carries the reading adopted in `01`–`03` (marked
ASSUMED, registered as A7–A13), the evidence, and a pointer to the `docs/open-questions.md`
entry (Q12–Q17) where Trey's decision is recorded. The dev implements the ASSUMED reading
exactly and does not choose among alternatives; if the tie-out fails, the alternatives are
tested through `03-tieout.md` §5, one at a time, and the outcome is written up — never a
factor.

| # | ambiguity | reading adopted (ASSUMED) | register | question | evidence |
|---|---|---|---|---|---|
| 1 | Does the WAL count Tranche Write-down Amounts as reductions of the balance? The PPM defines WAL as time "until its balance is reduced to zero" and gives no formula. | Yes: the WAL weight on a Payment Date is the net reduction of the Class Principal Balance (principal paid + write-downs − write-ups). | A10 | Q12 | M-2B WAL at 0 % CPR is 19.29 / 8.75 / 1.61 at CER 0 / 1 % / 5 % "To Scheduled Maturity"; principal alone cannot produce 1.61. |
| 2 | Day count and origin of the WAL clock. | 30/360 from the Closing Date 2026-02-17 to the unadjusted 25th of each Payment Date month: `t[n] = (30n + 8)/360`. | A9 | Q13 | A-1's schedule is fixed; 30/360 gives 1.587 → 1.59 as printed, actual/365 gives 1.583 → 1.58; 48/48 CER-0 cells tie with 30/360, 42/48 with actual/365. |
| 3 | Which UPB is tested against the 10 % clean-up threshold in Modeling Assumption (m)(ii). | The aggregate UPB at the end of the Reporting Period related to the Payment Date. | A11 | Q14 | Not exercised in the PPM grid at ≤ 35 % CPR before Payment Date 60 in the scratch replication; matters for actual-pool runs and high-CPR scenarios. |
| 4 | Whether the PPM's rounding rule (p99, "calculation on the Notes") governs the hypothetical structure's percentages and dollar amounts; how a Note/H pro rata split is rounded; whether rep-line amounts are rounded. | p99 applied to every structure percentage (5 decimals of a percent) and dollar amount (cent); pair split by exact ratio with the Note leg rounded and the H leg the remainder; rep-line amounts rounded to the cent at each step. | A12, A8, A7 | Q15 | A8 reproduces Appendix G's two columns from the aggregate; A12 makes the Payment Date 1 Subordinate Percentage exactly 3.52500 % (`02-waterfall.md` §2 knife-edge). |
| 5 | The brief's ±0.25 pp tolerance for decrement tables versus the PPM's whole-percent printing. | Primary pass: model rounded half-up to a whole percent equals the printed value; the ±0.25 pp result is reported as a flag. | A13 | Q16 | A correct model produces 23.47 where the PPM prints 23 (M-1, 25 % CPR, Feb 2027). Trey to confirm the definition of done. |
| 6 | Residual +0.01 to +0.03 (model longer) on some CER > 0 WAL cells in the scratch replication with the A2 credit-event convention. | Keep A2 as adopted; escalate with the per-cell table if the engine shows a cell outside ±0.02; test the §5 item-7 alternatives only then. | A2 (unchanged) | Q17 | 96 cells checked: 60 exact, 33 at ±0.01, 2 at +0.02, 1 at +0.03. |

Facts the dev must not re-derive differently (PPM-sourced, no ambiguity, but easy to get
wrong):

- The initial Senior Percentage is 96.47500 %, not 95.200 %: A-1 and A-1H are senior for
  this purpose (`02-waterfall.md` §1). The note on register row P32 and the narrative in
  Q8 said 95.200 %; the P32 note has been corrected and a correction line appended under
  Q8. The value of P32 (4.800 %, A-H subordination) is right.
- The Appendix G amount is used once on Payment Date 1 even though that Payment Date
  carries two collection months (T42: indexed by Payment Period).
- On the Maturity Date no Senior/Subordinate/Supplemental allocation is made; write-downs
  are, then 100 % of each Class Principal Balance is paid (P108).
- The Cumulative Net Loss Percentage used by the tests on Payment Date `n` includes the
  Principal Loss Amount of Payment Date `n` itself.
- The Class A-1 Cumulative Net Loss Test, once failed, stays failed.

Not ambiguous but deliberately deferred (see `00-overview.md` §5): MACR derivation, RM > 0,
the Delinquency Test's data input, Business Day calendars, actual-pool mode.
