# Tie-out — STACR 2026-DNA1 — 2026-09-07T16:04:09Z
Manifest: engine version 0.0.1, git commit 57510e4dee3abe0aaecb73e8e6c42a6fcf332b0a, Decimal precision 28, scenario grid CPR {0, 5, 10, 15, 25, 35} % x CER {0.00, 0.25, 0.50, 1.00, 1.50, 2.50, 3.00, 5.00} % x RM 0 x early redemption {off, on}; SHA-256: data/ppm_tables/appendix_c_rep_lines.csv f48cfaeaaa005258657a94cd34796584cded9f45138391bf20408207ef0e4361; data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv e1be1778423425b063744fb04ee68021775c3a98f8339f3ae3280e1150471eaf; data/ppm_tables/table1_classes.csv 6b25e9b72e91df44c7dcd7788aec98891ba072edf68dd154e40a81340f456465; data/ppm_tables/wal_tables.csv d50ed73d2436700e864f82c6058e41201b2f46d1b0adb8e3dea24d10ca77803a; data/ppm_tables/declining_balances.csv 860260b1cf02fbae75a89befabdcc509d38be8d788394b468bb3703dc82cfd06; data/ppm_tables/credit_event_sensitivity.csv 449094ea95cf641fac091628cd17d084e4c1e1ba21207197e7d105a70cef9596; data/deal_terms/stacr_2026_dna1.yaml 62fb79cda6b390da4dfc44d0bb617bbe72ef6ff073026893e07d96475a0fec52; docs/assumptions.csv d448b46a84ec153f192613d47ddf5475b09dd62e8d126248775381aff9ddc19c; conventions in force: A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13 A14 A15.

## 1. Summary
| family | cells | pass | fail | worst \|diff\| | tolerance | status |
|---|---|---|---|---|---|---|
| Table 1 windows | 4 | 4 | 0 | 0 | exact month | PASS |
| Declining Balances CER 0 | 366 | 366 | 0 | 0.49 | round-match (A13); ±0.25 pp reported | PASS |
| WAL CER 0 | 48 | 48 | 0 | 0.0048 | ±0.02 yr | PASS |
| WAL CER>0 | 336 | 324 | 12 | 0.0836 | ±0.02 yr | FAIL |
| Credit Event Sensitivity | 96 | 86 | 10 | 0.11 | round-match (A13); ±0.25 pp reported | FAIL |
Secondary window-band check (spec 03 section 2): 24 (Note, CPR) pairs, 0 failing.
Overall: FAIL.

## 2. Table 1 principal windows (10 % CPR, CER 0, early redemption on)
| Note | model first | model last | PPM window | pass |
|---|---|---|---|---|
| A-1 | 1 | 37 | 1-37 | pass |
| M-1 | 1 | 45 | 1-45 | pass |
| M-2A | 45 | 53 | 45-53 | pass |
| M-2B | 53 | 60 | 53-60 | pass |

## 3. Declining Balances (CER 0), one table per Note
### A-1
| CPR | row date | model % (2 dp) | PPM % | diff | round-match pass | \|diff\| ≤ 0.25 |
|---|---|---|---|---|---|---|
| 0 | February 25, 2027 | 55.00 | 55 | -0.00 | pass | yes |
| 5 | February 25, 2027 | 55.00 | 55 | -0.00 | pass | yes |
| 10 | February 25, 2027 | 55.00 | 55 | -0.00 | pass | yes |
| 15 | February 25, 2027 | 55.00 | 55 | -0.00 | pass | yes |
| 25 | February 25, 2027 | 55.00 | 55 | -0.00 | pass | yes |
| 35 | February 25, 2027 | 55.00 | 55 | -0.00 | pass | yes |
| 0 | February 25, 2028 | 37.00 | 37 | -0.00 | pass | yes |
| 5 | February 25, 2028 | 37.00 | 37 | -0.00 | pass | yes |
| 10 | February 25, 2028 | 37.00 | 37 | -0.00 | pass | yes |
| 15 | February 25, 2028 | 37.00 | 37 | -0.00 | pass | yes |
| 25 | February 25, 2028 | 37.00 | 37 | -0.00 | pass | yes |
| 35 | February 25, 2028 | 37.00 | 37 | -0.00 | pass | yes |
| 0 | February 25, 2029 | 19.00 | 19 | -0.00 | pass | yes |
| 5 | February 25, 2029 | 19.00 | 19 | -0.00 | pass | yes |
| 10 | February 25, 2029 | 19.00 | 19 | -0.00 | pass | yes |
| 15 | February 25, 2029 | 19.00 | 19 | -0.00 | pass | yes |
| 25 | February 25, 2029 | 19.00 | 19 | -0.00 | pass | yes |
| 35 | February 25, 2029 | 19.00 | 19 | -0.00 | pass | yes |
| 0 | February 25, 2030 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 5 | February 25, 2030 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2030 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2030 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2030 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2030 and thereafter | 0.00 | 0 | +0.00 | pass | yes |

| CPR | basis | model WAL (4 dp) | PPM | diff | ±0.02 |
|---|---|---|---|---|---|
| 0 | To Scheduled Maturity Date | 1.5971 | 1.60 | -0.0029 | pass |
| 5 | To Scheduled Maturity Date | 1.5868 | 1.59 | -0.0032 | pass |
| 10 | To Scheduled Maturity Date | 1.5868 | 1.59 | -0.0032 | pass |
| 15 | To Scheduled Maturity Date | 1.5868 | 1.59 | -0.0032 | pass |
| 25 | To Scheduled Maturity Date | 1.5868 | 1.59 | -0.0032 | pass |
| 35 | To Scheduled Maturity Date | 1.5868 | 1.59 | -0.0032 | pass |
| 0 | To Early Redemption Date | 1.5971 | 1.60 | -0.0029 | pass |
| 5 | To Early Redemption Date | 1.5868 | 1.59 | -0.0032 | pass |
| 10 | To Early Redemption Date | 1.5868 | 1.59 | -0.0032 | pass |
| 15 | To Early Redemption Date | 1.5868 | 1.59 | -0.0032 | pass |
| 25 | To Early Redemption Date | 1.5868 | 1.59 | -0.0032 | pass |
| 35 | To Early Redemption Date | 1.5868 | 1.59 | -0.0032 | pass |

| CPR | model last principal PD | must be after PD | must be on or before PD | pass |
|---|---|---|---|---|
| 0 | 39 | 36 | 48 | pass |
| 5 | 37 | 36 | 48 | pass |
| 10 | 37 | 36 | 48 | pass |
| 15 | 37 | 36 | 48 | pass |
| 25 | 37 | 36 | 48 | pass |
| 35 | 37 | 36 | 48 | pass |

