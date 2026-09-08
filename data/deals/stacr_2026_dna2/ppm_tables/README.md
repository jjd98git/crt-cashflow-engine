# PPM tables — tie-out targets for STACR REMIC 2026-DNA2

Transcribed by the `ppm-analyst` agent from `data/raw/stacr-2026-dna2-ppm.txt` (the
`pdftotext -layout` extract of the Private Placement Memorandum dated March 13, 2026; the extract
is cp1252-encoded with CRLF line endings). The PDF was not opened. Page numbers below are **PDF
page numbers** (1 + the number of form-feed characters before the line; the file has 293 pages of
text plus one empty trailing page); the PPM's own printed folio is PDF page minus 22 in the tables
region (e.g. PDF p141 carries printed folio 119).

Every value is copied as printed: no rounding, no unit conversion, no blank filled. Numbers are
stored as strings exactly as they appear (including `%` signs, thousands separators and trailing
zeros). File names, column names and conventions are identical to `data/ppm_tables/` (DNA1) so
that tie-out code can consume both deals.

**Read the "Extraction caveats" section before using these files.** The DNA2 extract is
row-shifted in four of the tables; the decoding is deterministic and cross-checked, but it is a
decode, not a plain transcription.

## Files

| File | Source pages | Rows |
|---|---|---|
| `appendix_c_rep_lines.csv` | p264 (Appendix C) | 38 |
| `wal_tables.csv` | p141-143 (Weighted Average Life Tables) | 4,356 |
| `declining_balances.csv` | p144-150 (Declining Balances Tables) | 4,500 |
| `credit_event_sensitivity.csv` | p151 (Credit Event Sensitivity Tables) | 96 |
| `table1_classes.csv` | p10-11 (Table 1) | 35 |
| `appendix_g_absent.md` | p9, p264-294 | one line: no Appendix G in this deal |
| `modeling_assumptions.yaml` | p138-140, p10-11, p141-165 | 19 assumptions + 5 table families + pricing-speed check |
| `register_rows.csv` | as cited per row | 45 (ids DNA2-T1 to DNA2-T45) |

### `appendix_c_rep_lines.csv`
"Assumed Characteristics of the Reference Obligations (as of the Cut-off Date)", 38 groups
(DNA1 had 31). Columns: `group`, `original_balance`, `outstanding_principal_balance`,
`remaining_term_months`, `original_term_months`, `interest_rate_pct`. Balances keep the printed
thousands separators and two decimals; the rate is the printed three-decimal percentage. This is
the pool the PPM's tables were computed on (Modeling Assumption (a), p138).

Verification (computed with `Decimal` after stripping separators):
- sum of `original_balance` = **27524842000.00** — equals the Aggregate Original Principal
  Balance $27,524,842,000 in "Selected Reference Obligation Data as of the Cut-off Date" (p229).
- sum of `outstanding_principal_balance` = **26703800234.86** — equals the Glossary Cut-off Date
  Balance $26,703,800,234.86 (p203) to the cent.
- balance-weighted interest rate 6.7198% (pool statistics: 6.720%); balance-weighted remaining
  term 351.84 months (statistics: 352); original term 359.99 (statistics: 360).

### `wal_tables.csv`
One row per (class, basis, CPR, CER, RM) cell. Columns:
`table_name`, `page`, `class_group_as_printed`, `class`, `class_footnote`, `basis`,
`early_redemption`, `cpr_pct`, `cer_pct`, `rm_pct`, `wal_years`.

- The PPM prints **seven** tables (DNA1: five), each headed by a class group: "Class M-1";
  "Class M-2, M-2R, M-2S, M-2T, M-2U and M-2I"; "Class M-2A, M-2AR, M-2AS, M-2AT, M-2AU and M-2AI"
  (all p141); "Class M-2B, M-2BR, M-2BS, M-2BT, M-2BU, M-2BI, M-2RB*, M-2SB*, M-2TB* and M-2UB*";
  "Class B-1, B-1R, B-1S, B-1T, B-1U and B-1I"; "Class B-1A, B-1AR and B-1AI" (all p142);
  "Class B-1B" (p143). `class_group_as_printed` keeps that heading; `class` is one member of it, so
  the group's cells are repeated once per member. All 5 Original Note classes and all 28 MACR
  classes in Table 1 are covered (33 classes x 11 rows x 12 cells = 4,356).
