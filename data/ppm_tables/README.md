# PPM tables — tie-out targets for STACR REMIC 2026-DNA1

Transcribed by the `ppm-analyst` agent from `data/raw/stacr-2026-dna1-ppm.txt` (the
`pdftotext -layout` extract of the Private Placement Memorandum dated February 12, 2026).
The PDF was not opened. Page numbers below are **PDF page numbers** (1 + the number of
form-feed characters before the line); the PPM's own printed folio is roughly PDF page
minus 21 in this region (e.g. PDF p139 carries printed folio 118).

Every value is copied as printed: no rounding, no unit conversion, no blank filled. Numbers
are stored as strings exactly as they appear (including `%` signs, thousands separators and
trailing zeros) so that a tie-out test can compare against the printed precision.

## Files

| File | Source pages | Rows |
|---|---|---|
| `appendix_c_rep_lines.csv` | p255 (Appendix C) | 31 |
| `wal_tables.csv` | p139-140 (Weighted Average Life Tables) | 3,168 |
| `declining_balances.csv` | p141-145 (Declining Balances Tables) | 3,168 |
| `credit_event_sensitivity.csv` | p146 (Credit Event Sensitivity Tables) | 96 |
| `table1_classes.csv` | p10-11 (Table 1) | 27 |
| `modeling_assumptions.yaml` | p136-138, p10-11, p147-156 | 19 assumptions + 5 table families |
| `register_rows.csv` | as cited per row | 40 (ids T1-T40) |

### `appendix_c_rep_lines.csv`
"Assumed Characteristics of the Reference Obligations (as of the Cut-off Date)", 31 groups.
Columns: `group`, `original_balance`, `outstanding_principal_balance`,
`remaining_term_months`, `original_term_months`, `interest_rate_pct`. Balances keep the
printed thousands separators and two decimals; the rate is the printed three-decimal
percentage. This is the pool the PPM's tables were computed on (Modeling Assumption (a)).

Verification (computed with `Decimal` after stripping separators):
- sum of `original_balance` = **23552092000.00** — equals 23,552,092,000 (register D3).
- sum of `outstanding_principal_balance` = **22781151551.84** — equals the Cut-off Date
  Balance 22,781,151,551.84 (register P10 / D6) to the cent.

### `wal_tables.csv`
One row per (class, basis, CPR, CER, RM) cell. Columns:
`table_name`, `page`, `class_group_as_printed`, `class`, `class_footnote`, `basis`,
`early_redemption`, `cpr_pct`, `cer_pct`, `rm_pct`, `wal_years`.

