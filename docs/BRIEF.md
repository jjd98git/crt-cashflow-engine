# CRT Cashflow Engine — Project Brief

Paste this as your opening message in Claude Code. Do not let it write engine code
until Phase 0 and Phase 1 are complete and I have signed off on the assumptions register.

---

## 1. Objective

Build an Intex-adjacent cashflow engine for Freddie Mac STACR CRT transactions. Given
(a) a CRT loan-level disclosure dataset and (b) the deal's Private Placement Memorandum,
the tool projects reference-pool and reference-tranche cashflows under user-supplied
prepayment, default, and severity scenarios, and exports an auditable Excel workbook.

Reference deal for v1: **STACR 2026-DNA1**.

**Definition of done for v1** — all four must hold:

1. The engine reproduces the PPM's decrement / weighted-average-life tables for every
   offered class, under the PPM's own stated structuring assumptions, within the
   tolerances in §7.
2. Every number the model consumes appears in the assumptions register (§8) with a
   traceable source, and I have marked each one confirmed.
3. The exported Excel workbook recomputes the same cashflows with live formulas and
   agrees with the Python engine cell-for-cell to the penny.
4. `pytest` is green, CI is green, and the repo is on GitHub.

Anything short of that is a work in progress, not a v1.

---

## 2. Non-negotiable engineering rules

These override any instinct toward "getting something running."

- **No fabricated data.** If a required field is missing, null, or ambiguous, raise an
  explicit error naming the field and the loan/record. Never default to zero, never
  forward-fill, never infer. A missing field is an escalation (§11), not a code branch.
- **No plugging.** If a tie-out fails, you diagnose which modeling convention differs.
  You never introduce a scaling factor, offset, or fudge to force agreement. A tuned
  match is a worse outcome than an honest mismatch.
- **Money is `Decimal`**, never `float`. Define rounding explicitly at every step and
  document the convention. Rates and factors may be float; balances, interest, principal,
  and losses may not.
- **Every assumption is registered.** No magic number appears in code without a
  corresponding row in `docs/assumptions.csv` and a comment citing its ID.
- **Deterministic and reproducible.** Every run writes a manifest: input file SHA-256
  hashes, scenario definition, engine version, git commit, UTC timestamp. Two runs of the
  same manifest produce byte-identical output.
- **Fail loud, fail early.** Validate on load: row counts, expected column set, date
  monotonicity, balance continuity, pool balance vs. deal-level totals. Assert; don't warn.
- **Tests before tuning.** Every cashflow component gets a unit test with a hand-computable
  case before it is wired into the waterfall.
- **The PDF is read once.** The PPM is extracted to structured YAML/JSON in Phase 1.
  After that, no agent re-reads the PDF; they read the extract. If the extract is wrong,
  fix the extract.

---

## 3. Phased plan with hard gates

Use plan mode before each phase and get my approval before writing code for it.
**Do not skip ahead.** Do not scaffold the GUI in Phase 0 because it is fun.

**Phase 0 — Data reconnaissance (no engine code).**
Unzip and profile the dataset. Produce `docs/data-inventory.md`: every file, its layout,
row counts, field list with dtypes, date ranges, null rates, and — critically — a
plain-English statement of what one row represents in each file. Reconcile the loan-level
pool balance to the deal-level disclosure. Identify which fields the cashflow model needs
and which of those are **absent**. Output: inventory + a gap list.

**Phase 1 — PPM extraction (no engine code).**
Extract deal terms to `data/deal_terms/stacr_2026_dna1.yaml` with a page/section citation
on every field: tranche names, original balances, coupon formulas (index, margin, day
count, floors/caps), payment date convention, principal allocation rules, loss allocation
rules, credit event definition, write-down/write-up mechanics, credit enhancement test,
delinquency test, cumulative net loss test, optional termination and mandatory
termination provisions, and the exact structuring assumptions behind the PPM's
CPR/decrement tables. Also transcribe the PPM's CPR tables themselves into
`data/ppm_tables/` as the tie-out target. Output: YAML + the assumptions register (§8).

**GATE: I review and confirm the assumptions register before any engine code is written.**