- `basis` is the printed column-block heading, "To Scheduled Maturity Date" or "To Early
  Redemption Date"; `early_redemption` is the yes/no equivalent.
- `cer_pct` and `rm_pct` are the PPM's own axis labels as printed, e.g. `0.25%`; `cpr_pct` is the
  column header without the sign, e.g. `10`.
- `class_footnote` is `*` for M-2RB, M-2SB, M-2TB and M-2UB, whose heading carries the p142
  footnote "* Based on Class Principal Balance."; empty otherwise.
- Grid: CPR 0, 5, 10, 15, 25, 35; (CER, RM) rows (0.00, 0.00), (0.25, 0.00), (0.50, 0.00),
  (1.00, 0.00), (1.50, 0.00), (2.50, 0.00), (3.00, 0.00), (5.00, 0.00), (0.00, 0.01),
  (0.50, 0.03), (1.00, 0.10) — identical to DNA1.
- No principal windows are printed in the WAL tables; the only windows are Table 1's.

### `declining_balances.csv`
"Percentages of Original Balances Outstanding and Weighted Average Lives", seven tables, one per
page p144-150 in the same class-group order as the WAL tables. Columns: `table_name`, `page`,
`class_group_as_printed`, `class`, `class_footnote`, `cpr_pct`, `date_or_month`,
`pct_of_original_balance`, `wal_years`.

- `date_or_month` is the row label exactly as printed with the leader dots removed: "Closing
  Date", "March 25, 2027", ..., then the last date label, then the two WAL rows "Weighted Average
  Life (years) to Scheduled Maturity Date" and "Weighted Average Life (years) to Early Redemption
  Date**". The last date label is "March 25, 2043 and thereafter" for M-1 (18 dates), "March 25,
  2045 and thereafter" for the M-2A group (20 dates) and "March 25, 2046" (21 dates, no "and
  thereafter") for the M-2, M-2B, B-1, B-1A and B-1B tables.
- Balance rows fill `pct_of_original_balance` (whole numbers as printed; footnote on p144:
  "Rounded to the nearest whole percentage.") and leave `wal_years` empty. The two WAL rows do the
  reverse.
- Footnote `**` (p144-150): "Based on the assumption that the Early Redemption Date occurs on the
  first eligible Payment Date." Footnote `*` (p147) as in the WAL tables. The dagger glyph that
  marks the rounding footnote on the heading and on the footnote line was not captured by the
  text extractor (the footnote line begins with a blank); the wording is present.
- Cross-check: every WAL row printed under a Declining Balances table equals the WAL-table cell
  for the same class, basis and CPR at CER 0.00% / RM 0.00% (0 mismatches over the 396 rows: 33
  classes x 2 bases x 6 CPRs), consistent with Modeling Assumption (d)(ii).