### M-1
| CPR | row date | model % (2 dp) | PPM % | diff | round-match pass | \|diff\| ≤ 0.25 |
|---|---|---|---|---|---|---|
| 0 | February 25, 2027 | 96.59 | 97 | -0.41 | pass | no |
| 5 | February 25, 2027 | 81.83 | 82 | -0.17 | pass | yes |
| 10 | February 25, 2027 | 67.13 | 67 | +0.13 | pass | yes |
| 15 | February 25, 2027 | 52.51 | 53 | -0.49 | pass | no |
| 25 | February 25, 2027 | 23.47 | 23 | +0.47 | pass | no |
| 35 | February 25, 2027 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2028 | 93.21 | 93 | +0.21 | pass | yes |
| 5 | February 25, 2028 | 65.88 | 66 | -0.12 | pass | yes |
| 10 | February 25, 2028 | 40.06 | 40 | +0.06 | pass | yes |
| 15 | February 25, 2028 | 15.75 | 16 | -0.25 | pass | yes |
| 25 | February 25, 2028 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2028 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2029 | 89.59 | 90 | -0.41 | pass | no |
| 5 | February 25, 2029 | 50.67 | 51 | -0.33 | pass | no |
| 10 | February 25, 2029 | 15.79 | 16 | -0.21 | pass | yes |
| 15 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2030 | 85.73 | 86 | -0.27 | pass | no |
| 5 | February 25, 2030 | 36.18 | 36 | +0.18 | pass | yes |
| 10 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2031 | 81.59 | 82 | -0.41 | pass | no |
| 5 | February 25, 2031 | 22.36 | 22 | +0.36 | pass | no |
| 10 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2032 | 77.17 | 77 | +0.17 | pass | yes |
| 5 | February 25, 2032 | 9.18 | 9 | +0.18 | pass | yes |
| 10 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2033 | 72.43 | 72 | +0.43 | pass | no |
| 5 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2034 | 67.37 | 67 | +0.37 | pass | no |
| 5 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2035 | 61.95 | 62 | -0.05 | pass | yes |
| 5 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2036 | 56.16 | 56 | +0.16 | pass | yes |
| 5 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2037 | 49.96 | 50 | -0.04 | pass | yes |
| 5 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2038 | 43.32 | 43 | +0.32 | pass | no |
| 5 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2039 | 36.23 | 36 | +0.23 | pass | yes |
| 5 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2040 | 28.64 | 29 | -0.36 | pass | no |
| 5 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2041 | 20.51 | 21 | -0.49 | pass | no |
| 5 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2042 | 11.82 | 12 | -0.18 | pass | yes |
| 5 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2043 | 2.52 | 3 | -0.48 | pass | no |
| 5 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2044 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 5 | February 25, 2044 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2044 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2044 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2044 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2044 and thereafter | 0.00 | 0 | +0.00 | pass | yes |

| CPR | basis | model WAL (4 dp) | PPM | diff | ±0.02 |
|---|---|---|---|---|---|
| 0 | To Scheduled Maturity Date | 10.3066 | 10.31 | -0.0034 | pass |
| 5 | To Scheduled Maturity Date | 3.2020 | 3.20 | +0.0020 | pass |
| 10 | To Scheduled Maturity Date | 1.7511 | 1.75 | +0.0011 | pass |
| 15 | To Scheduled Maturity Date | 1.1762 | 1.18 | -0.0038 | pass |
| 25 | To Scheduled Maturity Date | 0.6809 | 0.68 | +0.0009 | pass |
| 35 | To Scheduled Maturity Date | 0.4595 | 0.46 | -0.0005 | pass |
| 0 | To Early Redemption Date | 4.5888 | 4.59 | -0.0012 | pass |
| 5 | To Early Redemption Date | 3.0023 | 3.00 | +0.0023 | pass |
| 10 | To Early Redemption Date | 1.7511 | 1.75 | +0.0011 | pass |
| 15 | To Early Redemption Date | 1.1762 | 1.18 | -0.0038 | pass |
| 25 | To Early Redemption Date | 0.6809 | 0.68 | +0.0009 | pass |
| 35 | To Early Redemption Date | 0.4595 | 0.46 | -0.0005 | pass |

| CPR | model last principal PD | must be after PD | must be on or before PD | pass |
|---|---|---|---|---|
| 0 | 208 | 204 | 216 | pass |
| 5 | 81 | 72 | 84 | pass |
| 10 | 45 | 36 | 48 | pass |
| 15 | 30 | 24 | 36 | pass |
| 25 | 17 | 12 | 24 | pass |
| 35 | 12 | 0 | 12 | pass |

### M-2A
| CPR | row date | model % (2 dp) | PPM % | diff | round-match pass | \|diff\| ≤ 0.25 |
|---|---|---|---|---|---|---|
| 0 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 25 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 35 | February 25, 2027 | 61.81 | 62 | -0.19 | pass | yes |
| 0 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 25 | February 25, 2028 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2028 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2029 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2029 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2029 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2030 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2030 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2030 | 56.67 | 57 | -0.33 | pass | no |
| 15 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2031 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2031 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2032 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2032 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2033 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2033 | 75.27 | 75 | +0.27 | pass | no |
| 10 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2034 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2035 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2036 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2037 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2038 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2039 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2040 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2041 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2042 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2043 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2044 | 45.85 | 46 | -0.15 | pass | yes |
| 5 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2045 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 5 | February 25, 2045 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2045 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2045 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2045 and thereafter | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2045 and thereafter | 0.00 | 0 | +0.00 | pass | yes |

| CPR | basis | model WAL (4 dp) | PPM | diff | ±0.02 |
|---|---|---|---|---|---|
| 0 | To Scheduled Maturity Date | 18.0035 | 18.00 | +0.0035 | pass |
| 5 | To Scheduled Maturity Date | 7.3507 | 7.35 | +0.0007 | pass |
| 10 | To Scheduled Maturity Date | 4.1105 | 4.11 | +0.0005 | pass |
| 15 | To Scheduled Maturity Date | 2.7778 | 2.78 | -0.0022 | pass |
| 25 | To Scheduled Maturity Date | 1.6158 | 1.62 | -0.0042 | pass |
| 35 | To Scheduled Maturity Date | 1.0876 | 1.09 | -0.0024 | pass |
| 0 | To Early Redemption Date | 5.0222 | 5.02 | +0.0022 | pass |
| 5 | To Early Redemption Date | 5.0222 | 5.02 | +0.0022 | pass |
| 10 | To Early Redemption Date | 4.1105 | 4.11 | +0.0005 | pass |
| 15 | To Early Redemption Date | 2.7778 | 2.78 | -0.0022 | pass |
| 25 | To Early Redemption Date | 1.6158 | 1.62 | -0.0042 | pass |
| 35 | To Early Redemption Date | 1.0876 | 1.09 | -0.0024 | pass |

| CPR | model last principal PD | must be after PD | must be on or before PD | pass |
|---|---|---|---|---|
| 0 | 224 | 216 | 228 | pass |
| 5 | 95 | 84 | 96 | pass |
| 10 | 53 | 48 | 60 | pass |
| 15 | 36 | 24 | 36 | pass |
| 25 | 21 | 12 | 24 | pass |
| 35 | 14 | 12 | 24 | pass |

