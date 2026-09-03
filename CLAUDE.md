# CRT Cashflow Engine

Intex-adjacent cashflow engine for Freddie Mac STACR CRT transactions.
Reference deal for v1: **STACR REMIC 2026-DNA1** (closed 2026-02-17, $627.5MM offered).

## Read first
- `docs/BRIEF.md` — the project brief. It governs. Read it before any non-trivial work.
- `docs/RECON.md` — unverified positional observations from initial setup. A starting
  point for Phase 0, NOT a substitute for it. Verify everything in it.
- `docs/spec/` — the authoritative modeling spec. Implement this; do not invent alongside it.
- `docs/assumptions.csv` — every number the model uses, with provenance.
- `docs/open-questions.md` — what is blocked and awaiting the user.

## Absolute rules
1. **Never fabricate data.** Missing/null/ambiguous field -> raise, naming field and record.
   No defaults, no forward-fill, no inference.
2. **Never plug a number.** No scaling factor, offset, or fudge to force a tie-out.
   A tuned match is worse than an honest mismatch.
3. **Money is `Decimal`.** Rates and factors may be float; balances, interest, principal
   and losses may not. Rounding is explicit and documented at every step.
4. **No magic numbers.** Any constant in code cites an assumptions-register ID in a comment.
5. **Two attempts, then escalate.** Append to `docs/open-questions.md` with a recommendation.
   Do not proceed on a guess.
6. **Phase gates are hard.** No engine code before the Phase 1 gate is signed off by Trey.
7. **The PDF is read once.** Use `data/raw/stacr-2026-dna1-ppm.txt` (already extracted with
   `pdftotext -layout`). Work from `data/deal_terms/*.yaml` thereafter.
8. **Do not commit** anything in `data/raw/`. It is gitignored. Keep it that way.

## Layout
```
src/crt/io/          loaders + layout parsing + validation
src/crt/pool/        pool projection (amortization, prepay, default, severity)
src/crt/waterfall/   tranche allocation, performance tests, write-down/write-up
src/crt/scenarios/   scenario parsing and vector construction
src/crt/excel/       workbook export
tests/unit/          hand-computable cases per component
tests/tieout/        PPM WAL / declining-balance regression tests
docs/                brief, spec, assumptions, validation, open questions, status
```

## Environment
Windows 11, Git Bash. Python is NOT yet set up — the venv is yours to create:
```
uv venv && .venv\Scripts\activate && uv pip install -e ".[dev]"
```
Then:
```
pytest -q                  # full suite
pytest -q -m fast          # fast unit tests
ruff check src tests
mypy src/crt               # strict on the engine package
```
No Makefile — this is Windows; use the commands directly.

## Conventions
- Type hints everywhere; mypy strict on `src/crt`.
- Every cashflow function gets a unit test with a hand-computable case BEFORE it is wired
  into the waterfall.
- Runs are deterministic: same manifest -> byte-identical output.
- Conventional commits, one concept per commit. No 2,000-line "implement waterfall" commit.

## Style of work
Boring, explicit, slow code beats clever code. A finance reviewer who does not write Python
should be able to read the waterfall module and follow it.
