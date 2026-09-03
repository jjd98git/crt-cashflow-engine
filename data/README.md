# Data

Everything in `raw/` is gitignored. Both sources are publicly available; they are kept out
of the repo for size and reproducibility reasons, not confidentiality ones.

## Files

| File | Source | Notes |
|---|---|---|
| `raw/26DNA1_20260701_lld.txt` | Freddie Mac CRT loan-level disclosure | 2026-07 factor date |
| `raw/26DNA1_20260801_lld.txt` | Freddie Mac CRT loan-level disclosure | 2026-08 factor date |
| `raw/stacr-2026-dna1-ppm.pdf` | STACR REMIC 2026-DNA1 offering memorandum | 286 pages |
| `raw/stacr-2026-dna1-ppm.txt` | derived | `pdftotext -layout` extract; use this, not the PDF |

Originally downloaded as `fre-crt-2026-07-2026-08 (1).zip`. Note a second zip of the same
name without the `(1)` contains a DIFFERENT deal (26SPH3) plus a zipcode aggregate file —
do not confuse them.

## Format
Pipe-delimited, **no header row**, 93 positional fields, 64,434 rows per month, no ragged
rows. Because there is no header, the published Freddie Mac CRT file layout / data
dictionary is required to name fields. **It is not in the zip.** This is open question Q1.

## Committed derivatives
`data/deal_terms/*.yaml` and `data/ppm_tables/*` ARE committed — they are the extracted,
citable form of the offering document that the engine consumes.
