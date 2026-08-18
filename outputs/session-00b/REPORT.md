# Session 00b report — production construction, VIXY validation, timestamp

Decision addressed: **2.22**, production construction methodology for the
constant-maturity VX series. Gates **2.9**. Written 2026-08-17.
Data pulled 2026-08-17.

No strategy return, Sharpe ratio, allocation, signal or performance statistic is
computed anywhere in this session. Everything below is a construction, a
correlation between data series, or a distribution.

No Session 00A artifact was modified. `data/interim/vx-panel.parquet`,
`data/interim/vx-cm30.parquet` and everything under `outputs/session-00a/` were
opened read-only.

---

## 1. Headline measurements

**Realized maturity closest to 30 days with least variability: construction A,
the interpolation.** Mean 30.30 days, standard deviation 2.54,
mean absolute deviation from 30 of 0.48 days, and 1.49% of
sessions outside the 25-35 band. B and C are further out and more variable on
every one of those measures.

**Highest validation correlation: construction B, the S&P roll — but only the NAV
comparison separates B from C.** Against VIXY **NAV**, B reaches
**0.99992** against
C's 0.99976 and A's
0.99510.
Against VIXY **market price** B and C are indistinguishable — they differ in the
fourth decimal, and C is marginally ahead. A is last on every benchmark.

These two answers point at different constructions. That is the substantive
result of this session and is not resolved here.

Three further findings, each of which changes a premise carried into this session:

1. **The 2004-2005 problem is not caused by interpolation.** It is worse under B
   and C. See section 3.
2. **The 16:15 versus 16:00 mismatch is real, and it ended on 2020-10-26**, when
   Cboe moved VX daily settlement from 15:15 to 15:00 CT. It cannot explain 2022.
   See section 5.
3. **The 2022 correlation failure against VXX is a VXX-specific market-price
   dislocation**, not a futures-data or construction problem. VIXY, tracking the
   same index over the same days, correlates at 0.998. See section 4.3.

---

## 2. Methodology extract (step 1)

Full extract with quoted text in [`methodology-notes.md`](methodology-notes.md).
Condensed:

| Item | As documented |
|---|---|
| Contracts | 1st and 2nd month. Roll out m = 1st, roll in n = 2nd (Table 1) |
| Roll Period | Starts after the close on the Tuesday prior to the monthly Cboe VIX Futures Settlement Date, runs through the Tuesday prior to the next one |
| Weights | `CRW_m,t = 100*(dr/dt)`, `CRW_n,t = 100*((dt-dr)/dt)` |
| `dt` | Business days in the Roll Period, **including** the starting settlement date, **excluding** the next one. Held constant through new holidays and unscheduled closures |
| `dr` | Business days from **the following business day** to, but excluding, the next settlement date |
| Daily return | `CDR_t = Σ CRW_{i,t-1}·DCRP_{i,t} / Σ CRW_{i,t-1}·DCRP_{i,t-1} - 1` |
| Settlement price | Named `DCRP`, "Daily Contract Reference Price". **Not defined anywhere in the document** |
| Index struck at | **4:00 PM New York time** (Oct 2021 edition). Was **4:25 PM EST** in the Oct 2017 edition |
| Settlement-day treatment | On the settlement date `dr = dt-1`, so `CRW_m = (dt-1)/dt`. On the Tuesday before the next settlement date `dr = 0`, `CRW_m = 0` |

The single most important structural point is that both sides of the daily-return
ratio use `CRW_{i,t-1}`, *yesterday's* weights. The index return is the return on
a position actually held overnight. The Session 00A interpolation is not: its
daily change mixes the price move with the change in interpolation weights. That
difference is what section 4.2 measures.

### Sources that could not be retrieved

| Source | Result |
|---|---|
| `spglobal.com/spdji/.../methodology-sp-vix-futures-indices.pdf` (March 2026 edition) | **HTTP 403**, WebFetch and `requests`, with and without full browser headers |
| `spglobal.com/spdji/en/methodology/article/sp-vix-futures-indices-methodology/` | **HTTP 403**, same |
| Barclays iPath VXX product page (`ipathetn.barclays`) | DNS failure on `www.`; the redirect target returns a 4 KB JavaScript shell with no data |
| VXX daily NAV / indicative value, any free source | **Not obtained.** See section 4.4 |
| Cboe regulatory circular archive (`cdn.cboe.com/resources/regulation/circulars/`) | HTTP 403 in Session 00A, not re-attempted |

The S&P methodology **was** obtained — the document itself, two editions, from
third-party hosts. That is a primary document from a secondary host, not a
secondary source: the formulas quoted are S&P's own text. What is unverified is
whether the March 2026 edition still reads the same.

---

## 3. Maturity diagnostics (step 3)

Realized maturity is the weight-weighted days to expiry of the two legs,
`w1·d1 + w2·d2`, in calendar days.

### Full sample

| construction | sessions | mean_dte | sd_dte | min_dte | max_dte | frac_outside_25_35 | mean_abs_dev_from_30 |
|---|---|---|---|---|---|---|---|
| A_interpolation | 5635 | 30.30 | 2.54 | 27.00 | 62.00 | 0.0149 | 0.48 |
| B_sp_roll | 5635 | 32.75 | 5.02 | 27.42 | 65.61 | 0.1697 | 3.17 |
| C_fixed_roll | 5635 | 31.33 | 5.05 | 25.83 | 65.14 | 0.0729 | 2.83 |

### Split at the listing-cycle break