### M-2B
| CPR | row date | model % (2 dp) | PPM % | diff | round-match pass | \|diff\| ≤ 0.25 |
|---|---|---|---|---|---|---|
| 0 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 25 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 35 | February 25, 2027 | 100.00 | 100 | +0.00 | pass | yes |
| 0 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2028 | 100.00 | 100 | +0.00 | pass | yes |
| 25 | February 25, 2028 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2028 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2029 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2029 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2029 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2029 | 88.73 | 89 | -0.27 | pass | no |
| 25 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2029 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2030 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2030 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2030 | 100.00 | 100 | +0.00 | pass | yes |
| 15 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2030 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2031 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2031 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2031 | 14.79 | 15 | -0.21 | pass | yes |
| 15 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2031 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2032 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2032 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2032 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2033 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2033 | 100.00 | 100 | +0.00 | pass | yes |
| 10 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2033 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2034 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2034 | 87.85 | 88 | -0.15 | pass | yes |
| 10 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2034 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2035 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2035 | 4.41 | 4 | +0.41 | pass | no |
| 10 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2035 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2036 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2036 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2037 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2037 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2038 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2038 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2039 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2039 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2040 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2040 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2041 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2041 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2042 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2042 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2043 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2043 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2044 | 100.00 | 100 | +0.00 | pass | yes |
| 5 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2044 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2045 | 68.26 | 68 | +0.26 | pass | no |
| 5 | February 25, 2045 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2045 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2045 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2045 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2045 | 0.00 | 0 | +0.00 | pass | yes |
| 0 | February 25, 2046 | 0.00 | 0 | +0.00 | pass | yes |
| 5 | February 25, 2046 | 0.00 | 0 | +0.00 | pass | yes |
| 10 | February 25, 2046 | 0.00 | 0 | +0.00 | pass | yes |
| 15 | February 25, 2046 | 0.00 | 0 | +0.00 | pass | yes |
| 25 | February 25, 2046 | 0.00 | 0 | +0.00 | pass | yes |
| 35 | February 25, 2046 | 0.00 | 0 | +0.00 | pass | yes |

| CPR | basis | model WAL (4 dp) | PPM | diff | ±0.02 |
|---|---|---|---|---|---|
| 0 | To Scheduled Maturity Date | 19.2852 | 19.29 | -0.0048 | pass |
| 5 | To Scheduled Maturity Date | 8.5146 | 8.51 | +0.0046 | pass |
| 10 | To Scheduled Maturity Date | 4.8076 | 4.81 | -0.0024 | pass |
| 15 | To Scheduled Maturity Date | 3.2554 | 3.26 | -0.0046 | pass |
| 25 | To Scheduled Maturity Date | 1.8946 | 1.89 | +0.0046 | pass |
| 35 | To Scheduled Maturity Date | 1.2756 | 1.28 | -0.0044 | pass |
| 0 | To Early Redemption Date | 5.0222 | 5.02 | +0.0022 | pass |
| 5 | To Early Redemption Date | 5.0222 | 5.02 | +0.0022 | pass |
| 10 | To Early Redemption Date | 4.7922 | 4.79 | +0.0022 | pass |
| 15 | To Early Redemption Date | 3.2554 | 3.26 | -0.0046 | pass |
| 25 | To Early Redemption Date | 1.8946 | 1.89 | +0.0046 | pass |
| 35 | To Early Redemption Date | 1.2756 | 1.28 | -0.0044 | pass |

| CPR | model last principal PD | must be after PD | must be on or before PD | pass |
|---|---|---|---|---|
| 0 | 238 | 228 | 240 | pass |
| 5 | 109 | 108 | 120 | pass |
| 10 | 62 | 60 | 72 | pass |
| 15 | 42 | 36 | 48 | pass |
| 25 | 24 | 12 | 24 | pass |
| 35 | 16 | 12 | 24 | pass |

## 4. WAL, CER 0, RM 0
| Note | basis | CPR | model WAL (4 dp) | PPM | diff | ±0.02 | ±0.10 |
|---|---|---|---|---|---|---|---|
| A-1 | To Scheduled Maturity Date | 0 | 1.5971 | 1.60 | -0.0029 | pass | pass |
| A-1 | To Scheduled Maturity Date | 5 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Scheduled Maturity Date | 10 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Scheduled Maturity Date | 15 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Scheduled Maturity Date | 25 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Scheduled Maturity Date | 35 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Early Redemption Date | 0 | 1.5971 | 1.60 | -0.0029 | pass | pass |
| A-1 | To Early Redemption Date | 5 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Early Redemption Date | 10 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Early Redemption Date | 15 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Early Redemption Date | 25 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| A-1 | To Early Redemption Date | 35 | 1.5868 | 1.59 | -0.0032 | pass | pass |
| M-1 | To Scheduled Maturity Date | 0 | 10.3066 | 10.31 | -0.0034 | pass | pass |
| M-1 | To Scheduled Maturity Date | 5 | 3.2020 | 3.20 | +0.0020 | pass | pass |
| M-1 | To Scheduled Maturity Date | 10 | 1.7511 | 1.75 | +0.0011 | pass | pass |
| M-1 | To Scheduled Maturity Date | 15 | 1.1762 | 1.18 | -0.0038 | pass | pass |
| M-1 | To Scheduled Maturity Date | 25 | 0.6809 | 0.68 | +0.0009 | pass | pass |
| M-1 | To Scheduled Maturity Date | 35 | 0.4595 | 0.46 | -0.0005 | pass | pass |
| M-1 | To Early Redemption Date | 0 | 4.5888 | 4.59 | -0.0012 | pass | pass |
| M-1 | To Early Redemption Date | 5 | 3.0023 | 3.00 | +0.0023 | pass | pass |
| M-1 | To Early Redemption Date | 10 | 1.7511 | 1.75 | +0.0011 | pass | pass |
| M-1 | To Early Redemption Date | 15 | 1.1762 | 1.18 | -0.0038 | pass | pass |
| M-1 | To Early Redemption Date | 25 | 0.6809 | 0.68 | +0.0009 | pass | pass |
| M-1 | To Early Redemption Date | 35 | 0.4595 | 0.46 | -0.0005 | pass | pass |
| M-2A | To Scheduled Maturity Date | 0 | 18.0035 | 18.00 | +0.0035 | pass | pass |
| M-2A | To Scheduled Maturity Date | 5 | 7.3507 | 7.35 | +0.0007 | pass | pass |
| M-2A | To Scheduled Maturity Date | 10 | 4.1105 | 4.11 | +0.0005 | pass | pass |
| M-2A | To Scheduled Maturity Date | 15 | 2.7778 | 2.78 | -0.0022 | pass | pass |
| M-2A | To Scheduled Maturity Date | 25 | 1.6158 | 1.62 | -0.0042 | pass | pass |
| M-2A | To Scheduled Maturity Date | 35 | 1.0876 | 1.09 | -0.0024 | pass | pass |
| M-2A | To Early Redemption Date | 0 | 5.0222 | 5.02 | +0.0022 | pass | pass |
| M-2A | To Early Redemption Date | 5 | 5.0222 | 5.02 | +0.0022 | pass | pass |
| M-2A | To Early Redemption Date | 10 | 4.1105 | 4.11 | +0.0005 | pass | pass |
| M-2A | To Early Redemption Date | 15 | 2.7778 | 2.78 | -0.0022 | pass | pass |
| M-2A | To Early Redemption Date | 25 | 1.6158 | 1.62 | -0.0042 | pass | pass |
| M-2A | To Early Redemption Date | 35 | 1.0876 | 1.09 | -0.0024 | pass | pass |
| M-2B | To Scheduled Maturity Date | 0 | 19.2852 | 19.29 | -0.0048 | pass | pass |
| M-2B | To Scheduled Maturity Date | 5 | 8.5146 | 8.51 | +0.0046 | pass | pass |
| M-2B | To Scheduled Maturity Date | 10 | 4.8076 | 4.81 | -0.0024 | pass | pass |
| M-2B | To Scheduled Maturity Date | 15 | 3.2554 | 3.26 | -0.0046 | pass | pass |
| M-2B | To Scheduled Maturity Date | 25 | 1.8946 | 1.89 | +0.0046 | pass | pass |
| M-2B | To Scheduled Maturity Date | 35 | 1.2756 | 1.28 | -0.0044 | pass | pass |
| M-2B | To Early Redemption Date | 0 | 5.0222 | 5.02 | +0.0022 | pass | pass |
| M-2B | To Early Redemption Date | 5 | 5.0222 | 5.02 | +0.0022 | pass | pass |
| M-2B | To Early Redemption Date | 10 | 4.7922 | 4.79 | +0.0022 | pass | pass |
| M-2B | To Early Redemption Date | 15 | 3.2554 | 3.26 | -0.0046 | pass | pass |
| M-2B | To Early Redemption Date | 25 | 1.8946 | 1.89 | +0.0046 | pass | pass |
| M-2B | To Early Redemption Date | 35 | 1.2756 | 1.28 | -0.0044 | pass | pass |

