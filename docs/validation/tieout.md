# Tie-out — STACR 2026-DNA1 — 2026-09-07T17:29:16Z
Manifest: engine version 0.0.1, git commit 0dec32f29accafdacbf4a166dbe503d9c3881b62, Decimal precision 28, scenario grid CPR {0, 5, 10, 15, 25, 35} % x CER {0.00, 0.25, 0.50, 1.00, 1.50, 2.50, 3.00, 5.00} % x RM 0 x early redemption {off, on}; SHA-256: data/ppm_tables/appendix_c_rep_lines.csv f48cfaeaaa005258657a94cd34796584cded9f45138391bf20408207ef0e4361; data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv e1be1778423425b063744fb04ee68021775c3a98f8339f3ae3280e1150471eaf; data/ppm_tables/table1_classes.csv 6b25e9b72e91df44c7dcd7788aec98891ba072edf68dd154e40a81340f456465; data/ppm_tables/wal_tables.csv d50ed73d2436700e864f82c6058e41201b2f46d1b0adb8e3dea24d10ca77803a; data/ppm_tables/declining_balances.csv 860260b1cf02fbae75a89befabdcc509d38be8d788394b468bb3703dc82cfd06; data/ppm_tables/credit_event_sensitivity.csv 449094ea95cf641fac091628cd17d084e4c1e1ba21207197e7d105a70cef9596; data/deal_terms/stacr_2026_dna1.yaml 62fb79cda6b390da4dfc44d0bb617bbe72ef6ff073026893e07d96475a0fec52; docs/assumptions.csv eadea4366dc25e5374c175f998ea30881d82a7c19dfb6567320020cb75024d34; conventions in force: A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13 A14 A15.