| period | construction | sessions | mean_dte | sd_dte | frac_outside_25_35 | mean_abs_dev_from_30 |
|---|---|---|---|---|---|---|
| 2004-2005 | A_interpolation | 446 | 33.59 | 7.95 | 0.1883 | 3.72 |
| 2004-2005 | B_sp_roll | 446 | 42.42 | 12.26 | 0.5852 | 12.60 |
| 2004-2005 | C_fixed_roll | 446 | 41.20 | 12.24 | 0.5314 | 11.89 |
| 2006-2026 | A_interpolation | 5189 | 30.02 | 0.75 | 0.0000 | 0.21 |
| 2006-2026 | B_sp_roll | 5189 | 31.92 | 2.40 | 0.1339 | 2.36 |
| 2006-2026 | C_fixed_roll | 5189 | 30.48 | 2.41 | 0.0335 | 2.05 |

### By year

`*_out` is the fraction of sessions with realized maturity outside 25-35 days.

| year | A_mean | B_mean | C_mean | A_sd | B_sd | C_sd | A_out | B_out | C_out | A_clipping_rate |
|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 32.80 | 39.24 | 38.13 | 6.88 | 10.03 | 10.12 | 0.1546 | 0.5000 | 0.4278 | 0.2474 |
| 2005 | 34.20 | 44.86 | 43.56 | 8.65 | 13.24 | 13.18 | 0.2143 | 0.6508 | 0.6111 | 0.2976 |
| 2006 | 30.02 | 31.85 | 30.54 | 0.75 | 2.36 | 2.52 | 0.0000 | 0.1275 | 0.0438 | 0.0956 |
| 2007 | 30.02 | 31.83 | 30.37 | 0.75 | 2.41 | 2.44 | 0.0000 | 0.1195 | 0.0319 | 0.0956 |
| 2008 | 30.06 | 32.20 | 30.74 | 0.75 | 2.34 | 2.34 | 0.0000 | 0.1423 | 0.0316 | 0.0909 |
| 2009 | 30.02 | 31.91 | 30.46 | 0.75 | 2.43 | 2.41 | 0.0000 | 0.1548 | 0.0357 | 0.0952 |
| 2010 | 30.02 | 31.96 | 30.53 | 0.75 | 2.37 | 2.36 | 0.0000 | 0.1349 | 0.0317 | 0.0952 |
| 2011 | 30.02 | 31.78 | 30.33 | 0.75 | 2.46 | 2.47 | 0.0000 | 0.1270 | 0.0317 | 0.0952 |
| 2012 | 30.02 | 31.74 | 30.28 | 0.75 | 2.46 | 2.47 | 0.0000 | 0.1360 | 0.0320 | 0.0960 |
| 2013 | 30.06 | 32.17 | 30.70 | 0.80 | 2.44 | 2.46 | 0.0000 | 0.1468 | 0.0397 | 0.0952 |
| 2014 | 30.00 | 31.86 | 30.41 | 0.73 | 2.38 | 2.38 | 0.0000 | 0.1310 | 0.0317 | 0.0873 |
| 2015 | 30.02 | 31.88 | 30.43 | 0.75 | 2.39 | 2.39 | 0.0000 | 0.1423 | 0.0316 | 0.0949 |
| 2016 | 30.02 | 31.94 | 30.50 | 0.75 | 2.34 | 2.33 | 0.0000 | 0.1310 | 0.0317 | 0.0952 |
| 2017 | 30.02 | 31.84 | 30.39 | 0.75 | 2.37 | 2.38 | 0.0000 | 0.1275 | 0.0319 | 0.0956 |
| 2018 | 30.02 | 31.75 | 30.30 | 0.75 | 2.46 | 2.48 | 0.0000 | 0.1190 | 0.0317 | 0.0952 |
| 2019 | 30.04 | 32.17 | 30.70 | 0.73 | 2.37 | 2.38 | 0.0000 | 0.1389 | 0.0317 | 0.0873 |
| 2020 | 30.02 | 31.92 | 30.47 | 0.75 | 2.42 | 2.41 | 0.0000 | 0.1542 | 0.0356 | 0.0949 |
| 2021 | 30.02 | 31.96 | 30.53 | 0.75 | 2.37 | 2.36 | 0.0000 | 0.1349 | 0.0317 | 0.0952 |
| 2022 | 30.02 | 31.86 | 30.41 | 0.83 | 2.59 | 2.59 | 0.0000 | 0.1434 | 0.0478 | 0.1036 |
| 2023 | 30.02 | 31.87 | 30.42 | 0.75 | 2.40 | 2.41 | 0.0000 | 0.1360 | 0.0320 | 0.0960 |
| 2024 | 30.05 | 32.22 | 30.75 | 0.81 | 2.39 | 2.41 | 0.0000 | 0.1468 | 0.0397 | 0.0952 |
| 2025 | 30.00 | 31.81 | 30.35 | 0.73 | 2.38 | 2.38 | 0.0000 | 0.1275 | 0.0319 | 0.0876 |
| 2026 | 29.97 | 31.71 | 30.35 | 0.57 | 1.98 | 1.97 | 0.0000 | 0.0645 | 0.0065 | 0.0774 |

### Clipping and pinning

- **A**: clipping applies and is reported above. 0.1083 over the
  full sample, 0.2474
  in 2004 and 0.2976
  in 2005, against roughly 0.09-0.10 from 2006.
- **B and C**: **the concept does not apply.** Weights are `dr/dt` and
  `remaining/cycle` respectively, both ratios of non-negative business-day counts
  with numerator no greater than denominator, so both lie in [0,1] by construction.
  No clipping is possible and none occurred. Observed `w1` ranges
  0.000 to 0.977 for B and 0.000 to
  0.977 for C.

