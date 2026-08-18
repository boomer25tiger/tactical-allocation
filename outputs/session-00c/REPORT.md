# Session 00C, indicator relationships across the equity ETF panel

Measurement only. No decision is made, no parameter is selected, and no recommendation is given. No strategy return, Sharpe ratio, allocation, portfolio weight, or performance statistic is computed anywhere in this session. Every quantity below is a property of a single instrument's price series or a comparison between two such properties.

Informs decisions 6.9, 6.16, 6.7. Closes 1.12 and 2.20 by measurement. Addresses 6.20 and documents 6.8.

## Provenance

- yfinance version: **1.6.0**
- pull timestamp, UTC: **2026-08-17T17:19:47.051993+00:00**
- pull date, local: **2026-08-17**
- pandas 3.0.5, numpy 2.5.2, python 3.13.13
- request: `start=1995-01-01`, `auto_adjust=False`, `actions=True`
- tickers requested: **35**, failed: **0**
- raw pulls: `data/raw/etf/<TICKER>.parquet`, one file per ticker, SHA-256 and byte count in `outputs/session-00c/etf-manifest.csv`
- long panel: `data/interim/etf-panel.parquet`

### Pull integrity warning

The pull ran at 2026-08-17T17:19:47.051993+00:00, during the regular session of 2026-08-17. The final bar of every ticker is therefore a live intraday print, not a settled close. SPY volume on that bar is 12,650,704 against a trailing sixty-session median of 47,211,550, which confirms the bar is partial. Under decision 1.1 the pull is frozen and is not repeated, so this bar is now part of the frozen data. It is one session out of between 1,432 and 7,958 per ticker and moves no statistic in this report materially, but any later re-pull would not reproduce the recorded SHA-256 values, and the manifest hashes therefore certify this file set rather than a reproducible download.

## Step 1. Panel coverage

All 35 tickers returned data. No ticker failed to download and no ticker returned an empty frame.

| ticker | group | rows | first_date | last_date | n_dividends | n_splits | n_capital_gains | n_missing_close |
|---|---|---|---|---|---|---|---|---|
| IBB | additional_underlying | 6415 | 2001-02-12 | 2026-08-17 | 55 | 1 | 0 | 0 |
| XBI | additional_underlying | 5164 | 2006-02-06 | 2026-08-17 | 47 | 1 | 0 | 0 |
| IOO | benchmark | 6458 | 2000-12-08 | 2026-08-17 | 50 | 1 | 0 | 0 |
| QQQ | benchmark | 6902 | 1999-03-10 | 2026-08-17 | 89 | 1 | 0 | 0 |
| QQQE | benchmark | 3622 | 2012-03-21 | 2026-08-17 | 57 | 1 | 0 | 0 |
| SMH | benchmark | 6589 | 2000-06-05 | 2026-08-17 | 14 | 1 | 0 | 0 |
| SPY | benchmark | 7958 | 1995-01-03 | 2026-08-17 | 127 | 0 | 0 | 0 |
| VOOG | benchmark | 4008 | 2010-09-09 | 2026-08-17 | 63 | 1 | 0 | 0 |
| VOOV | benchmark | 4008 | 2010-09-09 | 2026-08-17 | 63 | 0 | 0 | 0 |
| VOX | benchmark | 5505 | 2004-09-29 | 2026-08-17 | 54 | 0 | 0 | 0 |
| VTV | benchmark | 5672 | 2004-01-30 | 2026-08-17 | 90 | 0 | 0 | 0 |
| XLF | benchmark | 6954 | 1998-12-22 | 2026-08-17 | 110 | 1 | 0 | 0 |
| XLK | benchmark | 6954 | 1998-12-22 | 2026-08-17 | 84 | 1 | 0 | 0 |
| XLP | benchmark | 6954 | 1998-12-22 | 2026-08-17 | 110 | 0 | 0 | 0 |
| XLY | benchmark | 6954 | 1998-12-22 | 2026-08-17 | 110 | 1 | 0 | 0 |
| AGG | defensive | 5757 | 2003-09-29 | 2026-08-17 | 274 | 0 | 0 | 0 |
| BIL | defensive | 4835 | 2007-05-30 | 2026-08-17 | 126 | 1 | 0 | 0 |
| BND | defensive | 4870 | 2007-04-10 | 2026-08-17 | 230 | 0 | 0 | 0 |
| BSV | defensive | 4870 | 2007-04-10 | 2026-08-17 | 232 | 0 | 0 | 0 |
| BTAL | defensive | 3753 | 2011-09-13 | 2026-08-17 | 8 | 0 | 0 | 0 |
| IEF | defensive | 6051 | 2002-07-30 | 2026-08-17 | 289 | 0 | 0 | 0 |
| KMLM | defensive | 1432 | 2020-12-02 | 2026-08-17 | 4 | 0 | 0 | 0 |
| TLT | defensive | 6051 | 2002-07-30 | 2026-08-17 | 287 | 0 | 0 | 0 |
| FAS | leveraged_inverse | 4461 | 2008-11-19 | 2026-08-17 | 40 | 5 | 0 | 0 |
| LABU | leveraged_inverse | 2822 | 2015-05-28 | 2026-08-17 | 17 | 2 | 0 | 0 |
| PSQ | leveraged_inverse | 5070 | 2006-06-21 | 2026-08-17 | 34 | 2 | 0 | 0 |
| QLD | leveraged_inverse | 5070 | 2006-06-21 | 2026-08-17 | 32 | 6 | 0 | 0 |
| SH | leveraged_inverse | 5070 | 2006-06-21 | 2026-08-17 | 35 | 2 | 0 | 0 |
| SOXL | leveraged_inverse | 4134 | 2010-03-11 | 2026-08-17 | 31 | 2 | 0 | 0 |
| SOXS | leveraged_inverse | 4134 | 2010-03-11 | 2026-08-17 | 25 | 10 | 0 | 0 |
| SPXL | leveraged_inverse | 4471 | 2008-11-05 | 2026-08-17 | 36 | 2 | 0 | 0 |
| SQQQ | leveraged_inverse | 4153 | 2010-02-11 | 2026-08-17 | 25 | 8 | 0 | 0 |
| TECL | leveraged_inverse | 4434 | 2008-12-30 | 2026-08-17 | 28 | 3 | 0 | 0 |
| TECS | leveraged_inverse | 4434 | 2008-12-30 | 2026-08-17 | 23 | 8 | 0 | 0 |
| TQQQ | leveraged_inverse | 4153 | 2010-02-11 | 2026-08-17 | 21 | 8 | 0 | 0 |

Capital gain distributions are zero for every ticker in the panel, so Yahoo's dividend stream is the entire recorded distribution stream and the total return construction loses nothing by using it alone.

The total return series is built as `r_t = (Close_t + Dividend_t) / Close_(t-1) - 1`, with reinvestment at the ex-date close per decision 1.11, on the split-adjusted close. Yahoo's adjusted close is carried separately in the same file.

Shortest histories, which bound every window that uses them: **KMLM** from 2020-12-02 (1,432 sessions), **LABU** from 2015-05-28 (2,822 sessions), **QQQE** from 2012-03-21 (3,622 sessions), **BTAL** from 2011-09-13 (3,753 sessions).

## Step 2. Distribution coverage diagnostic. Closes 1.12

Cumulative return from Yahoo's adjusted close against cumulative return from the raw close compounded with the dividend stream, over each ticker's full window. The flag threshold is an annualized difference above 10 basis points.

**No ticker in the panel is flagged.** The largest absolute annualized difference across all 35 tickers is **4.05 basis points** (KMLM), against a threshold of 10. The median absolute annualized difference is 0.205 basis points.

| ticker | n_sessions | n_distribution_events | cum_ret_adjclose | cum_ret_total_return | abs_diff_cum_adj_vs_tr | diff_ann_bp_adj_vs_tr | flag_gt_10bp | max_daily_ret_diff_bp |
|---|---|---|---|---|---|---|---|---|
| KMLM | 1432 | 4 | 0.4262 | 0.4293 | 0.003083 | -4.049 | False | 23.928 |
| FAS | 4461 | 40 | 14.0869 | 14.0149 | 0.072011 | 3.151 | False | 28.620 |
| SOXL | 4134 | 31 | 255.1863 | 254.7582 | 0.428108 | 1.430 | False | 12.781 |
| SH | 5070 | 35 | -0.9119 | -0.9121 | 0.000196 | 0.981 | False | 16.146 |
| QLD | 5070 | 32 | 94.7549 | 94.6173 | 0.137621 | 0.897 | False | 21.112 |
| VOOV | 4008 | 63 | 5.3721 | 5.3654 | 0.006643 | 0.737 | False | 2.701 |
| TQQQ | 4153 | 21 | 372.1335 | 372.4424 | 0.308953 | -0.720 | False | 3.669 |
| TECL | 4434 | 28 | 919.2347 | 919.9889 | 0.754205 | -0.686 | False | 26.888 |
| VOOG | 4008 | 63 | 11.1551 | 11.1480 | 0.007050 | 0.427 | False | 1.646 |
| SMH | 6589 | 14 | 13.2342 | 13.2221 | 0.012116 | 0.361 | False | 3.718 |
| SPXL | 4471 | 36 | 89.7216 | 89.7639 | 0.042276 | -0.339 | False | 9.839 |
| PSQ | 5070 | 34 | -0.9742 | -0.9742 | 0.000017 | 0.272 | False | 4.163 |
| VOX | 5505 | 54 | 5.0074 | 5.0043 | 0.003149 | 0.261 | False | 3.489 |
| TECS | 4434 | 23 | -1.0000 | -1.0000 | 0.000000 | -0.244 | False | 10.347 |
| XLF | 6954 | 110 | 4.2105 | 4.2074 | 0.003140 | 0.232 | False | 12.263 |
| SQQQ | 4153 | 25 | -1.0000 | -1.0000 | 0.000000 | 0.228 | False | 9.231 |
| SPY | 7958 | 127 | 28.2787 | 28.2976 | 0.018915 | -0.228 | False | 2.520 |
| IOO | 6458 | 50 | 5.8035 | 5.8068 | 0.003312 | -0.205 | False | 6.854 |
| BTAL | 3753 | 8 | -0.4415 | -0.4417 | 0.000170 | 0.197 | False | 2.210 |
| QQQE | 3622 | 57 | 6.2150 | 6.2166 | 0.001640 | -0.181 | False | 4.986 |
| XLY | 6954 | 110 | 11.4712 | 11.4740 | 0.002840 | -0.090 | False | 1.078 |
| BND | 4870 | 230 | 0.7637 | 0.7635 | 0.000283 | 0.085 | False | 0.405 |
| TLT | 6051 | 287 | 1.2846 | 1.2849 | 0.000343 | -0.065 | False | 1.289 |
| XLK | 6954 | 84 | 15.0176 | 15.0200 | 0.002386 | -0.060 | False | 1.312 |
| LABU | 2822 | 17 | -0.9058 | -0.9058 | 0.000007 | 0.054 | False | 2.158 |
| XBI | 5164 | 47 | 9.2838 | 9.2845 | 0.000711 | -0.038 | False | 0.869 |
| IEF | 6051 | 289 | 1.3066 | 1.3064 | 0.000159 | 0.030 | False | 1.186 |
| BIL | 4835 | 126 | 0.3008 | 0.3007 | 0.000064 | 0.026 | False | 0.031 |
| AGG | 5757 | 274 | 0.9825 | 0.9826 | 0.000080 | -0.018 | False | 0.660 |
| QQQ | 6902 | 89 | 15.9850 | 15.9856 | 0.000560 | -0.013 | False | 0.709 |
| VTV | 5672 | 90 | 7.2869 | 7.2866 | 0.000225 | 0.013 | False | 5.670 |
| XLP | 6954 | 110 | 5.1024 | 5.1022 | 0.000191 | 0.012 | False | 1.991 |
| SOXS | 4134 | 25 | -1.0000 | -1.0000 | 0.000000 | -0.008 | False | 27.465 |
| IBB | 6415 | 55 | 5.1123 | 5.1123 | 0.000035 | 0.002 | False | 0.948 |
| BSV | 4870 | 232 | 0.6114 | 0.6114 | 0.000001 | 0.000 | False | 0.743 |

### The six instruments where distribution coverage matters most

