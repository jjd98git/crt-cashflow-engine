# Open questions

Format: `ID | phase | raised-by | question | why blocked | what was tried | options + recommendation`

Every entry must carry a recommendation. Do not hand Trey a bare question.

---

## Q1 | Phase 0 | setup | OPEN

**Question.** The Freddie Mac CRT loan-level file layout / data dictionary is not in the
downloaded zip. The files have no header row and 93 positional fields.

**Why blocked.** Every field name is currently an inference from observed values. Naming a
field wrong silently produces a wrong cashflow that still runs and still looks plausible —
the worst failure mode this project has.

**What was tried.** Positional profiling of all 93 columns across both months
(see `docs/RECON.md`). It narrows the field set but cannot confirm any name.

**Options.**
1. **(Recommended)** Trey obtains the published Freddie Mac CRT file layout / user guide and
   drops it in `data/raw/`. He works in CRT at Freddie Mac and can source the authoritative
   version quickly.
2. Reconstruct the layout by cross-referencing the PPM's reference pool statistics against
   column aggregates. Slower, and confirms only the columns the PPM happens to describe.
3. Proceed on inferred names. **Not acceptable** — violates the no-fabrication rule.

---