### `credit_event_sensitivity.csv`
"Cumulative Credit Event Amount (as % of Reference Pool Cut-off Date Balance)", two tables ("to
Scheduled Maturity Date", "to Early Redemption Date"), 8 CER rows x 6 CPR columns each, p151.
Columns: `table_name`, `page`, `table_title`, `basis`, `early_redemption`, `cpr_pct`, `cer_pct`,
`cumulative_credit_event_amount_pct_of_cutoff_balance`. Values keep the printed one-decimal `%`
form. No RM axis. This page extracted cleanly; no decoding was needed.

### `table1_classes.csv`
Table 1 (p10) plus the X-IO row and footnote references (p11). Same columns as DNA1:
`note_type`, `class`, `class_footnote`, `original_class_principal_balance` (for MACR Notes the
printed "Maximum Class Principal Balance or Notional Principal Amount"), `balance_footnote`,
`initial_class_coupon`, `coupon_footnote`, `class_coupon_formula`, `class_coupon_minimum_rate`,
`cusip_number` (printed as the footnote reference "(14)" — see Appendix F, p293),
`scheduled_maturity_date` (March 2046 for every Note), `expected_ratings_sp_morningstar_dbrs`,
`expected_wal_years`, `expected_principal_window_months`, `expected_initial_credit_enhancement`.

- 35 rows: 5 Original Notes (M-1, M-2A, M-2B, B-1A, B-1B; total $507,200,000 = the Table 1
  title amount), 28 MACR Notes (M-2 family 6, M-2A family 5, M-2B family 5, M-2RB/SB/TB/UB 4,
  B-1 family 6, B-1AR and B-1AI), the B-2H Reference Tranche (coupon only) and X-IO.
- Footnote markers are kept in the adjacent `*_footnote` column: `(4)` Exchangeable Notes, `(5)`
  MACR Notes, `(6)` Notional Principal Amount, `(7)` fixed-rate IO coupon, `(8)`/`(9)` the
  M-2RB/SB/TB/UB balance and coupon rules, `(10)` B-2H, `(11)`-`(13)` X-IO. Footnote text is on
  p11 and is not repeated here.
- Table 1 prints only B-2H under "Class of Reference Tranche" (DNA1 also printed B-1H). Reference
  Tranche balances are in Table 3 (p24), outside this transcription. X-IO has no balance or coupon
  in Table 1; those cells are left empty.
- Dollar signs are dropped from balances; everything else is verbatim, including the space that
  Table 1 prints before the slash in "BB+ (sf) /BB (high) (sf)" (B-1A, B-1AR, B-1AI; Table 2
  prints the same rating without the space).

### `appendix_g_absent.md`
This deal has no Class A-1 Notes and no Appendix G (or any other scheduled-reduction table). The
Table of Contents (p9) lists Appendices A-F only; Appendix F (CUSIP Numbers) starts on p293 and
runs to the end of the document. A full-text search for "Appendix G", "Class A-1", "Reduction
Schedule", "Scheduled Reduction" and "Payment Period" returns nothing. Nothing in DNA2
corresponds to DNA1's fixed 36-month Class A-1 Reduction Amount schedule.

### `modeling_assumptions.yaml`
Modeling Assumptions (a) through (s) verbatim from p138-139 (line breaks and the page-break folio
"116" collapsed; (k) spans p138-139), the CPR / CER / RM definitions from p139-140, the Table 1
footnote (1) basis, and, for each of the five table families, which assumptions apply (Credit
Events, Preliminary Principal Loss Amount, Modification Events, early redemption, SOFR, the
Delinquency Test, the printed grid) with page ranges and an `extraction_caveat` per family. The
Cumulative Note Write-down Amount Tables (p152-154, seven tables) and Yield Tables (p155-165, with
the assumed price for each of the 33 classes) are recorded as existing but are not transcribed.
Same top-level keys as the DNA1 file; the DNA1 `class_a1_reduction_amount` block is replaced by
`scheduled_reduction_schedule: {exists: false, ...}`.

### `register_rows.csv`
Forty-five rows (DNA2-T1 to DNA2-T45) in the exact column order of `docs/assumptions.csv`,
covering the structuring assumptions above, the Table 1 values, the Appendix C sums, the absent
Appendix G and the extraction caveats. For the Manager to merge; `docs/assumptions.csv` was not
edited.

## Pricing-speed check
Table 1 footnote (1) (p11) states the expected WALs assume redemption on the Early Redemption Date
in March 2031, the Pricing Speed of 10% CPR from the Closing Date, no Credit Events and no
Modification Events. For every one of the 33 Note classes, the Table 1 expected WAL equals the
WAL-table cell at **CER 0.00%, RM 0.00%, 10% CPR, "To Early Redemption Date"**, and also the "to
Early Redemption Date**" WAL row at 10% CPR in the Declining Balances tables:

| Class family | Table 1 | WAL table, 10% CPR, early redemption | same cell, to scheduled maturity |
|---|---|---|---|
| M-1 | 1.59 | 1.59 | 1.59 |
| M-2A (+ AR/AS/AT/AU/AI) | 3.90 | 3.90 | 3.90 |
| M-2B (+ BR/BS/BT/BU/BI/RB/SB/TB/UB) | 4.85 | 4.85 | 4.96 |
| M-2 (+ R/S/T/U/I) | 4.38 | 4.38 | 4.43 |
| B-1A (+ AR/AI) | 5.02 | 5.02 | 6.29 |
| B-1B | 5.02 | 5.02 | 8.03 |
| B-1 (+ R/S/T/U/I) | 5.02 | 5.02 | 7.16 |

The last column shows that the early-redemption basis is what Table 1 uses (five of the seven
families differ under the scheduled-maturity basis), so the engine's Table 1 tie-out must run with
the early redemption of Modeling Assumption (m) switched on. 5.02 years is the March 2031 Payment
Date measured from the March 17, 2026 Closing Date; every B-1 class is expected to be paid in full
by the early redemption (window 60-60).

## Extraction caveats — how the row-shifted pages were decoded
`pdftotext -layout` placed the cells of one printed row on neighbouring text lines in four tables
of the DNA2 extract (DNA1's extract did not have this problem). In each case the decode is
column-by-column: a column's values are read in printed order and the k-th value is paired with
the k-th row label, guarded by a count assertion and by independent cross-checks. Every check
passed; a failure would have aborted the run rather than produce a file.

1. **Appendix C (p264).** The Original Balance column is printed one line above its group number
   (the first value sits on the header line) and the two term columns one line below (the last
   pair sits on a trailing line); the Outstanding Principal Balance and Interest Rate columns are
   on the group lines. Reading each column in order gives 38 values per column. Checks: both sums
   above tie exactly; outstanding <= original in every group; rates ascend down the table;
   balance-weighted rate and terms match the pool statistics.
2. **Weighted Average Life Tables (p141-143).** In every table the 0% CPR "To Scheduled
   Maturity" column and the 35% CPR "To Early Redemption" column are printed on the eleven CER/RM
   label lines; the ten middle columns are printed as eleven separate ten-value lines, six of
   them sharing a label line (rows 1, 3, 5, 7, 9, 11 as printed) and five trailing the table.
   Taking the ten-value lines in printed order as rows 1-11 is the only pairing consistent with
   the data: it makes the 35% CPR "to Scheduled Maturity" cell equal the 35% CPR "to Early
   Redemption" cell wherever the class is retired before March 2031 (e.g. M-1 rows 2-7 and 9-11)
   and the 0% CPR cells equal across bases wherever the class is written off before then (e.g.
   M-2 rows 6-8); the alternative pairing puts early-redemption WALs above scheduled-maturity
   WALs, which is impossible because early redemption only pulls principal reductions earlier.
   Checks enforced on all 7 x 11 x 6 cells: WAL to Early Redemption <= WAL to Scheduled Maturity;
   row 1 equals the Declining Balances WAL rows; the 10% CPR early-redemption cell equals Table 1.
3. **Declining Balances Tables (p144-150).** The value block is printed several lines below the
   date labels (p144-147) or interleaved on alternate lines (p148-150), and columns of zeros are
   run together ("500000", "100   00000", "100      40000"). Values are paired with labels in
   order; run-together digit strings are split into exactly six whole-percent values (a
   whitespace-delimited token that is itself a value 0-100 is one cell; only strings that cannot
   be a single value are split, and the split must be unique). Checks: value lines = date labels
   on every page; first row is 100 in every column; every CPR column is non-increasing down the
   dates; the two WAL lines equal the WAL tables' CER 0.00% / RM 0.00% row.
4. **Table 1 (p10).** Class, balance, footnote markers, CUSIP reference, maturity, WAL, window
   and credit enhancement are on the class lines for the Original Notes; the coupon, formula /
   minimum-rate and rating columns are printed three lines up / two lines down / three lines up.
   For the MACR Notes the balance, coupon, formula and minimum rate are on the class lines while
   the CUSIP-maturity, rating and WAL-window-CE columns are printed as ordered sequences over the
   block (28 of each). Checks: every floating initial coupon equals 3.67223% + its margin; all 28
   MACR ratings equal Table 2 (p12) and the Exchangeable Notes equal their MACR families' ratings;
   the MACR exchange structure fixes M-2A = M-2B = SOFR Rate + 1.60% and B-1A = B-1B = SOFR
   Rate + 2.10%, leaving SOFR Rate + 1.20% for M-1. **Two Table 1 values rest on column order
   alone**, with no independent confirmation in the extract: the M-1 margin (+1.20%, coupon
   4.87223%) and the M-1 rating (BBB+ (sf)/BBB (sf)). Both are marked medium confidence in
   `register_rows.csv` (DNA2-T33, DNA2-T34).

Other conventions:
- Parsed programmatically with per-row regexes that require exactly the expected token count
  (12 or 2+10 values per WAL row, 6 per Declining Balances / Credit Event Sensitivity row, 6
  fields per Appendix C group); any row failing that aborts the run. Row counts per table were
  asserted (11 CER/RM rows per WAL table, 8 CER rows per Credit Event Sensitivity table, 38
  Appendix C groups, 35 Table 1 rows, 33 yield-table captions).
- No cell was left blank in any transcribed table; the only empty cells are the Table 1 cells the
  PPM itself does not print (B-2H balance / ratings / WAL, X-IO).
- The CER definition (p140) gives an annual rate applied monthly but does not state the
  annual-to-monthly conversion or whether CER and CPR compete for the same balance — the same
  modeling question flagged for DNA1 (register row DNA2-T27).
- CSVs are written with Python's `csv` module, UTF-8, LF line endings. The YAML uses UTF-8 and
  keeps the PPM's typographic characters where they appear.
- Nothing under `src/`, `tests/` or `data/ppm_tables/` was touched, and nothing was committed.
- If any doubt about a decoded value arises, the right fix is to re-extract only p10, p141-150
  and p264 from the PDF and diff against these CSVs (agent rule: re-extract the page, do not
  re-parse the document).

## Differences from the DNA1 tables
- **Classes.** DNA1: 4 Original Notes (A-1, M-1, M-2A, M-2B) and 20 MACR classes; Table 1 printed
  B-1H and B-2H. DNA2: 5 Original Notes (M-1, M-2A, M-2B, B-1A, B-1B) and 28 MACR classes (the
  M-2 families as before plus B-1, B-1R, B-1S, B-1T, B-1U, B-1I, B-1AR, B-1AI); Table 1 prints
  B-2H only. There is no Class A-1 and therefore no fixed reduction schedule (DNA1 Appendix G).
- **Table families present.** Same five families in both deals (WAL, Declining Balances, Credit
  Event Sensitivity, Cumulative Note Write-down Amount, Yield). DNA2 prints 7 WAL tables, 7
  Declining Balances tables, 7 Cumulative Write-down tables and 33 Yield tables (DNA1: 5, 5, 5,
  24).
- **Grid values.** CPR list (0, 5, 10, 15, 25, 35), the 11 (CER, RM) rows and the 8 CER rows of
  the Credit Event Sensitivity tables are identical to DNA1. Declining Balances dates are
  March 25 (DNA1: February 25) and run to 2043/2045/2046 depending on the table (DNA1: 2030 and
  thereafter at the longest); the label "and thereafter" appears only on the M-1 and M-2A tables.
- **Structuring assumptions.** SOFR 3.67223% (DNA1 3.65786%); Closing Date March 17, 2026
  (DNA1 February 17, 2026); first collection month February 2026 and first Payment Date
  April 2026 (DNA1 January / March 2026); Early Redemption Date March 2031 (DNA1 February 2031);
  Scheduled Maturity March 2046 (DNA1 February 2046). The wording of assumptions (a)-(s) is
  otherwise the same, except that (b) no longer mentions a Class B-1H Reference Tranche.
- **Pool.** 38 rep-line groups totalling $26,703,800,234.86 outstanding / $27,524,842,000 original
  (DNA1: 31 groups, $22,781,151,551.84 / $23,552,092,000).
- **MACR coupon ladder.** R/S/T/U = SOFR Rate + 0.85 / 1.00 / 1.15 / 1.30% and IO 0.75000% for
  the M-2 families (DNA1: + 0.55 / 0.70 / 0.85 / 1.00%); B-1 family R/S/T/U = + 1.10 / 1.30 /
  1.50 / 1.70% and IO 1.00000%.
- **Extract quality.** The DNA1 extract needed no decoding; the DNA2 extract needed the four
  decodes described above.