**Phase 2 — Pool engine.**
Project the reference pool: scheduled amortization, voluntary prepayments (CPR), defaults
(CDR/credit events), loss severity, and the resulting principal/interest/loss vectors.
Loan-level and/or representative-line, whichever the data supports — state which and why.

**Phase 3 — Waterfall engine.**
Tranche-level principal allocation, interest accrual, loss write-down, write-up, and the
performance tests that gate subordinate principal. Sequential and pro-rata regimes, plus
the switch conditions.

**Phase 4 — Tie-out.** §7. This is the phase that determines whether the tool is real.

**Phase 5 — Excel export.** §9.

**Phase 6 — Scenario input.** User-supplied CPR/CDR/severity vectors and ramps.

**Phase 7 — GUI.**

**Phase 8 — AI shell.**

---

## 4. Agents — roster and how they actually communicate

Important mechanical correction to how you may be tempted to set this up: **Claude Code
subagents cannot talk to each other.** They are stateless, spawned by the main session,
and return exactly one final message. There is no back-and-forth between a dev agent and
a reviewer agent.

So the architecture is: **the main session is the Manager.** It is the only thing that
holds continuity, the only thing that talks to me, and the only router between agents.
Agents communicate through **files in the repo**, not through conversation.

### The Manager (main session — not a subagent)

- Owns the phase plan and the gates. Refuses to let work jump a gate.
- Routes work to subagents and reads their outputs.
- Owns `docs/open-questions.md`. Consolidates everything blocked or ambiguous and brings
  me **one batched list per phase**, not a trickle of interruptions.
- Acts as adversarial check: before accepting a subagent's output, it verifies at least
  one claim independently.
- Never writes engine code itself.

### `fintech-dev` (subagent)

Financial-engineering implementation. Strong background in cashflow modeling and
production numerical code. Follows §2 absolutely. Writes the engine, the tests, the
Excel exporter. Does **not** decide modeling conventions — it implements the spec in
`docs/spec/`. If the spec is ambiguous, it stops and writes to `docs/open-questions.md`
rather than choosing.

### `structured-cashflow-expert` (subagent)

Owns `docs/spec/` — the authoritative modeling specification. Determines *what* cashflows
must exist, the math and equations behind each, the order of operations, and what data
the dataset lacks. Writes each cashflow as an explicit equation before the dev implements it.

**Critical:** when validating, this agent must build an **independent** replication —
its own small recalculation of a period from first principles — and compare. It must not
review the dev's code and pronounce it correct. Reviewing an implementation against the
same mental model that produced it finds nothing.

### `ppm-analyst` (subagent)

Owns PDF extraction and the deal-terms YAML. Every extracted value carries a page and
section citation. Where the PPM and the dataset disagree, it flags the conflict — it does
not silently pick one. Works from the spec agent's list of "terms the model needs."

### Handoff protocol (the file-based substitute for conversation)

```
docs/spec/*.md              spec agent → dev agent    (what to build, with equations)
docs/open-questions.md      any agent → Manager → me  (blocked, batched per phase)
docs/assumptions.csv        all agents                (every number, with provenance)
docs/validation/*.md        spec agent                (independent replication results)
data/deal_terms/*.yaml      ppm agent → everyone      (extracted PPM terms)
```

Every entry in `open-questions.md` uses: `ID | phase | raised-by | question | why blocked |
what I tried | options with recommendation`. Give me a recommendation. Do not hand me a
bare question.

---

## 5. Data contracts

Source dataset: `fre-crt-2026-07-2026-08 (1).zip` (Freddie Mac CRT loan-level disclosure,
July–August 2026), in my Downloads folder. The matching PPM is `stacr-2026-dna1-ppm`,
also in Downloads.

- Parse against the **published file layout / data dictionary**, not by guessing from
  headers. If the layout file is not in the zip, that is an open question — retrieve or
  request it before parsing.
- Loader validates and rejects; it does not coerce.
- Two loan-months of history is thin. State explicitly what can and cannot be estimated
  from it — actual prepay/default experience almost certainly cannot be, which means the
  scenario inputs carry all the behavioral assumptions. Say so plainly rather than
  producing a projection that implies more empirical grounding than exists.
- Write a `data/README.md` with the public source links for the disclosure files and the
  PPM. Keep the source documents out of the repo for size and reproducibility reasons (§10),
  not confidentiality ones — both are public.