| ticker | n_sessions | n_distribution_events | cum_ret_adjclose | cum_ret_total_return | abs_diff_cum_adj_vs_tr | diff_ann_bp_adj_vs_tr | flag_gt_10bp | max_daily_ret_diff_bp | total_distributions_per_share |
|---|---|---|---|---|---|---|---|---|---|
| BND | 4870 | 230 | 0.7637 | 0.7635 | 0.000283 | 0.085 | False | 0.405 | 48.0960 |
| TLT | 6051 | 287 | 1.2846 | 1.2849 | 0.000343 | -0.065 | False | 1.289 | 84.4460 |
| IEF | 6051 | 289 | 1.3066 | 1.3064 | 0.000159 | 0.030 | False | 1.186 | 66.5710 |
| BIL | 4835 | 126 | 0.3008 | 0.3007 | 0.000064 | 0.026 | False | 0.031 | 24.1390 |
| AGG | 5757 | 274 | 0.9825 | 0.9826 | 0.000080 | -0.018 | False | 0.660 | 76.4070 |
| BSV | 4870 | 232 | 0.6114 | 0.6114 | 0.000001 | 0.000 | False | 0.743 | 34.9410 |

These are the highest-distribution-count instruments in the panel, between 126 and 289 events each, and they are the tightest in it. Every one agrees to under a tenth of a basis point per annum. BSV agrees to 0.0004 basis points over 4,870 sessions and 232 distributions.

### The literal price-plus-summed-distributions construction

Decision 1.12 as written compares against price return plus summed distributions. That construction does not reinvest, so it is not comparable to an adjusted close over long windows and diverges by an amount that grows with yield and horizon rather than by a data defect. It is carried in the CSV as `cum_ret_price_plus_sum_dist` and `diff_ann_bp_adj_vs_simple` and is not the basis of the flag. For the six focus instruments the two constructions differ as follows.

| ticker | cum_ret_adjclose | cum_ret_total_return | cum_ret_price_plus_sum_dist | diff_ann_bp_adj_vs_tr | diff_ann_bp_adj_vs_simple |
|---|---|---|---|---|---|
| BND | 0.7637 | 0.7635 | 0.5990 | 0.085 | 52.1 |
| TLT | 1.2846 | 1.2849 | 1.0361 | -0.065 | 49.5 |
| IEF | 1.3066 | 1.3064 | 0.9504 | 0.030 | 72.1 |
| BIL | 0.3008 | 0.3007 | 0.2629 | 0.026 | 15.6 |
| AGG | 0.9825 | 0.9826 | 0.7003 | -0.018 | 69.0 |
| BSV | 0.6114 | 0.6114 | 0.5011 | 0.000 | 37.5 |

The last column is the reason the compounded construction is the one carrying the flag: on TLT the non-reinvesting construction sits 50 basis points per annum away from the adjusted close purely through the absence of reinvestment.

### Adjusted open, decision 1.5

`AdjOpen = Open x (AdjClose / Close)` reproduces the raw open-to-close ratio for **all 35 tickers**. The largest relative error anywhere in the panel is **2.429e-16**, which is one unit in the last place of double precision. Failures at a 1e-9 relative tolerance: **0**. Failures at 1e-12: **0**.

### Adjustment factor behaviour

The ratio `AdjClose / Close` moves on a recorded dividend or split and on nothing else. Across the whole panel there are **0** sessions where the factor moved by more than one part in 100,000 without a recorded action, and **70** sessions carrying a recorded action with no factor move. Yahoo's adjustment is internally consistent with the actions it publishes.

### What the diagnostic cannot see, and one place it matters

The test compares two constructions that are both derived from the same Yahoo actions feed. If the feed omits a distribution, both sides omit it identically and the difference stays at zero. The test measures internal consistency, not completeness. Tickers whose recorded distribution stream begins more than three years after their first bar:

| ticker | first_date | first_distribution_date | years_listing_to_first_distribution | n_distribution_events | diff_ann_bp_adj_vs_tr |
|---|---|---|---|---|---|
| SMH | 2000-06-05 | 2012-12-24 | 12.55 | 14 | 0.361 |
| TECS | 2008-12-30 | 2018-03-20 | 9.22 | 23 | -0.244 |
| SQQQ | 2010-02-11 | 2017-12-26 | 7.87 | 25 | 0.228 |
| IBB | 2001-02-12 | 2005-12-23 | 4.86 | 55 | 0.002 |
| QQQ | 1999-03-10 | 2003-12-24 | 4.79 | 89 | -0.013 |
| TQQQ | 2010-02-11 | 2014-06-25 | 4.37 | 21 | -0.720 |

Most of these are economically plausible rather than defective. QQQ's first recorded distribution in December 2003 is consistent with the Nasdaq-100 paying almost nothing until Microsoft initiated its dividend that year. TQQQ, SQQQ and TECS are leveraged and inverse funds whose distributions come from collateral income, which was near zero through the period concerned. IBB is a low-yield biotech index fund. **SMH is different, and is treated in Step 3.**

## Step 3. SMH continuity at the 2011 conversion. Closes 2.20

Full inspection in `outputs/session-00c/smh-continuity.md`. Summary below.

- First date returned: **2000-06-05**, 6,589 sessions to 2026-08-17. yfinance returns the HOLDRS-era history; the series is not truncated at the conversion.
- No missing session relative to the SPY trading calendar over the common window, in either direction.
- No single-day absolute total return above 25 percent anywhere in the history. The largest is 17.16 percent, on 2025-04-09, nowhere near the conversion.
- No split and no distribution within 200 calendar days either side of the December 2011 conversion. The only recorded split is 2023-05-05.
- Daily return dispersion is 2.080 percent in the 60 sessions before the boundary and 1.231 percent in the 60 after. The fall is large but is not evidence of a splice: the pre-boundary window covers October to December 2011, the tail of the eurozone volatility episode, and the post-boundary window covers the calm of early 2012. No single session at the boundary carries an outsized move.

**Verdict: stitched on price, discontinuous on distributions.**

The price series crosses the conversion with no detectable break. The distribution series does not. yfinance records **zero distributions across the entire HOLDRS era**, 2000-06-05 to 2012-12-23, and the first of the 14 recorded distributions falls on 2012-12-24, 12.55 years after the first bar. The HOLDRS was a grantor trust that passed constituent dividends through to holders, so those distributions occurred and are absent from the feed. SMH total return before December 2012 is a price return wearing a total return label, and Step 2 cannot detect this because Yahoo's adjusted close omits exactly the same cash flows.

A second marker sits at the boundary and is consistent with a vehicle change rather than a price break: median daily volume falls from 15,201,800 in the 60 sessions before to 2,871,700 in the 60 after, a ratio of 0.19.

Nothing was adjusted. The economic discontinuity in the underlying vehicle, a fixed unrebalanced grantor-trust basket with a shrinking constituent count before the conversion against a rebalanced index fund after it, produces no price artefact and cannot be detected by any test in this session.

## Step 4. RSI divergence, long leveraged fund against underlying. Informs 6.9

Wilder RSI, alpha = 1/n per decision 1.6, on total return series, at periods 7, 14 and 28. Seven long leveraged pairs. Signed difference is RSI(leveraged) minus RSI(underlying).

### Pooled over each pair's full common window

| pair | rsi_period | n_sessions | first_date | mean_abs_diff | p95_abs_diff | p99_abs_diff | max_abs_diff | mean_signed_diff | correlation |
|---|---|---|---|---|---|---|---|---|---|
| FAS/XLF | 7 | 4454 | 2008-12-01 | 2.151 | 6.806 | 11.276 | 23.259 | -0.433 | 0.9818 |
| FAS/XLF | 14 | 4447 | 2008-12-10 | 1.705 | 4.776 | 7.976 | 15.056 | -0.592 | 0.9810 |
| FAS/XLF | 28 | 4433 | 2008-12-31 | 1.412 | 3.642 | 5.762 | 8.148 | -0.727 | 0.9786 |
| LABU/XBI | 7 | 2815 | 2015-06-08 | 1.546 | 3.009 | 4.431 | 9.945 | -1.464 | 0.9978 |
| LABU/XBI | 14 | 2808 | 2015-06-17 | 1.641 | 3.038 | 4.289 | 7.911 | -1.596 | 0.9966 |
| LABU/XBI | 28 | 2794 | 2015-07-08 | 1.702 | 3.194 | 4.395 | 5.742 | -1.670 | 0.9939 |
| QLD/QQQ | 7 | 5063 | 2006-06-30 | 0.802 | 1.966 | 3.551 | 15.868 | -0.641 | 0.9986 |
| QLD/QQQ | 14 | 5056 | 2006-07-12 | 0.752 | 1.669 | 2.619 | 7.325 | -0.686 | 0.9988 |
| QLD/QQQ | 28 | 5042 | 2006-08-01 | 0.762 | 1.612 | 2.646 | 4.298 | -0.736 | 0.9983 |
| SOXL/SMH | 7 | 4127 | 2010-03-22 | 2.847 | 7.723 | 11.168 | 23.133 | -1.622 | 0.9780 |
| SOXL/SMH | 14 | 4120 | 2010-03-31 | 2.371 | 5.981 | 8.291 | 14.121 | -1.720 | 0.9771 |
| SOXL/SMH | 28 | 4106 | 2010-04-21 | 2.103 | 4.952 | 6.500 | 8.113 | -1.756 | 0.9739 |
| SPXL/SPY | 7 | 4464 | 2008-11-14 | 1.139 | 2.470 | 4.023 | 15.837 | -0.987 | 0.9980 |
| SPXL/SPY | 14 | 4457 | 2008-11-25 | 1.149 | 2.243 | 4.552 | 11.925 | -1.074 | 0.9968 |
| SPXL/SPY | 28 | 4443 | 2008-12-16 | 1.154 | 2.255 | 4.281 | 5.734 | -1.124 | 0.9958 |
| TECL/XLK | 7 | 4427 | 2009-01-09 | 1.418 | 3.680 | 6.583 | 14.141 | -1.043 | 0.9959 |
| TECL/XLK | 14 | 4420 | 2009-01-21 | 1.306 | 2.922 | 4.713 | 7.334 | -1.125 | 0.9959 |
| TECL/XLK | 28 | 4406 | 2009-02-10 | 1.274 | 2.637 | 3.999 | 5.608 | -1.159 | 0.9941 |
| TQQQ/QQQ | 7 | 4146 | 2010-02-23 | 1.067 | 2.204 | 3.798 | 12.558 | -0.919 | 0.9984 |
| TQQQ/QQQ | 14 | 4139 | 2010-03-04 | 1.127 | 2.174 | 4.075 | 16.677 | -0.960 | 0.9961 |
| TQQQ/QQQ | 28 | 4125 | 2010-03-24 | 1.166 | 2.177 | 4.277 | 16.743 | -0.979 | 0.9900 |

RSI is invariant to a constant multiple on returns, so a frictionless constant-leverage fund would show a difference of exactly zero. The observed difference is the footprint of daily reset, financing, fees and variance drag. It is small in level, between 0.75 and 2.85 RSI points on average, and correlations run from 0.974 to 0.999. The signed difference is negative for **every pair at every period**, ranging from -0.43 to -1.76, which is the expected direction: drag pushes the leveraged fund's RSI below its underlying's.

### Crossing agreement, pooled