- The PPM prints five tables, each headed by a class group (e.g. "Class M-2, M-2R, M-2S,
  M-2T, M-2U and M-2I"). `class_group_as_printed` keeps that heading; `class` is one member
  of it, so the group's 12 printed cells are repeated once per member. All 4 Original Note
  classes and all 20 MACR classes in Table 1 are covered.
- `basis` is the printed column-block heading, "To Scheduled Maturity Date" or "To Early
  Redemption Date"; `early_redemption` is the yes/no equivalent.
- `cer_pct` and `rm_pct` are the PPM's own axis labels ("CER", "RM") as printed, e.g.
  `0.25%`. `cpr_pct` is the column header without the sign, e.g. `10`.
- `class_footnote` is `*` for M-2RB, M-2SB, M-2TB and M-2UB, whose heading carries the p140
  footnote "* Based on Class Principal Balance."; empty otherwise.
- The WAL tables print no principal windows, so none are recorded here. The only principal
  windows in the PPM are the Table 1 "Expected Principal Window (Months)" values.

### `declining_balances.csv`
"Percentages of Original Balances Outstanding† and Weighted Average Lives". One row per
(class, CPR, period label). Columns: `table_name`, `page`, `class_group_as_printed`,
`class`, `class_footnote`, `cpr_pct`, `date_or_month`, `pct_of_original_balance`,
`wal_years`.

- `date_or_month` is the row label exactly as printed with the leader dots removed:
  "Closing Date", "February 25, 2027", ..., "February 25, 2030 and thereafter", and the two
  WAL rows "Weighted Average Life (years) to Scheduled Maturity Date" and "Weighted Average
  Life (years) to Early Redemption Date**".
- Balance rows fill `pct_of_original_balance` (whole numbers as printed; the † footnote on
  p141 reads "Rounded to the nearest whole percentage.") and leave `wal_years` empty. The
  two WAL rows do the reverse.
- Footnote `**` (p141-145): "Based on the assumption that the Early Redemption Date occurs on
  the first eligible Payment Date." Footnote `*` (p145) as in the WAL tables.
- Period counts differ by table because each table stops at the year its class is retired at
  0% CPR: A-1 5 dates (+2 WAL rows), M-1 19, M-2 group 21, M-2A group 20, M-2B group 21.
- Cross-check: every WAL row printed under a Declining Balances table equals the WAL-table
  cell for the same class, basis and CPR at CER 0.00% / RM 0.00% (0 mismatches over the 60
  printed cells: 5 tables x 2 WAL rows x 6 CPRs), consistent with Modeling Assumption (d)(ii) (no Credit Events in these tables).

### `credit_event_sensitivity.csv`
"Cumulative Credit Event Amount (as % of Reference Pool Cut-off Date Balance)", two tables
("to Scheduled Maturity Date", "to Early Redemption Date"), 8 CER rows x 6 CPR columns each.
Columns: `table_name`, `page`, `table_title`, `basis`, `early_redemption`, `cpr_pct`,
`cer_pct`, `cumulative_credit_event_amount_pct_of_cutoff_balance`. Values keep the printed
one-decimal `%` form. There is no RM axis in these tables.

### `table1_classes.csv`
Table 1 (p10) plus the X-IO row and footnote references (p11). Columns follow the printed
column headers: `note_type`, `class`, `class_footnote`, `original_class_principal_balance`
(for MACR Notes this is the printed "Maximum Class Principal Balance or Notional Principal
Amount"), `balance_footnote`, `initial_class_coupon`, `coupon_footnote`,
`class_coupon_formula`, `class_coupon_minimum_rate`, `cusip_number` (printed as the
footnote reference "(14)" — see Appendix F), `scheduled_maturity_date`,
`expected_ratings_sp_morningstar_dbrs`, `expected_wal_years`,
`expected_principal_window_months`, `expected_initial_credit_enhancement`.

- The task schema asked for `expected_final_payment_date`; Table 1 prints no such column.
  The date column it does print is "Scheduled Maturity Date" (February 2046 for every Note),
  kept under its own name.
- Footnote markers printed against a value are kept in the adjacent `*_footnote` column
  rather than stripped, e.g. `(6)` = Notional Principal Amount, `(7)` = fixed-rate IO
  coupon, `(8)`/`(9)` = the M-2RB/SB/TB/UB balance and coupon rules. The footnote text is
  on p11 of the extract and is not repeated here.
- The B-1H and B-2H Reference Tranches are not Notes; Table 1 prints only their coupons.
  Their balances are in Table 3 (p23), outside this transcription. X-IO has no balance or
  coupon in Table 1 (footnotes (12), (13)). Those cells are left empty, not filled.
- Dollar signs are dropped from balances; everything else is verbatim.

### `modeling_assumptions.yaml`
Modeling Assumptions (a) through (s) verbatim from p136-137 (line breaks and the page-break
folio "115" collapsed; (k) spans p136-137), the CPR / CER / RM definitions from p137-138,
the Table 1 footnote (1) basis, and, for each of the five table families, which assumptions
apply: Credit Events, Preliminary Principal Loss Amount, Modification Events, early
redemption, SOFR, the Delinquency Test and the printed grid, with page ranges. The
Cumulative Note Write-down Amount Tables (p147-148) and Yield Tables (p149-156, with the
assumed price per class) are recorded as existing but are not transcribed.

### `register_rows.csv`
Forty rows (T1-T40) in the exact column order of `docs/assumptions.csv`, covering the
structuring assumptions above and the Table 1 values not already in P1-P8. For the Manager
to merge; `docs/assumptions.csv` was not edited.

## Pricing-speed check
Table 1 footnote (1) (p11) states the expected WALs assume redemption on the Early
Redemption Date in February 2031, the Pricing Speed of 10% CPR from the Closing Date, no
Credit Events and no Modification Events. For every one of the 24 Note classes, the Table 1
expected WAL equals the WAL-table cell at **CER 0.00%, RM 0.00%, 10% CPR, "To Early
Redemption Date"**, and also the "to Early Redemption Date**" WAL row at 10% CPR in the
Declining Balances tables:

| Class family | Table 1 | WAL table, 10% CPR, early redemption | same cell, to scheduled maturity |
|---|---|---|---|
| A-1 | 1.59 | 1.59 | 1.59 |
| M-1 | 1.75 | 1.75 | 1.75 |
| M-2A (+ AR/AS/AT/AU/AI) | 4.11 | 4.11 | 4.11 |
| M-2B (+ BR/BS/BT/BU/BI/RB/SB/TB/UB) | 4.79 | 4.79 | 4.81 |
| M-2 (+ R/S/T/U/I) | 4.45 | 4.45 | 4.46 |

The last column shows that the early-redemption basis is what Table 1 uses (M-2 and M-2B
differ under the scheduled-maturity basis), so the engine's Table 1 tie-out must run with
the early redemption of Modeling Assumption (m) switched on.

## Transcription conventions and caveats
- Parsed programmatically from the text extract with per-row regexes that require exactly
  the expected token count (12 values per WAL row, 6 per Declining Balances / Credit Event
  Sensitivity row, 6 fields per Appendix C row); any row failing that would have aborted the
  run. Row counts per table were asserted (11 CER/RM rows per WAL table, 8 CER rows per
  Credit Event Sensitivity table, 31 Appendix C groups, 27 Table 1 rows).
- `pdftotext -layout` column misalignment was visible in the Declining Balances headers
  (e.g. `10% 15% 25%` run together) but every data row split cleanly into six tokens, so
  no cell was ambiguous and no judgement call was needed. No cell was left blank in any
  transcribed table; the only empty cells are the Table 1 cells the PPM itself does not
  print (see above).
- The CER definition (p138) gives an annual rate applied monthly to the then-outstanding
  balance but does not state the annual-to-monthly conversion or whether CER and CPR
  compete for the same balance. That is a modeling question for the spec, not a
  transcription gap; it is flagged in register row T27.
- CSVs are written with Python's `csv` module, UTF-8, LF line endings. The YAML uses UTF-8
  and keeps the PPM's typographic characters (`†`, curly quotes) where they appear.
- Nothing under `src/` or `tests/` was touched, and nothing was committed.