### Does 2004-2005 remain problematic under B and C?

**Yes, and more so.** Sessions outside the 25-35 band in 2004-2005: A
18.8%, B 58.5%, C 53.1%. Mean absolute deviation
from 30 days: A 3.72, B 12.60, C 11.89.

The cause is the listing cycle, not the construction. Gaps between consecutive VX
expiries averaged 44.3 days in 2005 against 30.3 days in every year from 2006,
reaching 63 days at the widest. No two-contract construction can hold a 30-day
maturity when the two contracts available straddle a 63-day gap.

The high clipping rate that motivated this session is therefore a **symptom**
rather than the disease, and it is the mechanism by which A degrades *least*
badly: clipping pins the series to the front contract and bounds the maturity
error, where B and C hold whatever the calendar offers and drift to a mean of
42.4 and 41.2 days.

A further consequence, found while implementing B: on **48 sessions in 2004-2006**
the true 2nd-month contract required by S&P Table 1 **had not yet been listed**.
B is not computable on those sessions from listed contracts alone. All 48 were
filled using the interpolation the S&P document specifies for exactly this case,
and each is flagged `price_fill` in `data/interim/vx-cm30-b.parquet`. The last
such session is 2006-08-18.

---

## 4. Extended validation (step 4)

### 4.1 The pulls

| Series | Rows | First | Last | Note |
|---|---|---|---|---|
| VIXY (yfinance, `auto_adjust=False`, `actions=True`, start 2010-01-01) | 3,926 | **2011-01-04** | 2026-08-14 | 6 reverse splits; `ret(Close)` and `ret(Adj Close)` agree to 0.0e+00 |
| VXX (yfinance, same settings, start 2009-01-01) | 2,150 | 2018-01-25 | 2026-08-14 | 3 reverse splits; iPath Series B only, as in Session 00A |
| VIXY NAV (ProShares, issuer) | 3,927 | **2011-01-03** | 2026-08-14 | stated `NAV Change (%)` matches `NAV / Prior NAV - 1` to 5.0e-08 |

VIXY requested from 2010-01-01 returns nothing before **2011-01-04**; the fund
launched in January 2011. As anticipated, VIXY carries no share-class
discontinuity — it extends the validation window from 8 years to **15 years and 7
months**, more than doubling it.

### 4.2 Correlation, session-weighted over the full overlap

| construction | VIXY | VXX | VIXY_NAV |
|---|---|---|---|
| A_interpolation | 0.956838 | 0.949920 | 0.995100 |
| B_sp_roll | 0.962248 | 0.954184 | 0.999920 |
| C_fixed_roll | 0.962373 | 0.954601 | 0.999759 |

### 4.3 Daily return correlation by year

**Against VIXY NAV** — this isolates construction from market-price noise,
because NAV is struck from the same futures settlement prices the constructions use:

| year | A_interpolation | B_sp_roll | C_fixed_roll |
|---|---|---|---|
| 2011 | 0.99487 | 0.99977 | 0.99963 |
| 2012 | 0.99529 | 0.99998 | 0.99987 |
| 2013 | 0.99515 | 0.99999 | 0.99975 |
| 2014 | 0.99288 | 0.99999 | 0.99967 |
| 2015 | 0.99594 | 0.99926 | 0.99908 |
| 2016 | 0.99394 | 1.00000 | 0.99991 |
| 2017 | 0.99105 | 1.00000 | 0.99963 |
| 2018 | 0.99800 | 0.99991 | 0.99984 |
| 2019 | 0.99275 | 1.00000 | 0.99990 |
| 2020 | 0.99577 | 1.00000 | 0.99985 |
| 2021 | 0.99613 | 1.00000 | 0.99986 |
| 2022 | 0.99739 | 1.00000 | 0.99986 |
| 2023 | 0.99508 | 1.00000 | 0.99986 |
| 2024 | 0.99667 | 1.00000 | 0.99986 |
| 2025 | 0.99554 | 0.99987 | 0.99980 |
| 2026 | 0.99519 | 0.99998 | 0.99979 |

B reproduces VIXY NAV at 0.99999 or better in nine of sixteen years and never
below 0.99926. This is the cleanest evidence in the session: **construction B is
a correct implementation of the index VIXY tracks.** A sits near 0.995 — visibly
and consistently below, in every single year.

**Against VIXY market price:**

| year | A_interpolation | B_sp_roll | C_fixed_roll |
|---|---|---|---|
| 2011 | 0.9735 | 0.9806 | 0.9806 |
| 2012 | 0.9372 | 0.9429 | 0.9425 |
| 2013 | 0.9568 | 0.9659 | 0.9654 |
| 2014 | 0.9317 | 0.9339 | 0.9337 |
| 2015 | 0.9491 | 0.9479 | 0.9482 |
| 2016 | 0.9522 | 0.9603 | 0.9609 |
| 2017 | 0.9287 | 0.9424 | 0.9421 |
| 2018 | 0.8145 | 0.8129 | 0.8159 |
| 2019 | 0.9601 | 0.9684 | 0.9687 |
| 2020 | 0.9591 | 0.9683 | 0.9683 |
| 2021 | 0.9911 | 0.9960 | 0.9959 |
| 2022 | 0.9952 | 0.9980 | 0.9978 |
| 2023 | 0.9935 | 0.9977 | 0.9977 |
| 2024 | 0.9944 | 0.9985 | 0.9983 |
| 2025 | 0.9930 | 0.9981 | 0.9980 |
| 2026 | 0.9931 | 0.9975 | 0.9974 |

**Against VXX market price:**