## 5. WAL, CER > 0, RM 0
| Note | basis | CER | CPR | model | PPM | diff | ±0.02 |
|---|---|---|---|---|---|---|---|
| A-1 | To Scheduled Maturity Date | 0.25% | 0 | 1.5964 | 1.60 | -0.0036 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.25% | 0 | 1.5964 | 1.60 | -0.0036 | pass |
| A-1 | To Early Redemption Date | 0.25% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.25% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.25% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.25% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.25% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.50% | 0 | 1.5966 | 1.60 | -0.0034 | pass |
| A-1 | To Scheduled Maturity Date | 0.50% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.50% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.50% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.50% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.50% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.50% | 0 | 1.5966 | 1.60 | -0.0034 | pass |
| A-1 | To Early Redemption Date | 0.50% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.50% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.50% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.50% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.50% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.00% | 0 | 1.5970 | 1.60 | -0.0030 | pass |
| A-1 | To Scheduled Maturity Date | 1.00% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.00% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.00% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.00% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.00% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.00% | 0 | 1.5970 | 1.60 | -0.0030 | pass |
| A-1 | To Early Redemption Date | 1.00% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.00% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.00% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.00% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.00% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 0 | 3.8491 | 3.84 | +0.0091 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 5 | 5.1870 | 5.18 | +0.0070 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.50% | 0 | 2.1135 | 2.11 | +0.0035 | pass |
| A-1 | To Early Redemption Date | 1.50% | 5 | 2.0122 | 2.01 | +0.0022 | pass |
| A-1 | To Early Redemption Date | 1.50% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.50% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.50% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 1.50% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 0 | 3.5251 | 3.52 | +0.0051 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 5 | 4.2520 | 4.25 | +0.0020 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 10 | 6.7178 | 6.71 | +0.0078 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 15 | 6.7332 | 6.73 | +0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 25 | 4.2910 | 4.28 | +0.0110 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 35 | 2.8068 | 2.80 | +0.0068 | pass |
| A-1 | To Early Redemption Date | 2.50% | 0 | 2.6822 | 2.68 | +0.0022 | pass |
| A-1 | To Early Redemption Date | 2.50% | 5 | 2.6310 | 2.63 | +0.0010 | pass |
| A-1 | To Early Redemption Date | 2.50% | 10 | 2.5810 | 2.58 | +0.0010 | pass |
| A-1 | To Early Redemption Date | 2.50% | 15 | 2.5322 | 2.53 | +0.0022 | pass |
| A-1 | To Early Redemption Date | 2.50% | 25 | 2.3497 | 2.35 | -0.0003 | pass |
| A-1 | To Early Redemption Date | 2.50% | 35 | 2.0368 | 2.04 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 0 | 3.1795 | 3.18 | -0.0005 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 5 | 3.7700 | 3.77 | -0.0000 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 10 | 4.9139 | 4.91 | +0.0039 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 15 | 7.1650 | 7.15 | +0.0150 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 25 | 4.7078 | 4.70 | +0.0078 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 35 | 3.2787 | 3.27 | +0.0087 | pass |
| A-1 | To Early Redemption Date | 3.00% | 0 | 2.8435 | 2.84 | +0.0035 | pass |
| A-1 | To Early Redemption Date | 3.00% | 5 | 2.8435 | 2.84 | +0.0035 | pass |
| A-1 | To Early Redemption Date | 3.00% | 10 | 2.7885 | 2.79 | -0.0015 | pass |
| A-1 | To Early Redemption Date | 3.00% | 15 | 2.7347 | 2.73 | +0.0047 | pass |
| A-1 | To Early Redemption Date | 3.00% | 25 | 2.6310 | 2.63 | +0.0010 | pass |
| A-1 | To Early Redemption Date | 3.00% | 35 | 2.4181 | 2.42 | -0.0019 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 0 | 2.5216 | 2.52 | +0.0016 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 5 | 2.7824 | 2.78 | +0.0024 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 10 | 3.1678 | 3.17 | -0.0022 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 15 | 3.6156 | 3.62 | -0.0044 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 25 | 5.4821 | 5.46 | +0.0221 | FAIL |
| A-1 | To Scheduled Maturity Date | 5.00% | 35 | 3.8567 | 3.84 | +0.0167 | pass |
| A-1 | To Early Redemption Date | 5.00% | 0 | 2.5216 | 2.52 | +0.0016 | pass |
| A-1 | To Early Redemption Date | 5.00% | 5 | 2.7824 | 2.78 | +0.0024 | pass |
| A-1 | To Early Redemption Date | 5.00% | 10 | 3.1660 | 3.17 | -0.0040 | pass |
| A-1 | To Early Redemption Date | 5.00% | 15 | 3.3622 | 3.36 | +0.0022 | pass |
| A-1 | To Early Redemption Date | 5.00% | 25 | 3.4753 | 3.48 | -0.0047 | pass |
| A-1 | To Early Redemption Date | 5.00% | 35 | 2.9866 | 2.98 | +0.0066 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 0 | 17.4132 | 17.42 | -0.0068 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 5 | 4.4032 | 4.40 | +0.0032 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 10 | 2.1032 | 2.10 | +0.0032 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 15 | 1.3477 | 1.35 | -0.0023 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 25 | 0.7605 | 0.76 | +0.0005 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 35 | 0.5298 | 0.53 | -0.0002 | pass |
| M-1 | To Early Redemption Date | 0.25% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 0.25% | 5 | 3.5064 | 3.51 | -0.0036 | pass |
| M-1 | To Early Redemption Date | 0.25% | 10 | 2.1032 | 2.10 | +0.0032 | pass |
| M-1 | To Early Redemption Date | 0.25% | 15 | 1.3477 | 1.35 | -0.0023 | pass |
| M-1 | To Early Redemption Date | 0.25% | 25 | 0.7605 | 0.76 | +0.0005 | pass |
| M-1 | To Early Redemption Date | 0.25% | 35 | 0.5298 | 0.53 | -0.0002 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 0 | 19.9209 | 19.92 | +0.0009 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 5 | 6.8452 | 6.85 | -0.0048 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 10 | 2.7142 | 2.71 | +0.0042 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 15 | 1.6522 | 1.65 | +0.0022 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 25 | 0.8825 | 0.88 | +0.0025 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 35 | 0.5602 | 0.56 | +0.0002 | pass |
| M-1 | To Early Redemption Date | 0.50% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 0.50% | 5 | 4.0607 | 4.06 | +0.0007 | pass |
| M-1 | To Early Redemption Date | 0.50% | 10 | 2.6829 | 2.68 | +0.0029 | pass |
| M-1 | To Early Redemption Date | 0.50% | 15 | 1.6522 | 1.65 | +0.0022 | pass |
| M-1 | To Early Redemption Date | 0.50% | 25 | 0.8825 | 0.88 | +0.0025 | pass |
| M-1 | To Early Redemption Date | 0.50% | 35 | 0.5602 | 0.56 | +0.0002 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 0 | 13.7275 | 13.70 | +0.0275 | FAIL |
| M-1 | To Scheduled Maturity Date | 1.00% | 5 | 18.8696 | 18.86 | +0.0096 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 10 | 12.6463 | 12.64 | +0.0063 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 15 | 8.8077 | 8.82 | -0.0123 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 25 | 4.5875 | 4.58 | +0.0075 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 35 | 2.6445 | 2.64 | +0.0045 | pass |
| M-1 | To Early Redemption Date | 1.00% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 1.00% | 5 | 4.8819 | 4.88 | +0.0019 | pass |
| M-1 | To Early Redemption Date | 1.00% | 10 | 4.7613 | 4.76 | +0.0013 | pass |
| M-1 | To Early Redemption Date | 1.00% | 15 | 4.6351 | 4.63 | +0.0051 | pass |
| M-1 | To Early Redemption Date | 1.00% | 25 | 3.7506 | 3.75 | +0.0006 | pass |
| M-1 | To Early Redemption Date | 1.00% | 35 | 2.6445 | 2.64 | +0.0045 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 0 | 8.6061 | 8.59 | +0.0161 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 5 | 11.8025 | 11.78 | +0.0225 | FAIL |
| M-1 | To Scheduled Maturity Date | 1.50% | 10 | 14.8726 | 14.86 | +0.0126 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 15 | 8.7171 | 8.71 | +0.0071 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 25 | 5.1289 | 5.12 | +0.0089 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 35 | 3.2592 | 3.25 | +0.0092 | pass |
| M-1 | To Early Redemption Date | 1.50% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 1.50% | 5 | 4.8819 | 4.88 | +0.0019 | pass |
| M-1 | To Early Redemption Date | 1.50% | 10 | 4.7615 | 4.76 | +0.0015 | pass |
| M-1 | To Early Redemption Date | 1.50% | 15 | 4.6353 | 4.63 | +0.0053 | pass |
| M-1 | To Early Redemption Date | 1.50% | 25 | 4.2485 | 4.25 | -0.0015 | pass |
| M-1 | To Early Redemption Date | 1.50% | 35 | 3.1930 | 3.19 | +0.0030 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 0 | 5.0028 | 5.00 | +0.0028 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 5 | 5.8768 | 5.87 | +0.0068 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 10 | 7.5903 | 7.58 | +0.0103 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 15 | 7.8049 | 7.79 | +0.0149 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 25 | 4.1959 | 4.19 | +0.0059 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 35 | 3.1062 | 3.10 | +0.0062 | pass |
| M-1 | To Early Redemption Date | 2.50% | 0 | 4.7061 | 4.70 | +0.0061 | pass |
| M-1 | To Early Redemption Date | 2.50% | 5 | 4.9223 | 4.92 | +0.0023 | pass |
| M-1 | To Early Redemption Date | 2.50% | 10 | 5.0210 | 5.02 | +0.0010 | pass |
| M-1 | To Early Redemption Date | 2.50% | 15 | 5.0188 | 5.02 | -0.0012 | pass |
| M-1 | To Early Redemption Date | 2.50% | 25 | 4.1146 | 4.11 | +0.0046 | pass |
| M-1 | To Early Redemption Date | 2.50% | 35 | 3.1062 | 3.10 | +0.0062 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 0 | 4.1276 | 4.12 | +0.0076 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 5 | 4.6899 | 4.69 | -0.0001 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 10 | 5.6192 | 5.61 | +0.0092 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 15 | 7.1685 | 7.16 | +0.0085 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 25 | 3.8929 | 3.88 | +0.0129 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 35 | 2.7954 | 2.79 | +0.0054 | pass |
| M-1 | To Early Redemption Date | 3.00% | 0 | 4.1243 | 4.12 | +0.0043 | pass |
| M-1 | To Early Redemption Date | 3.00% | 5 | 4.5045 | 4.50 | +0.0045 | pass |
| M-1 | To Early Redemption Date | 3.00% | 10 | 4.8018 | 4.80 | +0.0018 | pass |
| M-1 | To Early Redemption Date | 3.00% | 15 | 4.9885 | 4.99 | -0.0015 | pass |
| M-1 | To Early Redemption Date | 3.00% | 25 | 3.8694 | 3.86 | +0.0094 | pass |
| M-1 | To Early Redemption Date | 3.00% | 35 | 2.7954 | 2.79 | +0.0054 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 0 | 2.4138 | 2.41 | +0.0038 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 5 | 2.5878 | 2.59 | -0.0022 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 10 | 2.8159 | 2.81 | +0.0059 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 15 | 3.1349 | 3.13 | +0.0049 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 25 | 3.7987 | 3.79 | +0.0087 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 35 | 2.4036 | 2.39 | +0.0136 | pass |
| M-1 | To Early Redemption Date | 5.00% | 0 | 2.4138 | 2.41 | +0.0038 | pass |
| M-1 | To Early Redemption Date | 5.00% | 5 | 2.5878 | 2.59 | -0.0022 | pass |
| M-1 | To Early Redemption Date | 5.00% | 10 | 2.8159 | 2.81 | +0.0059 | pass |
| M-1 | To Early Redemption Date | 5.00% | 15 | 3.1349 | 3.13 | +0.0049 | pass |
| M-1 | To Early Redemption Date | 5.00% | 25 | 3.7898 | 3.78 | +0.0098 | pass |
| M-1 | To Early Redemption Date | 5.00% | 35 | 2.4036 | 2.39 | +0.0136 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 0 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 5 | 10.2672 | 10.28 | -0.0128 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 10 | 5.0019 | 5.00 | +0.0019 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 15 | 3.1989 | 3.20 | -0.0011 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 25 | 1.7925 | 1.79 | +0.0025 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 35 | 1.1837 | 1.18 | +0.0037 | pass |
| M-2A | To Early Redemption Date | 0.25% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.25% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.25% | 10 | 4.9043 | 4.90 | +0.0043 | pass |
| M-2A | To Early Redemption Date | 0.25% | 15 | 3.1989 | 3.20 | -0.0011 | pass |
| M-2A | To Early Redemption Date | 0.25% | 25 | 1.7925 | 1.79 | +0.0025 | pass |
| M-2A | To Early Redemption Date | 0.25% | 35 | 1.1837 | 1.18 | +0.0037 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 0 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 5 | 15.9707 | 16.00 | -0.0293 | FAIL |
| M-2A | To Scheduled Maturity Date | 0.50% | 10 | 6.2921 | 6.29 | +0.0021 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 15 | 3.6801 | 3.68 | +0.0001 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 25 | 2.0174 | 2.02 | -0.0026 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 35 | 1.3646 | 1.36 | +0.0046 | pass |
| M-2A | To Early Redemption Date | 0.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.50% | 15 | 3.6801 | 3.68 | +0.0001 | pass |
| M-2A | To Early Redemption Date | 0.50% | 25 | 2.0174 | 2.02 | -0.0026 | pass |
| M-2A | To Early Redemption Date | 0.50% | 35 | 1.3646 | 1.36 | +0.0046 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 0 | 9.6546 | 9.64 | +0.0146 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 5 | 14.1612 | 14.12 | +0.0412 | FAIL |
| M-2A | To Scheduled Maturity Date | 1.00% | 10 | 19.8507 | 19.85 | +0.0007 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 15 | 13.3101 | 13.39 | -0.0799 | FAIL |
| M-2A | To Scheduled Maturity Date | 1.00% | 25 | 7.7591 | 7.76 | -0.0009 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 35 | 4.9463 | 4.94 | +0.0063 | pass |
| M-2A | To Early Redemption Date | 1.00% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 35 | 4.8784 | 4.88 | -0.0016 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 0 | 6.2255 | 6.22 | +0.0055 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 5 | 7.6151 | 7.60 | +0.0151 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 10 | 10.8803 | 10.86 | +0.0203 | FAIL |
| M-2A | To Scheduled Maturity Date | 1.50% | 15 | 15.2503 | 15.24 | +0.0103 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 25 | 9.5610 | 9.55 | +0.0110 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 35 | 6.6294 | 6.62 | +0.0094 | pass |
| M-2A | To Early Redemption Date | 1.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 35 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 0 | 3.6401 | 3.64 | +0.0001 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 5 | 4.0441 | 4.04 | +0.0041 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 10 | 4.6470 | 4.64 | +0.0070 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 15 | 5.6817 | 5.68 | +0.0017 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 25 | 6.2216 | 6.21 | +0.0116 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 35 | 4.7761 | 4.77 | +0.0061 | pass |
| M-2A | To Early Redemption Date | 2.50% | 0 | 3.6401 | 3.64 | +0.0001 | pass |
| M-2A | To Early Redemption Date | 2.50% | 5 | 4.0441 | 4.04 | +0.0041 | pass |
| M-2A | To Early Redemption Date | 2.50% | 10 | 4.6470 | 4.64 | +0.0070 | pass |
| M-2A | To Early Redemption Date | 2.50% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 2.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 2.50% | 35 | 4.7303 | 4.72 | +0.0103 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 0 | 3.0069 | 3.00 | +0.0069 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 5 | 3.2770 | 3.27 | +0.0070 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 10 | 3.6459 | 3.64 | +0.0059 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 15 | 4.1991 | 4.20 | -0.0009 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 25 | 6.1939 | 6.17 | +0.0239 | FAIL |
| M-2A | To Scheduled Maturity Date | 3.00% | 35 | 4.1253 | 4.12 | +0.0053 | pass |
| M-2A | To Early Redemption Date | 3.00% | 0 | 3.0069 | 3.00 | +0.0069 | pass |
| M-2A | To Early Redemption Date | 3.00% | 5 | 3.2770 | 3.27 | +0.0070 | pass |
| M-2A | To Early Redemption Date | 3.00% | 10 | 3.6459 | 3.64 | +0.0059 | pass |
| M-2A | To Early Redemption Date | 3.00% | 15 | 4.1991 | 4.20 | -0.0009 | pass |
| M-2A | To Early Redemption Date | 3.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 3.00% | 35 | 4.1253 | 4.12 | +0.0053 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 0 | 1.7633 | 1.76 | +0.0033 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 5 | 1.8503 | 1.85 | +0.0003 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 10 | 1.9530 | 1.95 | +0.0030 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 15 | 2.0890 | 2.09 | -0.0010 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 25 | 2.4868 | 2.49 | -0.0032 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 35 | 3.4485 | 3.46 | -0.0115 | pass |
| M-2A | To Early Redemption Date | 5.00% | 0 | 1.7633 | 1.76 | +0.0033 | pass |
| M-2A | To Early Redemption Date | 5.00% | 5 | 1.8503 | 1.85 | +0.0003 | pass |
| M-2A | To Early Redemption Date | 5.00% | 10 | 1.9530 | 1.95 | +0.0030 | pass |
| M-2A | To Early Redemption Date | 5.00% | 15 | 2.0890 | 2.09 | -0.0010 | pass |
| M-2A | To Early Redemption Date | 5.00% | 25 | 2.4868 | 2.49 | -0.0032 | pass |
| M-2A | To Early Redemption Date | 5.00% | 35 | 3.4485 | 3.46 | -0.0115 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 0 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 5 | 11.9859 | 11.99 | -0.0041 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 10 | 5.8952 | 5.89 | +0.0052 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 15 | 3.7467 | 3.75 | -0.0033 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 25 | 2.1047 | 2.10 | +0.0047 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 35 | 1.3764 | 1.38 | -0.0036 | pass |
| M-2B | To Early Redemption Date | 0.25% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.25% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.25% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.25% | 15 | 3.7467 | 3.75 | -0.0033 | pass |
| M-2B | To Early Redemption Date | 0.25% | 25 | 2.1047 | 2.10 | +0.0047 | pass |
| M-2B | To Early Redemption Date | 0.25% | 35 | 1.3764 | 1.38 | -0.0036 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 0 | 19.8514 | 19.83 | +0.0214 | FAIL |
| M-2B | To Scheduled Maturity Date | 0.50% | 5 | 18.6817 | 18.71 | -0.0283 | FAIL |
| M-2B | To Scheduled Maturity Date | 0.50% | 10 | 7.5367 | 7.54 | -0.0033 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 15 | 4.3616 | 4.36 | +0.0016 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 25 | 2.3282 | 2.33 | -0.0018 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 35 | 1.5718 | 1.57 | +0.0018 | pass |
| M-2B | To Early Redemption Date | 0.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.50% | 15 | 4.3616 | 4.36 | +0.0016 | pass |
| M-2B | To Early Redemption Date | 0.50% | 25 | 2.3282 | 2.33 | -0.0018 | pass |
| M-2B | To Early Redemption Date | 0.50% | 35 | 1.5718 | 1.57 | +0.0018 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 0 | 8.7646 | 8.75 | +0.0146 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 5 | 12.1247 | 12.10 | +0.0247 | FAIL |
| M-2B | To Scheduled Maturity Date | 1.00% | 10 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 15 | 14.3764 | 14.46 | -0.0836 | FAIL |
| M-2B | To Scheduled Maturity Date | 1.00% | 25 | 8.1867 | 8.18 | +0.0067 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 35 | 5.3335 | 5.33 | +0.0035 | pass |
| M-2B | To Early Redemption Date | 1.00% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 35 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 0 | 5.6751 | 5.67 | +0.0051 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 5 | 6.7841 | 6.77 | +0.0141 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 10 | 9.0559 | 9.04 | +0.0159 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 15 | 19.1405 | 19.13 | +0.0105 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 25 | 11.3168 | 11.31 | +0.0068 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 35 | 8.0808 | 8.08 | +0.0008 | pass |
| M-2B | To Early Redemption Date | 1.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 35 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 0 | 3.3207 | 3.32 | +0.0007 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 5 | 3.6554 | 3.65 | +0.0054 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 10 | 4.1276 | 4.12 | +0.0076 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 15 | 4.8818 | 4.88 | +0.0018 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 25 | 7.0725 | 7.06 | +0.0125 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 35 | 5.5413 | 5.53 | +0.0113 | pass |
| M-2B | To Early Redemption Date | 2.50% | 0 | 3.3207 | 3.32 | +0.0007 | pass |
| M-2B | To Early Redemption Date | 2.50% | 5 | 3.6554 | 3.65 | +0.0054 | pass |
| M-2B | To Early Redemption Date | 2.50% | 10 | 4.1276 | 4.12 | +0.0076 | pass |
| M-2B | To Early Redemption Date | 2.50% | 15 | 4.8458 | 4.84 | +0.0058 | pass |
| M-2B | To Early Redemption Date | 2.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 2.50% | 35 | 4.8556 | 4.86 | -0.0044 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 0 | 2.7472 | 2.74 | +0.0072 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 5 | 2.9702 | 2.97 | +0.0002 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 10 | 3.2633 | 3.26 | +0.0033 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 15 | 3.6840 | 3.68 | +0.0040 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 25 | 5.8196 | 5.83 | -0.0104 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 35 | 4.6649 | 4.65 | +0.0149 | pass |
| M-2B | To Early Redemption Date | 3.00% | 0 | 2.7472 | 2.74 | +0.0072 | pass |
| M-2B | To Early Redemption Date | 3.00% | 5 | 2.9702 | 2.97 | +0.0002 | pass |
| M-2B | To Early Redemption Date | 3.00% | 10 | 3.2633 | 3.26 | +0.0033 | pass |
| M-2B | To Early Redemption Date | 3.00% | 15 | 3.6840 | 3.68 | +0.0040 | pass |
| M-2B | To Early Redemption Date | 3.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 3.00% | 35 | 4.6529 | 4.64 | +0.0129 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 0 | 1.6127 | 1.61 | +0.0027 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 5 | 1.6831 | 1.68 | +0.0031 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 10 | 1.7686 | 1.77 | -0.0014 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 15 | 1.8692 | 1.87 | -0.0008 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 25 | 2.1783 | 2.18 | -0.0017 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 35 | 2.8124 | 2.82 | -0.0076 | pass |
| M-2B | To Early Redemption Date | 5.00% | 0 | 1.6127 | 1.61 | +0.0027 | pass |
| M-2B | To Early Redemption Date | 5.00% | 5 | 1.6831 | 1.68 | +0.0031 | pass |
| M-2B | To Early Redemption Date | 5.00% | 10 | 1.7686 | 1.77 | -0.0014 | pass |
| M-2B | To Early Redemption Date | 5.00% | 15 | 1.8692 | 1.87 | -0.0008 | pass |
| M-2B | To Early Redemption Date | 5.00% | 25 | 2.1783 | 2.18 | -0.0017 | pass |
| M-2B | To Early Redemption Date | 5.00% | 35 | 2.8124 | 2.82 | -0.0076 | pass |

