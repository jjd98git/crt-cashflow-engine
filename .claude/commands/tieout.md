---
description: Run the PPM tie-out and report the diagnosis
---

Regenerate `docs/validation/tieout.md`. For every offered class and every scenario in the
PPM's Weighted Average Life and Declining Balances tables, report model vs PPM vs difference:

- first principal payment date  — exact month match required, no tolerance
- last principal payment date   — exact month match required, no tolerance
- weighted average life          — within +/- 0.02 years
- declining balance percentages  — within +/- 0.25 percentage points at each stated period

Also run the Credit Event Sensitivity tables where the engine supports them.

If anything fails, produce a ranked hypothesis list (accrual convention -> termination
assumption -> test thresholds -> allocation order -> day count -> rounding) and test ONE
hypothesis at a time. Report which hypothesis was correct and what changed.

Never introduce a scaling factor, offset or correction to force agreement. If you cannot find
the cause, say so and escalate to `docs/open-questions.md`.