| year | A_interpolation | B_sp_roll | C_fixed_roll |
|---|---|---|---|
| 2018 | 0.7862 | 0.7837 | 0.7868 |
| 2019 | 0.9596 | 0.9680 | 0.9683 |
| 2020 | 0.9670 | 0.9743 | 0.9744 |
| 2021 | 0.9930 | 0.9965 | 0.9962 |
| 2022 | 0.8797 | 0.8832 | 0.8842 |
| 2023 | 0.9917 | 0.9966 | 0.9964 |
| 2024 | 0.9932 | 0.9971 | 0.9970 |
| 2025 | 0.9922 | 0.9967 | 0.9966 |
| 2026 | 0.9912 | 0.9956 | 0.9956 |

Two features of these tables matter.

**A regime break at 2020-2021.** Against VIXY market price every construction
jumps from roughly 0.93-0.96 to roughly 0.998 and stays there. The break
coincides with the Cboe settlement-time change of 2020-10-26. Section 5 measures
it directly.

**2022 is VXX-specific.** In 2022 the constructions correlate with VIXY at
0.995-0.998 but with VXX at 0.880-0.884. VIXY and VXX track the same S&P index
and both close at 16:00 ET, so no futures-timestamp effect can separate them —
yet **VIXY and VXX correlate with each other at only 0.8847 in 2022**, against
0.996-0.999 in every other year. Monthly correlation between VIXY and VXX in 2022:

| Month | corr(VIXY, VXX) |
|---|---|
| Jan | 0.9995 |
| Feb | 0.9995 |
| Mar | 0.9216 |
| Apr | 0.8426 |
| May | 0.9073 |
| Jun | 0.9342 |
| Jul | 0.8912 |
| **Aug** | **0.3951** |
| Sep | 0.7963 |
| Oct | 0.9985 |
| Nov | 0.9989 |
| Dec | 0.9976 |

The dislocation runs March to September 2022 and is bounded on both sides by
normal months. Barclays **suspended further sales and issuances of VXX on
2022-03-14** for want of shelf capacity, and **resumed on 2022-08-01**; a
suspended ETN cannot be arbitraged to indicative value and trades at an
uncontrolled premium.

- https://www.businesswire.com/news/home/20220314005483/en/Barclays-Suspends-Until-Further-Notice-Further-Sales-and-Issuances-of-Two-Series-of-iPath
- https://www.businesswire.com/news/home/20220725005471/en/Barclays-Resumes-Further-Issuances-and-Sales-of-Certain-iPath%C2%AE-ETNs
- https://www.sec.gov/Archives/edgar/data/312070/000095010322004469/dp169097_424b2-vxxetns.htm

The suspension and resumption dates bracket the measured dislocation. The
Session 00A attribution of the 2022 shortfall to a settlement-timestamp mismatch
is not supported: the mismatch had already been removed in October 2020, and the
2022 effect is absent from VIXY over the identical sessions.

### 4.4 Maximum rolling 252-session cumulative divergence

**Against VIXY NAV:**

| year | A_interpolation | B_sp_roll | C_fixed_roll |
|---|---|---|---|
| 2011 | 0.3599 | 0.0077 | 0.0082 |
| 2012 | 0.5821 | 0.0276 | 0.0289 |
| 2013 | 0.6615 | 0.0031 | 0.0103 |
| 2014 | 0.6951 | 0.0121 | 0.0322 |
| 2015 | 0.8398 | 0.0253 | 0.0212 |
| 2016 | 0.6406 | 0.0187 | 0.0201 |
| 2017 | 0.6986 | 0.0012 | 0.0073 |
| 2018 | 1.4118 | 0.0233 | 0.0741 |
| 2019 | 0.5100 | 0.0218 | 0.0690 |
| 2020 | 2.2495 | 0.0218 | 0.1207 |
| 2021 | 0.8075 | 0.0137 | 0.0193 |
| 2022 | 0.9606 | 0.0084 | 0.0066 |
| 2023 | 0.4287 | 0.0097 | 0.0219 |
| 2024 | 0.9350 | 0.0291 | 0.0396 |
| 2025 | 0.6070 | 0.0500 | 0.0429 |
| 2026 | 0.6415 | 0.0175 | 0.0202 |

This is the sharpest separation in the session. B stays within 0.0012 to 0.0500
of VIXY NAV over any rolling year. A reaches **2.2495** in 2020 and exceeds 0.35
in every year. A's daily changes are not held-position returns, so its level
drifts away from any tradeable position; the drift is largest when the term
structure is steepest.

**Against VIXY market price:**

| year | A_interpolation | B_sp_roll | C_fixed_roll |
|---|---|---|---|
| 2011 | - | - | - |
| 2012 | 0.6061 | 0.0554 | 0.0484 |
| 2013 | 0.6648 | 0.0230 | 0.0211 |
| 2014 | 0.6998 | 0.0775 | 0.0854 |
| 2015 | 0.8673 | 0.0594 | 0.0529 |
| 2016 | 0.6442 | 0.0890 | 0.0966 |
| 2017 | 0.7077 | 0.0151 | 0.0195 |
| 2018 | 1.6907 | 0.2834 | 0.2861 |
| 2019 | 0.5352 | 0.2365 | 0.2353 |
| 2020 | 2.2890 | 0.0944 | 0.1421 |
| 2021 | 0.8080 | 0.0359 | 0.0291 |
| 2022 | 0.9607 | 0.0121 | 0.0160 |
| 2023 | 0.4283 | 0.0100 | 0.0219 |
| 2024 | 0.9324 | 0.0317 | 0.0422 |
| 2025 | 0.6200 | 0.0483 | 0.0495 |
| 2026 | 0.6408 | 0.0182 | 0.0216 |