| pair | rsi_period | n_sessions | agree_70 | n_disagree_70 | agree_80 | n_disagree_80 | agree_30 | n_disagree_30 | agree_20 | n_disagree_20 |
|---|---|---|---|---|---|---|---|---|---|---|
| FAS/XLF | 7 | 4454 | 0.9650 | 156 | 0.9847 | 68 | 0.9820 | 80 | 0.9951 | 22 |
| FAS/XLF | 14 | 4447 | 0.9798 | 90 | 0.9971 | 13 | 0.9951 | 22 | 0.9993 | 3 |
| FAS/XLF | 28 | 4433 | 0.9932 | 30 | 1.0000 | 0 | 0.9989 | 5 | 1.0000 | 0 |
| LABU/XBI | 7 | 2815 | 0.9794 | 58 | 0.9982 | 5 | 0.9872 | 36 | 0.9972 | 8 |
| LABU/XBI | 14 | 2808 | 0.9961 | 11 | 0.9989 | 3 | 0.9947 | 15 | 1.0000 | 0 |
| LABU/XBI | 28 | 2794 | 0.9986 | 4 | 1.0000 | 0 | 0.9996 | 1 | 1.0000 | 0 |
| QLD/QQQ | 7 | 5063 | 0.9850 | 76 | 0.9931 | 35 | 0.9951 | 25 | 0.9976 | 12 |
| QLD/QQQ | 14 | 5056 | 0.9915 | 43 | 0.9994 | 3 | 0.9966 | 17 | 0.9998 | 1 |
| QLD/QQQ | 28 | 5042 | 0.9962 | 19 | 1.0000 | 0 | 1.0000 | 0 | 1.0000 | 0 |
| SOXL/SMH | 7 | 4127 | 0.9494 | 209 | 0.9818 | 75 | 0.9741 | 107 | 0.9956 | 18 |
| SOXL/SMH | 14 | 4120 | 0.9675 | 134 | 0.9956 | 18 | 0.9947 | 22 | 1.0000 | 0 |
| SOXL/SMH | 28 | 4106 | 0.9900 | 41 | 1.0000 | 0 | 0.9998 | 1 | 1.0000 | 0 |
| SPXL/SPY | 7 | 4464 | 0.9805 | 87 | 0.9899 | 45 | 0.9915 | 38 | 0.9982 | 8 |
| SPXL/SPY | 14 | 4457 | 0.9829 | 76 | 0.9987 | 6 | 0.9964 | 16 | 0.9996 | 2 |
| SPXL/SPY | 28 | 4443 | 0.9964 | 16 | 0.9998 | 1 | 1.0000 | 0 | 1.0000 | 0 |
| TECL/XLK | 7 | 4427 | 0.9781 | 97 | 0.9853 | 65 | 0.9853 | 65 | 0.9982 | 8 |
| TECL/XLK | 14 | 4420 | 0.9839 | 71 | 0.9962 | 17 | 0.9977 | 10 | 1.0000 | 0 |
| TECL/XLK | 28 | 4406 | 0.9961 | 17 | 1.0000 | 0 | 1.0000 | 0 | 1.0000 | 0 |
| TQQQ/QQQ | 7 | 4146 | 0.9826 | 72 | 0.9932 | 28 | 0.9928 | 30 | 0.9990 | 4 |
| TQQQ/QQQ | 14 | 4139 | 0.9894 | 44 | 0.9961 | 16 | 0.9983 | 7 | 0.9998 | 1 |
| TQQQ/QQQ | 28 | 4125 | 0.9910 | 37 | 0.9983 | 7 | 1.0000 | 0 | 1.0000 | 0 |

At the canonical period 14 and the canonical tier-one threshold 70, agreement runs from 96.75 percent (SOXL against SMH) to 99.15 percent (QLD against QQQ). The disagreement counts are the operative number: between 43 and 134 sessions per pair over 4,100 to 5,100 sessions.

### By year, canonical period 14

Mean absolute RSI difference:

| window | FAS/XLF | LABU/XBI | QLD/QQQ | SOXL/SMH | SPXL/SPY | TECL/XLK | TQQQ/QQQ |
|---|---|---|---|---|---|---|---|
| 2006 |  |  | 1.427 |  |  |  |  |
| 2007 |  |  | 1.104 |  |  |  |  |
| 2008 | 3.457 |  | 1.500 |  | 7.369 |  |  |
| 2009 | 2.261 |  | 0.760 |  | 1.331 | 1.320 |  |
| 2010 | 1.228 |  | 0.532 | 2.180 | 0.767 | 1.506 | 1.993 |
| 2011 | 1.444 |  | 0.576 | 3.215 | 1.173 | 1.910 | 1.021 |
| 2012 | 0.890 |  | 0.415 | 2.434 | 1.012 | 1.826 | 0.678 |
| 2013 | 1.066 |  | 0.365 | 2.402 | 0.598 | 0.760 | 0.545 |
| 2014 | 1.204 |  | 0.423 | 2.418 | 0.612 | 0.759 | 0.670 |
| 2015 | 0.912 | 1.924 | 0.509 | 2.123 | 0.863 | 0.911 | 0.861 |
| 2016 | 1.754 | 1.673 | 0.504 | 1.970 | 0.728 | 0.807 | 0.787 |
| 2017 | 2.483 | 1.084 | 0.506 | 1.885 | 0.752 | 0.858 | 0.661 |
| 2018 | 2.554 | 1.524 | 0.731 | 1.247 | 1.170 | 1.294 | 1.176 |
| 2019 | 2.883 | 1.455 | 0.695 | 1.886 | 1.146 | 1.128 | 1.053 |
| 2020 | 2.892 | 1.913 | 0.782 | 2.352 | 1.569 | 1.819 | 1.494 |
| 2021 | 1.092 | 1.354 | 0.467 | 1.490 | 0.600 | 0.868 | 0.781 |
| 2022 | 1.248 | 2.109 | 0.807 | 2.034 | 1.219 | 1.449 | 1.527 |
| 2023 | 1.721 | 1.686 | 1.030 | 2.739 | 1.535 | 1.481 | 1.490 |
| 2024 | 1.613 | 1.756 | 1.100 | 4.283 | 1.871 | 1.690 | 1.609 |
| 2025 | 1.791 | 1.726 | 1.099 | 3.219 | 1.786 | 1.689 | 1.677 |
| 2026 | 1.458 | 1.591 | 0.849 | 2.403 | 1.440 | 1.509 | 1.359 |

Agreement at threshold 70:

| window | FAS/XLF | LABU/XBI | QLD/QQQ | SOXL/SMH | SPXL/SPY | TECL/XLK | TQQQ/QQQ |
|---|---|---|---|---|---|---|---|
| 2006 |  |  | 1.0000 |  |  |  |  |
| 2007 |  |  | 0.9761 |  |  |  |  |
| 2008 | 1.0000 |  | 0.9921 |  | 1.0000 |  |  |
| 2009 | 0.9960 |  | 0.9960 |  | 0.9960 | 0.9500 |  |
| 2010 | 0.9881 |  | 1.0000 | 0.9844 | 0.9802 | 0.9762 | 0.9621 |
| 2011 | 0.9921 |  | 1.0000 | 0.9563 | 0.9841 | 0.9921 | 0.9960 |
| 2012 | 0.9960 |  | 0.9960 | 0.9840 | 0.9600 | 0.9800 | 0.9960 |
| 2013 | 0.9683 |  | 0.9960 | 0.9484 | 0.9921 | 0.9960 | 0.9960 |
| 2014 | 0.9683 |  | 0.9881 | 0.9325 | 0.9921 | 0.9921 | 0.9881 |
| 2015 | 1.0000 | 1.0000 | 0.9960 | 0.9921 | 0.9960 | 0.9960 | 1.0000 |
| 2016 | 0.9802 | 1.0000 | 1.0000 | 0.9206 | 0.9960 | 0.9960 | 1.0000 |
| 2017 | 0.9402 | 0.9960 | 0.9801 | 0.9681 | 0.9801 | 0.9761 | 0.9880 |
| 2018 | 0.9920 | 1.0000 | 0.9801 | 1.0000 | 1.0000 | 0.9880 | 0.9801 |
| 2019 | 0.9246 | 0.9841 | 0.9960 | 0.9722 | 0.9563 | 0.9802 | 0.9921 |
| 2020 | 0.9881 | 0.9960 | 0.9921 | 0.9921 | 0.9960 | 0.9921 | 0.9960 |
| 2021 | 0.9762 | 1.0000 | 1.0000 | 0.9881 | 1.0000 | 1.0000 | 1.0000 |
| 2022 | 1.0000 | 1.0000 | 1.0000 | 0.9960 | 1.0000 | 1.0000 | 1.0000 |
| 2023 | 0.9720 | 1.0000 | 0.9920 | 0.9640 | 0.9520 | 0.9640 | 0.9920 |
| 2024 | 0.9762 | 0.9841 | 0.9841 | 0.9603 | 0.9484 | 0.9881 | 0.9802 |
| 2025 | 0.9880 | 0.9960 | 0.9680 | 0.9280 | 0.9800 | 0.9560 | 0.9640 |
| 2026 | 0.9936 | 1.0000 | 0.9936 | 0.9615 | 0.9808 | 0.9872 | 0.9808 |

Annualized standard deviation of the underlying's daily total return, carried so the divergence can be read against volatility as well as against the rate environment:

| window | FAS/XLF | LABU/XBI | QLD/QQQ | SOXL/SMH | SPXL/SPY | TECL/XLK | TQQQ/QQQ |
|---|---|---|---|---|---|---|---|
| 2006 |  |  | 0.146 |  |  |  |  |
| 2007 |  |  | 0.182 |  |  |  |  |
| 2008 | 0.691 |  | 0.399 |  | 0.448 |  |  |
| 2009 | 0.648 |  | 0.256 |  | 0.266 | 0.250 |  |
| 2010 | 0.254 |  | 0.193 | 0.263 | 0.179 | 0.187 | 0.195 |
| 2011 | 0.333 |  | 0.237 | 0.276 | 0.230 | 0.226 | 0.237 |
| 2012 | 0.175 |  | 0.153 | 0.204 | 0.127 | 0.148 | 0.153 |
| 2013 | 0.143 |  | 0.122 | 0.165 | 0.111 | 0.115 | 0.122 |
| 2014 | 0.128 |  | 0.138 | 0.176 | 0.112 | 0.126 | 0.138 |
| 2015 | 0.176 | 0.406 | 0.179 | 0.218 | 0.154 | 0.177 | 0.179 |
| 2016 | 0.187 | 0.391 | 0.162 | 0.220 | 0.131 | 0.153 | 0.162 |
| 2017 | 0.131 | 0.223 | 0.103 | 0.162 | 0.067 | 0.104 | 0.103 |
| 2018 | 0.195 | 0.309 | 0.229 | 0.280 | 0.170 | 0.233 | 0.229 |
| 2019 | 0.155 | 0.264 | 0.162 | 0.257 | 0.125 | 0.180 | 0.162 |
| 2020 | 0.453 | 0.409 | 0.356 | 0.442 | 0.334 | 0.402 | 0.356 |
| 2021 | 0.189 | 0.319 | 0.182 | 0.303 | 0.130 | 0.193 | 0.182 |
| 2022 | 0.245 | 0.463 | 0.321 | 0.426 | 0.242 | 0.328 | 0.321 |
| 2023 | 0.162 | 0.284 | 0.179 | 0.275 | 0.131 | 0.185 | 0.179 |
| 2024 | 0.142 | 0.255 | 0.180 | 0.349 | 0.126 | 0.222 | 0.180 |
| 2025 | 0.191 | 0.274 | 0.236 | 0.380 | 0.195 | 0.276 | 0.236 |
| 2026 | 0.154 | 0.295 | 0.216 | 0.439 | 0.137 | 0.292 | 0.216 |

Periods 7 and 28, and the remaining thresholds, by year, are in `rsi-leveraged-divergence.csv`.

### The rate-environment expectation

The session prompt states that financing drag varies with the rate environment and that the divergence should widen when rates are high. **The measurement supports this.** QLD against QQQ is the cleanest test in the panel: it is the longest leveraged history, it spans two full rate cycles, and at 2x it carries the least variance drag, so the financing component is least contaminated.

| window | n_sessions | mean_abs_diff | mean_signed_diff | underlying_ann_ret_sd |
|---|---|---|---|---|
| 2006 | 120 | 1.4272 | -1.4239 | 0.1460 |
| 2007 | 251 | 1.1041 | -0.9241 | 0.1816 |
| 2008 | 253 | 1.4995 | -1.2955 | 0.3993 |
| 2009 | 252 | 0.7603 | -0.4474 | 0.2556 |
| 2010 | 252 | 0.5318 | -0.3499 | 0.1930 |
| 2011 | 252 | 0.5759 | -0.5169 | 0.2370 |
| 2012 | 250 | 0.4152 | -0.2894 | 0.1533 |
| 2013 | 252 | 0.3650 | -0.2683 | 0.1223 |
| 2014 | 252 | 0.4229 | -0.4162 | 0.1383 |
| 2015 | 252 | 0.5094 | -0.4952 | 0.1787 |
| 2016 | 252 | 0.5041 | -0.4878 | 0.1617 |
| 2017 | 251 | 0.5063 | -0.4885 | 0.1032 |
| 2018 | 251 | 0.7309 | -0.7292 | 0.2289 |
| 2019 | 252 | 0.6954 | -0.6906 | 0.1619 |
| 2020 | 253 | 0.7817 | -0.7467 | 0.3563 |
| 2021 | 252 | 0.4672 | -0.4383 | 0.1822 |
| 2022 | 251 | 0.8068 | -0.7774 | 0.3215 |
| 2023 | 250 | 1.0299 | -1.0299 | 0.1787 |
| 2024 | 252 | 1.1004 | -1.0992 | 0.1801 |
| 2025 | 250 | 1.0988 | -1.0984 | 0.2360 |
| 2026 | 156 | 0.8494 | -0.8393 | 0.2159 |

