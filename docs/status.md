# Status

| Phase | State | Notes |
|---|---|---|
| 0 — Data reconnaissance | **complete, gate passed 2026-09-03** | `docs/data-inventory.md` + gap list; layout v4.2 retrieved; pool reconciled to PPM to the cent |
| 1 — PPM extraction | complete, gate closed 2026-09-03 (provisional register sign-off) | `data/deal_terms/stacr_2026_dna1.yaml` (258 cited fields); `data/ppm_tables/` (Appendix C, Appendix G, Table 1, WAL, Declining Balances, Credit Event Sensitivity); register 168 rows awaiting Trey |
| 2 — Pool engine | **built** (rep-line, spec 01) | 2026-09-07 |
| 3 — Waterfall engine | **built** (spec 02) | 2026-09-07 |
| 4 — Tie-out | **PASS 2026-09-07** | all 5 families, 850 cells; Q21 resolved (credit events and prepayments both on the beginning balance) |
| 5 — Excel export | blocked | Excel is installed on this machine; LibreOffice is not |
| 6 — Scenario input | partial | flat YAML scenarios + run API + CSV export built 2026-09-07; ramps/steps validated but rejected by the engine; actual-pool mode needs Q4 |
| 7 — GUI | **v1 built** (Streamlit) | `streamlit run src/crt/gui/app.py`; single run, compare, CSV download; Excel button disabled until Phase 5 |
| 8 — AI shell | blocked | |

Tie-out status (2026-09-07, `python -m crt.tieout`, 11 s): **PASS**. Table 1 windows 4/4 exact; Declining Balances CER 0 366/366 round-match; WAL CER 0 48/48 (worst 0.0048 yr); WAL CER>0 336/336 within ±0.02 (worst 0.0050 yr); Credit Event Sensitivity 96/96 round-match (worst 0.05 pp).

## Phase 0 summary (2026-09-03)

**Shipped.** `docs/data-inventory.md`; `scripts/phase0_profile.py` and
`scripts/phase0_reconcile.py` (reproduce every number); venv (`uv`, Python 3.13.12);
layout and glossary v4.2 saved to `data/raw/`.

**Register changes.** D3–D5 upgraded to high confidence with layout field names; D6–D12
added (dataset facts); P9–P23 added (PPM facts read during reconciliation, flagged for
Phase 1 re-citation); C2 marked CONTRADICTED by the PPM (no 180-day credit event trigger).
Nothing is confirmed by Trey yet.

**Open.** Q1 (confirm layout version), Q2 (tie-out input is Appendix C), Q3 (balance
continuity rule), Q4 (payment date statements), Q5 (Accounting Net Yield), Q6 (file →
Payment Date mapping).

## Phase 1 summary (2026-09-03)

**Shipped.** Deal-terms YAML with 258 fields, each with value, page, section and verbatim
quote. Tie-out tables transcribed: Appendix C rep-lines (sums reconcile to the cent),
Appendix G Class A-1 reduction schedule (81% of the class over 36 months), Table 1, WAL
tables (3,168 cells), Declining Balances (3,168 cells), Credit Event Sensitivity (96 cells),
Modeling Assumptions (a) to (s) verbatim. `docs/assumptions.md` rendered from the register.

**Register changes.** C1, C4, C6, C7, C8, C9, C10, C11 confirmed; C2, C3, C5, C12 overridden
by the PPM; P24 to P107 and 34 T rows added. 168 rows, 4 confirmed by Trey, 164 awaiting
his sign-off at this gate.

**Independently verified by the Manager.** Appendix C and G sums; A-1, M-1, M-2A and M-2B
WAL cells at 10% CPR against PPM p139-140; the C5 override against p214 and p107; the
Cumulative Net Loss Test schedule against p194.

**Open.** Q7 (Accounting Net Yield for actual-pool runs), Q8 (first-Payment-Date
denominators), Q9 (Class A-1 Reduction Amount reading), Q10 (prepayment start month in the
PPM tables), Q11 (CPR/CER monthly conversion). Q4 still awaits the payment date statements.

## Phases 2-4 summary (2026-09-07)

**Shipped.** Spec 00-04; engine packages io, pool, waterfall, scenarios, tieout (32
modules, mypy strict, ruff clean); 29 fast unit tests from the spec's worked examples; 11
tie-out regression tests (2 failing honestly: CER>0 WAL and Credit Event Sensitivity);
`docs/validation/tieout.md` + manifest regenerated on every run.

**Open.** Q12-Q17 (spec conventions A7-A15, need Trey's confirmation), Q18-Q20 (dev
edge cases, v1-neutral), Q21 (escalation: within-month credit-event timing; no single
alternative to A2/A3 ties both tables). Q4 still awaits payment date statements.

## 2026-09-07 afternoon

**Shipped.** Q21 resolved by first-principles replication (structured-cashflow-expert,
`docs/validation/q21-credit-event-timing.md`): the PPM takes credit events and prepayments
both on the beginning-of-month balance, simultaneously, with only survivors amortizing.
Spec 01 §3 amended, A2/A3/A15 revised (ASSUMED, unconfirmed), engine updated, all tie-out
tests green. Run API (`crt.api.run_scenario`), CSV export, validated scenario YAML files,
and a Streamlit GUI (single run, compare, downloads) built and verified in the browser.

**Open.** Trey to confirm A2, A3, A15 (revised today); Q18-Q20 (v1-neutral edge cases);
Q22 (pool interest columns); Q4 (payment date statements, deferred). Next: Phase 5 Excel
export with live formulas and the workbook recalculation test; GUI compare-chart x-axis
cosmetic fix; MACR classes; RM>0 tables.