## 6. Credit Event Sensitivity
| basis | CER | CPR | model % (2 dp) | PPM % | diff | round-match pass | \|diff\| ≤ 0.25 |
|---|---|---|---|---|---|---|---|
| To Scheduled Maturity Date | 0.00% | 0 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 5 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 10 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 15 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 25 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 35 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 0 | 4.01 | 4.0% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 5 | 2.64 | 2.6% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 10 | 1.84 | 1.8% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 15 | 1.35 | 1.4% | -0.05 | FAIL | yes |
| To Scheduled Maturity Date | 0.25% | 25 | 0.83 | 0.8% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 35 | 0.57 | 0.6% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 0 | 7.85 | 7.9% | -0.05 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 5 | 5.18 | 5.2% | -0.02 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 10 | 3.62 | 3.6% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 15 | 2.67 | 2.7% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 25 | 1.65 | 1.6% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 35 | 1.14 | 1.1% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 0 | 15.06 | 15.1% | -0.04 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 5 | 10.01 | 10.0% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 10 | 7.04 | 7.1% | -0.06 | FAIL | yes |
| To Scheduled Maturity Date | 1.00% | 15 | 5.22 | 5.2% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 25 | 3.25 | 3.2% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 35 | 2.25 | 2.3% | -0.05 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 0 | 21.67 | 21.7% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 5 | 14.51 | 14.5% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 10 | 10.29 | 10.3% | -0.01 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 15 | 7.67 | 7.7% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 25 | 4.81 | 4.8% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 35 | 3.35 | 3.3% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 0 | 33.29 | 33.4% | -0.11 | FAIL | yes |
| To Scheduled Maturity Date | 2.50% | 5 | 22.64 | 22.7% | -0.06 | FAIL | yes |
| To Scheduled Maturity Date | 2.50% | 10 | 16.27 | 16.3% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 15 | 12.27 | 12.3% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 25 | 7.81 | 7.8% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 35 | 5.49 | 5.5% | -0.01 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 0 | 38.39 | 38.5% | -0.11 | FAIL | yes |
| To Scheduled Maturity Date | 3.00% | 5 | 26.31 | 26.3% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 10 | 19.02 | 19.0% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 15 | 14.43 | 14.4% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 25 | 9.25 | 9.2% | +0.05 | FAIL | yes |
| To Scheduled Maturity Date | 3.00% | 35 | 6.53 | 6.5% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 0 | 54.90 | 55.0% | -0.10 | FAIL | yes |
| To Scheduled Maturity Date | 5.00% | 5 | 38.75 | 38.8% | -0.05 | FAIL | yes |
| To Scheduled Maturity Date | 5.00% | 10 | 28.74 | 28.7% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 15 | 22.25 | 22.2% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 25 | 14.68 | 14.6% | +0.08 | FAIL | yes |
| To Scheduled Maturity Date | 5.00% | 35 | 10.54 | 10.5% | +0.04 | pass | yes |
| To Early Redemption Date | 0.00% | 0 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 5 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 10 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 15 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 25 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 35 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.25% | 0 | 1.22 | 1.2% | +0.02 | pass | yes |
| To Early Redemption Date | 0.25% | 5 | 1.08 | 1.1% | -0.02 | pass | yes |
| To Early Redemption Date | 0.25% | 10 | 0.96 | 1.0% | -0.04 | pass | yes |
| To Early Redemption Date | 0.25% | 15 | 0.84 | 0.8% | +0.04 | pass | yes |
| To Early Redemption Date | 0.25% | 25 | 0.66 | 0.7% | -0.04 | pass | yes |
| To Early Redemption Date | 0.25% | 35 | 0.51 | 0.5% | +0.01 | pass | yes |
| To Early Redemption Date | 0.50% | 0 | 2.44 | 2.4% | +0.04 | pass | yes |
| To Early Redemption Date | 0.50% | 5 | 2.15 | 2.2% | -0.05 | pass | yes |
| To Early Redemption Date | 0.50% | 10 | 1.90 | 1.9% | +0.00 | pass | yes |
| To Early Redemption Date | 0.50% | 15 | 1.68 | 1.7% | -0.02 | pass | yes |
| To Early Redemption Date | 0.50% | 25 | 1.31 | 1.3% | +0.01 | pass | yes |
| To Early Redemption Date | 0.50% | 35 | 1.02 | 1.0% | +0.02 | pass | yes |
| To Early Redemption Date | 1.00% | 0 | 4.82 | 4.8% | +0.02 | pass | yes |
| To Early Redemption Date | 1.00% | 5 | 4.27 | 4.3% | -0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 10 | 3.77 | 3.8% | -0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 15 | 3.33 | 3.3% | +0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 25 | 2.60 | 2.6% | +0.00 | pass | yes |
| To Early Redemption Date | 1.00% | 35 | 2.03 | 2.0% | +0.03 | pass | yes |
| To Early Redemption Date | 1.50% | 0 | 7.16 | 7.2% | -0.04 | pass | yes |
| To Early Redemption Date | 1.50% | 5 | 6.34 | 6.3% | +0.04 | pass | yes |
| To Early Redemption Date | 1.50% | 10 | 5.61 | 5.6% | +0.01 | pass | yes |
| To Early Redemption Date | 1.50% | 15 | 4.96 | 5.0% | -0.04 | pass | yes |
| To Early Redemption Date | 1.50% | 25 | 3.87 | 3.9% | -0.03 | pass | yes |
| To Early Redemption Date | 1.50% | 35 | 3.03 | 3.0% | +0.03 | pass | yes |
| To Early Redemption Date | 2.50% | 0 | 11.70 | 11.7% | -0.00 | pass | yes |
| To Early Redemption Date | 2.50% | 5 | 10.36 | 10.4% | -0.04 | pass | yes |
| To Early Redemption Date | 2.50% | 10 | 9.18 | 9.2% | -0.02 | pass | yes |
| To Early Redemption Date | 2.50% | 15 | 8.12 | 8.1% | +0.02 | pass | yes |
| To Early Redemption Date | 2.50% | 25 | 6.37 | 6.4% | -0.03 | pass | yes |
| To Early Redemption Date | 2.50% | 35 | 4.95 | 4.9% | +0.05 | FAIL | yes |
| To Early Redemption Date | 3.00% | 0 | 13.90 | 13.9% | -0.00 | pass | yes |
| To Early Redemption Date | 3.00% | 5 | 12.32 | 12.3% | +0.02 | pass | yes |
| To Early Redemption Date | 3.00% | 10 | 10.92 | 10.9% | +0.02 | pass | yes |
| To Early Redemption Date | 3.00% | 15 | 9.67 | 9.7% | -0.03 | pass | yes |
| To Early Redemption Date | 3.00% | 25 | 7.58 | 7.6% | -0.02 | pass | yes |
| To Early Redemption Date | 3.00% | 35 | 5.91 | 5.9% | +0.01 | pass | yes |
| To Early Redemption Date | 5.00% | 0 | 22.25 | 22.3% | -0.05 | pass | yes |
| To Early Redemption Date | 5.00% | 5 | 19.77 | 19.8% | -0.03 | pass | yes |
| To Early Redemption Date | 5.00% | 10 | 17.56 | 17.6% | -0.04 | pass | yes |
| To Early Redemption Date | 5.00% | 15 | 15.59 | 15.6% | -0.01 | pass | yes |
| To Early Redemption Date | 5.00% | 25 | 12.29 | 12.3% | -0.01 | pass | yes |
| To Early Redemption Date | 5.00% | 35 | 9.51 | 9.5% | +0.01 | pass | yes |