Divergence sits near 1.1 to 1.4 RSI points in the high-rate years 2006, 2007, 2023, 2024 and 2025, and near 0.37 to 0.58 in the zero-rate years 2010 to 2015 and 2021. Volatility confounds the raw comparison, so the controlled version is a pair of years with almost identical underlying dispersion and opposite rate regimes:

| year | QQQ annualized return sd | approximate policy rate | mean absolute RSI difference |
|---|---|---|---|
| 2011 | 0.237 | near zero | 0.576 |
| 2025 | 0.236 | around 4 percent | 1.099 |

At matched volatility the divergence roughly doubles between the zero-rate and the high-rate year. The reverse control points the same way: 2020 carries the second-highest volatility in the sample, 0.356, at a zero policy rate, and produces a divergence of 0.782, lower than 2023 at 0.179 volatility and a 5 percent rate, which produces 1.030.

## Step 5. RSI on the inverse fund against 100 minus RSI on the underlying. Addresses 6.20

The proposition under test is RSI(inverse) = 100 - RSI(underlying). Signed difference is RSI(inverse) minus [100 - RSI(underlying)]. Correlation is between those same two series. Crossing agreement tests whether RSI(inverse) above 70 coincides with RSI(underlying) below 30, and correspondingly at 80, 30 and 20.

| pair | rsi_period | n_sessions | mean_abs_diff | p95_abs_diff | p99_abs_diff | max_abs_diff | mean_signed_diff | correlation |
|---|---|---|---|---|---|---|---|---|
| PSQ/QQQ | 7 | 5063 | 1.160 | 3.035 | 5.128 | 14.980 | -0.137 | 0.9956 |
| PSQ/QQQ | 14 | 5056 | 1.062 | 2.639 | 3.912 | 6.725 | -0.195 | 0.9938 |
| PSQ/QQQ | 28 | 5042 | 1.048 | 2.620 | 3.652 | 5.120 | -0.218 | 0.9882 |
| SH/SPY | 7 | 5063 | 1.378 | 4.022 | 6.713 | 16.292 | 0.309 | 0.9931 |
| SH/SPY | 14 | 5056 | 1.257 | 3.544 | 5.900 | 10.550 | 0.234 | 0.9891 |
| SH/SPY | 28 | 5042 | 1.199 | 3.290 | 5.227 | 7.523 | 0.175 | 0.9806 |
| SOXS/SMH | 7 | 4127 | 3.160 | 8.226 | 13.958 | 48.666 | -1.609 | 0.9659 |
| SOXS/SMH | 14 | 4120 | 2.763 | 6.509 | 17.466 | 32.352 | -1.805 | 0.9428 |
| SOXS/SMH | 28 | 4106 | 2.412 | 5.214 | 12.442 | 28.183 | -1.755 | 0.9298 |
| SQQQ/QQQ | 7 | 4146 | 1.289 | 3.093 | 5.308 | 15.113 | -0.932 | 0.9964 |
| SQQQ/QQQ | 14 | 4139 | 1.363 | 3.172 | 6.665 | 16.868 | -1.048 | 0.9923 |
| SQQQ/QQQ | 28 | 4125 | 1.465 | 3.185 | 6.438 | 18.111 | -1.121 | 0.9787 |
| TECS/XLK | 7 | 4427 | 1.631 | 4.352 | 7.701 | 15.809 | -1.131 | 0.9933 |
| TECS/XLK | 14 | 4420 | 1.547 | 3.935 | 6.023 | 9.354 | -1.209 | 0.9911 |
| TECS/XLK | 28 | 4406 | 1.554 | 3.752 | 5.577 | 8.075 | -1.233 | 0.9843 |

Crossing agreement:

| pair | rsi_period | n_sessions | agree_70 | n_disagree_70 | agree_80 | n_disagree_80 | agree_30 | n_disagree_30 | agree_20 | n_disagree_20 |
|---|---|---|---|---|---|---|---|---|---|---|
| PSQ/QQQ | 7 | 5063 | 0.9911 | 45 | 0.9974 | 13 | 0.9757 | 123 | 0.9858 | 72 |
| PSQ/QQQ | 14 | 5056 | 0.9949 | 26 | 0.9998 | 1 | 0.9808 | 97 | 0.9980 | 10 |
| PSQ/QQQ | 28 | 5042 | 0.9996 | 2 | 1.0000 | 0 | 0.9923 | 39 | 1.0000 | 0 |
| SH/SPY | 7 | 5063 | 0.9909 | 46 | 0.9962 | 19 | 0.9641 | 182 | 0.9850 | 76 |
| SH/SPY | 14 | 5056 | 0.9966 | 17 | 0.9996 | 2 | 0.9721 | 141 | 0.9986 | 7 |
| SH/SPY | 28 | 5042 | 0.9996 | 2 | 1.0000 | 0 | 0.9954 | 23 | 1.0000 | 0 |
| SOXS/SMH | 7 | 4127 | 0.9767 | 96 | 0.9956 | 18 | 0.9481 | 214 | 0.9750 | 103 |
| SOXS/SMH | 14 | 4120 | 0.9954 | 19 | 0.9993 | 3 | 0.9583 | 172 | 0.9881 | 49 |
| SOXS/SMH | 28 | 4106 | 0.9990 | 4 | 1.0000 | 0 | 0.9713 | 118 | 1.0000 | 0 |
| SQQQ/QQQ | 7 | 4146 | 0.9928 | 30 | 0.9978 | 9 | 0.9812 | 78 | 0.9887 | 47 |
| SQQQ/QQQ | 14 | 4139 | 0.9978 | 9 | 1.0000 | 0 | 0.9816 | 76 | 0.9915 | 35 |
| SQQQ/QQQ | 28 | 4125 | 0.9993 | 3 | 1.0000 | 0 | 0.9806 | 80 | 0.9959 | 17 |
| TECS/XLK | 7 | 4427 | 0.9896 | 46 | 0.9980 | 9 | 0.9763 | 105 | 0.9808 | 85 |
| TECS/XLK | 14 | 4420 | 0.9980 | 9 | 0.9998 | 1 | 0.9760 | 106 | 0.9955 | 20 |
| TECS/XLK | 28 | 4406 | 0.9991 | 4 | 1.0000 | 0 | 0.9898 | 45 | 1.0000 | 0 |

The identity holds closely but not exactly. Mean absolute difference runs from 1.05 to 3.16 RSI points and correlations from 0.930 to 0.996. PSQ and SH, the two unlevered inverses, are the tightest: 1.06 and 1.26 RSI points at period 14.

The agreement rates are asymmetric, and the asymmetry is systematic. At period 14 every pair agrees more often on the overbought side of the inverse than on the oversold side. SH against SPY agrees on 99.66 percent of sessions at threshold 70 but only 97.21 percent at threshold 30, 141 disagreement sessions against 17. SOXS against SMH is 99.54 percent against 95.83 percent, 19 sessions against 172. Testing whether the inverse is oversold is a materially worse proxy for the underlying being overbought than the reverse.

### Inverse against inverse, directly. The specific question in 6.20

Decision 6.20 names PSQ and SH. The comparison below is direct, with no 100-minus transform, and asks whether one inverse carries information the other does not.

| pair | rsi_period | n_sessions | mean_abs_diff | p95_abs_diff | max_abs_diff | correlation | agree_70 | n_disagree_70 | agree_30 | n_disagree_30 |
|---|---|---|---|---|---|---|---|---|---|---|
| PSQ/SH | 7 | 5063 | 5.743 | 15.944 | 38.909 | 0.8912 | 0.9571 | 217 | 0.8673 | 672 |
| PSQ/SH | 14 | 5056 | 4.048 | 10.851 | 23.504 | 0.8918 | 0.9877 | 62 | 0.9163 | 423 |
| PSQ/SH | 28 | 5042 | 2.802 | 7.411 | 14.125 | 0.8904 | 0.9984 | 8 | 0.9833 | 84 |
| PSQ/SQQQ | 7 | 4146 | 0.916 | 2.064 | 13.620 | 0.9982 | 0.9957 | 18 | 0.9829 | 71 |
| PSQ/SQQQ | 14 | 4139 | 0.890 | 1.869 | 16.165 | 0.9961 | 0.9993 | 3 | 0.9867 | 55 |
| PSQ/SQQQ | 28 | 4125 | 0.930 | 1.829 | 17.860 | 0.9862 | 0.9998 | 1 | 0.9891 | 45 |
| SH/SQQQ | 7 | 4146 | 5.686 | 15.636 | 39.075 | 0.8947 | 0.9614 | 160 | 0.8625 | 570 |
| SH/SQQQ | 14 | 4139 | 4.086 | 10.925 | 22.580 | 0.8922 | 0.9930 | 29 | 0.9017 | 407 |
| SH/SQQQ | 28 | 4125 | 2.931 | 7.704 | 18.951 | 0.8776 | 0.9988 | 5 | 0.9784 | 89 |

PSQ and SH are **not** duplicates of each other. At period 14 they differ by 4.05 RSI points on average with a correlation of 0.892, and they disagree on 423 of 5,056 sessions at threshold 30. PSQ and SQQQ **are** near-duplicates: 0.89 RSI points and a correlation of 0.996, which is expected since both track QQQ at different multiples. The separation between PSQ and SH is the separation between QQQ and SPY, not anything contributed by the inverse wrappers.

## Step 6. SMA crossover divergence. Informs 6.16

Simple moving averages at 20, 50, 100, 150, 200 and 250 sessions on total return series. Offsets are leveraged crossover position minus underlying crossover position in sessions, so a positive offset means the leveraged series crossed later. Crossovers are matched one to one, nearest first by absolute offset, within a 60-session window; unmatched events are counted separately.

### Agreement on whether price sits above the average

| sma_length | FAS/XLF | LABU/XBI | QLD/QQQ | SOXL/SMH | SPXL/SPY | TECL/XLK | TQQQ/QQQ |
|---|---|---|---|---|---|---|---|
| 20 | 0.9529 | 0.9590 | 0.9814 | 0.9337 | 0.9780 | 0.9692 | 0.9722 |
| 50 | 0.9461 | 0.9347 | 0.9753 | 0.9143 | 0.9622 | 0.9503 | 0.9608 |
| 100 | 0.9317 | 0.8873 | 0.9688 | 0.8890 | 0.9410 | 0.9319 | 0.9413 |
| 150 | 0.9318 | 0.8414 | 0.9555 | 0.8803 | 0.9236 | 0.9055 | 0.9323 |
| 200 | 0.9331 | 0.8532 | 0.9569 | 0.8686 | 0.9349 | 0.9138 | 0.9355 |
| 250 | 0.9231 | 0.8523 | 0.9508 | 0.8494 | 0.9242 | 0.8989 | 0.9326 |

Disagreement sessions:

| sma_length | FAS/XLF | LABU/XBI | QLD/QQQ | SOXL/SMH | SPXL/SPY | TECL/XLK | TQQQ/QQQ |
|---|---|---|---|---|---|---|---|
| 20 | 209 | 115 | 94 | 273 | 98 | 136 | 115 |
| 50 | 238 | 181 | 124 | 350 | 167 | 218 | 161 |
| 100 | 298 | 307 | 155 | 448 | 258 | 295 | 238 |
| 150 | 294 | 424 | 219 | 477 | 330 | 405 | 271 |
| 200 | 285 | 385 | 210 | 517 | 278 | 365 | 255 |
| 250 | 324 | 380 | 237 | 585 | 320 | 423 | 263 |

Agreement falls monotonically as the average lengthens, from 93 to 98 percent at 20 sessions down to 85 to 95 percent at 250. At the canonical 200-session average, decision 6.5, disagreement runs from 210 sessions (QLD against QQQ) to 517 (SOXL against SMH).

### Disagreement run lengths, canonical 200-session average

