# CRT Cashflow Engine

[![CI](https://github.com/jjd98git/crt-cashflow-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/jjd98git/crt-cashflow-engine/actions/workflows/ci.yml)

Intex-adjacent cashflow engine for Freddie Mac STACR credit risk transfer transactions.
Given a CRT loan-level disclosure dataset and the deal's offering memorandum, it projects
reference-pool and reference-tranche cashflows under user-supplied prepayment, default and
severity scenarios, and exports an auditable Excel workbook.

Reference deal for v1: **STACR REMIC 2026-DNA1**.

## Status
Phases 0-3 complete; Phase 4 tie-out running (CER 0 families tie exactly; CER>0 open as Q21). Run `python -m crt.tieout`. See `docs/status.md` and `docs/validation/tieout.md`.

## Setup (Windows 11 / Git Bash)
```bash
uv venv
source .venv/Scripts/activate      # or .venv\Scripts\activate in PowerShell
uv pip install -e ".[dev]"
pytest -q
```

## Run on GitHub (no local setup)
- **Codespaces**: on the repo page click *Code → Codespaces → Create codespace on main*. The
  devcontainer installs everything and runs the fast tests. Then in the Codespace terminal run
  `./gui.sh`; the forwarded port 8501 opens the GUI in your browser. Run the tie-out with
  `.venv/bin/python -m crt.tieout`.
- **CI**: every push runs ruff, mypy, the unit and GUI tests, the full PPM tie-out, and a
  secret scan; the regenerated tie-out report is attached to each run as an artifact
  (*Actions → the run → Artifacts → tieout-report*).

## Run in the browser
**https://jjd98git.github.io/crt-cashflow-engine/** - no install, no login. The page loads the
real Python engine (the `crt` wheel built from this repository) into the browser with
[Pyodide](https://pyodide.org/) and runs it client-side in a Web Worker; nothing is uploaded.
You can pick a PPM grid point or type a scenario, see the Note summary, the tranche stack, the
write-downs and the pool balance, open the full tables, download the CSV bundle or the Excel
workbook, and run the 96-scenario PPM tie-out on demand. Every number on the page is a string the
engine produced; the page does no arithmetic.

- **Data travels as JavaScript.** The engine wheel, its two pure-Python dependencies
  (openpyxl, et_xmlfile), the deal data and the build manifest are packed at build time into
  one script, `data/bundle.js` (`self.CRT_BUNDLE = {...}`; text files as strings, wheels as
  base64, each with its SHA-256 and byte count). The worker loads it with `importScripts` and
  never fetches a data file; it decodes each file, hashes it and compares against the manifest
  before writing it into Pyodide's file system. Field evidence behind this: a corporate proxy
  that filters by file type let the site's scripts and the CDN's runtime through but dropped a
  same-site `manifest.json` with `TypeError: Failed to fetch`. The same files are still served
  as `manifest.json` / `manifest.bin` and `files/<hash>.bin` for diag.html and `curl` checks;
  the app does not depend on them.
- **Runtime: this site, then the CDN.** Pyodide fetches its own files by name
  (`pyodide.asm.wasm`, `python_stdlib.zip`, `pyodide-lock.json`, two `.whl`) from an
  `indexURL`, so it cannot travel inside a script. The worker tries the candidates in
  `scripts/build_web.py` `RUNTIME_CANDIDATES` in order: the self-hosted copy under `pyodide/`
  on this site, then the same pinned release on `cdn.jsdelivr.net`. Each candidate is probed
  with a GET of its small `pyodide-lock.json` (10-second timeout); a candidate whose probe
  fails is logged in the boot panel with the exact URL and reason and skipped. If
  `loadPyodide` fails or hangs beyond 90 seconds after a candidate's `pyodide.js` was
  imported, the page terminates the worker and restarts it at the next candidate. Chart.js
  loads from `vendor/` on this site with an `onerror` fallback to the same release on cdnjs.
  The engine line under the title says where the runtime, Chart.js and the data came from and
  which origins were contacted (informational). `?runtime=site-only` or `?runtime=cdn-only`
  on the page URL restricts the candidates, for diagnosis.
- **What a proxy would have to block for the page to fail:** JavaScript itself (the page's
  own scripts, or `data/bundle.js`, from this site *and* Chart.js from cdnjs), or the Pyodide
  runtime (WebAssembly, `.zip`, `.json`, `.whl`) from *both* this site and cdn.jsdelivr.net.
  Blocking any one of those file types on one host is not enough.
- **Diagnostics.** If the page cannot start, it names the exact URL that failed;
  [diag.html](https://jjd98git.github.io/crt-cashflow-engine/diag.html) loads the bundle the
  way the worker does (a script tag) and reports whether it parsed, fetches both runtime
  candidates' `pyodide-lock.json`, and then tests every served file one at a time (status,
  bytes, SHA-256, content type).

The site is built by `scripts/build_web.py` (pinned SHA-256 for every downloaded runtime and
vendor file, cached under `web/.cache/`) and deployed by `.github/workflows/pages.yml` on every
push to `main`. To build and serve it locally: `.venv\Scripts\python scripts\build_web.py`, then
`python -m http.server 8777` inside `web\dist` and open http://127.0.0.1:8777/.

## Run locally
- GUI: double-click `gui.cmd`. From PowerShell run two separate lines (PowerShell 5.1 has
  no `&&`): `cd "C:\Users\jjdeg\OneDrive\Desktop\crt-cashflow-engine"` then
  `.venv\Scripts\python -m streamlit run src\crt\gui\app.py`.
- Tie-out: double-click `tieout.cmd`, or run `.venv\Scripts\python -m crt.tieout`.
- Scenario files live in `scenarios/`; CSV bundles download from the GUI.

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
