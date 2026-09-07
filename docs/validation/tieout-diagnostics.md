| hypothesis (§5 number) | change tried | family/cells affected | before | after | kept? |
|---|---|---|---|---|---|
| 7 (A2 conversion) | monthly credit-event rate = CER / 12 (scratch pool re-projection, engine unchanged) | Credit Event Sensitivity, 48 "To Scheduled Maturity" cells | 39/48 round-match, worst 0.11 pp | 40/48 at low CER, then 0.3–0.9 pp short at CER ≥ 1.5 % | no |
| 7 (A1 + A2 conversion) | SMM = CPR / 12 and credit-event rate = CER / 12 | Credit Event Sensitivity, 48 sched cells | 39/48 | 33/96 overall, worst 1.63 pp | no |
| 7 (A2 basis) | credit events on the beginning-of-month balance before scheduled principal; credit-event loans pay no scheduled principal that month (H7b) | Credit Event Sensitivity sched cells; WAL CER > 0 | 39/48; WAL 324/336 within ±0.02, worst 0.084 | CES 39/48 with a different failure set (every CPR 0 cell fixed; CER ≥ 3 % / CPR ≥ 10 % cells overshoot by 0.05–0.21 pp); WAL 330/336, worst 0.038 | no — not a full fix on either table; escalated as Q21 |
| 7 (A3 order) | prepayments before credit events, both on the balance net of scheduled principal (H7c) | Credit Event Sensitivity sched cells | 39/48 | 47/96 overall, worst 0.33 pp, model short everywhere | no |
| 7 (A2 + A3 basis) | credit events and prepayments both on the beginning-of-month balance, before scheduled principal (H7e) | Credit Event Sensitivity sched cells; WAL CER > 0 | 39/48; WAL 324/336, worst 0.084 | CES 44/48 (90/96 overall, worst 0.18 pp); WAL 327/336 but worst −0.10 (M-2B, CER 1.00 %, CPR 15 %) | no — escalated as Q21 |
| 7 (A3 basis) | prepayments on the beginning-of-month balance, credit events on the beginning balance net of prepayments (H7f) | Credit Event Sensitivity sched cells | 39/48 | 51/96 overall, worst 0.33 pp | no |

Trials were run in a scratch script outside `src/` on 2026-09-07 by fintech-dev; the engine
implements A1–A15 exactly as specified and was not changed. "To Early Redemption Date" cells
at 35 % CPR were excluded from the CES trial counts because the scratch re-projection did not
model the 10 % clean-up call (A11) that the engine applies there.