| pair | n_sessions | n_disagree_sessions | n_disagreement_runs | run_mean | run_median | run_p95 | run_max | run_n_len_1 | run_n_len_2_5 | run_n_len_6_20 | run_n_len_gt_20 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FAS/XLF | 4262 | 285 | 114 | 2.50 | 1.0 | 8.00 | 14 | 58 | 44 | 12 | 0 |
| LABU/XBI | 2623 | 385 | 82 | 4.70 | 3.0 | 13.95 | 26 | 32 | 25 | 23 | 2 |
| QLD/QQQ | 4871 | 210 | 94 | 2.23 | 2.0 | 6.35 | 14 | 45 | 43 | 6 | 0 |
| SOXL/SMH | 3935 | 517 | 103 | 5.02 | 2.0 | 14.80 | 72 | 34 | 46 | 19 | 4 |
| SPXL/SPY | 4272 | 278 | 78 | 3.56 | 2.0 | 8.30 | 48 | 28 | 40 | 9 | 1 |
| TECL/XLK | 4235 | 365 | 106 | 3.44 | 2.0 | 10.00 | 26 | 43 | 46 | 16 | 1 |
| TQQQ/QQQ | 3954 | 255 | 84 | 3.04 | 2.0 | 6.85 | 21 | 30 | 45 | 8 | 1 |

Most disagreements are short. The median run is one to three sessions and roughly a third are a single session. The tail is not short: SOXL against SMH has four runs longer than 20 sessions and a maximum of 72 consecutive sessions on which the leveraged fund and its underlying disagree about which side of the 200-day average they are on. SPXL against SPY reaches 48 and LABU against XBI reaches 26.

### Crossover offsets, canonical 200-session average, full window

| pair | direction | n_crossovers_underlying | n_crossovers_leveraged | n_matched | n_unmatched_underlying | n_unmatched_leveraged | mean_offset | median_offset | sd_offset | p05_offset | p95_offset | min_offset | max_offset | frac_offset_zero | frac_abs_offset_le_1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FAS/XLF | all | 134 | 134 | 90 | 44 | 44 | -2.73 | 0.0 | 12.49 | -19.6 | 12.0 | -59 | 25 | 0.222 | 0.311 |
| FAS/XLF | down | 134 | 134 | 45 | 22 | 22 | -4.56 | -1.0 | 12.44 | -19.8 | 5.4 | -59 | 22 | 0.244 | 0.378 |
| FAS/XLF | up | 134 | 134 | 45 | 22 | 22 | -0.91 | 0.0 | 12.41 | -18.8 | 12.8 | -54 | 25 | 0.200 | 0.244 |
| LABU/XBI | all | 85 | 83 | 31 | 54 | 52 | -1.13 | -1.0 | 9.38 | -17.5 | 14.5 | -22 | 17 | 0.065 | 0.129 |
| LABU/XBI | down | 85 | 83 | 15 | 27 | 26 | -5.53 | -5.0 | 6.75 | -17.3 | 2.7 | -18 | 9 | 0.133 | 0.200 |
| LABU/XBI | up | 85 | 83 | 16 | 27 | 26 | 3.00 | 3.5 | 9.79 | -11.5 | 16.2 | -22 | 17 | 0.000 | 0.062 |
| QLD/QQQ | all | 118 | 114 | 84 | 34 | 30 | -1.50 | 0.0 | 10.31 | -22.4 | 9.0 | -35 | 26 | 0.262 | 0.476 |
| QLD/QQQ | down | 118 | 114 | 42 | 17 | 15 | -2.71 | -1.0 | 9.96 | -22.7 | 8.8 | -35 | 20 | 0.262 | 0.476 |
| QLD/QQQ | up | 118 | 114 | 42 | 17 | 15 | -0.29 | 1.0 | 10.64 | -18.8 | 9.0 | -33 | 26 | 0.262 | 0.476 |
| SOXL/SMH | all | 100 | 110 | 67 | 33 | 43 | 4.99 | 1.0 | 19.73 | -14.0 | 47.5 | -41 | 60 | 0.030 | 0.164 |
| SOXL/SMH | down | 100 | 110 | 33 | 17 | 22 | 0.79 | -3.0 | 18.61 | -14.8 | 43.4 | -41 | 56 | 0.030 | 0.152 |
| SOXL/SMH | up | 100 | 110 | 34 | 16 | 21 | 9.06 | 4.0 | 20.20 | -11.3 | 52.5 | -37 | 60 | 0.029 | 0.176 |
| SPXL/SPY | all | 90 | 92 | 59 | 31 | 33 | 6.73 | 0.0 | 16.49 | -7.1 | 48.7 | -16 | 59 | 0.220 | 0.373 |
| SPXL/SPY | down | 90 | 92 | 30 | 15 | 16 | 4.13 | -1.0 | 16.99 | -7.3 | 43.7 | -16 | 59 | 0.300 | 0.467 |
| SPXL/SPY | up | 90 | 92 | 29 | 16 | 17 | 9.41 | 3.0 | 15.79 | -4.2 | 44.0 | -8 | 58 | 0.138 | 0.276 |
| TECL/XLK | all | 90 | 134 | 70 | 20 | 64 | 5.83 | 1.0 | 15.80 | -13.0 | 41.4 | -19 | 60 | 0.086 | 0.257 |
| TECL/XLK | down | 90 | 134 | 35 | 10 | 32 | 2.14 | -1.0 | 14.78 | -13.6 | 36.3 | -19 | 52 | 0.114 | 0.314 |
| TECL/XLK | up | 90 | 134 | 35 | 10 | 32 | 9.51 | 3.0 | 16.14 | -11.6 | 45.0 | -14 | 60 | 0.057 | 0.200 |
| TQQQ/QQQ | all | 86 | 90 | 62 | 24 | 28 | 0.85 | 1.0 | 16.03 | -26.9 | 33.6 | -34 | 47 | 0.065 | 0.177 |
| TQQQ/QQQ | down | 86 | 90 | 31 | 12 | 14 | -2.52 | -2.0 | 15.78 | -27.5 | 26.0 | -34 | 43 | 0.129 | 0.226 |
| TQQQ/QQQ | up | 86 | 90 | 31 | 12 | 14 | 4.23 | 3.0 | 15.82 | -18.5 | 31.5 | -30 | 47 | 0.000 | 0.129 |

Median offsets sit at or near zero but the distribution is wide and asymmetric. Only 3 to 26 percent of matched crossovers are simultaneous, and only 13 to 48 percent fall within one session. The 5th to 95th percentile range spans roughly 27 sessions before to 48 sessions after. A material fraction of crossovers cannot be matched at all inside a 60-session window: TECL produces 134 crossovers against XLK's 90 at the 200-day average, and 64 of TECL's are unmatched.

**Upward crossings lag more than downward crossings, for all seven pairs.** At the 200-day average the mean up-offset exceeds the mean down-offset by 8.5 sessions for LABU, 8.3 for SOXL, 7.4 for TECL, 6.7 for TQQQ, 5.3 for SPXL, 3.6 for FAS and 2.4 for QLD. This is the variance-drag signature: after a decline the leveraged fund must climb further than its underlying to regain its own moving average, so it confirms an uptrend late.

### Full offset table across all SMA lengths

| pair | sma_length | direction | n_matched | mean_offset | median_offset | p05_offset | p95_offset | frac_offset_zero |
|---|---|---|---|---|---|---|---|---|
| FAS/XLF | 20 | down | 237 | -0.05 | 0.0 | -2.0 | 2.2 | 0.738 |
| FAS/XLF | 20 | up | 237 | 0.23 | 0.0 | -1.2 | 2.0 | 0.730 |
| FAS/XLF | 50 | down | 144 | 0.17 | 0.0 | -2.8 | 5.5 | 0.660 |
| FAS/XLF | 50 | up | 144 | 1.19 | 0.0 | -2.8 | 4.8 | 0.611 |
| FAS/XLF | 100 | down | 96 | -1.26 | 0.0 | -21.5 | 8.0 | 0.562 |
| FAS/XLF | 100 | up | 96 | -0.29 | 0.0 | -18.0 | 7.2 | 0.365 |
| FAS/XLF | 150 | down | 61 | -2.92 | 0.0 | -17.0 | 2.0 | 0.590 |
| FAS/XLF | 150 | up | 61 | -0.31 | 0.0 | -12.0 | 10.0 | 0.295 |
| FAS/XLF | 200 | down | 45 | -4.56 | -1.0 | -19.8 | 5.4 | 0.244 |
| FAS/XLF | 200 | up | 45 | -0.91 | 0.0 | -18.8 | 12.8 | 0.200 |
| FAS/XLF | 250 | down | 38 | 2.45 | -0.5 | -22.1 | 42.6 | 0.237 |
| FAS/XLF | 250 | up | 37 | 0.73 | 1.0 | -32.8 | 30.0 | 0.054 |
| LABU/XBI | 20 | down | 160 | 0.78 | 0.0 | -1.0 | 0.1 | 0.769 |
| LABU/XBI | 20 | up | 160 | 0.86 | 0.0 | 0.0 | 2.0 | 0.756 |
| LABU/XBI | 50 | down | 87 | 0.31 | 0.0 | -24.8 | 32.4 | 0.437 |
| LABU/XBI | 50 | up | 88 | 0.47 | 0.0 | -29.2 | 31.6 | 0.466 |
| LABU/XBI | 100 | down | 65 | -1.22 | -1.0 | -37.4 | 34.2 | 0.231 |
| LABU/XBI | 100 | up | 66 | 2.61 | 1.0 | -33.5 | 43.0 | 0.212 |
| LABU/XBI | 150 | down | 35 | -2.97 | -3.0 | -23.6 | 19.2 | 0.029 |
| LABU/XBI | 150 | up | 35 | 3.51 | 3.0 | -17.3 | 25.6 | 0.029 |
| LABU/XBI | 200 | down | 15 | -5.53 | -5.0 | -17.3 | 2.7 | 0.133 |
| LABU/XBI | 200 | up | 16 | 3.00 | 3.5 | -11.5 | 16.2 | 0.000 |
| LABU/XBI | 250 | down | 21 | -3.33 | -3.0 | -39.0 | 25.0 | 0.000 |
| LABU/XBI | 250 | up | 20 | -3.60 | 1.5 | -37.2 | 18.1 | 0.050 |
| QLD/QQQ | 20 | down | 264 | 0.21 | 0.0 | -1.0 | 0.0 | 0.932 |
| QLD/QQQ | 20 | up | 265 | 0.43 | 0.0 | 0.0 | 1.0 | 0.860 |
| QLD/QQQ | 50 | down | 150 | -0.21 | 0.0 | -1.0 | 0.0 | 0.753 |
| QLD/QQQ | 50 | up | 150 | 0.35 | 0.0 | 0.0 | 1.0 | 0.747 |
| QLD/QQQ | 100 | down | 92 | -0.41 | 0.0 | -2.0 | 0.0 | 0.598 |
| QLD/QQQ | 100 | up | 92 | 0.68 | 0.0 | 0.0 | 3.9 | 0.598 |
| QLD/QQQ | 150 | down | 56 | 0.75 | 0.0 | -9.5 | 22.5 | 0.482 |
| QLD/QQQ | 150 | up | 56 | 3.38 | 1.0 | -7.2 | 26.8 | 0.214 |
| QLD/QQQ | 200 | down | 42 | -2.71 | -1.0 | -22.7 | 8.8 | 0.262 |
| QLD/QQQ | 200 | up | 42 | -0.29 | 1.0 | -18.8 | 9.0 | 0.262 |
| QLD/QQQ | 250 | down | 39 | -1.18 | -1.0 | -24.4 | 18.4 | 0.282 |
| QLD/QQQ | 250 | up | 39 | 3.74 | 3.0 | -15.2 | 25.6 | 0.077 |
| SOXL/SMH | 20 | down | 246 | -0.11 | 0.0 | -8.8 | 4.0 | 0.679 |
| SOXL/SMH | 20 | up | 246 | 0.83 | 0.0 | -4.5 | 8.0 | 0.675 |
| SOXL/SMH | 50 | down | 118 | -1.75 | 0.0 | -27.7 | 15.1 | 0.483 |
| SOXL/SMH | 50 | up | 118 | 0.16 | 1.0 | -25.3 | 17.4 | 0.364 |
| SOXL/SMH | 100 | down | 63 | -1.13 | -1.0 | -22.6 | 24.7 | 0.333 |
| SOXL/SMH | 100 | up | 65 | 1.83 | 1.0 | -22.0 | 28.0 | 0.154 |
| SOXL/SMH | 150 | down | 39 | -2.13 | -1.0 | -30.6 | 26.2 | 0.154 |
| SOXL/SMH | 150 | up | 39 | 3.44 | 2.0 | -28.4 | 33.5 | 0.077 |
| SOXL/SMH | 200 | down | 33 | 0.79 | -3.0 | -14.8 | 43.4 | 0.030 |
| SOXL/SMH | 200 | up | 34 | 9.06 | 4.0 | -11.3 | 52.5 | 0.029 |
| SOXL/SMH | 250 | down | 25 | 3.16 | -2.0 | -26.2 | 45.4 | 0.080 |
| SOXL/SMH | 250 | up | 25 | 9.00 | 8.0 | -33.4 | 46.0 | 0.000 |
| SPXL/SPY | 20 | down | 235 | -0.72 | 0.0 | -1.0 | 0.0 | 0.872 |
| SPXL/SPY | 20 | up | 236 | -1.03 | 0.0 | 0.0 | 1.0 | 0.839 |
| SPXL/SPY | 50 | down | 133 | 0.74 | 0.0 | -2.0 | 0.0 | 0.662 |
| SPXL/SPY | 50 | up | 134 | 1.63 | 0.0 | 0.0 | 5.7 | 0.649 |
| SPXL/SPY | 100 | down | 74 | -0.92 | 0.0 | -5.7 | 11.0 | 0.514 |
| SPXL/SPY | 100 | up | 75 | 1.37 | 1.0 | -3.2 | 12.9 | 0.280 |
| SPXL/SPY | 150 | down | 48 | 1.62 | -1.0 | -4.7 | 21.3 | 0.229 |
| SPXL/SPY | 150 | up | 49 | 4.43 | 2.0 | -7.0 | 32.6 | 0.184 |
| SPXL/SPY | 200 | down | 30 | 4.13 | -1.0 | -7.3 | 43.7 | 0.300 |
| SPXL/SPY | 200 | up | 29 | 9.41 | 3.0 | -4.2 | 44.0 | 0.138 |
| SPXL/SPY | 250 | down | 42 | 0.29 | -1.5 | -36.4 | 42.9 | 0.071 |
| SPXL/SPY | 250 | up | 40 | 3.55 | 2.5 | -28.2 | 44.1 | 0.025 |
| TECL/XLK | 20 | down | 230 | 0.24 | 0.0 | -1.0 | 0.0 | 0.852 |
| TECL/XLK | 20 | up | 229 | 0.16 | 0.0 | 0.0 | 1.0 | 0.764 |
| TECL/XLK | 50 | down | 137 | 0.16 | 0.0 | -3.2 | 8.2 | 0.599 |
| TECL/XLK | 50 | up | 138 | 1.22 | 0.0 | -6.0 | 11.2 | 0.529 |
| TECL/XLK | 100 | down | 81 | -0.54 | 0.0 | -14.0 | 26.0 | 0.494 |
| TECL/XLK | 100 | up | 81 | 0.63 | 1.0 | -22.0 | 20.0 | 0.284 |
| TECL/XLK | 150 | down | 46 | 1.02 | -1.0 | -13.2 | 34.2 | 0.196 |
| TECL/XLK | 150 | up | 45 | 5.47 | 2.0 | -12.4 | 41.4 | 0.111 |
| TECL/XLK | 200 | down | 35 | 2.14 | -1.0 | -13.6 | 36.3 | 0.114 |
| TECL/XLK | 200 | up | 35 | 9.51 | 3.0 | -11.6 | 45.0 | 0.057 |
| TECL/XLK | 250 | down | 29 | -2.21 | -2.0 | -33.4 | 29.2 | 0.138 |
| TECL/XLK | 250 | up | 29 | 7.31 | 5.0 | -21.6 | 37.2 | 0.034 |
| TQQQ/QQQ | 20 | down | 214 | -0.23 | 0.0 | -1.0 | 0.0 | 0.864 |
| TQQQ/QQQ | 20 | up | 214 | 0.14 | 0.0 | 0.0 | 1.0 | 0.780 |
| TQQQ/QQQ | 50 | down | 120 | 0.52 | 0.0 | -1.0 | 0.3 | 0.592 |
| TQQQ/QQQ | 50 | up | 120 | 1.35 | 0.0 | 0.0 | 5.1 | 0.667 |
| TQQQ/QQQ | 100 | down | 74 | 1.31 | 0.0 | -5.1 | 23.1 | 0.446 |
| TQQQ/QQQ | 100 | up | 75 | 3.59 | 1.0 | -1.8 | 25.6 | 0.320 |
| TQQQ/QQQ | 150 | down | 40 | -1.40 | -1.0 | -20.4 | 19.4 | 0.200 |
| TQQQ/QQQ | 150 | up | 40 | 3.42 | 1.0 | -10.8 | 23.4 | 0.175 |
| TQQQ/QQQ | 200 | down | 31 | -2.52 | -2.0 | -27.5 | 26.0 | 0.129 |
| TQQQ/QQQ | 200 | up | 31 | 4.23 | 3.0 | -18.5 | 31.5 | 0.000 |
| TQQQ/QQQ | 250 | down | 31 | -0.55 | -1.0 | -32.5 | 28.0 | 0.161 |
| TQQQ/QQQ | 250 | up | 31 | 6.29 | 5.0 | -25.5 | 34.5 | 0.032 |

