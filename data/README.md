# Data

Everything in `raw/` is gitignored. All sources are publicly available; they are kept out
of the repo for size and reproducibility reasons, not confidentiality ones.

## Files

| File | Source | Notes |
|---|---|---|
| `raw/26DNA1_20260701_lld.txt` | Freddie Mac CRT loan-level monthly disclosure (Clarity download) | 2026-07 reporting period |
| `raw/26DNA1_20260801_lld.txt` | Freddie Mac CRT loan-level monthly disclosure (Clarity download) | 2026-08 reporting period |
| `raw/stacr-2026-dna1-ppm.pdf` | STACR REMIC 2026-DNA1 private placement memorandum | 285 pages |
| `raw/stacr-2026-dna1-ppm.txt` | derived | `pdftotext -layout` extract; use this, not the PDF |
| `raw/crt-reference-pool-disclosure-file-layouts-v4.2.pdf` | https://capitalmarkets.freddiemac.com/crt/docs/pdfs/crt-reference-pool-disclosure-file-layouts.pdf | Version 4.2, effective July 2026. Defines the 93 positional fields |
| `raw/crt-reference-pool-disclosure-file-layouts-v4.2.txt` | derived | `pdftotext -layout` extract |
| `raw/crt-reference-pool-glossary.pdf` | https://capitalmarkets.freddiemac.com/crt/docs/pdfs/crt-reference-pool-glossary.pdf | Version 4.2. Field definitions and code enumerations |
| `raw/crt-reference-pool-glossary.txt` | derived | `pdftotext -layout` extract |

SHA-256 hashes of every raw file are listed in `docs/data-inventory.md` §1.

Loan-level files were originally downloaded as `fre-crt-2026-07-2026-08 (1).zip` from
Clarity (https://capitalmarkets.freddiemac.com/crt/clarity, registration required). Note a
second zip of the same name without the `(1)` contains a DIFFERENT deal (26SPH3) plus a
zipcode aggregate file — do not confuse them.

## Format
Pipe-delimited, **no header row**, 93 positional fields per the layout document above,
64,434 rows per month, no ragged rows. Field names, types and observed contents are
tabulated in `docs/data-inventory.md` §3.

## Not yet in hand
- The monthly STACR 2026-DNA1 payment date statements (class balances, factors, losses).
  See open question Q4.
- The at-issuance loan-level file. Not needed: field 14 of the monthly file reproduces the
  cut-off pool exactly.

## Committed derivatives
`data/deal_terms/*.yaml` and `data/ppm_tables/*` ARE committed — they are the extracted,
citable form of the offering document that the engine consumes.