---

## 6. Modeling conventions — starting defaults

These are my starting assumptions for a STACR DNA actual-loss structure. **Every one is a
hypothesis, not a fact.** The `ppm-analyst` must confirm or override each against the PPM
and record the outcome in the assumptions register. Any that the PPM contradicts: the PPM
wins, and the override gets flagged to me.

| # | Convention | Default assumption | Status |
|---|---|---|---|
| C1 | Loss basis | Actual loss (not fixed severity) | CONFIRM |
| C2 | Credit event trigger | 180+ days delinquent, or short sale / deed-in-lieu / third-party sale / REO disposition / note sale, whichever occurs first | CONFIRM |
| C3 | Loss components | Realized loss on liquidation, plus modification losses; net of any recoveries and reversals | CONFIRM |
| C4 | Coupon index | 30-day Average SOFR + class margin, Act/360, floored at zero | CONFIRM |
| C5 | Principal allocation | Sequential to reference tranches, subject to performance tests | CONFIRM |
| C6 | Loss allocation | Reverse sequential, from the most subordinate tranche upward | CONFIRM |
| C7 | Write-up | Subsequent recoveries write balances back up in sequential order | CONFIRM |
| C8 | Performance tests gating subordinate principal | Minimum credit enhancement test, delinquency test, cumulative net loss test | CONFIRM — get exact thresholds and formulas |
| C9 | Reference pool | 30-year fixed-rate, original LTV band ~60.01–80% (the DNA series) | CONFIRM |
| C10 | Termination | Optional termination on stated date/clean-up threshold; scheduled mandatory termination | CONFIRM — this materially affects WAL |
| C11 | Payment date / accrual period | Monthly, per the PPM's stated convention | CONFIRM |
| C12 | Prepay/default conventions | CPR on beginning-of-period scheduled balance; CDR on the same basis; SDA not used | CONFIRM |

Add rows for anything the PPM defines that this table missed. A convention that is neither
confirmed nor overridden by end of Phase 1 is an open question, not a default.

---

## 7. Tie-out specification

The PPM's decrement and WAL tables are the acceptance test. Reproducing them is the
single most important deliverable in this project.

- **Replicate the PPM's structuring assumptions exactly first**: stated pricing/settlement
  date, assumed index level, assumed default and severity (often zero in these tables),
  whether the optional termination is exercised, and the delay/dated dates. A tie-out run
  against different assumptions is not a tie-out; it is a coincidence hunt. Extract these
  assumptions verbatim in Phase 1 and record them as their own register entries.
- Tie-out targets, per class, per CPR scenario in the PPM tables:
  - **First and last principal payment date: exact month match.** No tolerance. This is
    the test that catches waterfall errors that WAL alone hides.
  - **WAL: within ±0.02 years.** Report ±0.1 as a first milestone, but v1 requires ±0.02.
  - **Decrement table percentages: within ±0.25 percentage points** at every stated period.
- Produce `docs/validation/tieout.md`: a per-class, per-scenario table of model vs. PPM
  vs. difference, plus pass/fail against each tolerance. Regenerate it on every run.
- Add the tie-out as a **regression test in CI**. A change that breaks the tie-out must
  fail the build.
- If it does not tie: write a diagnostic hypothesis list ranked by likely cause
  (accrual convention → termination assumption → test thresholds → allocation order →
  day count → rounding), test them one at a time, and document what was actually wrong.
  See the no-plugging rule in §2.

---

## 8. Assumptions register — the number ledger

This is the artifact I check the tool against, so it is a first-class deliverable, not
documentation.

`docs/assumptions.csv`, columns:

```
id, phase, item, value, unit, source_type, source_ref, extracted_by, confidence,
used_in, confirmed_by_user, notes
```

- `source_type` ∈ `{PPM, DATASET, DERIVED, ASSUMED, USER}`.
- `source_ref` = PPM page and section, or dataset file and field name, or the formula and
  its inputs' IDs. `ASSUMED` requires an explanation in `notes`.
- `used_in` = the module and function that consumes it, so I can trace any number to the
  code that uses it.