### Stress regime, the 60 sessions after each 20 percent underlying drawdown

A drawdown entry is a session on which the underlying's total return index first falls 20 percent or more below its running maximum. The stress window is the union of the 60 sessions following each entry.

| pair | scope | n_sessions | n_drawdown_entries | frac_agree_above_below | n_disagree_sessions | n_disagreement_runs | run_max | n_matched | mean_offset | median_offset |
|---|---|---|---|---|---|---|---|---|---|---|
| FAS/XLF | all | 4262 | 30 | 0.9331 | 285 | 114 | 14 | 90 | -2.73 | 0.0 |
| FAS/XLF | post_dd20 | 951 | 30 | 0.8854 | 109 | 33 | 14 | 23 | 8.17 | 5.0 |
| LABU/XBI | all | 2623 | 20 | 0.8532 | 385 | 82 | 26 | 31 | -1.13 | -1.0 |
| LABU/XBI | post_dd20 | 555 | 20 | 0.7315 | 149 | 27 | 26 | 10 | 1.20 | 2.5 |
| QLD/QQQ | all | 4871 | 27 | 0.9569 | 210 | 94 | 14 | 84 | -1.50 | 0.0 |
| QLD/QQQ | post_dd20 | 772 | 27 | 0.9275 | 56 | 20 | 14 | 20 | -7.25 | 0.0 |
| SOXL/SMH | all | 3935 | 33 | 0.8686 | 517 | 103 | 72 | 67 | 4.99 | 1.0 |
| SOXL/SMH | post_dd20 | 814 | 33 | 0.7408 | 211 | 27 | 57 | 20 | 11.15 | 12.0 |
| SPXL/SPY | all | 4272 | 8 | 0.9349 | 278 | 78 | 48 | 59 | 6.73 | 0.0 |
| SPXL/SPY | post_dd20 | 224 | 8 | 0.8884 | 25 | 6 | 9 | 5 | 33.60 | 35.0 |
| TECL/XLK | all | 4235 | 18 | 0.9138 | 365 | 106 | 26 | 70 | 5.83 | 1.0 |
| TECL/XLK | post_dd20 | 430 | 18 | 0.7907 | 90 | 12 | 26 | 6 | 24.17 | 23.0 |
| TQQQ/QQQ | all | 3954 | 14 | 0.9355 | 255 | 84 | 21 | 62 | 0.85 | 1.0 |
| TQQQ/QQQ | post_dd20 | 441 | 14 | 0.8707 | 57 | 9 | 21 | 8 | 11.12 | 16.5 |

**The prompt's expectation that variance drag concentrates the divergence in stress holds, and the effect is large.** Agreement falls for all seven pairs: SOXL against SMH from 86.9 to 74.1 percent, LABU against XBI from 85.3 to 73.2, TECL against XLK from 91.4 to 79.1, TQQQ against QQQ from 93.6 to 87.1. Crossover offsets move sharply positive, meaning the leveraged fund crosses later: SPXL against SPY runs a mean offset of +33.6 sessions and a median of +35 inside the stress window against a full-window median of 0, TECL +24.2 against +1, SOXL +11.2 against +1.

Sample sizes inside the stress window are small and should be read as such. SPXL has 8 drawdown entries, 224 stress sessions and 5 matched crossovers; TECL has 6 matched crossovers. The direction is consistent across all seven pairs; the magnitudes for the narrower pairs are not precisely estimated.

## Step 7. Vote structure. Informs 6.7, documents 6.8

A vote is one instrument's total return index against its own simple moving average. The effective number of independent votes is the reciprocal of the sum of squared normalized eigenvalues of the vote correlation matrix, so it runs from 1 for perfectly redundant votes to k for perfectly independent ones.

The four vote sets have very different maximal windows, so each is reported on its own window and on two shared ones: `common_with_S3` restricts to the window the current set supports, and `common_all_sets` restricts to the window every set including KMLM supports.

Effective independent votes, `native`:

| sma_length | S3_current | alt1_TLT_for_SOXL | alt2_KMLM_for_SOXL | alt3_drop_SOXL |
|---|---|---|---|---|
| 50 | 1.685 | 2.383 | 2.177 | 1.544 |
| 100 | 1.658 | 2.293 | 2.107 | 1.471 |
| 150 | 1.702 | 2.354 | 1.978 | 1.508 |
| 200 | 1.674 | 2.349 | 1.780 | 1.481 |
| 250 | 1.742 | 2.377 | 1.806 | 1.488 |

Sessions per set: S3_current 4,085, alt1_TLT_for_SOXL 6,002, alt2_KMLM_for_SOXL 1,383, alt3_drop_SOXL 6,540.

Effective independent votes, `common_with_S3`:

| sma_length | S3_current | alt1_TLT_for_SOXL | alt2_KMLM_for_SOXL | alt3_drop_SOXL |
|---|---|---|---|---|
| 50 | 1.685 | 2.387 | 2.177 | 1.581 |
| 100 | 1.658 | 2.269 | 2.107 | 1.487 |
| 150 | 1.702 | 2.269 | 1.978 | 1.496 |
| 200 | 1.674 | 2.207 | 1.780 | 1.449 |
| 250 | 1.742 | 2.251 | 1.806 | 1.479 |

Sessions per set: S3_current 4,085, alt1_TLT_for_SOXL 4,085, alt2_KMLM_for_SOXL 1,383, alt3_drop_SOXL 4,085.

Effective independent votes, `common_all_sets`:

| sma_length | S3_current | alt1_TLT_for_SOXL | alt2_KMLM_for_SOXL | alt3_drop_SOXL |
|---|---|---|---|---|
| 50 | 1.636 | 2.160 | 2.177 | 1.495 |
| 100 | 1.694 | 2.061 | 2.107 | 1.418 |
| 150 | 1.593 | 1.810 | 1.978 | 1.315 |
| 200 | 1.473 | 1.699 | 1.780 | 1.190 |
| 250 | 1.553 | 1.811 | 1.806 | 1.243 |

Sessions per set: S3_current 1,383, alt1_TLT_for_SOXL 1,383, alt2_KMLM_for_SOXL 1,383, alt3_drop_SOXL 1,383.

The ranking is stable across all three window bases and all five average lengths: alt1 above alt2 above S3 above alt3 in absolute count. On native windows, S3 measures 1.658 to 1.742 effective votes out of four, alt1 with TLT measures 2.293 to 2.383, alt2 with KMLM measures 1.780 to 2.177, and alt3 with three votes measures 1.471 to 1.544 out of three. As a fraction of the votes cast, alt3 at 0.49 to 0.51 exceeds S3 at 0.41 to 0.44, and alt1 at 0.57 to 0.60 exceeds both.

### S3 pairwise structure

Pairwise agreement, fraction of sessions the two votes are in the same state:

| sma_length | QQQ/SMH | QQQ/SOXL | SMH/SOXL | SPY/QQQ | SPY/SMH | SPY/SOXL |
|---|---|---|---|---|---|---|
| 50 | 0.8551 | 0.8223 | 0.9143 | 0.8962 | 0.8335 | 0.8002 |
| 100 | 0.8766 | 0.8146 | 0.8890 | 0.9202 | 0.9033 | 0.8240 |
| 150 | 0.8939 | 0.8083 | 0.8803 | 0.9378 | 0.9009 | 0.8108 |
| 200 | 0.9070 | 0.8127 | 0.8686 | 0.9454 | 0.9139 | 0.8155 |
| 250 | 0.9086 | 0.7915 | 0.8494 | 0.9454 | 0.9127 | 0.7972 |

Pairwise correlation of the vote indicators:

| sma_length | QQQ/SMH | QQQ/SOXL | SMH/SOXL | SPY/QQQ | SPY/SMH | SPY/SOXL |
|---|---|---|---|---|---|---|
| 50 | 0.6580 | 0.6247 | 0.8237 | 0.7406 | 0.6043 | 0.5763 |
| 100 | 0.6524 | 0.5841 | 0.7620 | 0.7575 | 0.7254 | 0.6133 |
| 150 | 0.6651 | 0.5643 | 0.7379 | 0.7702 | 0.6873 | 0.5742 |
| 200 | 0.6887 | 0.5757 | 0.7094 | 0.7890 | 0.7128 | 0.5835 |
| 250 | 0.6799 | 0.5392 | 0.6737 | 0.7718 | 0.6961 | 0.5533 |

### Vote count distribution, S3

| sma_length | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 50 | 0.1892 | 0.0732 | 0.0955 | 0.0923 | 0.5498 |
| 100 | 0.1527 | 0.0406 | 0.0830 | 0.1061 | 0.6176 |
| 150 | 0.1217 | 0.0346 | 0.0906 | 0.1006 | 0.6524 |
| 200 | 0.1174 | 0.0325 | 0.0813 | 0.1047 | 0.6640 |
| 250 | 0.1048 | 0.0358 | 0.0777 | 0.1256 | 0.6561 |

The distribution is strongly bimodal. At the 200-session average, 66.4 percent of sessions have all four votes bullish and 11.7 percent have none, leaving 21.9 percent split across the three intermediate states. The votes move together far more often than they disagree.

### Bull classification and leave-one-out sensitivity, S3

Fraction of sessions classified bull at each absolute vote threshold:

| sma_length | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 50 | 0.8108 | 0.7376 | 0.6421 | 0.5498 |
| 100 | 0.8473 | 0.8067 | 0.7237 | 0.6176 |
| 150 | 0.8783 | 0.8437 | 0.7531 | 0.6524 |
| 200 | 0.8826 | 0.8501 | 0.7687 | 0.6640 |
| 250 | 0.8952 | 0.8595 | 0.7817 | 0.6561 |

Fraction of sessions on which the classification flips when one vote is removed, holding the absolute threshold fixed, at the 200-session average:

| key2 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| QQQ | 0.0155 | 0.0653 | 0.1027 | 0.6640 |
| SMH | 0.0053 | 0.0272 | 0.1047 | 0.6640 |
| SOXL | 0.0000 | 0.0028 | 0.0030 | 0.6640 |
| SPY | 0.0117 | 0.0673 | 0.1037 | 0.6640 |

The threshold-4 column is degenerate and should be read as an artefact of the convention, not a finding: with the absolute threshold held at 4 and only three votes remaining, the bull condition is unsatisfiable, so the flip fraction necessarily equals the bull fraction for every vote. The informative columns are thresholds 2 and 3.

**SOXL is close to inert.** At threshold 2 its removal changes the classification on 0.28 percent of sessions and at threshold 3 on 0.30 percent, against 6.5 to 6.7 percent and 10.3 to 10.5 percent for SPY, QQQ and SMH. Under decision 6.7's simple majority, threshold 3 of 4, that is **12 sessions out of 3,935** for SOXL against 412 for SMH, 408 for SPY and 404 for QQQ.

### Alternative vote sets

**alt1_TLT_for_SOXL**, members SPY, QQQ, SMH, TLT, 6,002 sessions at the 50-session average, 2003-05-14 to 2026-08-17 at the 200-session average.

| sma_length | QQQ/SMH | QQQ/TLT | SMH/TLT | SPY/QQQ | SPY/SMH | SPY/TLT |
|---|---|---|---|---|---|---|
| 50 | 0.8504 | 0.4870 | 0.4780 | 0.8864 | 0.8194 | 0.4950 |
| 100 | 0.8636 | 0.5094 | 0.5010 | 0.9042 | 0.8730 | 0.5050 |
| 150 | 0.8728 | 0.5449 | 0.5122 | 0.9107 | 0.8628 | 0.5339 |
| 200 | 0.8744 | 0.5456 | 0.4997 | 0.9152 | 0.8628 | 0.5330 |
| 250 | 0.8694 | 0.5441 | 0.4704 | 0.9171 | 0.8540 | 0.5322 |

Fraction bull by threshold:

| sma_length | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 50 | 0.9162 | 0.7483 | 0.6343 | 0.2929 |
| 100 | 0.9296 | 0.7925 | 0.7018 | 0.3453 |
| 150 | 0.9393 | 0.8292 | 0.7499 | 0.3782 |
| 200 | 0.9433 | 0.8375 | 0.7656 | 0.3775 |
| 250 | 0.9535 | 0.8483 | 0.7780 | 0.3726 |

**alt2_KMLM_for_SOXL**, members SPY, QQQ, SMH, KMLM, 1,383 sessions at the 50-session average, 2021-09-17 to 2026-08-17 at the 200-session average.

| sma_length | QQQ/KMLM | QQQ/SMH | SMH/KMLM | SPY/KMLM | SPY/QQQ | SPY/SMH |
|---|---|---|---|---|---|---|
| 50 | 0.4035 | 0.8713 | 0.4035 | 0.4309 | 0.9046 | 0.8366 |
| 100 | 0.4276 | 0.8792 | 0.4359 | 0.4299 | 0.9242 | 0.8980 |
| 150 | 0.4341 | 0.9119 | 0.4489 | 0.4224 | 0.9462 | 0.9221 |
| 200 | 0.3601 | 0.9481 | 0.3779 | 0.3658 | 0.9603 | 0.9521 |
| 250 | 0.3195 | 0.9417 | 0.3339 | 0.3347 | 0.9476 | 0.9383 |

Fraction bull by threshold:

| sma_length | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 50 | 0.9436 | 0.7527 | 0.6443 | 0.2632 |
| 100 | 0.9520 | 0.7944 | 0.6999 | 0.3151 |
| 150 | 0.9540 | 0.8075 | 0.7217 | 0.3445 |
| 200 | 0.9440 | 0.7916 | 0.7461 | 0.2806 |
| 250 | 0.9611 | 0.7870 | 0.7430 | 0.2477 |

**alt3_drop_SOXL**, members SPY, QQQ, SMH, 6,540 sessions at the 50-session average, 2001-03-20 to 2026-08-17 at the 200-session average.

| sma_length | QQQ/SMH | SPY/QQQ | SPY/SMH |
|---|---|---|---|
| 50 | 0.8506 | 0.8872 | 0.8252 |
| 100 | 0.8612 | 0.9009 | 0.8761 |
| 150 | 0.8644 | 0.9034 | 0.8626 |
| 200 | 0.8717 | 0.9124 | 0.8642 |
| 250 | 0.8678 | 0.9194 | 0.8585 |

Fraction bull by threshold:

| sma_length | 1 | 2 | 3 |
|---|---|---|---|
| 50 | 0.7489 | 0.6593 | 0.5304 |
| 100 | 0.7752 | 0.7083 | 0.5943 |
| 150 | 0.8026 | 0.7377 | 0.6179 |
| 200 | 0.8059 | 0.7401 | 0.6300 |
| 250 | 0.8189 | 0.7489 | 0.6418 |

KMLM's window is the binding constraint on alt2: it supports 1,383 sessions at the 50-session average and 1,233 at the 250-session average, beginning 2021-09-17 for the 200-session case. Any comparison involving alt2 on its native window covers a single rate cycle.

Per-vote leave-one-out flip fractions for every set, threshold and average length are in `vote-structure.csv`.

## Step 8. Overbought panel structure. Informs 6.9

The disjunction is the OR across the panel: it fires on a session if any member's RSI exceeds the threshold. Marginal contribution is the fraction of disjunction firings on which that name is the only member firing.

Common windows, set by the shortest member of each panel:

| panel | rsi_period | n_sessions | first_date | last_date |
|---|---|---|---|---|
| S1_eleven | 7 | 3615 | 2012-03-30 | 2026-08-17 |
| S1_eleven | 14 | 3608 | 2012-04-11 | 2026-08-17 |
| S1_eleven | 28 | 3594 | 2012-05-01 | 2026-08-17 |
| T11_five | 7 | 4146 | 2010-02-23 | 2026-08-17 |
| T11_five | 14 | 4139 | 2010-03-04 | 2026-08-17 |
| T11_five | 28 | 4125 | 2010-03-24 | 2026-08-17 |

The two panels are not measured over the same window. S1 starts 2012-04-11 because QQQE lists in March 2012; T11 starts 2010-03-04 because TQQQ lists in February 2010. Firing rates are not directly comparable across panels.

### Effective number of independent signals

| rsi_period | S1_eleven | T11_five |
|---|---|---|
| 7 | 1.769 | 1.398 |
| 14 | 1.765 | 1.394 |
| 28 | 1.798 | 1.403 |

Mean pairwise RSI correlation within panel:

| rsi_period | S1_eleven | T11_five |
|---|---|---|
| 7 | 0.7040 | 0.7947 |
| 14 | 0.7040 | 0.7970 |
| 28 | 0.6944 | 0.7933 |

**Eleven names carry 1.77 independent signals. Five names carry 1.39.** The result is insensitive to the RSI period. Mean pairwise correlation is 0.70 in S1 and 0.79 in T11; the smaller panel is the more redundant one per name, because it is entirely large-cap US equity beta while S1 at least contains XLP and VOX.

### S1_eleven, pairwise RSI correlation at period 14

|  | QQQE | VTV | VOX | TECL | VOOG | VOOV | TQQQ | XLP | XLY | FAS | SPY |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QQQE | 1.000 | 0.736 | 0.616 | 0.871 | 0.899 | 0.762 | 0.910 | 0.442 | 0.815 | 0.698 | 0.895 |
| VTV | 0.736 | 1.000 | 0.576 | 0.629 | 0.714 | 0.977 | 0.619 | 0.598 | 0.673 | 0.882 | 0.873 |
| VOX | 0.616 | 0.576 | 1.000 | 0.561 | 0.638 | 0.622 | 0.588 | 0.402 | 0.626 | 0.536 | 0.684 |
| TECL | 0.871 | 0.629 | 0.561 | 1.000 | 0.939 | 0.657 | 0.967 | 0.373 | 0.745 | 0.579 | 0.877 |
| VOOG | 0.899 | 0.714 | 0.638 | 0.939 | 1.000 | 0.729 | 0.957 | 0.465 | 0.846 | 0.668 | 0.952 |
| VOOV | 0.762 | 0.977 | 0.622 | 0.657 | 0.729 | 1.000 | 0.647 | 0.582 | 0.708 | 0.884 | 0.888 |
| TQQQ | 0.910 | 0.619 | 0.588 | 0.967 | 0.957 | 0.647 | 1.000 | 0.381 | 0.806 | 0.584 | 0.884 |
| XLP | 0.442 | 0.598 | 0.402 | 0.373 | 0.465 | 0.582 | 0.381 | 1.000 | 0.453 | 0.446 | 0.525 |
| XLY | 0.815 | 0.673 | 0.626 | 0.745 | 0.846 | 0.708 | 0.806 | 0.453 | 1.000 | 0.683 | 0.847 |
| FAS | 0.698 | 0.882 | 0.536 | 0.579 | 0.668 | 0.884 | 0.584 | 0.446 | 0.683 | 1.000 | 0.805 |
| SPY | 0.895 | 0.873 | 0.684 | 0.877 | 0.952 | 0.888 | 0.884 | 0.525 | 0.847 | 0.805 | 1.000 |

### T11_five, pairwise RSI correlation at period 14

|  | SPY | IOO | TQQQ | VTV | XLF |
|---|---|---|---|---|---|
| SPY | 1.000 | 0.930 | 0.890 | 0.889 | 0.795 |
| IOO | 0.930 | 1.000 | 0.841 | 0.801 | 0.698 |
| TQQQ | 0.890 | 0.841 | 1.000 | 0.658 | 0.586 |
| VTV | 0.889 | 0.801 | 0.658 | 1.000 | 0.882 |
| XLF | 0.795 | 0.698 | 0.586 | 0.882 | 1.000 |

### Firing rates and marginal contribution

**S1_eleven**

Disjunction firing rate: threshold 70 fires on 0.2985 of sessions (1,077 days), threshold 75 fires on 0.1095 of sessions (395 days), threshold 80 fires on 0.0294 of sessions (106 days).

