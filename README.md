# CRT Cashflow Engine

Intex-adjacent cashflow engine for Freddie Mac STACR credit risk transfer transactions.
Given a CRT loan-level disclosure dataset and the deal's offering memorandum, it projects
reference-pool and reference-tranche cashflows under user-supplied prepayment, default and
severity scenarios, and exports an auditable Excel workbook.

Reference deal for v1: **STACR REMIC 2026-DNA1**.

## Status
Phase 0 (data reconnaissance) — complete, awaiting gate sign-off. See `docs/status.md` and `docs/data-inventory.md`.

## Setup (Windows 11 / Git Bash)
```bash
uv venv
source .venv/Scripts/activate      # or .venv\Scripts\activate in PowerShell
uv pip install -e ".[dev]"
pytest -q
```

## Data
Source files are in `data/raw/` and are gitignored. See `data/README.md` for provenance.

## How this project is run
Read `docs/BRIEF.md` first. Work proceeds in phases with hard gates; no engine code is
written before the Phase 1 gate is signed off. `CLAUDE.md` holds the non-negotiable
engineering rules. `/gate` and `/tieout` are the two slash commands.

## Definition of done for v1
1. Reproduces the PPM's WAL and declining-balance tables within the tolerances in the brief.
2. Every number in `docs/assumptions.csv` traced to a source and confirmed by Trey.
3. Excel export recomputes with live formulas and agrees with the engine to the penny.
4. pytest green, CI green, on GitHub.