## 7. Diagnostics (only when anything fails)
| hypothesis (§5 number) | change tried | family/cells affected | before | after | kept? |
|---|---|---|---|---|---|
| 7 (A2 conversion) | monthly credit-event rate = CER / 12 (scratch pool re-projection, engine unchanged) | Credit Event Sensitivity, 48 "To Scheduled Maturity" cells | 39/48 round-match, worst 0.11 pp | 40/48 at low CER, then 0.3–0.9 pp short at CER ≥ 1.5 % | no |
| 7 (A1 + A2 conversion) | SMM = CPR / 12 and credit-event rate = CER / 12 | Credit Event Sensitivity, 48 sched cells | 39/48 | 33/96 overall, worst 1.63 pp | no |
| 7 (A2 basis) | credit events on the beginning-of-month balance before scheduled principal; credit-event loans pay no scheduled principal that month (H7b) | Credit Event Sensitivity sched cells; WAL CER > 0 | 39/48; WAL 324/336 within ±0.02, worst 0.084 | CES 39/48 with a different failure set (every CPR 0 cell fixed; CER ≥ 3 % / CPR ≥ 10 % cells overshoot by 0.05–0.21 pp); WAL 330/336, worst 0.038 | no — not a full fix on either table; escalated as Q21 |
| 7 (A3 order) | prepayments before credit events, both on the balance net of scheduled principal (H7c) | Credit Event Sensitivity sched cells | 39/48 | 47/96 overall, worst 0.33 pp, model short everywhere | no |
| 7 (A2 + A3 basis) | credit events and prepayments both on the beginning-of-month balance, before scheduled principal (H7e) | Credit Event Sensitivity sched cells; WAL CER > 0 | 39/48; WAL 324/336, worst 0.084 | CES 44/48 (90/96 overall, worst 0.18 pp); WAL 327/336 but worst −0.10 (M-2B, CER 1.00 %, CPR 15 %) | no — escalated as Q21 |
| 7 (A3 basis) | prepayments on the beginning-of-month balance, credit events on the beginning balance net of prepayments (H7f) | Credit Event Sensitivity sched cells | 39/48 | 51/96 overall, worst 0.33 pp | no |

Trials were run in a scratch script outside `src/` on 2026-09-07 by fintech-dev; the engine
implements A1–A15 exactly as specified and was not changed. "To Early Redemption Date" cells
at 35 % CPR were excluded from the CES trial counts because the scratch re-projection did not
model the 10 % clean-up call (A11) that the engine applies there.