### 4.5 NAV retrieval

**VIXY NAV: obtained.** ProShares publishes a complete daily NAV history at
`https://accounts.profunds.com/etfdata/ByFund/VIXY-historical_nav.csv`, 3,927
rows from 2011-01-03. Saved to `data/interim/vixy-nav-proshares-s00b.parquet`.
The file's `NAV Change (%)` column was verified split-neutral against
`NAV / Prior NAV - 1` to 5.0e-08 across all rows; a naive `pct_change` of the NAV
column disagrees with it on zero sessions, so the series carries no reverse-split
discontinuity. Correlations against NAV are reported above alongside market price.

**VXX NAV or indicative value: not obtained.** Attempted:
`https://www.ipathetn.barclays/` (DNS failure), `https://ipathetn.barclays/details.app?instrumentId=341408`
(redirects to `ipathetn.cib.barclays`, returns a 4 KB JavaScript shell with no
embedded data), `https://stooq.com/q/d/l/?s=vxx.iv&i=d` (796-byte error page).
No free daily historical indicative-value series for VXX was located. The VXX
comparisons above are therefore market price only, which is precisely the
limitation that section 4.3 exposes.

---

## 5. Timestamp investigation (step 5)

### 5.1 Findings from Cboe sources

**The VX daily settlement time changed.** Primary sources, both retrieved in full:

- Cboe notice **C2020092202**, "Adjustment of Daily Marking and Settlement Price
  Reference Time for Proprietary Index Products":
  https://cdn.cboe.com/resources/release_notes/2020/Adjustment-of-Daily-Settlement-Time-for-Proprietary-Index-Products-Notice.pdf
  > "Effective **October 26, 2020** ... CFE will transition the time in relation to
  > which daily settlement prices are calculated for the following products from
  > **3:15 p.m. to 3:00 p.m. CT** (noon CT on early market close days): Cboe
  > Volatility Index ("VX") futures, Mini Cboe Volatility Index ("VXM") futures."

- CFE rule certification **CFE-2020-028**, filed with the CFTC 2020-09-23:
  https://cdn.cboe.com/resources/regulation/rule_filings/pending/2020/20-028-Daily-Settlement-Determination-Time.pdf
  > "The time in relation to which the daily settlement price of a VX futures
  > contract is currently determined is the close of regular trading hours in VX
  > futures ... Accordingly, the time in relation to which the daily settlement
  > price of a VX futures contract is currently determined is **3:15 p.m.**" (CT)

Corroborated independently by S&P: Appendix I of the October 2021 methodology
lists a "Change in VIX Settlement Times" effective **10/23/2020 after close**,
from a "4:15 PM ET stop time" to a "4:00 PM ET stop time", and renames the index
variant from `(0930-1615 ET)` to `(0930-1600 ET)`. Friday close, Monday live —
the same event.

**So: 16:15 ET from inception through 2020-10-23; 16:00 ET from 2020-10-26.**
From 2020-10-26 the VX settlement reference time and the US equity close coincide.

**Does CFE publish a separate 16:00 ET mark alongside the 16:15 settlement?** No
evidence of one was found. C2020092202 describes a *transition* of the single
daily settlement reference time, not the addition of a second mark. The "Daily
Final Indicative Prices" file described in the same notice covers index
**options**, not VX futures.

**Was there any earlier change, 2004 to 2020?** **Inconclusive.** CFE-2020-028
establishes that the reference time was the close of regular trading hours and
that this was 3:15 p.m. CT in 2020, but it does not say when regular trading
hours were last altered. The Cboe regulatory circular archive returned HTTP 403
in Session 00A and was not re-attempted. It is **not** concluded that the time
was unchanged from 2004 to 2020.

### 5.2 Direct measurement of the mismatch

Construction B against VIXY market price, split at 2020-10-26:

| Regime | Sessions | Correlation | Mean abs daily difference |
|---|---|---|---|
| Pre 2020-10-26, VX settle 16:15 ET | 2,468 | 0.924702 | 0.00892 |
| Post 2020-10-26, VX settle 16:00 ET | 1,457 | **0.997558** | **0.00226** |

Mean absolute daily difference falls by a factor of **3.9** at the documented
change. This is the clearest single measurement in the session, and it dates the
15-minute mismatch precisely rather than treating it as a standing property.

### 5.3 Difference conditional on decile of absolute VIXY return

**All sessions:**

| decile | n | abs_vixy_ret_lo | abs_vixy_ret_hi | mean_diff | sd_diff | mean_abs_diff | median_abs_diff | p95_abs_diff | max_abs_diff |
|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 393.0 | 0.0000 | 0.0038 | -0.00049 | 0.00712 | 0.00483 | 0.00295 | 0.01485 | 0.04391 |
| 2.0 | 392.0 | 0.0038 | 0.0077 | -0.00000 | 0.00675 | 0.00450 | 0.00285 | 0.01439 | 0.03691 |
| 3.0 | 393.0 | 0.0078 | 0.0116 | 0.00042 | 0.01080 | 0.00593 | 0.00353 | 0.01747 | 0.11345 |
| 4.0 | 393.0 | 0.0116 | 0.0165 | 0.00023 | 0.00766 | 0.00511 | 0.00320 | 0.01602 | 0.04565 |
| 5.0 | 392.0 | 0.0165 | 0.0216 | 0.00037 | 0.00789 | 0.00518 | 0.00314 | 0.01603 | 0.04976 |
| 6.0 | 392.0 | 0.0216 | 0.0273 | 0.00049 | 0.00880 | 0.00526 | 0.00296 | 0.01575 | 0.07441 |
| 7.0 | 392.0 | 0.0273 | 0.0348 | -0.00027 | 0.01448 | 0.00634 | 0.00348 | 0.01973 | 0.22710 |
| 8.0 | 393.0 | 0.0349 | 0.0459 | -0.00014 | 0.00985 | 0.00595 | 0.00341 | 0.01906 | 0.08432 |
| 9.0 | 392.0 | 0.0459 | 0.0656 | -0.00034 | 0.01200 | 0.00729 | 0.00393 | 0.02327 | 0.10618 |
| 10.0 | 393.0 | 0.0656 | 0.4305 | 0.00097 | 0.03769 | 0.01405 | 0.00601 | 0.05167 | 0.61866 |

