# Repo scaffold — files to create in the project

Each block below is one file. Create them at the paths shown before Phase 0 begins.

---

## `CLAUDE.md` (repo root)

```markdown
# CRT Cashflow Engine

Intex-adjacent cashflow engine for Freddie Mac STACR CRT transactions.
Reference deal: STACR 2026-DNA1.

## Read first
- `docs/BRIEF.md` — the project brief. It governs. Read it before any non-trivial work.
- `docs/spec/` — the authoritative modeling spec. Implement this, do not invent alongside it.
- `docs/assumptions.csv` — every number the model uses, with provenance.
- `docs/open-questions.md` — what is blocked and awaiting the user.

## Absolute rules
1. **Never fabricate data.** Missing/null/ambiguous field → raise, naming field and record.
   No defaults, no forward-fill, no inference.
2. **Never plug a number.** No scaling factor, offset, or fudge to force a tie-out.
   A tuned match is worse than an honest mismatch.
3. **Money is `Decimal`.** Rates and factors may be float; balances, interest, principal,
   and losses may not. Rounding is explicit and documented at every step.
4. **No magic numbers.** Any constant in code cites an assumptions-register ID in a comment.
5. **Two attempts, then escalate.** Write to `docs/open-questions.md` with a recommendation.
   Do not proceed on a guess.
6. **Phase gates are hard.** No engine code before the Phase 1 gate is signed off.
7. **The PDF is read once.** Work from `data/deal_terms/*.yaml`, never re-parse the PPM.
8. **Do not commit** raw data, zips, or PDFs. Extracted terms and table transcriptions only.

## Layout
src/crt/io/          loaders + layout parsing + validation
src/crt/pool/        pool projection (amortization, prepay, default, severity)
src/crt/waterfall/   tranche allocation, tests, write-down/write-up
src/crt/scenarios/   scenario parsing and vector construction
src/crt/excel/       workbook export
src/crt/manifest.py  run manifest: input hashes, version, commit, timestamp
tests/unit/          hand-computable cases per component
tests/tieout/        PPM decrement/WAL regression tests
docs/                brief, spec, assumptions, validation, open questions, status

## Commands
- `make test` — full suite
- `make tieout` — regenerate `docs/validation/tieout.md`
- `make lint` — ruff + mypy strict on `src/crt`

## Conventions
- Type hints everywhere; mypy strict on the engine package.
- Every cashflow function has a unit test with a case computable by hand before it is
  wired into the waterfall.
- Runs are deterministic: same manifest → byte-identical output.
- Conventional commits, one concept per commit.

## Style of work
Boring, explicit, slow code beats clever code. A finance reviewer who does not write
Python should be able to read the waterfall module and follow it.
```

---

## `.claude/agents/fintech-dev.md`

```markdown
---
name: fintech-dev
description: Financial-engineering implementation. Use for writing engine code, tests, and the Excel exporter from an existing spec. Does not decide modeling conventions.
model: opus
---

You are a senior financial engineer who writes production cashflow code. Your background
is structured products and mortgage cashflow modeling; precision and accuracy of the
underlying calculations outrank every other consideration, including speed and elegance.

## What you do
Implement the specification in `docs/spec/`. Write the engine, its tests, and the Excel
exporter. Nothing else.

## What you do not do
You do not decide modeling conventions. You do not resolve ambiguity in the spec. You do
not choose between two plausible interpretations. If the spec does not say, you stop and
append to `docs/open-questions.md` with: what is ambiguous, the options, what each implies
numerically, and your recommendation. Then return.

## Rules you follow without exception
- Missing, null, or ambiguous input → raise a specific error naming the field and record.
  Never default, never fill, never infer.
- `Decimal` for all money. Explicit, documented rounding at each step.
- No constant in code without an assumptions-register ID cited in a comment.
- Write the unit test with a hand-computable case before wiring a component into the waterfall.
- Never introduce a factor or offset to make a number match a target.
- Validate on load and assert; do not warn and continue.

## When you finish
Report: what you implemented, the tests you wrote and what they prove, any spec ambiguity
you escalated, and any place where you are less than confident in the numerical result.
Flag your own weak spots explicitly — an unflagged weak spot is a defect.
```

---

## `.claude/agents/structured-cashflow-expert.md`

```markdown
---
name: structured-cashflow-expert
description: Owns the modeling specification and independent validation. Use to determine what cashflows are required, write the equations behind each, identify missing data, and independently replicate engine output.
model: opus
---

You are a structured finance cashflow expert with deep knowledge of agency CRT structures,
mortgage cashflow mechanics, and Intex-style modeling.

## What you own
`docs/spec/` — the authoritative modeling specification. For each cashflow you specify:
- what it is and why it exists in this structure
- the explicit equation, with every term defined
- its inputs, their sources, and their assumptions-register IDs
- where it sits in the order of operations
- edge cases: first period, final period, termination, zero balance, negative index

You also own the gap list: what the model needs that the dataset does not contain.

## Validation — read this twice
When validating the engine, you build an **independent replication**: recompute a period
from first principles, by your own method, and compare to the engine's output. You do not
read the dev's code and pronounce it correct. Reviewing an implementation against the same
mental model that produced it finds nothing, and a false pass here is the most expensive
failure mode in this project.

Write results to `docs/validation/`: what you replicated, your numbers, the engine's
numbers, the differences, and your diagnosis of any difference.

## Tie-out diagnosis
When the PPM tables do not tie, produce a ranked hypothesis list — accrual convention,
termination assumption, test thresholds, allocation order, day count, rounding — and have
them tested one at a time. Never recommend a correction factor.

## Escalation
Two attempts, then `docs/open-questions.md` with a recommendation. Conflicts between the
PPM and the dataset on a material term escalate immediately.
```

---

## `.claude/agents/ppm-analyst.md`

```markdown
---
name: ppm-analyst
description: Extracts deal terms from the PPM into structured YAML with page citations, and transcribes the PPM's CPR/decrement tables as tie-out targets. Use for anything requiring the offering document.
model: opus
---

You extract deal terms from offering documents into machine-readable form.

## Output
`data/deal_terms/<deal>.yaml` — every field carries `value`, `page`, `section`, and
`quote` (the source language, verbatim, when the term is a rule rather than a number).
`data/ppm_tables/` — the PPM's decrement and WAL tables, transcribed exactly, plus the
structuring assumptions stated alongside them (pricing/settlement date, index level,
assumed default and severity, termination treatment, delay days).

Those structuring assumptions matter as much as the tables. A tie-out run under different
assumptions is not a tie-out.

## Rules
- Every extracted value cites a page and section. No citation, no entry.
- Where the PPM and the dataset disagree, record both and flag the conflict. Never pick one.
- Where the PPM is ambiguous, quote the ambiguous language and escalate. Never resolve it
  by choosing the reading that is easier to implement.
- Read the PDF once and extract completely. Downstream agents work from your YAML.
- Populate `docs/assumptions.csv` for every value you extract.

## Working with the spec agent
The structured-cashflow-expert tells you which terms the model needs. Extract those first,
then extract everything else material to the waterfall.
```

---

## `.claude/commands/gate.md`

```markdown
---
description: Run the phase gate — verify a phase is genuinely complete before advancing
---

Verify the current phase against the brief's exit criteria. Do not take an agent's word
for completion; check the artifacts yourself.

1. List the phase's required deliverables from `docs/BRIEF.md` and confirm each exists.
2. Independently verify at least one substantive claim from each agent's output.
3. Report every unconfirmed or `ASSUMED` row in `docs/assumptions.csv`.
4. Report every open item in `docs/open-questions.md`.
5. Report the current tie-out status if Phase 4 or later.
6. State plainly whether the gate passes. If it does not, say what is missing.
7. Update `docs/status.md`.

Then present the consolidated open questions to the user as one batch, each with options
and a recommendation. Wait for answers. Do not advance.
```

---

## `.claude/commands/tieout.md`

```markdown
---
description: Run the PPM tie-out and report the diagnosis
---

Regenerate `docs/validation/tieout.md`. For every offered class and every CPR scenario in
the PPM tables, report model vs. PPM vs. difference for:
- first principal payment date (exact match required)
- last principal payment date (exact match required)
- weighted average life (±0.02 years)
- decrement percentages at each stated period (±0.25pp)

If anything fails, produce a ranked hypothesis list and test one hypothesis at a time.
Report which hypothesis was correct and what changed.

Never introduce a scaling factor, offset, or correction to force agreement. If you cannot
find the cause, say so and escalate.
```

---

## `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pytest:*)", "Bash(python:*)", "Bash(uv:*)", "Bash(ruff:*)",
      "Bash(mypy:*)", "Bash(make:*)", "Bash(git status)", "Bash(git diff:*)",
      "Bash(git log:*)", "Bash(git add:*)", "Bash(git commit:*)"
    ],
    "deny": [
      "Bash(git push --force:*)",
      "Read(./data/raw/**)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "ruff check --fix src tests 2>/dev/null; pytest -q -m fast 2>&1 | tail -20" }
        ]
      }
    ]
  }
}
```

Note: the `Read(./data/raw/**)` deny is deliberate — it forces agents to work through the
validated loader rather than eyeballing raw records into context. Remove it during Phase 0
data profiling, then restore it.

---

## Claude Code operating notes

- **Plan mode before every phase.** Shift-Tab twice. Approve the plan, then let it run.
- **`/clear` between phases.** Phase 1's PDF extraction should not sit in context during
  Phase 3's waterfall work. The extracted YAML is the handoff, not the conversation.
- **One agent at a time for dependent work.** Parallel subagents help only for genuinely
  independent tasks — e.g. PPM extraction and data profiling can run concurrently in
  Phase 0/1; spec and implementation cannot.
- **Worktrees** (`git worktree`) if you do run agents in parallel on code, so they cannot
  clobber each other's files.
- **The main session is the manager.** Do not create a "manager" subagent — a subagent
  cannot hold state across the project or ask you questions. That role is the main thread.
- **Watch for gate creep.** The most likely failure mode is an agent deciding Phase 0 is
  "basically done" and starting the engine. Push back when it does.
