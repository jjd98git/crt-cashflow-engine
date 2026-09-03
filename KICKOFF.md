# Paste this as your first message in Claude Code

---

Read `CLAUDE.md`, `docs/BRIEF.md`, `docs/RECON.md`, `docs/open-questions.md` and
`docs/assumptions.csv`. The environment is already scaffolded — the repo skeleton, the three
subagent definitions, `/gate`, `/tieout`, the data and the PPM text extract all exist. You
write all the code from here.

Before anything else:

1. Tell me anything in the brief you think is wrong, under-specified, or that you would
   push back on. I want the disagreement now, not after Phase 3.
2. Set up the Python environment (`uv venv`, install `-e ".[dev]"`) and confirm `pytest`
   runs clean on an empty suite.
3. Then begin **Phase 0 only**. `docs/RECON.md` is unverified positional guesswork from
   setup — verify it, do not inherit it. Produce `docs/data-inventory.md` as the real
   Phase 0 deliverable, including the gap list of what the cashflow model needs and the
   dataset does not contain.

Stop at the Phase 0 gate and run `/gate`. Do not write engine code.

Note Q1 in `docs/open-questions.md` — the file layout document is missing. Flag it early;
I can source it.