**Pre 2020-10-26 (VX settle 16:15 ET):**

| decile | n | abs_vixy_ret_lo | abs_vixy_ret_hi | mean_diff | sd_diff | mean_abs_diff | median_abs_diff | p95_abs_diff | max_abs_diff |
|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 247.0 | 0.0000 | 0.0038 | -0.00056 | 0.00873 | 0.00650 | 0.00526 | 0.01899 | 0.04391 |
| 2.0 | 247.0 | 0.0038 | 0.0078 | 0.00011 | 0.00844 | 0.00621 | 0.00451 | 0.01862 | 0.03691 |
| 3.0 | 247.0 | 0.0078 | 0.0113 | 0.00103 | 0.01301 | 0.00758 | 0.00502 | 0.02021 | 0.11345 |
| 4.0 | 246.0 | 0.0113 | 0.0163 | 0.00002 | 0.00983 | 0.00721 | 0.00567 | 0.01998 | 0.04565 |
| 5.0 | 247.0 | 0.0163 | 0.0212 | 0.00064 | 0.00952 | 0.00693 | 0.00502 | 0.01781 | 0.04976 |
| 6.0 | 247.0 | 0.0212 | 0.0270 | 0.00075 | 0.01101 | 0.00722 | 0.00490 | 0.02275 | 0.07441 |
| 7.0 | 246.0 | 0.0271 | 0.0348 | -0.00023 | 0.01822 | 0.00904 | 0.00637 | 0.02416 | 0.22710 |
| 8.0 | 247.0 | 0.0348 | 0.0465 | -0.00024 | 0.01234 | 0.00842 | 0.00600 | 0.02291 | 0.08432 |
| 9.0 | 247.0 | 0.0465 | 0.0653 | -0.00037 | 0.01477 | 0.00988 | 0.00706 | 0.02803 | 0.10618 |
| 10.0 | 247.0 | 0.0653 | 0.3910 | 0.00104 | 0.04741 | 0.02019 | 0.01113 | 0.06083 | 0.61866 |

**Post 2020-10-26 (VX settle 16:00 ET):**

| decile | n | abs_vixy_ret_lo | abs_vixy_ret_hi | mean_diff | sd_diff | mean_abs_diff | median_abs_diff | p95_abs_diff | max_abs_diff |
|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 146.0 | 0.0000 | 0.0039 | -0.00040 | 0.00250 | 0.00186 | 0.00149 | 0.00474 | 0.01258 |
| 2.0 | 146.0 | 0.0039 | 0.0076 | -0.00009 | 0.00245 | 0.00192 | 0.00155 | 0.00480 | 0.00831 |
| 3.0 | 145.0 | 0.0077 | 0.0121 | -0.00012 | 0.00289 | 0.00214 | 0.00150 | 0.00534 | 0.01273 |
| 4.0 | 146.0 | 0.0121 | 0.0168 | -0.00013 | 0.00267 | 0.00201 | 0.00158 | 0.00497 | 0.01112 |
| 5.0 | 146.0 | 0.0168 | 0.0221 | 0.00012 | 0.00285 | 0.00208 | 0.00150 | 0.00519 | 0.01526 |
| 6.0 | 145.0 | 0.0221 | 0.0275 | -0.00027 | 0.00284 | 0.00212 | 0.00166 | 0.00519 | 0.01301 |
| 7.0 | 146.0 | 0.0275 | 0.0349 | -0.00022 | 0.00293 | 0.00213 | 0.00158 | 0.00596 | 0.01151 |
| 8.0 | 145.0 | 0.0350 | 0.0440 | 0.00019 | 0.00276 | 0.00205 | 0.00153 | 0.00557 | 0.00961 |
| 9.0 | 146.0 | 0.0441 | 0.0658 | -0.00007 | 0.00302 | 0.00235 | 0.00197 | 0.00569 | 0.01139 |
| 10.0 | 146.0 | 0.0664 | 0.4305 | 0.00065 | 0.00556 | 0.00390 | 0.00255 | 0.01141 | 0.02693 |

**Is the difference concentrated in large-move days? Partly, but it is not
primarily a large-move phenomenon.**

- The top decile of `|VIXY return|` holds **21.8%** of the total absolute
  difference while holding 10% of the sessions — a concentration factor of about
  2.2, not the 5 or 10 that "concentrated in large moves" would imply.
- The difference is present at **every** decile. In the pre-change regime even the
  smallest-move decile carries a mean absolute difference of 0.0065, 65 basis
  points a day, against 0.0202 in the top decile — a factor of 3 across the whole
  range of market conditions.
- After the change the gradient flattens further: 0.00186 in decile 1 against
  0.00390 in decile 10, a factor of 2.1, and the maximum absolute difference over
  1,457 sessions falls to 0.0269 from 0.6187.
