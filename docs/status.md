# Status

| Phase | State | Notes |
|---|---|---|
| 0 — Data reconnaissance | **complete, at gate** | `docs/data-inventory.md` + gap list; layout v4.2 retrieved; pool reconciled to PPM to the cent |
| 1 — PPM extraction | not started | PPM already extracted to text at `data/raw/stacr-2026-dna1-ppm.txt`; Appendix C (31 groups) is the tie-out pool |
| 2 — Pool engine | blocked by gate 1 | must accept rep-line inputs (Q2) |
| 3 — Waterfall engine | blocked | |
| 4 — Tie-out | blocked | |
| 5 — Excel export | blocked | Excel is installed on this machine; LibreOffice is not |
| 6 — Scenario input | blocked | actual-pool runs need payment date statements (Q4) |
| 7 — GUI | blocked | stack not chosen; propose in plan mode |
| 8 — AI shell | blocked | |

Tie-out status: not yet run.

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