- Also render `docs/assumptions.md` — a human-readable version grouped by category, with
  everything `ASSUMED` or unconfirmed at the top under a heading I cannot miss.
- Every value in the register is asserted against in a test. If the YAML says the M-1
  margin is X, a test asserts the engine used X.

---

## 9. Outputs

**Excel workbook** (`openpyxl`/`xlsxwriter`), and it must be genuinely auditable:

- **Live formulas, not pasted values.** A reviewer must be able to click a cell and see
  the arithmetic. Hardcoded outputs defeat the purpose of the export.
- Tabs: `Inputs` (scenario + all register values, in one place, editable),
  `Pool` (period-by-period pool cashflows), one tab per tranche, `Waterfall` (allocation
  detail per period), `Summary` (WAL, duration, principal window, total loss by class),
  `TieOut` (model vs. PPM), `Assumptions` (the full register).
- **A test opens the exported workbook, recalculates, and asserts agreement with the
  Python engine to the penny.** This is the check that makes the export trustworthy.
- Also emit CSV/Parquet of every cashflow vector so results are consumable outside Excel.

**Scenario inputs**: YAML or CSV supporting flat vectors, ramps (e.g. 6 CPR ramping to
18 over 12 months), and step schedules, for CPR, CDR, severity, delinquency transition,
and index path. Validate on load; reject anything malformed with a specific message.

**GUI**: propose the stack in plan mode before building. Requirements: load a deal, pick or
edit a scenario, run, see tranche cashflows and summary metrics, compare two scenarios
side by side, export to Excel. Recommend an option and explain the trade-off; I have not
committed to a stack and I want your reasoning before you pick one.

**AI shell**: a conversational layer for follow-up questions, running on Sonnet. Hard rule:
**the model does no arithmetic.** It exposes the engine's functions as tools, calls them,
and reports engine output. Every numeric answer cites the run manifest ID it came from.
If a question requires a number the engine did not produce, the correct answer is to run
the engine, not to estimate. Read-only against saved runs by default; scenario mutation
requires explicit confirmation.

---

## 10. Repository and CI

- GitHub, **private**. Confirm the repo name with me before creating it.
- `.gitignore` excludes `data/raw/`, `*.zip`, and `*.pdf`. Both source documents are
  public, so this is a hygiene call, not a confidentiality one: large binaries bloat the
  repo, and a documented download link in `data/README.md` is a better reproducibility
  contract than a checked-in copy that silently drifts from the published version.
  Commit the *extracted deal terms* YAML and the PPM table transcriptions.
- No credentials, API keys, or `.env` committed. Add a pre-commit secret scan.
- CI on push: ruff, mypy (strict on the engine package), `pytest` including the tie-out
  regression test.
- Conventional commits. Small, reviewable commits — one concept each. No 2,000-line
  "implement waterfall" commit.
- `README.md` with setup, how to obtain the data, how to run a scenario, and the current
  tie-out status.

---

## 11. Escalation protocol

- An agent that cannot resolve something in **two attempts** stops and writes to
  `docs/open-questions.md`. It does not keep trying, and it does not proceed on a guess.
- The Manager consolidates and brings me the batch at a phase gate, or immediately if the
  whole phase is blocked.
- Escalate to me immediately, without batching: a PPM–dataset conflict on a material term;
  data required by the model that does not exist in the dataset; a tie-out failure that
  survives the diagnostic list in §7.
- Never resolve an ambiguity by picking the option that makes the code simpler.

---

## 12. Guardrails

- **No engine code before the Phase 1 gate.** Documents and data profiling only.
- If you find yourself considering a workaround to make a number match, stop and escalate.
- Prefer boring, explicit, slow code over clever code. This is a calculation engine;
  readability by a non-programmer reviewer is a feature.
- Keep the context lean: extract once, read the extract thereafter.
- At the end of each phase, write a short status to `docs/status.md`: what shipped, what
  is open, what changed in the register, and what the tie-out currently reads.

---

## 13. First actions

1. Read this brief back to me as a one-page plan with the phase gates, and tell me
   anything in it you think is wrong or under-specified.
2. Create the repo skeleton, `CLAUDE.md`, and `.claude/agents/` (see the scaffold file).
3. Begin Phase 0. Stop at the gate.