- Mean signed difference is close to zero in every decile in both regimes, so the
  mismatch is dispersion, not bias.

The reading consistent with all of this: the 15-minute gap injected a roughly
proportional error on every session, which naturally scales with the size of the
day's move but is not confined to tail days.

### 5.4 The twenty largest absolute differences

**All twenty fall in the pre-2020-10-26 regime** (20 of 20). The largest
post-change difference anywhere is 0.0269, which would not enter this table.

| trade_date | regime | cdr | vixy_ret | diff | front_contract | front_settle_prev | front_settle_t | second_contract | second_settle_prev | second_settle_t |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018-02-05 | pre_1615ET | 0.96103 | 0.34237 | 0.61866 | VXG2018 | 15.625 | 33.225 | VXH2018 | 14.975 | 27.975 |
| 2018-02-06 | pre_1615ET | -0.25956 | -0.03246 | -0.22710 | VXG2018 | 33.225 | 23.875 | VXH2018 | 27.975 | 21.025 |
| 2018-02-08 | pre_1615ET | 0.11440 | 0.24139 | -0.12698 | VXG2018 | 23.425 | 28.100 | VXH2018 | 19.875 | 21.650 |
| 2014-10-15 | pre_1615ET | 0.12462 | 0.01117 | 0.11345 | VXV2014 | 20.900 | 23.950 | VXX2014 | 19.750 | 22.100 |
| 2012-12-28 | pre_1615ET | 0.15712 | 0.05094 | 0.10618 | VXF2013 | 19.100 | 22.350 | VXG2013 | 19.400 | 21.950 |
| 2016-06-24 | pre_1615ET | 0.32709 | 0.24053 | 0.08655 | VXN2016 | 16.675 | 22.650 | VXQ2016 | 17.625 | 22.125 |
| 2012-12-31 | pre_1615ET | -0.18849 | -0.10379 | -0.08469 | VXF2013 | 22.350 | 17.700 | VXG2013 | 21.950 | 18.500 |
| 2015-09-17 | pre_1615ET | 0.07506 | -0.00948 | 0.08453 | VXV2015 | 18.975 | 20.425 | VXX2015 | 19.250 | 20.075 |
| 2016-06-28 | pre_1615ET | -0.18591 | -0.10153 | -0.08438 | VXN2016 | 23.650 | 18.875 | VXQ2016 | 23.025 | 19.375 |
| 2018-02-07 | pre_1615ET | -0.04485 | 0.03947 | -0.08432 | VXG2018 | 23.875 | 23.425 | VXH2018 | 21.025 | 19.875 |
| 2015-08-25 | pre_1615ET | 0.00685 | 0.09001 | -0.08316 | VXU2015 | 25.125 | 25.325 | VXV2015 | 22.500 | 22.550 |
| 2018-10-11 | pre_1615ET | 0.01114 | 0.08912 | -0.07798 | VXV2018 | 20.125 | 21.175 | VXX2018 | 18.525 | 18.525 |
| 2015-08-24 | pre_1615ET | 0.25443 | 0.17878 | 0.07565 | VXU2015 | 19.900 | 25.125 | VXV2015 | 18.625 | 22.500 |
| 2014-10-16 | pre_1615ET | -0.05117 | 0.02324 | -0.07441 | VXV2014 | 23.950 | 22.300 | VXX2014 | 22.100 | 21.050 |
| 2013-04-15 | pre_1615ET | 0.18944 | 0.11604 | 0.07339 | VXJ2013 | 12.750 | 16.700 | VXK2013 | 14.150 | 16.650 |
| 2015-09-18 | pre_1615ET | 0.05315 | 0.12235 | -0.06921 | VXV2015 | 20.425 | 21.525 | VXX2015 | 20.075 | 20.975 |
| 2020-03-27 | pre_1615ET | 0.15316 | 0.08854 | 0.06462 | VXJ2020 | 45.875 | 53.425 | VXK2020 | 39.650 | 44.825 |
| 2011-08-09 | pre_1615ET | -0.16119 | -0.09897 | -0.06222 | VXQ2011 | 36.550 | 30.500 | VXU2011 | 30.200 | 25.400 |
| 2020-03-09 | pre_1615ET | 0.21236 | 0.27415 | -0.06178 | VXH2020 | 35.775 | 44.375 | VXJ2020 | 30.325 | 36.225 |
| 2012-06-25 | pre_1615ET | 0.02528 | 0.08388 | -0.05860 | VXN2012 | 21.850 | 22.450 | VXQ2012 | 23.900 | 24.250 |

2018-02-05 is the extreme case: the front contract settled 15.625 then 33.225, a
move of +113% struck at 16:15, against VIXY's +34.2% struck at 16:00. Full file
including weights and days to expiry in `timestamp-top20-sessions.csv`; the same
rows are stacked into `timestamp-diagnostics.csv` under `block = top20_session`.

---

## 6. Term structure (step 6)

Front two contracts, nearest two listed carrying a settlement price, the same
convention used in Session 00A. Slope is `(second - front) / front`.