## 1. Summary
| family | cells | pass | fail | worst \|diff\| | tolerance | status |
|---|---|---|---|---|---|---|
| Table 1 windows | 4 | 4 | 0 | 0 | exact month | PASS |
| Declining Balances CER 0 | 366 | 366 | 0 | 0.49 | round-match (A13); ±0.25 pp reported | PASS |
| WAL CER 0 | 48 | 48 | 0 | 0.0048 | ±0.02 yr | PASS |
| WAL CER>0 | 336 | 336 | 0 | 0.0050 | ±0.02 yr | PASS |
| Credit Event Sensitivity | 96 | 96 | 0 | 0.05 | round-match (A13); ±0.25 pp reported | PASS |
Secondary window-band check (spec 03 section 2): 24 (Note, CPR) pairs, 0 failing.
Overall: PASS.

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
| A-1 | To Scheduled Maturity Date | 0.25% | 0 | 1.5965 | 1.60 | -0.0035 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 5 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 10 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 15 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 25 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 0.25% | 35 | 1.5868 | 1.59 | -0.0032 | pass |
| A-1 | To Early Redemption Date | 0.25% | 0 | 1.5965 | 1.60 | -0.0035 | pass |
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
| A-1 | To Scheduled Maturity Date | 1.50% | 0 | 3.8436 | 3.84 | +0.0036 | pass |
| A-1 | To Scheduled Maturity Date | 1.50% | 5 | 5.1781 | 5.18 | -0.0019 | pass |
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
| A-1 | To Scheduled Maturity Date | 2.50% | 0 | 3.5208 | 3.52 | +0.0008 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 5 | 4.2468 | 4.25 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 10 | 6.7076 | 6.71 | -0.0024 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 15 | 6.7254 | 6.73 | -0.0046 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 25 | 4.2845 | 4.28 | +0.0045 | pass |
| A-1 | To Scheduled Maturity Date | 2.50% | 35 | 2.8025 | 2.80 | +0.0025 | pass |
| A-1 | To Early Redemption Date | 2.50% | 0 | 2.6822 | 2.68 | +0.0022 | pass |
| A-1 | To Early Redemption Date | 2.50% | 5 | 2.6310 | 2.63 | +0.0010 | pass |
| A-1 | To Early Redemption Date | 2.50% | 10 | 2.5810 | 2.58 | +0.0010 | pass |
| A-1 | To Early Redemption Date | 2.50% | 15 | 2.5322 | 2.53 | +0.0022 | pass |
| A-1 | To Early Redemption Date | 2.50% | 25 | 2.3497 | 2.35 | -0.0003 | pass |
| A-1 | To Early Redemption Date | 2.50% | 35 | 2.0368 | 2.04 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 0 | 3.1755 | 3.18 | -0.0045 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 5 | 3.7660 | 3.77 | -0.0040 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 10 | 4.9108 | 4.91 | +0.0008 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 15 | 7.1545 | 7.15 | +0.0045 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 25 | 4.6987 | 4.70 | -0.0013 | pass |
| A-1 | To Scheduled Maturity Date | 3.00% | 35 | 3.2720 | 3.27 | +0.0020 | pass |
| A-1 | To Early Redemption Date | 3.00% | 0 | 2.8435 | 2.84 | +0.0035 | pass |
| A-1 | To Early Redemption Date | 3.00% | 5 | 2.8435 | 2.84 | +0.0035 | pass |
| A-1 | To Early Redemption Date | 3.00% | 10 | 2.7885 | 2.79 | -0.0015 | pass |
| A-1 | To Early Redemption Date | 3.00% | 15 | 2.7347 | 2.73 | +0.0047 | pass |
| A-1 | To Early Redemption Date | 3.00% | 25 | 2.6310 | 2.63 | +0.0010 | pass |
| A-1 | To Early Redemption Date | 3.00% | 35 | 2.4181 | 2.42 | -0.0019 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 0 | 2.5188 | 2.52 | -0.0012 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 5 | 2.7802 | 2.78 | +0.0002 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 10 | 3.1668 | 3.17 | -0.0032 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 15 | 3.6182 | 3.62 | -0.0018 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 25 | 5.4640 | 5.46 | +0.0040 | pass |
| A-1 | To Scheduled Maturity Date | 5.00% | 35 | 3.8428 | 3.84 | +0.0028 | pass |
| A-1 | To Early Redemption Date | 5.00% | 0 | 2.5188 | 2.52 | -0.0012 | pass |
| A-1 | To Early Redemption Date | 5.00% | 5 | 2.7802 | 2.78 | +0.0002 | pass |
| A-1 | To Early Redemption Date | 5.00% | 10 | 3.1650 | 3.17 | -0.0050 | pass |
| A-1 | To Early Redemption Date | 5.00% | 15 | 3.3627 | 3.36 | +0.0027 | pass |
| A-1 | To Early Redemption Date | 5.00% | 25 | 3.4753 | 3.48 | -0.0047 | pass |
| A-1 | To Early Redemption Date | 5.00% | 35 | 2.9835 | 2.98 | +0.0035 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 0 | 17.4241 | 17.42 | +0.0041 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 5 | 4.4038 | 4.40 | +0.0038 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 10 | 2.1030 | 2.10 | +0.0030 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 15 | 1.3475 | 1.35 | -0.0025 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 25 | 0.7604 | 0.76 | +0.0004 | pass |
| M-1 | To Scheduled Maturity Date | 0.25% | 35 | 0.5298 | 0.53 | -0.0002 | pass |
| M-1 | To Early Redemption Date | 0.25% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 0.25% | 5 | 3.5063 | 3.51 | -0.0037 | pass |
| M-1 | To Early Redemption Date | 0.25% | 10 | 2.1030 | 2.10 | +0.0030 | pass |
| M-1 | To Early Redemption Date | 0.25% | 15 | 1.3475 | 1.35 | -0.0025 | pass |
| M-1 | To Early Redemption Date | 0.25% | 25 | 0.7604 | 0.76 | +0.0004 | pass |
| M-1 | To Early Redemption Date | 0.25% | 35 | 0.5298 | 0.53 | -0.0002 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 0 | 19.9209 | 19.92 | +0.0009 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 5 | 6.8520 | 6.85 | +0.0020 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 10 | 2.7136 | 2.71 | +0.0036 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 15 | 1.6517 | 1.65 | +0.0017 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 25 | 0.8822 | 0.88 | +0.0022 | pass |
| M-1 | To Scheduled Maturity Date | 0.50% | 35 | 0.5599 | 0.56 | -0.0001 | pass |
| M-1 | To Early Redemption Date | 0.50% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 0.50% | 5 | 4.0605 | 4.06 | +0.0005 | pass |
| M-1 | To Early Redemption Date | 0.50% | 10 | 2.6824 | 2.68 | +0.0024 | pass |
| M-1 | To Early Redemption Date | 0.50% | 15 | 1.6517 | 1.65 | +0.0017 | pass |
| M-1 | To Early Redemption Date | 0.50% | 25 | 0.8822 | 0.88 | +0.0022 | pass |
| M-1 | To Early Redemption Date | 0.50% | 35 | 0.5599 | 0.56 | -0.0001 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 0 | 13.6965 | 13.70 | -0.0035 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 5 | 18.8598 | 18.86 | -0.0002 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 10 | 12.6386 | 12.64 | -0.0014 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 15 | 8.8209 | 8.82 | +0.0009 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 25 | 4.5838 | 4.58 | +0.0038 | pass |
| M-1 | To Scheduled Maturity Date | 1.00% | 35 | 2.6420 | 2.64 | +0.0020 | pass |
| M-1 | To Early Redemption Date | 1.00% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 1.00% | 5 | 4.8818 | 4.88 | +0.0018 | pass |
| M-1 | To Early Redemption Date | 1.00% | 10 | 4.7611 | 4.76 | +0.0011 | pass |
| M-1 | To Early Redemption Date | 1.00% | 15 | 4.6348 | 4.63 | +0.0048 | pass |
| M-1 | To Early Redemption Date | 1.00% | 25 | 3.7493 | 3.75 | -0.0007 | pass |
| M-1 | To Early Redemption Date | 1.00% | 35 | 2.6420 | 2.64 | +0.0020 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 0 | 8.5928 | 8.59 | +0.0028 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 5 | 11.7754 | 11.78 | -0.0046 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 10 | 14.8645 | 14.86 | +0.0045 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 15 | 8.7077 | 8.71 | -0.0023 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 25 | 5.1224 | 5.12 | +0.0024 | pass |
| M-1 | To Scheduled Maturity Date | 1.50% | 35 | 3.2536 | 3.25 | +0.0036 | pass |
| M-1 | To Early Redemption Date | 1.50% | 0 | 4.9972 | 5.00 | -0.0028 | pass |
| M-1 | To Early Redemption Date | 1.50% | 5 | 4.8818 | 4.88 | +0.0018 | pass |
| M-1 | To Early Redemption Date | 1.50% | 10 | 4.7612 | 4.76 | +0.0012 | pass |
| M-1 | To Early Redemption Date | 1.50% | 15 | 4.6349 | 4.63 | +0.0049 | pass |
| M-1 | To Early Redemption Date | 1.50% | 25 | 4.2464 | 4.25 | -0.0036 | pass |
| M-1 | To Early Redemption Date | 1.50% | 35 | 3.1883 | 3.19 | -0.0017 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 0 | 4.9964 | 5.00 | -0.0036 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 5 | 5.8700 | 5.87 | +0.0000 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 10 | 7.5830 | 7.58 | +0.0030 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 15 | 7.7906 | 7.79 | +0.0006 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 25 | 4.1879 | 4.19 | -0.0021 | pass |
| M-1 | To Scheduled Maturity Date | 2.50% | 35 | 3.0995 | 3.10 | -0.0005 | pass |
| M-1 | To Early Redemption Date | 2.50% | 0 | 4.7034 | 4.70 | +0.0034 | pass |
| M-1 | To Early Redemption Date | 2.50% | 5 | 4.9210 | 4.92 | +0.0010 | pass |
| M-1 | To Early Redemption Date | 2.50% | 10 | 5.0209 | 5.02 | +0.0009 | pass |
| M-1 | To Early Redemption Date | 2.50% | 15 | 5.0183 | 5.02 | -0.0017 | pass |
| M-1 | To Early Redemption Date | 2.50% | 25 | 4.1087 | 4.11 | -0.0013 | pass |
| M-1 | To Early Redemption Date | 2.50% | 35 | 3.0995 | 3.10 | -0.0005 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 0 | 4.1227 | 4.12 | +0.0027 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 5 | 4.6851 | 4.69 | -0.0049 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 10 | 5.6150 | 5.61 | +0.0050 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 15 | 7.1587 | 7.16 | -0.0013 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 25 | 3.8834 | 3.88 | +0.0034 | pass |
| M-1 | To Scheduled Maturity Date | 3.00% | 35 | 2.7887 | 2.79 | -0.0013 | pass |
| M-1 | To Early Redemption Date | 3.00% | 0 | 4.1197 | 4.12 | -0.0003 | pass |
| M-1 | To Early Redemption Date | 3.00% | 5 | 4.5018 | 4.50 | +0.0018 | pass |
| M-1 | To Early Redemption Date | 3.00% | 10 | 4.8005 | 4.80 | +0.0005 | pass |
| M-1 | To Early Redemption Date | 3.00% | 15 | 4.9882 | 4.99 | -0.0018 | pass |
| M-1 | To Early Redemption Date | 3.00% | 25 | 3.8619 | 3.86 | +0.0019 | pass |
| M-1 | To Early Redemption Date | 3.00% | 35 | 2.7887 | 2.79 | -0.0013 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 0 | 2.4111 | 2.41 | +0.0011 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 5 | 2.5855 | 2.59 | -0.0045 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 10 | 2.8143 | 2.81 | +0.0043 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 15 | 3.1347 | 3.13 | +0.0047 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 25 | 3.7859 | 3.79 | -0.0041 | pass |
| M-1 | To Scheduled Maturity Date | 5.00% | 35 | 2.3885 | 2.39 | -0.0015 | pass |
| M-1 | To Early Redemption Date | 5.00% | 0 | 2.4111 | 2.41 | +0.0011 | pass |
| M-1 | To Early Redemption Date | 5.00% | 5 | 2.5855 | 2.59 | -0.0045 | pass |
| M-1 | To Early Redemption Date | 5.00% | 10 | 2.8143 | 2.81 | +0.0043 | pass |
| M-1 | To Early Redemption Date | 5.00% | 15 | 3.1347 | 3.13 | +0.0047 | pass |
| M-1 | To Early Redemption Date | 5.00% | 25 | 3.7781 | 3.78 | -0.0019 | pass |
| M-1 | To Early Redemption Date | 5.00% | 35 | 2.3885 | 2.39 | -0.0015 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 0 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 5 | 10.2832 | 10.28 | +0.0032 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 10 | 5.0013 | 5.00 | +0.0013 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 15 | 3.1984 | 3.20 | -0.0016 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 25 | 1.7922 | 1.79 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 0.25% | 35 | 1.1835 | 1.18 | +0.0035 | pass |
| M-2A | To Early Redemption Date | 0.25% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.25% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.25% | 10 | 4.9039 | 4.90 | +0.0039 | pass |
| M-2A | To Early Redemption Date | 0.25% | 15 | 3.1984 | 3.20 | -0.0016 | pass |
| M-2A | To Early Redemption Date | 0.25% | 25 | 1.7922 | 1.79 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.25% | 35 | 1.1835 | 1.18 | +0.0035 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 0 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 5 | 15.9963 | 16.00 | -0.0037 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 10 | 6.2911 | 6.29 | +0.0011 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 15 | 3.6791 | 3.68 | -0.0009 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 25 | 2.0167 | 2.02 | -0.0033 | pass |
| M-2A | To Scheduled Maturity Date | 0.50% | 35 | 1.3643 | 1.36 | +0.0043 | pass |
| M-2A | To Early Redemption Date | 0.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 0.50% | 15 | 3.6791 | 3.68 | -0.0009 | pass |
| M-2A | To Early Redemption Date | 0.50% | 25 | 2.0167 | 2.02 | -0.0033 | pass |
| M-2A | To Early Redemption Date | 0.50% | 35 | 1.3643 | 1.36 | +0.0043 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 0 | 9.6390 | 9.64 | -0.0010 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 5 | 14.1242 | 14.12 | +0.0042 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 10 | 19.8476 | 19.85 | -0.0024 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 15 | 13.3908 | 13.39 | +0.0008 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 25 | 7.7568 | 7.76 | -0.0032 | pass |
| M-2A | To Scheduled Maturity Date | 1.00% | 35 | 4.9420 | 4.94 | +0.0020 | pass |
| M-2A | To Early Redemption Date | 1.00% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.00% | 35 | 4.8753 | 4.88 | -0.0047 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 0 | 6.2169 | 6.22 | -0.0031 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 5 | 7.6047 | 7.60 | +0.0047 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 10 | 10.8601 | 10.86 | +0.0001 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 15 | 15.2363 | 15.24 | -0.0037 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 25 | 9.5502 | 9.55 | +0.0002 | pass |
| M-2A | To Scheduled Maturity Date | 1.50% | 35 | 6.6214 | 6.62 | +0.0014 | pass |
| M-2A | To Early Redemption Date | 1.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 1.50% | 35 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 0 | 3.6358 | 3.64 | -0.0042 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 5 | 4.0396 | 4.04 | -0.0004 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 10 | 4.6425 | 4.64 | +0.0025 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 15 | 5.6783 | 5.68 | -0.0017 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 25 | 6.2099 | 6.21 | -0.0001 | pass |
| M-2A | To Scheduled Maturity Date | 2.50% | 35 | 4.7663 | 4.77 | -0.0037 | pass |
| M-2A | To Early Redemption Date | 2.50% | 0 | 3.6358 | 3.64 | -0.0042 | pass |
| M-2A | To Early Redemption Date | 2.50% | 5 | 4.0396 | 4.04 | -0.0004 | pass |
| M-2A | To Early Redemption Date | 2.50% | 10 | 4.6425 | 4.64 | +0.0025 | pass |
| M-2A | To Early Redemption Date | 2.50% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 2.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 2.50% | 35 | 4.7239 | 4.72 | +0.0039 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 0 | 3.0037 | 3.00 | +0.0037 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 5 | 3.2735 | 3.27 | +0.0035 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 10 | 3.6428 | 3.64 | +0.0028 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 15 | 4.1971 | 4.20 | -0.0029 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 25 | 6.1672 | 6.17 | -0.0028 | pass |
| M-2A | To Scheduled Maturity Date | 3.00% | 35 | 4.1151 | 4.12 | -0.0049 | pass |
| M-2A | To Early Redemption Date | 3.00% | 0 | 3.0037 | 3.00 | +0.0037 | pass |
| M-2A | To Early Redemption Date | 3.00% | 5 | 3.2735 | 3.27 | +0.0035 | pass |
| M-2A | To Early Redemption Date | 3.00% | 10 | 3.6428 | 3.64 | +0.0028 | pass |
| M-2A | To Early Redemption Date | 3.00% | 15 | 4.1971 | 4.20 | -0.0029 | pass |
| M-2A | To Early Redemption Date | 3.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2A | To Early Redemption Date | 3.00% | 35 | 4.1151 | 4.12 | -0.0049 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 0 | 1.7613 | 1.76 | +0.0013 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 5 | 1.8487 | 1.85 | -0.0013 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 10 | 1.9518 | 1.95 | +0.0018 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 15 | 2.0880 | 2.09 | -0.0020 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 25 | 2.4881 | 2.49 | -0.0019 | pass |
| M-2A | To Scheduled Maturity Date | 5.00% | 35 | 3.4605 | 3.46 | +0.0005 | pass |
| M-2A | To Early Redemption Date | 5.00% | 0 | 1.7613 | 1.76 | +0.0013 | pass |
| M-2A | To Early Redemption Date | 5.00% | 5 | 1.8487 | 1.85 | -0.0013 | pass |
| M-2A | To Early Redemption Date | 5.00% | 10 | 1.9518 | 1.95 | +0.0018 | pass |
| M-2A | To Early Redemption Date | 5.00% | 15 | 2.0880 | 2.09 | -0.0020 | pass |
| M-2A | To Early Redemption Date | 5.00% | 25 | 2.4881 | 2.49 | -0.0019 | pass |
| M-2A | To Early Redemption Date | 5.00% | 35 | 3.4605 | 3.46 | +0.0005 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 0 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 5 | 11.9911 | 11.99 | +0.0011 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 10 | 5.8947 | 5.89 | +0.0047 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 15 | 3.7461 | 3.75 | -0.0039 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 25 | 2.1043 | 2.10 | +0.0043 | pass |
| M-2B | To Scheduled Maturity Date | 0.25% | 35 | 1.3761 | 1.38 | -0.0039 | pass |
| M-2B | To Early Redemption Date | 0.25% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.25% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.25% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.25% | 15 | 3.7461 | 3.75 | -0.0039 | pass |
| M-2B | To Early Redemption Date | 0.25% | 25 | 2.1043 | 2.10 | +0.0043 | pass |
| M-2B | To Early Redemption Date | 0.25% | 35 | 1.3761 | 1.38 | -0.0039 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 0 | 19.8264 | 19.83 | -0.0036 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 5 | 18.7084 | 18.71 | -0.0016 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 10 | 7.5425 | 7.54 | +0.0025 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 15 | 4.3606 | 4.36 | +0.0006 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 25 | 2.3275 | 2.33 | -0.0025 | pass |
| M-2B | To Scheduled Maturity Date | 0.50% | 35 | 1.5712 | 1.57 | +0.0012 | pass |
| M-2B | To Early Redemption Date | 0.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 0.50% | 15 | 4.3606 | 4.36 | +0.0006 | pass |
| M-2B | To Early Redemption Date | 0.50% | 25 | 2.3275 | 2.33 | -0.0025 | pass |
| M-2B | To Early Redemption Date | 0.50% | 35 | 1.5712 | 1.57 | +0.0012 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 0 | 8.7520 | 8.75 | +0.0020 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 5 | 12.0984 | 12.10 | -0.0016 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 10 | 20.0222 | 20.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 15 | 14.4577 | 14.46 | -0.0023 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 25 | 8.1840 | 8.18 | +0.0040 | pass |
| M-2B | To Scheduled Maturity Date | 1.00% | 35 | 5.3317 | 5.33 | +0.0017 | pass |
| M-2B | To Early Redemption Date | 1.00% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.00% | 35 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 0 | 5.6681 | 5.67 | -0.0019 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 5 | 6.7747 | 6.77 | +0.0047 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 10 | 9.0419 | 9.04 | +0.0019 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 15 | 19.1322 | 19.13 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 25 | 11.3133 | 11.31 | +0.0033 | pass |
| M-2B | To Scheduled Maturity Date | 1.50% | 35 | 8.0774 | 8.08 | -0.0026 | pass |
| M-2B | To Early Redemption Date | 1.50% | 0 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 5 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 10 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 15 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 1.50% | 35 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 0 | 3.3177 | 3.32 | -0.0023 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 5 | 3.6513 | 3.65 | +0.0013 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 10 | 4.1238 | 4.12 | +0.0038 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 15 | 4.8785 | 4.88 | -0.0015 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 25 | 7.0592 | 7.06 | -0.0008 | pass |
| M-2B | To Scheduled Maturity Date | 2.50% | 35 | 5.5305 | 5.53 | +0.0005 | pass |
| M-2B | To Early Redemption Date | 2.50% | 0 | 3.3177 | 3.32 | -0.0023 | pass |
| M-2B | To Early Redemption Date | 2.50% | 5 | 3.6513 | 3.65 | +0.0013 | pass |
| M-2B | To Early Redemption Date | 2.50% | 10 | 4.1238 | 4.12 | +0.0038 | pass |
| M-2B | To Early Redemption Date | 2.50% | 15 | 4.8436 | 4.84 | +0.0036 | pass |
| M-2B | To Early Redemption Date | 2.50% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 2.50% | 35 | 4.8556 | 4.86 | -0.0044 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 0 | 2.7443 | 2.74 | +0.0043 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 5 | 2.9678 | 2.97 | -0.0022 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 10 | 3.2609 | 3.26 | +0.0009 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 15 | 3.6818 | 3.68 | +0.0018 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 25 | 5.8267 | 5.83 | -0.0033 | pass |
| M-2B | To Scheduled Maturity Date | 3.00% | 35 | 4.6534 | 4.65 | +0.0034 | pass |
| M-2B | To Early Redemption Date | 3.00% | 0 | 2.7443 | 2.74 | +0.0043 | pass |
| M-2B | To Early Redemption Date | 3.00% | 5 | 2.9678 | 2.97 | -0.0022 | pass |
| M-2B | To Early Redemption Date | 3.00% | 10 | 3.2609 | 3.26 | +0.0009 | pass |
| M-2B | To Early Redemption Date | 3.00% | 15 | 3.6818 | 3.68 | +0.0018 | pass |
| M-2B | To Early Redemption Date | 3.00% | 25 | 5.0222 | 5.02 | +0.0022 | pass |
| M-2B | To Early Redemption Date | 3.00% | 35 | 4.6439 | 4.64 | +0.0039 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 0 | 1.6108 | 1.61 | +0.0008 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 5 | 1.6816 | 1.68 | +0.0016 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 10 | 1.7675 | 1.77 | -0.0025 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 15 | 1.8685 | 1.87 | -0.0015 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 25 | 2.1789 | 2.18 | -0.0011 | pass |
| M-2B | To Scheduled Maturity Date | 5.00% | 35 | 2.8189 | 2.82 | -0.0011 | pass |
| M-2B | To Early Redemption Date | 5.00% | 0 | 1.6108 | 1.61 | +0.0008 | pass |
| M-2B | To Early Redemption Date | 5.00% | 5 | 1.6816 | 1.68 | +0.0016 | pass |
| M-2B | To Early Redemption Date | 5.00% | 10 | 1.7675 | 1.77 | -0.0025 | pass |
| M-2B | To Early Redemption Date | 5.00% | 15 | 1.8685 | 1.87 | -0.0015 | pass |
| M-2B | To Early Redemption Date | 5.00% | 25 | 2.1789 | 2.18 | -0.0011 | pass |
| M-2B | To Early Redemption Date | 5.00% | 35 | 2.8189 | 2.82 | -0.0011 | pass |