| name | individual_70 | individual_75 | individual_80 | sole_trigger_70 | sole_trigger_75 | sole_trigger_80 | sole_days_70 | sole_days_75 | sole_days_80 |
|---|---|---|---|---|---|---|---|---|---|
| FAS | 0.0685 | 0.0191 | 0.0036 | 0.0381 | 0.0532 | 0.0189 | 41 | 21 | 2 |
| QQQE | 0.0743 | 0.0236 | 0.0033 | 0.0269 | 0.0380 | 0.0189 | 29 | 15 | 2 |
| SPY | 0.0912 | 0.0274 | 0.0055 | 0.0056 | 0.0076 | 0.0094 | 6 | 3 | 1 |
| TECL | 0.0989 | 0.0302 | 0.0089 | 0.0204 | 0.0481 | 0.1038 | 22 | 19 | 11 |
| TQQQ | 0.1084 | 0.0355 | 0.0083 | 0.0214 | 0.0329 | 0.0566 | 23 | 13 | 6 |
| VOOG | 0.1042 | 0.0333 | 0.0069 | 0.0130 | 0.0177 | 0.0283 | 14 | 7 | 3 |
| VOOV | 0.0759 | 0.0177 | 0.0053 | 0.0046 | 0.0025 | 0.0000 | 5 | 1 | 0 |
| VOX | 0.0599 | 0.0136 | 0.0025 | 0.0724 | 0.0608 | 0.0755 | 78 | 24 | 8 |
| VTV | 0.0776 | 0.0213 | 0.0058 | 0.0139 | 0.0152 | 0.0000 | 15 | 6 | 0 |
| XLP | 0.0629 | 0.0133 | 0.0022 | 0.0919 | 0.0759 | 0.0660 | 99 | 30 | 7 |
| XLY | 0.0829 | 0.0330 | 0.0094 | 0.0464 | 0.1342 | 0.1509 | 50 | 53 | 16 |

**T11_five**

Disjunction firing rate: threshold 70 fires on 0.2136 of sessions (884 days), threshold 75 fires on 0.0749 of sessions (310 days), threshold 80 fires on 0.0205 of sessions (85 days).

| name | individual_70 | individual_75 | individual_80 | sole_trigger_70 | sole_trigger_75 | sole_trigger_80 | sole_days_70 | sole_days_75 | sole_days_80 |
|---|---|---|---|---|---|---|---|---|---|
| IOO | 0.0722 | 0.0145 | 0.0034 | 0.0486 | 0.0258 | 0.0235 | 43 | 8 | 2 |
| SPY | 0.0983 | 0.0280 | 0.0051 | 0.0192 | 0.0226 | 0.0235 | 17 | 7 | 2 |
| TQQQ | 0.1227 | 0.0471 | 0.0130 | 0.2421 | 0.3548 | 0.4824 | 214 | 110 | 41 |
| VTV | 0.0812 | 0.0220 | 0.0051 | 0.0520 | 0.0419 | 0.0471 | 46 | 13 | 4 |
| XLF | 0.0689 | 0.0210 | 0.0048 | 0.0701 | 0.1032 | 0.0941 | 62 | 32 | 8 |

The disjunction fires far more often than any single condition. In S1 at threshold 70 no individual name fires on more than 10.8 percent of sessions, yet the OR across eleven fires on 29.9 percent. In T11 the individual maximum is 12.3 percent and the OR fires on 21.4 percent. Widening a panel loosens the effective threshold.

Marginal contributions are highly unequal. In S1 at threshold 70, XLP (9.2 percent of firings), VOX (7.2) and XLY (4.6) are the names that most often fire alone, while SPY (0.56) and VOOV (0.46) almost never do. The names that carry the panel are the defensive and non-technology ones, which is the opposite of where the strategy thesis places its emphasis. In T11, TQQQ alone accounts for 24.2 percent of firings at threshold 70 and 48.2 percent at threshold 80; SPY accounts for 1.9 and 2.4 percent.

Periods 7 and 28, the disjunction rate with each name removed, and the sole-trigger day counts for all thresholds are in `overbought-panel-structure.csv`.

## What the measurements show, by decision

No decision is taken and no parameter is selected below. These are statements of what was measured.

### 1.12 Distribution coverage diagnostic

Cumulative return from Yahoo's adjusted close and cumulative return from raw close compounded with the dividend stream agree to within 4.05 basis points per annum for every one of the 35 tickers, against the 10 basis point flag threshold. No ticker is flagged. The six instruments where coverage matters most, BIL, BSV, AGG, BND, TLT and IEF, agree to within 0.09 basis points per annum. The adjustment factor moves only on recorded actions, with zero exceptions across the panel. The decision 1.5 adjusted open identity reproduces to one unit in the last place for all 35 tickers. The diagnostic measures internal consistency between two constructions drawn from the same actions feed, and by construction cannot detect a distribution the feed omits entirely.

### 2.20 SMH 2011 conversion continuity

The series is stitched, not truncated and not discontinuous on price. yfinance returns 6,589 sessions from 2000-06-05, spanning the HOLDRS era and the conversion, with no missing session against the SPY calendar, no single-day absolute return above 25 percent, and no split or distribution within 200 calendar days of the December 2011 boundary. The series is discontinuous on distributions: zero are recorded across the entire HOLDRS era and the first falls on 2012-12-24, 12.55 years after the first bar, so pre-2013 SMH total return is price return. Median volume falls by 81 percent across the boundary.

### 6.9 Overbought panel membership

The S1 eleven-name panel carries 1.77 effective independent signals and the T11 five-name panel 1.39, at every RSI period tested. The disjunction fires on 29.9 percent of sessions in S1 at threshold 70 against a maximum individual rate of 10.8 percent, and on 21.4 percent in T11 against 12.3 percent. Sole-trigger contributions are concentrated in XLP, VOX and XLY for S1 and in TQQQ for T11; SPY is nearly redundant in both, at 0.56 and 1.92 percent of firings respectively. Separately, RSI on a long leveraged fund and RSI on its underlying differ by 0.75 to 2.85 points on average and agree on the 70 threshold on 96.8 to 99.2 percent of sessions, so including both a leveraged fund and its underlying in one panel adds little that is independent.

### 6.16 S2 trend filter series, TQQQ own price against QQQ

At the canonical 200-session average, TQQQ and QQQ disagree about which side of their own moving average they sit on for 255 of 3,954 sessions, 6.45 percent, in 84 separate runs with a median run of 2 sessions and a maximum of 21. Their crossovers match at a median offset of +1 session but only 6.5 percent are simultaneous and the 5th to 95th percentile range spans -26.9 to +33.7 sessions. Upward crossings lag downward crossings by 6.7 sessions on average. Inside the 60 sessions after a 20 percent QQQ drawdown, agreement falls from 93.6 to 87.1 percent and the mean crossover offset rises from +0.86 to +11.1 sessions. The same pattern holds across all seven leveraged pairs and strengthens with leverage and underlying volatility.

### 6.20 PSQ and SH inverse redundancy

RSI(inverse) = 100 - RSI(underlying) holds to a mean absolute difference of 1.06 points for PSQ against QQQ and 1.26 for SH against SPY at period 14, with correlations of 0.994 and 0.989. Agreement is asymmetric: 99.5 and 99.7 percent at threshold 70 against 98.1 and 97.2 percent at threshold 30. Against each other, PSQ and SH are not redundant: 4.05 points mean absolute difference, correlation 0.892, 423 disagreement sessions at threshold 30. PSQ and SQQQ are near-duplicates at 0.89 points and correlation 0.996.

### 6.7 Vote threshold, and 6.8 vote membership

The S3 vote set of SPY, QQQ, SMH and SOXL carries 1.66 to 1.74 effective independent votes out of four, stable across all five average lengths and all three window bases. The vote count distribution is bimodal, with 66.4 percent of sessions unanimous bull and 11.7 percent unanimous bear at the 200-session average. Under simple majority, decision 6.7, removing SOXL changes the classification on 12 of 3,935 sessions, 0.30 percent, against 412 for SMH, 408 for SPY and 404 for QQQ. Substituting TLT for SOXL raises the effective independent votes to 2.29 to 2.38 on its native window and 2.21 to 2.39 restricted to the S3 window; KMLM raises it to 1.78 to 2.18 on a window beginning 2021; dropping SOXL leaves 1.47 to 1.54 out of three.

## Results that contradict an expectation stated in DECISIONS-OPEN-v2.md

Flagged, not reconciled.

### 6.8 states that SOXL and SMH votes are near-duplicates. They are the least duplicative equity pair in the set.

The register gives as the reason for adding a non-equity leg that "SOXL and SMH votes are near-duplicates". Measured, SOXL and SMH are the **least** similar of the three equity-equity pairings at every average length from 100 sessions upward, and SPY and QQQ are the most similar throughout.

| SMA | SMH/SOXL agreement | SPY/QQQ agreement | SMH/SOXL correlation | SPY/QQQ correlation |
|---|---|---|---|---|
| 50 | 0.9143 | 0.8962 | 0.8237 | 0.7406 |
| 100 | 0.8890 | 0.9202 | 0.7620 | 0.7575 |
| 150 | 0.8803 | 0.9378 | 0.7379 | 0.7702 |
| 200 | 0.8686 | 0.9454 | 0.7094 | 0.7890 |
| 250 | 0.8494 | 0.9454 | 0.6737 | 0.7718 |

At the canonical 200-session average, SMH and SOXL agree on 86.9 percent of sessions with a vote correlation of 0.709, while SPY and QQQ agree on 94.5 percent with a correlation of 0.789. The stated premise is contradicted by the measurement.

The conclusion the register draws from that premise, that SOXL contributes little, is separately supported by the leave-one-out result: removing SOXL changes the majority classification on 12 of 3,935 sessions, against 412 for SMH. But the mechanism is not duplication of SMH. SOXL is the *least* correlated vote in the set and is still nearly inert, because it is almost never on the winning side of a split decision. These are different facts and they point to different remedies.

### 6.9's framing assumes the two panels are comparable. Their windows differ by two years.

S1's eleven names support a common window only from 2012-04-11, bounded by QQQE, while T11's five support one from 2010-03-04, bounded by TQQQ. The 2010 to 2012 period, which contains a 20 percent QQQ drawdown, is in one panel's window and not the other's. Firing rates quoted side by side are not measured on the same sample.

### 1.12's tolerance is not the binding constraint on distribution quality.

The register treats 1.12 as a tolerance to be set. No tolerance in the plausible range separates anything in this panel: the worst ticker is at 4.05 basis points per annum and the median is at 0.06. The diagnostic as specified passes everything. The actual distribution defect found in this session, SMH's missing HOLDRS-era distributions, is invisible to it at any tolerance, because both sides of the comparison read the same feed.

## Limitations

- The final bar of every series is a live intraday print, as described under Provenance.
- Leveraged and inverse funds in this panel have had their stated daily multiples changed during their listed lives, including the Direxion change of 31 March 2020 covered by open decision 3.11. No multiple schedule was applied. Divergences measured here therefore blend the mechanical effects of daily reset and financing with any multiple change inside the window.
- The stress-regime subsets in Step 6 are small, between 224 and 951 sessions and between 5 and 23 matched crossovers per pair.
- Crossover matching uses a fixed 60-session window and a nearest-first one-to-one rule. Unmatched events are reported but not otherwise attributed.
- Effective independent counts from the eigenvalue method are computed on the full window and assume a stable correlation structure through it.
- Policy-rate levels referenced in the Step 4 discussion are not pulled in this session and are used only qualitatively. Decision 2.4 fixes FRED DFF as the source when a rate series is required.

## Files written

| file | contents |
|---|---|
| `outputs/session-00c/panel-coverage.csv` | per-ticker rows, first and last date, action counts, download status |
| `outputs/session-00c/etf-manifest.csv` | SHA-256, bytes, rows, dates, pull timestamp, yfinance version |
| `outputs/session-00c/pull-metadata.json` | versions and pull parameters |
| `outputs/session-00c/distribution-coverage.csv` | Step 2, all 35 tickers |
| `outputs/session-00c/smh-continuity.md` | Step 3, full inspection |
| `outputs/session-00c/rsi-leveraged-divergence.csv` | Step 4, pooled and by year |
| `outputs/session-00c/rsi-inverse-relationship.csv` | Step 5, pooled and by year, plus inverse against inverse |
| `outputs/session-00c/sma-crossover-divergence.csv` | Step 6, both scopes, three directions |
| `outputs/session-00c/vote-structure.csv` | Step 7, four sets, three window bases |
| `outputs/session-00c/overbought-panel-structure.csv` | Step 8, two panels, three RSI periods |
| `data/raw/etf/*.parquet` | frozen raw pulls, 35 files |
| `data/interim/etf-panel.parquet` | long panel, total return and adjusted close |