| year | sessions | frac_contango | frac_backwardation | frac_flat | median_abs_slope | median_signed_slope | mean_signed_slope | frac_expiry_sessions | median_front_dte | median_second_dte |
|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 194 | 0.9691 | 0.0258 | 0.0052 | 0.0839 | 0.0839 | 0.0932 | 0.0361 | 20.0 | 51.0 |
| 2005 | 252 | 0.9762 | 0.0238 | 0.0000 | 0.0691 | 0.0691 | 0.0752 | 0.0357 | 20.0 | 62.5 |
| 2006 | 251 | 0.8964 | 0.1036 | 0.0000 | 0.0694 | 0.0659 | 0.0668 | 0.0478 | 14.0 | 44.0 |
| 2007 | 251 | 0.7211 | 0.2789 | 0.0000 | 0.0405 | 0.0316 | 0.0284 | 0.0478 | 14.0 | 44.0 |
| 2008 | 253 | 0.5217 | 0.4783 | 0.0000 | 0.0417 | 0.0034 | -0.0126 | 0.0474 | 14.0 | 44.0 |
| 2009 | 252 | 0.7341 | 0.2619 | 0.0040 | 0.0577 | 0.0482 | 0.0466 | 0.0476 | 14.0 | 44.0 |
| 2010 | 252 | 0.9286 | 0.0675 | 0.0040 | 0.1155 | 0.1155 | 0.1018 | 0.0476 | 14.0 | 44.0 |
| 2011 | 252 | 0.6825 | 0.3095 | 0.0079 | 0.0681 | 0.0462 | 0.0300 | 0.0476 | 14.0 | 44.0 |
| 2012 | 250 | 0.9880 | 0.0120 | 0.0000 | 0.0964 | 0.0964 | 0.1014 | 0.0480 | 14.0 | 44.0 |
| 2013 | 252 | 0.9444 | 0.0516 | 0.0040 | 0.0752 | 0.0749 | 0.0725 | 0.0476 | 14.0 | 44.0 |
| 2014 | 252 | 0.8889 | 0.0833 | 0.0278 | 0.0544 | 0.0530 | 0.0461 | 0.0476 | 14.0 | 44.0 |
| 2015 | 253 | 0.7747 | 0.2213 | 0.0040 | 0.0651 | 0.0532 | 0.0430 | 0.0474 | 14.0 | 44.0 |
| 2016 | 252 | 0.8532 | 0.1468 | 0.0000 | 0.1036 | 0.1036 | 0.0920 | 0.0476 | 14.0 | 44.0 |
| 2017 | 251 | 0.9442 | 0.0478 | 0.0080 | 0.0992 | 0.0992 | 0.0923 | 0.0478 | 14.0 | 44.0 |
| 2018 | 252 | 0.6230 | 0.3690 | 0.0079 | 0.0512 | 0.0220 | 0.0171 | 0.0476 | 14.0 | 44.0 |
| 2019 | 252 | 0.8968 | 0.0833 | 0.0198 | 0.0685 | 0.0685 | 0.0712 | 0.0476 | 14.0 | 44.0 |
| 2020 | 253 | 0.7154 | 0.2767 | 0.0079 | 0.0674 | 0.0423 | 0.0362 | 0.0474 | 14.0 | 44.0 |
| 2021 | 252 | 0.9881 | 0.0119 | 0.0000 | 0.1000 | 0.1000 | 0.0999 | 0.0476 | 14.0 | 44.0 |
| 2022 | 251 | 0.7570 | 0.2430 | 0.0000 | 0.0392 | 0.0374 | 0.0397 | 0.0478 | 14.0 | 44.0 |
| 2023 | 250 | 0.9880 | 0.0120 | 0.0000 | 0.0754 | 0.0754 | 0.0795 | 0.0480 | 14.0 | 44.0 |
| 2024 | 252 | 0.8135 | 0.1865 | 0.0000 | 0.0611 | 0.0579 | 0.0453 | 0.0476 | 14.0 | 44.0 |
| 2025 | 251 | 0.8088 | 0.1912 | 0.0000 | 0.0705 | 0.0569 | 0.0516 | 0.0478 | 14.0 | 44.0 |
| 2026 | 155 | 0.8323 | 0.1677 | 0.0000 | 0.0557 | 0.0538 | 0.0534 | 0.0452 | 14.0 | 43.0 |

Full sample: contango on **83.53%** of sessions, backwardation on **16.02%**, flat
on 0.44%, median absolute slope **0.0697**. Excluding the 250 expiry sessions, on
which the front contract has zero days to expiry and carries its final settlement
value, the figures are essentially unchanged: contango 83.60%, backwardation
15.93%, median absolute slope 0.0690.

Most backwardated year: 2008 at 47.83%. Most persistently in contango: 2012,
2021 and 2023, each at 98.80%. No inference is drawn.

---

## 7. Artifacts written

| Path | Contents |
|---|---|
| `outputs/session-00b/methodology-notes.md` | S&P extract with quoted formulas, provenance, Cboe timestamp sources |
| `outputs/session-00b/maturity-diagnostics.csv` | step 3, by construction and year |
| `outputs/session-00b/validation-extended.csv` | step 4, three constructions against VIXY, VXX and VIXY NAV |
| `outputs/session-00b/timestamp-diagnostics.csv` | step 5, decile blocks plus the top-20 sessions |
| `outputs/session-00b/timestamp-top20-sessions.csv` | step 5, the twenty sessions on their own |
| `outputs/session-00b/term-structure.csv` | step 6 |
| `data/interim/vx-cm30-a.parquet` | construction A, 5,635 sessions |
| `data/interim/vx-cm30-b.parquet` | construction B, 5,635 sessions |
| `data/interim/vx-cm30-c.parquet` | construction C, 5,635 sessions |
| `data/interim/vixy-nav-proshares-s00b.parquet` | issuer NAV, 3,927 rows |
| `data/interim/vixy-yfinance-raw-s00b.parquet`, `vxx-yfinance-raw-s00b.parquet` | raw pulls |
| `data/interim/vx-term-structure-s00b.parquet` | per-session term structure |

Session 00A artifacts unmodified. Working tree left dirty. Nothing committed.
No construction selected and no sample start date recommended.
