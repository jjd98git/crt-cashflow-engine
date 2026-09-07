| hypothesis (§5 number) | change tried | family/cells affected | before | after | kept? |
|---|---|---|---|---|---|
| 7 (A2 conversion) | monthly credit-event rate = CER / 12 (scratch pool re-projection, engine unchanged) | Credit Event Sensitivity, 48 "To Scheduled Maturity" cells | 39/48 round-match, worst 0.11 pp | 40/48 at low CER, then 0.3–0.9 pp short at CER ≥ 1.5 % | no |
| 7 (A1 + A2 conversion) | SMM = CPR / 12 and credit-event rate = CER / 12 | Credit Event Sensitivity, 48 sched cells | 39/48 | 33/96 overall, worst 1.63 pp | no |
| 7 (A2 basis) | credit events on the beginning-of-month balance before scheduled principal; credit-event loans pay no scheduled principal that month (H7b) | Credit Event Sensitivity sched cells; WAL CER > 0 | 39/48; WAL 324/336 within ±0.02, worst 0.084 | CES 39/48 with a different failure set (every CPR 0 cell fixed; CER ≥ 3 % / CPR ≥ 10 % cells overshoot by 0.05–0.21 pp); WAL 330/336, worst 0.038 | no — not a full fix on either table; escalated as Q21 |
| 7 (A3 order) | prepayments before credit events, both on the balance net of scheduled principal (H7c) | Credit Event Sensitivity sched cells | 39/48 | 47/96 overall, worst 0.33 pp, model short everywhere | no |
| 7 (A2 + A3 basis) | credit events and prepayments both on the beginning-of-month balance, before scheduled principal (H7e) | Credit Event Sensitivity sched cells; WAL CER > 0 | 39/48; WAL 324/336, worst 0.084 | CES 44/48 (90/96 overall, worst 0.18 pp); WAL 327/336 but worst −0.10 (M-2B, CER 1.00 %, CPR 15 %) | no — escalated as Q21 |
| 7 (A3 basis) | prepayments on the beginning-of-month balance, credit events on the beginning balance net of prepayments (H7f) | Credit Event Sensitivity sched cells | 39/48 | 51/96 overall, worst 0.33 pp | no |
| 7 (A2 + A3 basis, simultaneous on the beginning balance, survivors amortize) | credit events and prepayments in full both on the beginning-of-month balance, neither net of the other; only the surviving loans make the month's scheduled payment (Q21 resolution, `q21-credit-event-timing.md`; implemented in `src/crt/pool/rep_line.py` 2026-09-07, spec 01-pool.md section 3 as amended) | Credit Event Sensitivity, all 96 cells; WAL CER > 0, all 336 cells; CER 0 families re-run | CES 86/96 round-match, worst 0.11 pp; WAL CER > 0 324/336, worst 0.084 | CES 96/96, worst 0.05 pp; WAL CER > 0 336/336, worst 0.0050; Table 1 windows 4/4, Declining Balances CER 0 366/366 (worst 0.49), WAL CER 0 48/48 (worst 0.0048) unchanged | yes — adopted as A2/A3 revised 2026-09-07 |

Trials were run in a scratch script outside `src/` on 2026-09-07 by fintech-dev; the engine
implements A1–A15 exactly as specified and was not changed. "To Early Redemption Date" cells
at 35 % CPR were excluded from the CES trial counts because the scratch re-projection did not
model the 10 % clean-up call (A11) that the engine applies there.

2026-09-07 (fintech-dev): the last row is the engine itself, not a scratch trial — `rep_line.py`
now implements spec 01-pool.md section 3 as amended under Q21; the "before" column is engine
0.0.1 as first reported, the "after" column is the regenerated `tieout.md`.
