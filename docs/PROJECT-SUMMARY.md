# CRT Cashflow Engine — project summary (2026-09-08)

## What it is

A cashflow engine for Freddie Mac STACR credit-risk-transfer deals, built to reproduce
what a structuring desk's model (Intex-style) produces from the deal's offering
memorandum, and then to run the user's own prepayment and credit-event scenarios through
the same structure. The reference deal is **STACR REMIC 2026-DNA1** ($627.5MM offered,
closed 2026-02-17, $22.78bn reference pool).

It is built to be audited: every number the model consumes is in a register with its
source (PPM page, dataset field, or a decision by Trey), every run writes a manifest with
input hashes, all money arithmetic is exact Decimal, and the acceptance test is the PPM's
own tables.

## What it does today

| Capability | State |
|---|---|
| Projects the reference pool (31 PPM rep-lines) under CPR and CER assumptions | done |
| Runs the hypothetical structure: 12 reference tranches, senior/subordinate split, the four performance tests, the scheduled Class A-1 amortization (Appendix G), supplemental reduction, write-downs and write-ups, early redemption | done |
| Produces per-note cashflows (A-1, M-1, M-2A, M-2B), WAL, principal windows, per-tranche principal and write-downs, pool vectors | done |
| **Ties out to the PPM**: Table 1 windows exact, 366 declining-balance cells, 384 WAL cells within ±0.02 yr (worst 0.005), 96 credit-event-sensitivity cells | **PASS, 850 cells** |
| Excel workbook export with stacked tranche charts (engine values, no formulas yet) | done |
| CSV bundle of every cashflow vector plus a run manifest | done |
| Scenario files (flat CPR/CER/SOFR/early-redemption); ramps and steps validated but not yet run by the engine | partial |
| Local GUI (Streamlit): run, compare two scenarios, download | done |
| Browser app at https://jjd98git.github.io/crt-cashflow-engine/ running the real engine client-side (Pyodide), proxy-hardened | done, first working example on a corporate network |
| GitHub repo with CI (lint, strict types, 97 unit tests, full tie-out on every push) and Codespaces | done (repo currently public) |

## How the tie-out was earned

Two things that were not in the brief turned out to matter most:

1. The PPM's tables are computed on **Appendix C's 31 representative lines**, not the
   64,434-loan disclosure file. The engine is therefore a rep-line engine; the loan file is
   for actual-pool mode later.
2. The PPM does not state how credit events and prepayments interact within a month. The
   first engine build missed 12 WAL cells and 10 sensitivity cells. An independent
   first-principles replication swept 104 candidate conventions and found exactly one that
   reproduces every cell: credit events and prepayments both on the beginning-of-month
   balance, simultaneously, with only survivors amortizing. No factor was tuned anywhere.

## Decisions on record

22 open questions were raised and resolved with Trey (`docs/open-questions.md`): layout
version, tie-out input, loader policy, WAL clock and weights, rounding, pass criteria, the
credit-event convention, and more. The register (`docs/assumptions.csv`, 186 rows) is
provisionally accepted; three rows revised on 2026-09-07 (A2, A3, A15) still need explicit
confirmation.

## Next steps, in order

1. **Sign off the register.** Confirm A2/A3/A15 and the remaining PPM rows. This is v1
   definition-of-done item 2.
2. **Phase 5 proper: live-formula Excel workbook** and the test that recalculates it in
   Excel and matches the engine to the penny (v1 item 3). Decide Q22 (pool interest columns)
   before the layout freezes.
3. **Browser app residuals.** Collect the remaining issues seen on the work machine and fix
   them; the diag page names failing URLs.
4. **Complete the structure**: MACR exchangeable classes from exchange ratios; the RM > 0
   modification tables; the Cumulative Note Write-down and Yield tables.
5. **Scenario vectors in the engine** (ramps and step schedules for CPR, CER, severity,
   SOFR path), then actual-pool mode from the loan-level file (needs the payment date
   statements, Q4, and a Distressed Principal Balance input for the Delinquency Test).
6. **Second deal.** Run the next STACR DNA or HQA print end to end. This is the real test
   of generality and the prerequisite for the AI shell.
7. **AI shell (Phase 8).** Claude with the engine's functions as tools: extract a PPM,
   run the tie-out, run scenarios, export; the model does no arithmetic and every number
   cites a run manifest.
8. **Repo hygiene.** Return the repo to private once GitHub login is sorted (Pages on the
   free plan needs a public repo; the alternative is a small hosted server).

## Where things live

| Item | Path |
|---|---|
| Brief and rules | `docs/BRIEF.md`, `CLAUDE.md` |
| Status and history | `docs/status.md` |
| Register | `docs/assumptions.csv`, rendered `docs/assumptions.md` |
| Open questions and decisions | `docs/open-questions.md` |
| Modeling spec | `docs/spec/00-04` |
| Tie-out report | `docs/validation/tieout.md`, regenerated by `python -m crt.tieout` |
| Deal terms and PPM tables | `data/deal_terms/`, `data/ppm_tables/` |
| Engine | `src/crt/` (io, pool, waterfall, scenarios, tieout, excel, gui, api) |
| Browser app | `web/`, built by `scripts/build_web.py`, deployed by `.github/workflows/pages.yml` |
