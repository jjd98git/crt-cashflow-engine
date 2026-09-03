# Open questions

Format: `ID | phase | raised-by | question | why blocked | what was tried | options + recommendation`

Every entry must carry a recommendation. Do not hand Trey a bare question.

---

## Q1 | Phase 0 | setup | RESOLVED PENDING CONFIRMATION

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

## Q2 | Phase 0 | manager | OPEN — tie-out input is Appendix C, not the loan-level file

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

## Q3 | Phase 0 | manager | OPEN — balance continuity rule vs 26 unexplained UPB increases

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

## Q4 | Phase 0 | manager | OPEN — deal-level payment date statements are not in the dataset

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

## Q5 | Phase 0 | manager | OPEN — Accounting Net Yield is not disclosed

**Question.** Original and Current Accrual Rate are "the lesser of Accounting Net Yield
and the mortgage rate minus 0.35%" (PPM p194, p207). They drive Modification Loss/Gain
Amounts and the delinquent-interest term of Credit Event Net Loss. Accounting Net Yield is
not a field in the loan-level file (gap G5).

**Recommendation.** Phase 1 ppm-analyst checks whether the PPM states an assumed ANY (or
an assumed accrual-rate haircut) in the Modeling Assumptions for its RM tables. If it does,
use it for the tie-out and expose it as a scenario input for actual runs. If it does not,
escalate immediately: RM>0 WAL tables cannot be tied without it.

---

## Q6 | Phase 0 | manager | OPEN — which file feeds which Payment Date

**Question.** The inventory infers that the `202607` file (paid through June 2026) feeds
the July 2026 Payment Date. The PPM's "Reporting Period" definition (p212) has a two-part
structure (collections vs prepayments vs delinquency status, with different windows).

**Recommendation.** Phase 1 ppm-analyst transcribes the Reporting Period definition
verbatim and the structured-cashflow-expert states the file→Payment Date mapping in the
spec before Phase 2. Trey can short-circuit this if he knows the convention.