## 6. Credit Event Sensitivity
| basis | CER | CPR | model % (2 dp) | PPM % | diff | round-match pass | \|diff\| ≤ 0.25 |
|---|---|---|---|---|---|---|---|
| To Scheduled Maturity Date | 0.00% | 0 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 5 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 10 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 15 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 25 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.00% | 35 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 0 | 4.02 | 4.0% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 5 | 2.64 | 2.6% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 10 | 1.84 | 1.8% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 15 | 1.35 | 1.4% | -0.05 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 25 | 0.83 | 0.8% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 0.25% | 35 | 0.57 | 0.6% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 0 | 7.87 | 7.9% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 5 | 5.19 | 5.2% | -0.01 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 10 | 3.62 | 3.6% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 15 | 2.67 | 2.7% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 25 | 1.65 | 1.6% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 0.50% | 35 | 1.14 | 1.1% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 0 | 15.09 | 15.1% | -0.01 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 5 | 10.03 | 10.0% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 10 | 7.05 | 7.1% | -0.05 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 15 | 5.23 | 5.2% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 25 | 3.25 | 3.2% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 1.00% | 35 | 2.25 | 2.3% | -0.05 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 0 | 21.72 | 21.7% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 5 | 14.54 | 14.5% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 10 | 10.29 | 10.3% | -0.01 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 15 | 7.68 | 7.7% | -0.02 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 25 | 4.81 | 4.8% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 1.50% | 35 | 3.35 | 3.3% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 0 | 33.37 | 33.4% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 5 | 22.67 | 22.7% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 10 | 16.27 | 16.3% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 15 | 12.27 | 12.3% | -0.03 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 25 | 7.81 | 7.8% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 2.50% | 35 | 5.48 | 5.5% | -0.02 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 0 | 38.48 | 38.5% | -0.02 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 5 | 26.34 | 26.3% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 10 | 19.03 | 19.0% | +0.03 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 15 | 14.42 | 14.4% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 25 | 9.24 | 9.2% | +0.04 | pass | yes |
| To Scheduled Maturity Date | 3.00% | 35 | 6.52 | 6.5% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 0 | 55.02 | 55.0% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 5 | 38.76 | 38.8% | -0.04 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 10 | 28.72 | 28.7% | +0.02 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 15 | 22.21 | 22.2% | +0.01 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 25 | 14.65 | 14.6% | +0.05 | pass | yes |
| To Scheduled Maturity Date | 5.00% | 35 | 10.51 | 10.5% | +0.01 | pass | yes |
| To Early Redemption Date | 0.00% | 0 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 5 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 10 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 15 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 25 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.00% | 35 | 0.00 | 0.0% | +0.00 | pass | yes |
| To Early Redemption Date | 0.25% | 0 | 1.23 | 1.2% | +0.03 | pass | yes |
| To Early Redemption Date | 0.25% | 5 | 1.08 | 1.1% | -0.02 | pass | yes |
| To Early Redemption Date | 0.25% | 10 | 0.96 | 1.0% | -0.04 | pass | yes |
| To Early Redemption Date | 0.25% | 15 | 0.84 | 0.8% | +0.04 | pass | yes |
| To Early Redemption Date | 0.25% | 25 | 0.66 | 0.7% | -0.04 | pass | yes |
| To Early Redemption Date | 0.25% | 35 | 0.51 | 0.5% | +0.01 | pass | yes |
| To Early Redemption Date | 0.50% | 0 | 2.44 | 2.4% | +0.04 | pass | yes |
| To Early Redemption Date | 0.50% | 5 | 2.16 | 2.2% | -0.04 | pass | yes |
| To Early Redemption Date | 0.50% | 10 | 1.90 | 1.9% | +0.00 | pass | yes |
| To Early Redemption Date | 0.50% | 15 | 1.68 | 1.7% | -0.02 | pass | yes |
| To Early Redemption Date | 0.50% | 25 | 1.31 | 1.3% | +0.01 | pass | yes |
| To Early Redemption Date | 0.50% | 35 | 1.02 | 1.0% | +0.02 | pass | yes |
| To Early Redemption Date | 1.00% | 0 | 4.83 | 4.8% | +0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 5 | 4.27 | 4.3% | -0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 10 | 3.77 | 3.8% | -0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 15 | 3.33 | 3.3% | +0.03 | pass | yes |
| To Early Redemption Date | 1.00% | 25 | 2.60 | 2.6% | +0.00 | pass | yes |
| To Early Redemption Date | 1.00% | 35 | 2.03 | 2.0% | +0.03 | pass | yes |
| To Early Redemption Date | 1.50% | 0 | 7.17 | 7.2% | -0.03 | pass | yes |
| To Early Redemption Date | 1.50% | 5 | 6.34 | 6.3% | +0.04 | pass | yes |
| To Early Redemption Date | 1.50% | 10 | 5.61 | 5.6% | +0.01 | pass | yes |
| To Early Redemption Date | 1.50% | 15 | 4.96 | 5.0% | -0.04 | pass | yes |
| To Early Redemption Date | 1.50% | 25 | 3.87 | 3.9% | -0.03 | pass | yes |
| To Early Redemption Date | 1.50% | 35 | 3.03 | 3.0% | +0.03 | pass | yes |
| To Early Redemption Date | 2.50% | 0 | 11.71 | 11.7% | +0.01 | pass | yes |
| To Early Redemption Date | 2.50% | 5 | 10.37 | 10.4% | -0.03 | pass | yes |
| To Early Redemption Date | 2.50% | 10 | 9.18 | 9.2% | -0.02 | pass | yes |
| To Early Redemption Date | 2.50% | 15 | 8.13 | 8.1% | +0.03 | pass | yes |
| To Early Redemption Date | 2.50% | 25 | 6.36 | 6.4% | -0.04 | pass | yes |
| To Early Redemption Date | 2.50% | 35 | 4.95 | 4.9% | +0.05 | pass | yes |
| To Early Redemption Date | 3.00% | 0 | 13.91 | 13.9% | +0.01 | pass | yes |
| To Early Redemption Date | 3.00% | 5 | 12.33 | 12.3% | +0.03 | pass | yes |
| To Early Redemption Date | 3.00% | 10 | 10.92 | 10.9% | +0.02 | pass | yes |
| To Early Redemption Date | 3.00% | 15 | 9.67 | 9.7% | -0.03 | pass | yes |
| To Early Redemption Date | 3.00% | 25 | 7.58 | 7.6% | -0.02 | pass | yes |
| To Early Redemption Date | 3.00% | 35 | 5.90 | 5.9% | +0.00 | pass | yes |
| To Early Redemption Date | 5.00% | 0 | 22.28 | 22.3% | -0.02 | pass | yes |
| To Early Redemption Date | 5.00% | 5 | 19.78 | 19.8% | -0.02 | pass | yes |
| To Early Redemption Date | 5.00% | 10 | 17.56 | 17.6% | -0.04 | pass | yes |
| To Early Redemption Date | 5.00% | 15 | 15.58 | 15.6% | -0.02 | pass | yes |
| To Early Redemption Date | 5.00% | 25 | 12.28 | 12.3% | -0.02 | pass | yes |
| To Early Redemption Date | 5.00% | 35 | 9.49 | 9.5% | -0.01 | pass | yes |

