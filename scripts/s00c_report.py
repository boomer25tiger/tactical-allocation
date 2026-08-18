"""Session 00C, Step 9. Assemble REPORT.md from the written artifacts.

Reads only the CSVs produced by the earlier steps, so every number in the report
is traceable to a file on disk. Reports measurements. Recommends nothing and
selects no parameter.
"""

import json

import numpy as np
import pandas as pd

from s00c_indicators import OUT

L = []
A = L.append


def md(df: pd.DataFrame, fmt=None, index=False) -> str:
    d = df.copy()
    if index:
        d = d.reset_index()
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            f = (fmt or {}).get(c, "{:.4f}")
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else f.format(v))
        else:
            d[c] = d[c].astype(str)
    head = "| " + " | ".join(str(c) for c in d.columns) + " |"
    rule = "|" + "|".join("---" for _ in d.columns) + "|"
    body = ["| " + " | ".join(r) + " |" for r in d.itertuples(index=False)]
    return "\n".join([head, rule] + body)


def pivot_md(df, index, columns, values, fmt="{:.4f}"):
    p = df.pivot(index=index, columns=columns, values=values)
    p = p.reset_index()
    p.columns.name = None
    return md(p, fmt={c: fmt for c in p.columns})


def main():
    meta = json.loads((OUT / "pull-metadata.json").read_text())
    cov = pd.read_csv(OUT / "panel-coverage.csv")
    man = pd.read_csv(OUT / "etf-manifest.csv")
    dist = pd.read_csv(OUT / "distribution-coverage.csv")
    smh = (OUT / "smh-continuity.md").read_text()
    d4 = pd.read_csv(OUT / "rsi-leveraged-divergence.csv")
    d5 = pd.read_csv(OUT / "rsi-inverse-relationship.csv")
    d6 = pd.read_csv(OUT / "sma-crossover-divergence.csv")
    d7 = pd.read_csv(OUT / "vote-structure.csv", dtype={"key1": str, "key2": str})
    d8 = pd.read_csv(OUT / "overbought-panel-structure.csv",
                     dtype={"key1": str, "key2": str})

    A("# Session 00C, indicator relationships across the equity ETF panel")
    A("")
    A("Measurement only. No decision is made, no parameter is selected, and no "
      "recommendation is given. No strategy return, Sharpe ratio, allocation, "
      "portfolio weight, or performance statistic is computed anywhere in this "
      "session. Every quantity below is a property of a single instrument's "
      "price series or a comparison between two such properties.")
    A("")
    A("Informs decisions 6.9, 6.16, 6.7. Closes 1.12 and 2.20 by measurement. "
      "Addresses 6.20 and documents 6.8.")
    A("")

    # ------------------------------------------------------------ provenance
    A("## Provenance")
    A("")
    A(f"- yfinance version: **{meta['yfinance_version']}**")
    A(f"- pull timestamp, UTC: **{meta['pull_timestamp_utc']}**")
    A(f"- pull date, local: **{meta['pull_date_local']}**")
    A(f"- pandas {meta['pandas_version']}, numpy {meta['numpy_version']}, "
      f"python {meta['python_version']}")
    A(f"- request: `start={meta['start_requested']}`, "
      f"`auto_adjust={meta['auto_adjust']}`, `actions={meta['actions']}`")
    A(f"- tickers requested: **{meta['n_tickers']}**, failed: **{meta['n_failed']}**")
    A("- raw pulls: `data/raw/etf/<TICKER>.parquet`, one file per ticker, "
      "SHA-256 and byte count in `outputs/session-00c/etf-manifest.csv`")
    A("- long panel: `data/interim/etf-panel.parquet`")
    A("")
    A("### Pull integrity warning")
    A("")
    A(f"The pull ran at {meta['pull_timestamp_utc']}, during the regular session "
      f"of {meta['pull_date_local']}. The final bar of every ticker is therefore "
      "a live intraday print, not a settled close. SPY volume on that bar is "
      "12,650,704 against a trailing sixty-session median of 47,211,550, which "
      "confirms the bar is partial. Under decision 1.1 the pull is frozen and is "
      "not repeated, so this bar is now part of the frozen data. It is one "
      "session out of between 1,432 and 7,958 per ticker and moves no statistic "
      "in this report materially, but any later re-pull would not reproduce the "
      "recorded SHA-256 values, and the manifest hashes therefore certify this "
      "file set rather than a reproducible download.")
    A("")

    # ------------------------------------------------------------ step 1
    A("## Step 1. Panel coverage")
    A("")
    A(f"All {meta['n_tickers']} tickers returned data. No ticker failed to "
      "download and no ticker returned an empty frame.")
    A("")
    c = cov[["ticker", "group", "rows", "first_date", "last_date", "n_dividends",
             "n_splits", "n_capital_gains", "n_missing_close"]]
    A(md(c.sort_values(["group", "ticker"])))
    A("")
    A("Capital gain distributions are zero for every ticker in the panel, so "
      "Yahoo's dividend stream is the entire recorded distribution stream and "
      "the total return construction loses nothing by using it alone.")
    A("")
    A("The total return series is built as "
      "`r_t = (Close_t + Dividend_t) / Close_(t-1) - 1`, with reinvestment at "
      "the ex-date close per decision 1.11, on the split-adjusted close. Yahoo's "
      "adjusted close is carried separately in the same file.")
    A("")
    A("Shortest histories, which bound every window that uses them: "
      + ", ".join(f"**{r.ticker}** from {r.first_date} ({r.rows:,} sessions)"
                  for r in cov.nsmallest(4, "rows").itertuples()) + ".")
    A("")

    # ------------------------------------------------------------ step 2
    A("## Step 2. Distribution coverage diagnostic. Closes 1.12")
    A("")
    A("Cumulative return from Yahoo's adjusted close against cumulative return "
      "from the raw close compounded with the dividend stream, over each "
      "ticker's full window. The flag threshold is an annualized difference "
      "above 10 basis points.")
    A("")
    A(f"**No ticker in the panel is flagged.** The largest absolute annualized "
      f"difference across all 35 tickers is "
      f"**{dist.abs_diff_ann_bp_adj_vs_tr.max():.2f} basis points** "
      f"({dist.loc[dist.abs_diff_ann_bp_adj_vs_tr.idxmax(), 'ticker']}), against "
      f"a threshold of {10:.0f}. The median absolute annualized difference is "
      f"{dist.abs_diff_ann_bp_adj_vs_tr.median():.3f} basis points.")
    A("")
    cc = ["ticker", "n_sessions", "n_distribution_events", "cum_ret_adjclose",
          "cum_ret_total_return", "abs_diff_cum_adj_vs_tr",
          "diff_ann_bp_adj_vs_tr", "flag_gt_10bp", "max_daily_ret_diff_bp"]
    A(md(dist[cc], fmt={"cum_ret_adjclose": "{:,.4f}",
                        "cum_ret_total_return": "{:,.4f}",
                        "abs_diff_cum_adj_vs_tr": "{:.6f}",
                        "diff_ann_bp_adj_vs_tr": "{:.3f}",
                        "max_daily_ret_diff_bp": "{:.3f}"}))
    A("")
    A("### The six instruments where distribution coverage matters most")
    A("")
    f = dist[dist.focus_instrument].sort_values("abs_diff_ann_bp_adj_vs_tr",
                                                ascending=False)
    A(md(f[cc + ["total_distributions_per_share"]],
         fmt={"cum_ret_adjclose": "{:,.4f}", "cum_ret_total_return": "{:,.4f}",
              "abs_diff_cum_adj_vs_tr": "{:.6f}", "diff_ann_bp_adj_vs_tr": "{:.3f}",
              "max_daily_ret_diff_bp": "{:.3f}",
              "total_distributions_per_share": "{:,.4f}"}))
    A("")
    A("These are the highest-distribution-count instruments in the panel, "
      "between 126 and 289 events each, and they are the tightest in it. Every "
      "one agrees to under a tenth of a basis point per annum. BSV agrees to "
      "0.0004 basis points over 4,870 sessions and 232 distributions.")
    A("")
    A("### The literal price-plus-summed-distributions construction")
    A("")
    A("Decision 1.12 as written compares against price return plus summed "
      "distributions. That construction does not reinvest, so it is not "
      "comparable to an adjusted close over long windows and diverges by an "
      "amount that grows with yield and horizon rather than by a data defect. "
      "It is carried in the CSV as `cum_ret_price_plus_sum_dist` and "
      "`diff_ann_bp_adj_vs_simple` and is not the basis of the flag. For the six "
      "focus instruments the two constructions differ as follows.")
    A("")
    A(md(dist[dist.focus_instrument][
        ["ticker", "cum_ret_adjclose", "cum_ret_total_return",
         "cum_ret_price_plus_sum_dist", "diff_ann_bp_adj_vs_tr",
         "diff_ann_bp_adj_vs_simple"]],
        fmt={"cum_ret_adjclose": "{:,.4f}", "cum_ret_total_return": "{:,.4f}",
             "cum_ret_price_plus_sum_dist": "{:,.4f}",
             "diff_ann_bp_adj_vs_tr": "{:.3f}",
             "diff_ann_bp_adj_vs_simple": "{:,.1f}"}))
    A("")
    A("The last column is the reason the compounded construction is the one "
      "carrying the flag: on TLT the non-reinvesting construction sits "
      f"{abs(dist.loc[dist.ticker=='TLT','diff_ann_bp_adj_vs_simple'].iloc[0]):,.0f} "
      "basis points per annum away from the adjusted close purely through the "
      "absence of reinvestment.")
    A("")
    A("### Adjusted open, decision 1.5")
    A("")
    A(f"`AdjOpen = Open x (AdjClose / Close)` reproduces the raw open-to-close "
      f"ratio for **all 35 tickers**. The largest relative error anywhere in the "
      f"panel is **{dist.adjopen_max_rel_error.max():.3e}**, which is one unit "
      f"in the last place of double precision. Failures at a 1e-9 relative "
      f"tolerance: **{int(dist.adjopen_n_fail_1e_9.sum())}**. Failures at 1e-12: "
      f"**{int(dist.adjopen_n_fail_1e_12.sum())}**.")
    A("")
    A("### Adjustment factor behaviour")
    A("")
    nm = int(dist.n_adjfactor_moves_without_recorded_action.sum())
    na = int(dist.n_recorded_actions_without_adjfactor_move.sum())
    A(f"The ratio `AdjClose / Close` moves on a recorded dividend or split and "
      f"on nothing else. Across the whole panel there are **{nm}** sessions "
      f"where the factor moved by more than one part in 100,000 without a "
      f"recorded action, and **{na}** sessions carrying a recorded action with "
      f"no factor move. Yahoo's adjustment is internally consistent with the "
      f"actions it publishes.")
    A("")
    A("### What the diagnostic cannot see, and one place it matters")
    A("")
    late = dist[dist.flag_distribution_stream_starts_late].sort_values(
        "years_listing_to_first_distribution", ascending=False)
    A("The test compares two constructions that are both derived from the same "
      "Yahoo actions feed. If the feed omits a distribution, both sides omit it "
      "identically and the difference stays at zero. The test measures internal "
      "consistency, not completeness. Tickers whose recorded distribution stream "
      "begins more than three years after their first bar:")
    A("")
    A(md(late[["ticker", "first_date", "first_distribution_date",
               "years_listing_to_first_distribution", "n_distribution_events",
               "diff_ann_bp_adj_vs_tr"]],
        fmt={"years_listing_to_first_distribution": "{:.2f}",
             "diff_ann_bp_adj_vs_tr": "{:.3f}"}))
    A("")
    A("Most of these are economically plausible rather than defective. QQQ's "
      "first recorded distribution in December 2003 is consistent with the "
      "Nasdaq-100 paying almost nothing until Microsoft initiated its dividend "
      "that year. TQQQ, SQQQ and TECS are leveraged and inverse funds whose "
      "distributions come from collateral income, which was near zero through "
      "the period concerned. IBB is a low-yield biotech index fund. **SMH is "
      "different, and is treated in Step 3.**")
    A("")

    # ------------------------------------------------------------ step 3
    A("## Step 3. SMH continuity at the 2011 conversion. Closes 2.20")
    A("")
    A("Full inspection in `outputs/session-00c/smh-continuity.md`. Summary "
      "below.")
    A("")
    s = dist[dist.ticker == "SMH"].iloc[0]
    A(f"- First date returned: **{s.first_date}**, {int(s.n_sessions):,} sessions "
      f"to {s.last_date}. yfinance returns the HOLDRS-era history; the series is "
      "not truncated at the conversion.")
    A("- No missing session relative to the SPY trading calendar over the common "
      "window, in either direction.")
    A("- No single-day absolute total return above 25 percent anywhere in the "
      "history. The largest is 17.16 percent, on 2025-04-09, nowhere near the "
      "conversion.")
    A("- No split and no distribution within 200 calendar days either side of "
      "the December 2011 conversion. The only recorded split is 2023-05-05.")
    A("- Daily return dispersion is 2.080 percent in the 60 sessions before the "
      "boundary and 1.231 percent in the 60 after. The fall is large but is not "
      "evidence of a splice: the pre-boundary window covers October to December "
      "2011, the tail of the eurozone volatility episode, and the post-boundary "
      "window covers the calm of early 2012. No single session at the boundary "
      "carries an outsized move.")
    A("")
    A("**Verdict: stitched on price, discontinuous on distributions.**")
    A("")
    A("The price series crosses the conversion with no detectable break. The "
      "distribution series does not. yfinance records **zero distributions "
      "across the entire HOLDRS era**, 2000-06-05 to 2012-12-23, and the first "
      "of the 14 recorded distributions falls on 2012-12-24, 12.55 years after "
      "the first bar. The HOLDRS was a grantor trust that passed constituent "
      "dividends through to holders, so those distributions occurred and are "
      "absent from the feed. SMH total return before December 2012 is a price "
      "return wearing a total return label, and Step 2 cannot detect this "
      "because Yahoo's adjusted close omits exactly the same cash flows.")
    A("")
    A("A second marker sits at the boundary and is consistent with a vehicle "
      "change rather than a price break: median daily volume falls from "
      "15,201,800 in the 60 sessions before to 2,871,700 in the 60 after, a "
      "ratio of 0.19.")
    A("")
    A("Nothing was adjusted. The economic discontinuity in the underlying "
      "vehicle, a fixed unrebalanced grantor-trust basket with a shrinking "
      "constituent count before the conversion against a rebalanced index fund "
      "after it, produces no price artefact and cannot be detected by any test "
      "in this session.")
    A("")

    # ------------------------------------------------------------ step 4
    A("## Step 4. RSI divergence, long leveraged fund against underlying. "
      "Informs 6.9")
    A("")
    A("Wilder RSI, alpha = 1/n per decision 1.6, on total return series, at "
      "periods 7, 14 and 28. Seven long leveraged pairs. Signed difference is "
      "RSI(leveraged) minus RSI(underlying).")
    A("")
    A("### Pooled over each pair's full common window")
    A("")
    p4 = d4[(d4.window == "pooled")][
        ["pair", "rsi_period", "n_sessions", "first_date", "mean_abs_diff",
         "p95_abs_diff", "p99_abs_diff", "max_abs_diff", "mean_signed_diff",
         "correlation"]]
    A(md(p4, fmt={"mean_abs_diff": "{:.3f}", "p95_abs_diff": "{:.3f}",
                  "p99_abs_diff": "{:.3f}", "max_abs_diff": "{:.3f}",
                  "mean_signed_diff": "{:.3f}", "correlation": "{:.4f}"}))
    A("")
    A("RSI is invariant to a constant multiple on returns, so a frictionless "
      "constant-leverage fund would show a difference of exactly zero. The "
      "observed difference is the footprint of daily reset, financing, fees and "
      "variance drag. It is small in level, between 0.75 and 2.85 RSI points on "
      "average, and correlations run from 0.974 to 0.999. The signed difference "
      "is negative for **every pair at every period**, ranging from -0.43 to "
      "-1.76, which is the expected direction: drag pushes the leveraged fund's "
      "RSI below its underlying's.")
    A("")
    A("### Crossing agreement, pooled")
    A("")
    t4 = d4[(d4.window == "pooled")][
        ["pair", "rsi_period", "n_sessions", "agree_70", "n_disagree_70",
         "agree_80", "n_disagree_80", "agree_30", "n_disagree_30",
         "agree_20", "n_disagree_20"]]
    A(md(t4))
    A("")
    A("At the canonical period 14 and the canonical tier-one threshold 70, "
      "agreement runs from 96.75 percent (SOXL against SMH) to 99.15 percent "
      "(QLD against QQQ). The disagreement counts are the operative number: "
      "between 43 and 134 sessions per pair over 4,100 to 5,100 sessions.")
    A("")
    A("### By year, canonical period 14")
    A("")
    A("Mean absolute RSI difference:")
    A("")
    y = d4[(d4.rsi_period == 14) & (d4.window != "pooled")]
    A(pivot_md(y, "window", "pair", "mean_abs_diff", "{:.3f}"))
    A("")
    A("Agreement at threshold 70:")
    A("")
    A(pivot_md(y, "window", "pair", "agree_70", "{:.4f}"))
    A("")
    A("Annualized standard deviation of the underlying's daily total return, "
      "carried so the divergence can be read against volatility as well as "
      "against the rate environment:")
    A("")
    A(pivot_md(y, "window", "pair", "underlying_ann_ret_sd", "{:.3f}"))
    A("")
    A("Periods 7 and 28, and the remaining thresholds, by year, are in "
      "`rsi-leveraged-divergence.csv`.")
    A("")
    A("### The rate-environment expectation")
    A("")
    A("The session prompt states that financing drag varies with the rate "
      "environment and that the divergence should widen when rates are high. "
      "**The measurement supports this.** QLD against QQQ is the cleanest test "
      "in the panel: it is the longest leveraged history, it spans two full rate "
      "cycles, and at 2x it carries the least variance drag, so the financing "
      "component is least contaminated.")
    A("")
    q = d4[(d4.pair == "QLD/QQQ") & (d4.rsi_period == 14) & (d4.window != "pooled")]
    A(md(q[["window", "n_sessions", "mean_abs_diff", "mean_signed_diff",
            "underlying_ann_ret_sd"]],
         fmt={"mean_abs_diff": "{:.4f}", "mean_signed_diff": "{:.4f}",
              "underlying_ann_ret_sd": "{:.4f}"}))
    A("")
    A("Divergence sits near 1.1 to 1.4 RSI points in the high-rate years 2006, "
      "2007, 2023, 2024 and 2025, and near 0.37 to 0.58 in the zero-rate years "
      "2010 to 2015 and 2021. Volatility confounds the raw comparison, so the "
      "controlled version is a pair of years with almost identical underlying "
      "dispersion and opposite rate regimes:")
    A("")
    A("| year | QQQ annualized return sd | approximate policy rate | "
      "mean absolute RSI difference |")
    A("|---|---|---|---|")
    A("| 2011 | 0.237 | near zero | 0.576 |")
    A("| 2025 | 0.236 | around 4 percent | 1.099 |")
    A("")
    A("At matched volatility the divergence roughly doubles between the "
      "zero-rate and the high-rate year. The reverse control points the same "
      "way: 2020 carries the second-highest volatility in the sample, 0.356, at "
      "a zero policy rate, and produces a divergence of 0.782, lower than 2023 "
      "at 0.179 volatility and a 5 percent rate, which produces 1.030.")
    A("")

    # ------------------------------------------------------------ step 5
    A("## Step 5. RSI on the inverse fund against 100 minus RSI on the "
      "underlying. Addresses 6.20")
    A("")
    A("The proposition under test is RSI(inverse) = 100 - RSI(underlying). "
      "Signed difference is RSI(inverse) minus [100 - RSI(underlying)]. "
      "Correlation is between those same two series. Crossing agreement tests "
      "whether RSI(inverse) above 70 coincides with RSI(underlying) below 30, "
      "and correspondingly at 80, 30 and 20.")
    A("")
    p5 = d5[(d5.window == "pooled") & (d5.pair_type == "fund_vs_underlying")]
    A(md(p5[["pair", "rsi_period", "n_sessions", "mean_abs_diff", "p95_abs_diff",
             "p99_abs_diff", "max_abs_diff", "mean_signed_diff", "correlation"]],
        fmt={"mean_abs_diff": "{:.3f}", "p95_abs_diff": "{:.3f}",
             "p99_abs_diff": "{:.3f}", "max_abs_diff": "{:.3f}",
             "mean_signed_diff": "{:.3f}", "correlation": "{:.4f}"}))
    A("")
    A("Crossing agreement:")
    A("")
    A(md(p5[["pair", "rsi_period", "n_sessions", "agree_70", "n_disagree_70",
             "agree_80", "n_disagree_80", "agree_30", "n_disagree_30",
             "agree_20", "n_disagree_20"]]))
    A("")
    A("The identity holds closely but not exactly. Mean absolute difference "
      "runs from 1.05 to 3.16 RSI points and correlations from 0.930 to 0.996. "
      "PSQ and SH, the two unlevered inverses, are the tightest: 1.06 and 1.26 "
      "RSI points at period 14.")
    A("")
    A("The agreement rates are asymmetric, and the asymmetry is systematic. At "
      "period 14 every pair agrees more often on the overbought side of the "
      "inverse than on the oversold side. SH against SPY agrees on 99.66 percent "
      "of sessions at threshold 70 but only 97.21 percent at threshold 30, 141 "
      "disagreement sessions against 17. SOXS against SMH is 99.54 percent "
      "against 95.83 percent, 19 sessions against 172. Testing whether the "
      "inverse is oversold is a materially worse proxy for the underlying being "
      "overbought than the reverse.")
    A("")
    A("### Inverse against inverse, directly. The specific question in 6.20")
    A("")
    A("Decision 6.20 names PSQ and SH. The comparison below is direct, with no "
      "100-minus transform, and asks whether one inverse carries information the "
      "other does not.")
    A("")
    x5 = d5[(d5.window == "pooled") & (d5.pair_type == "inverse_vs_inverse")]
    A(md(x5[["pair", "rsi_period", "n_sessions", "mean_abs_diff", "p95_abs_diff",
             "max_abs_diff", "correlation", "agree_70", "n_disagree_70",
             "agree_30", "n_disagree_30"]],
        fmt={"mean_abs_diff": "{:.3f}", "p95_abs_diff": "{:.3f}",
             "max_abs_diff": "{:.3f}", "correlation": "{:.4f}"}))
    A("")
    A("PSQ and SH are **not** duplicates of each other. At period 14 they differ "
      "by 4.05 RSI points on average with a correlation of 0.892, and they "
      "disagree on 423 of 5,056 sessions at threshold 30. PSQ and SQQQ **are** "
      "near-duplicates: 0.89 RSI points and a correlation of 0.996, which is "
      "expected since both track QQQ at different multiples. The separation "
      "between PSQ and SH is the separation between QQQ and SPY, not anything "
      "contributed by the inverse wrappers.")
    A("")

    # ------------------------------------------------------------ step 6
    A("## Step 6. SMA crossover divergence. Informs 6.16")
    A("")
    A("Simple moving averages at 20, 50, 100, 150, 200 and 250 sessions on "
      "total return series. Offsets are leveraged crossover position minus "
      "underlying crossover position in sessions, so a positive offset means the "
      "leveraged series crossed later. Crossovers are matched one to one, "
      "nearest first by absolute offset, within a 60-session window; unmatched "
      "events are counted separately.")
    A("")
    A("### Agreement on whether price sits above the average")
    A("")
    m = (d6.scope == "all") & (d6.direction == "all")
    A(pivot_md(d6[m], "sma_length", "pair", "frac_agree_above_below", "{:.4f}"))
    A("")
    A("Disagreement sessions:")
    A("")
    A(pivot_md(d6[m], "sma_length", "pair", "n_disagree_sessions", "{:,.0f}"))
    A("")
    A("Agreement falls monotonically as the average lengthens, from 93 to 98 "
      "percent at 20 sessions down to 85 to 95 percent at 250. At the canonical "
      "200-session average, decision 6.5, disagreement runs from 210 sessions "
      "(QLD against QQQ) to 517 (SOXL against SMH).")
    A("")
    A("### Disagreement run lengths, canonical 200-session average")
    A("")
    A(md(d6[m & (d6.sma_length == 200)][
        ["pair", "n_sessions", "n_disagree_sessions", "n_disagreement_runs",
         "run_mean", "run_median", "run_p95", "run_max", "run_n_len_1",
         "run_n_len_2_5", "run_n_len_6_20", "run_n_len_gt_20"]],
        fmt={"run_mean": "{:.2f}", "run_median": "{:.1f}", "run_p95": "{:.2f}"}))
    A("")
    A("Most disagreements are short. The median run is one to three sessions and "
      "roughly a third are a single session. The tail is not short: SOXL against "
      "SMH has four runs longer than 20 sessions and a maximum of 72 consecutive "
      "sessions on which the leveraged fund and its underlying disagree about "
      "which side of the 200-day average they are on. SPXL against SPY reaches "
      "48 and LABU against XBI reaches 26.")
    A("")
    A("### Crossover offsets, canonical 200-session average, full window")
    A("")
    m2 = (d6.scope == "all") & (d6.sma_length == 200)
    A(md(d6[m2][["pair", "direction", "n_crossovers_underlying",
                 "n_crossovers_leveraged", "n_matched", "n_unmatched_underlying",
                 "n_unmatched_leveraged", "mean_offset", "median_offset",
                 "sd_offset", "p05_offset", "p95_offset", "min_offset",
                 "max_offset", "frac_offset_zero", "frac_abs_offset_le_1"]],
        fmt={"mean_offset": "{:.2f}", "median_offset": "{:.1f}",
             "sd_offset": "{:.2f}", "p05_offset": "{:.1f}",
             "p95_offset": "{:.1f}", "frac_offset_zero": "{:.3f}",
             "frac_abs_offset_le_1": "{:.3f}"}))
    A("")
    A("Median offsets sit at or near zero but the distribution is wide and "
      "asymmetric. Only 3 to 26 percent of matched crossovers are simultaneous, "
      "and only 13 to 48 percent fall within one session. The 5th to 95th "
      "percentile range spans roughly 27 sessions before to 48 sessions after. "
      "A material fraction of crossovers cannot be matched at all inside a "
      "60-session window: TECL produces 134 crossovers against XLK's 90 at the "
      "200-day average, and 64 of TECL's are unmatched.")
    A("")
    A("**Upward crossings lag more than downward crossings, for all seven "
      "pairs.** At the 200-day average the mean up-offset exceeds the mean "
      "down-offset by 8.5 sessions for LABU, 8.3 for SOXL, 7.4 for TECL, 6.7 for "
      "TQQQ, 5.3 for SPXL, 3.6 for FAS and 2.4 for QLD. This is the "
      "variance-drag signature: "
      "after a decline the leveraged fund must climb further than its underlying "
      "to regain its own moving average, so it confirms an uptrend late.")
    A("")
    A("### Full offset table across all SMA lengths")
    A("")
    A(md(d6[(d6.scope == "all") & (d6.direction != "all")][
        ["pair", "sma_length", "direction", "n_matched", "mean_offset",
         "median_offset", "p05_offset", "p95_offset", "frac_offset_zero"]],
        fmt={"mean_offset": "{:.2f}", "median_offset": "{:.1f}",
             "p05_offset": "{:.1f}", "p95_offset": "{:.1f}",
             "frac_offset_zero": "{:.3f}"}))
    A("")
    A("### Stress regime, the 60 sessions after each 20 percent underlying "
      "drawdown")
    A("")
    A("A drawdown entry is a session on which the underlying's total return "
      "index first falls 20 percent or more below its running maximum. The "
      "stress window is the union of the 60 sessions following each entry.")
    A("")
    m3 = (d6.direction == "all") & (d6.sma_length == 200)
    A(md(d6[m3][["pair", "scope", "n_sessions", "n_drawdown_entries",
                 "frac_agree_above_below", "n_disagree_sessions",
                 "n_disagreement_runs", "run_max", "n_matched", "mean_offset",
                 "median_offset"]],
        fmt={"frac_agree_above_below": "{:.4f}", "mean_offset": "{:.2f}",
             "median_offset": "{:.1f}"}))
    A("")
    A("**The prompt's expectation that variance drag concentrates the divergence "
      "in stress holds, and the effect is large.** Agreement falls for all seven "
      "pairs: SOXL against SMH from 86.9 to 74.1 percent, LABU against XBI from "
      "85.3 to 73.2, TECL against XLK from 91.4 to 79.1, TQQQ against QQQ from "
      "93.6 to 87.1. Crossover offsets move sharply positive, meaning the "
      "leveraged fund crosses later: SPXL against SPY runs a mean offset of "
      "+33.6 sessions and a median of +35 inside the stress window against a "
      "full-window median of 0, TECL +24.2 against +1, SOXL +11.2 against +1.")
    A("")
    A("Sample sizes inside the stress window are small and should be read as "
      "such. SPXL has 8 drawdown entries, 224 stress sessions and 5 matched "
      "crossovers; TECL has 6 matched crossovers. The direction is consistent "
      "across all seven pairs; the magnitudes for the narrower pairs are not "
      "precisely estimated.")
    A("")

    # ------------------------------------------------------------ step 7
    A("## Step 7. Vote structure. Informs 6.7, documents 6.8")
    A("")
    A("A vote is one instrument's total return index against its own simple "
      "moving average. The effective number of independent votes is the "
      "reciprocal of the sum of squared normalized eigenvalues of the vote "
      "correlation matrix, so it runs from 1 for perfectly redundant votes to k "
      "for perfectly independent ones.")
    A("")
    A("The four vote sets have very different maximal windows, so each is "
      "reported on its own window and on two shared ones: `common_with_S3` "
      "restricts to the window the current set supports, and `common_all_sets` "
      "restricts to the window every set including KMLM supports.")
    A("")
    for basis in ("native", "common_with_S3", "common_all_sets"):
        e = d7[(d7.metric == "effective_independent_votes") &
               (d7.window_basis == basis)]
        ns = d7[d7.window_basis == basis].groupby("vote_set").n_sessions.first()
        A(f"Effective independent votes, `{basis}`:")
        A("")
        A(pivot_md(e, "sma_length", "vote_set", "value", "{:.3f}"))
        A("")
        A("Sessions per set: " + ", ".join(f"{k} {v:,}" for k, v in ns.items()) + ".")
        A("")
    A("The ranking is stable across all three window bases and all five average "
      "lengths: alt1 above alt2 above S3 above alt3 in absolute count. On native "
      "windows, S3 measures 1.658 to 1.742 effective votes out of four, alt1 "
      "with TLT measures 2.293 to 2.383, alt2 with KMLM measures 1.780 to 2.177, "
      "and alt3 with three votes measures 1.471 to 1.544 out of three. As a "
      "fraction of the votes cast, alt3 at 0.49 to 0.51 exceeds S3 at 0.41 to "
      "0.44, and alt1 at 0.57 to 0.60 exceeds both.")
    A("")
    A("### S3 pairwise structure")
    A("")
    A("Pairwise agreement, fraction of sessions the two votes are in the same "
      "state:")
    A("")
    s3a = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
             & (d7.metric == "pairwise_agreement")].copy()
    s3a["vote_pair"] = s3a.key1 + "/" + s3a.key2
    A(pivot_md(s3a, "sma_length", "vote_pair", "value", "{:.4f}"))
    A("")
    A("Pairwise correlation of the vote indicators:")
    A("")
    s3c = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
             & (d7.metric == "pairwise_correlation")].copy()
    s3c["vote_pair"] = s3c.key1 + "/" + s3c.key2
    A(pivot_md(s3c, "sma_length", "vote_pair", "value", "{:.4f}"))
    A("")
    A("### Vote count distribution, S3")
    A("")
    v = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
           & (d7.metric == "vote_count_fraction")]
    A(pivot_md(v, "sma_length", "key1", "value", "{:.4f}"))
    A("")
    A("The distribution is strongly bimodal. At the 200-session average, 66.4 "
      "percent of sessions have all four votes bullish and 11.7 percent have "
      "none, leaving 21.9 percent split across the three intermediate states. "
      "The votes move together far more often than they disagree.")
    A("")
    A("### Bull classification and leave-one-out sensitivity, S3")
    A("")
    A("Fraction of sessions classified bull at each absolute vote threshold:")
    A("")
    fb = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
            & (d7.metric == "frac_bull")]
    A(pivot_md(fb, "sma_length", "key1", "value", "{:.4f}"))
    A("")
    A("Fraction of sessions on which the classification flips when one vote is "
      "removed, holding the absolute threshold fixed, at the 200-session "
      "average:")
    A("")
    fl = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
            & (d7.metric == "flip_fraction_leave_one_out")
            & (d7.sma_length == 200)]
    A(pivot_md(fl, "key2", "key1", "value", "{:.4f}"))
    A("")
    A("The threshold-4 column is degenerate and should be read as an artefact "
      "of the convention, not a finding: with the absolute threshold held at 4 "
      "and only three votes remaining, the bull condition is unsatisfiable, so "
      "the flip fraction necessarily equals the bull fraction for every vote. "
      "The informative columns are thresholds 2 and 3.")
    A("")
    A("**SOXL is close to inert.** At threshold 2 its removal changes the "
      "classification on 0.28 percent of sessions and at threshold 3 on 0.30 "
      "percent, against 6.5 to 6.7 percent and 10.3 to 10.5 percent for SPY, QQQ "
      "and SMH. Under decision 6.7's simple majority, threshold 3 of 4, that is "
      "**12 sessions out of 3,935** for SOXL against 412 for SMH, 408 for SPY "
      "and 404 for QQQ.")
    A("")
    A("### Alternative vote sets")
    A("")
    for s in ["alt1_TLT_for_SOXL", "alt2_KMLM_for_SOXL", "alt3_drop_SOXL"]:
        sub = d7[(d7.vote_set == s) & (d7.window_basis == "native")]
        A(f"**{s}**, members {sub.members.iloc[0].replace('|', ', ')}, "
          f"{sub.n_sessions.iloc[0]:,} sessions at the 50-session average, "
          f"{sub[sub.sma_length == 200].first_date.iloc[0]} to "
          f"{sub[sub.sma_length == 200].last_date.iloc[0]} at the 200-session "
          f"average.")
        A("")
        a = sub[sub.metric == "pairwise_agreement"].copy()
        a["vote_pair"] = a.key1 + "/" + a.key2
        A(pivot_md(a, "sma_length", "vote_pair", "value", "{:.4f}"))
        A("")
        fb2 = sub[sub.metric == "frac_bull"]
        A("Fraction bull by threshold:")
        A("")
        A(pivot_md(fb2, "sma_length", "key1", "value", "{:.4f}"))
        A("")
    A("KMLM's window is the binding constraint on alt2: it supports 1,383 "
      "sessions at the 50-session average and 1,233 at the 250-session average, "
      "beginning 2021-09-17 for the 200-session case. Any comparison involving "
      "alt2 on its native window covers a single rate cycle.")
    A("")
    A("Per-vote leave-one-out flip fractions for every set, threshold and "
      "average length are in `vote-structure.csv`.")
    A("")

    # ------------------------------------------------------------ step 8
    A("## Step 8. Overbought panel structure. Informs 6.9")
    A("")
    A("The disjunction is the OR across the panel: it fires on a session if any "
      "member's RSI exceeds the threshold. Marginal contribution is the fraction "
      "of disjunction firings on which that name is the only member firing.")
    A("")
    w = d8.groupby(["panel", "rsi_period"])[
        ["n_sessions", "first_date", "last_date"]].first().reset_index()
    A("Common windows, set by the shortest member of each panel:")
    A("")
    A(md(w))
    A("")
    A("The two panels are not measured over the same window. S1 starts "
      "2012-04-11 because QQQE lists in March 2012; T11 starts 2010-03-04 "
      "because TQQQ lists in February 2010. Firing rates are not directly "
      "comparable across panels.")
    A("")
    A("### Effective number of independent signals")
    A("")
    A(pivot_md(d8[d8.metric == "effective_independent_signals"],
               "rsi_period", "panel", "value", "{:.3f}"))
    A("")
    A("Mean pairwise RSI correlation within panel:")
    A("")
    A(pivot_md(d8[d8.metric == "mean_pairwise_rsi_correlation"],
               "rsi_period", "panel", "value", "{:.4f}"))
    A("")
    A("**Eleven names carry 1.77 independent signals. Five names carry 1.39.** "
      "The result is insensitive to the RSI period. Mean pairwise correlation is "
      "0.70 in S1 and 0.79 in T11; the smaller panel is the more redundant one "
      "per name, because it is entirely large-cap US equity beta while S1 at "
      "least contains XLP and VOX.")
    A("")
    for p in ["S1_eleven", "T11_five"]:
        A(f"### {p}, pairwise RSI correlation at period 14")
        A("")
        sub = d8[(d8.panel == p) & (d8.rsi_period == 14)
                 & (d8.metric == "pairwise_rsi_correlation")].copy()
        names = d8[d8.panel == p].members.iloc[0].split("|")
        M = pd.DataFrame(np.eye(len(names)), index=names, columns=names)
        for r in sub.itertuples():
            M.loc[r.key1, r.key2] = M.loc[r.key2, r.key1] = r.value
        A(md(M.reset_index().rename(columns={"index": ""}),
             fmt={c: "{:.3f}" for c in M.columns}))
        A("")
    A("### Firing rates and marginal contribution")
    A("")
    for p in ["S1_eleven", "T11_five"]:
        A(f"**{p}**")
        A("")
        sub = d8[(d8.panel == p) & (d8.rsi_period == 14)]
        dj = sub[sub.metric == "disjunction_firing_rate"].set_index("key1")["value"]
        djd = sub[sub.metric == "disjunction_firing_days"].set_index("key1")["value"]
        A("Disjunction firing rate: " + ", ".join(
            f"threshold {t} fires on {dj[t]:.4f} of sessions ({int(djd[t]):,} days)"
            for t in ["70", "75", "80"]) + ".")
        A("")
        ind = sub[sub.metric == "individual_firing_rate"].pivot(
            index="key2", columns="key1", values="value").add_prefix("individual_")
        mc = sub[sub.metric == "marginal_contribution"].pivot(
            index="key2", columns="key1", values="value").add_prefix("sole_trigger_")
        mcd = sub[sub.metric == "marginal_contribution_days"].pivot(
            index="key2", columns="key1", values="value").add_prefix("sole_days_")
        tab = pd.concat([ind, mc, mcd], axis=1).reset_index().rename(
            columns={"key2": "name"})
        A(md(tab, fmt={**{c: "{:.4f}" for c in tab.columns if c.startswith(
            ("individual", "sole_trigger"))},
            **{c: "{:,.0f}" for c in tab.columns if c.startswith("sole_days")}}))
        A("")
    A("The disjunction fires far more often than any single condition. In S1 at "
      "threshold 70 no individual name fires on more than 10.8 percent of "
      "sessions, yet the OR across eleven fires on 29.9 percent. In T11 the "
      "individual maximum is 12.3 percent and the OR fires on 21.4 percent. "
      "Widening a panel loosens the effective threshold.")
    A("")
    A("Marginal contributions are highly unequal. In S1 at threshold 70, XLP "
      "(9.2 percent of firings), VOX (7.2) and XLY (4.6) are the names that most "
      "often fire alone, while SPY (0.56) and VOOV (0.46) almost never do. The "
      "names that carry the panel are the defensive and non-technology ones, "
      "which is the opposite of where the strategy thesis places its emphasis. "
      "In T11, TQQQ alone accounts for 24.2 percent of firings at threshold 70 "
      "and 48.2 percent at threshold 80; SPY accounts for 1.9 and 2.4 percent.")
    A("")
    A("Periods 7 and 28, the disjunction rate with each name removed, and the "
      "sole-trigger day counts for all thresholds are in "
      "`overbought-panel-structure.csv`.")
    A("")

    # ------------------------------------------------------------ decisions
    A("## What the measurements show, by decision")
    A("")
    A("No decision is taken and no parameter is selected below. These are "
      "statements of what was measured.")
    A("")
    A("### 1.12 Distribution coverage diagnostic")
    A("")
    A("Cumulative return from Yahoo's adjusted close and cumulative return from "
      "raw close compounded with the dividend stream agree to within 4.05 basis "
      "points per annum for every one of the 35 tickers, against the 10 basis "
      "point flag threshold. No ticker is flagged. The six instruments where "
      "coverage matters most, BIL, BSV, AGG, BND, TLT and IEF, agree to within "
      "0.09 basis points per annum. The adjustment factor moves only on recorded "
      "actions, with zero exceptions across the panel. The decision 1.5 adjusted "
      "open identity reproduces to one unit in the last place for all 35 "
      "tickers. The diagnostic measures internal consistency between two "
      "constructions drawn from the same actions feed, and by construction "
      "cannot detect a distribution the feed omits entirely.")
    A("")
    A("### 2.20 SMH 2011 conversion continuity")
    A("")
    A("The series is stitched, not truncated and not discontinuous on price. "
      "yfinance returns 6,589 sessions from 2000-06-05, spanning the HOLDRS era "
      "and the conversion, with no missing session against the SPY calendar, no "
      "single-day absolute return above 25 percent, and no split or distribution "
      "within 200 calendar days of the December 2011 boundary. The series is "
      "discontinuous on distributions: zero are recorded across the entire "
      "HOLDRS era and the first falls on 2012-12-24, 12.55 years after the first "
      "bar, so pre-2013 SMH total return is price return. Median volume falls by "
      "81 percent across the boundary.")
    A("")
    A("### 6.9 Overbought panel membership")
    A("")
    A("The S1 eleven-name panel carries 1.77 effective independent signals and "
      "the T11 five-name panel 1.39, at every RSI period tested. The disjunction "
      "fires on 29.9 percent of sessions in S1 at threshold 70 against a maximum "
      "individual rate of 10.8 percent, and on 21.4 percent in T11 against 12.3 "
      "percent. Sole-trigger contributions are concentrated in XLP, VOX and XLY "
      "for S1 and in TQQQ for T11; SPY is nearly redundant in both, at 0.56 and "
      "1.92 percent of firings respectively. Separately, RSI on a long leveraged "
      "fund and RSI on its underlying differ by 0.75 to 2.85 points on average "
      "and agree on the 70 threshold on 96.8 to 99.2 percent of sessions, so "
      "including both a leveraged fund and its underlying in one panel adds "
      "little that is independent.")
    A("")
    A("### 6.16 S2 trend filter series, TQQQ own price against QQQ")
    A("")
    A("At the canonical 200-session average, TQQQ and QQQ disagree about which "
      "side of their own moving average they sit on for 255 of 3,954 sessions, "
      "6.45 percent, in 84 separate runs with a median run of 2 sessions and a "
      "maximum of 21. Their crossovers match at a median offset of +1 session "
      "but only 6.5 percent are simultaneous and the 5th to 95th percentile "
      "range spans -26.9 to +33.7 sessions. Upward crossings lag downward "
      "crossings by 6.7 sessions on average. Inside the 60 sessions after a 20 "
      "percent QQQ drawdown, agreement falls from 93.6 to 87.1 percent and the "
      "mean crossover offset rises from +0.86 to +11.1 sessions. The same "
      "pattern holds across all seven leveraged pairs and strengthens with "
      "leverage and underlying volatility.")
    A("")
    A("### 6.20 PSQ and SH inverse redundancy")
    A("")
    A("RSI(inverse) = 100 - RSI(underlying) holds to a mean absolute difference "
      "of 1.06 points for PSQ against QQQ and 1.26 for SH against SPY at period "
      "14, with correlations of 0.994 and 0.989. Agreement is asymmetric: 99.5 "
      "and 99.7 percent at threshold 70 against 98.1 and 97.2 percent at "
      "threshold 30. Against each other, PSQ and SH are not redundant: 4.05 "
      "points mean absolute difference, correlation 0.892, 423 disagreement "
      "sessions at threshold 30. PSQ and SQQQ are near-duplicates at 0.89 points "
      "and correlation 0.996.")
    A("")
    A("### 6.7 Vote threshold, and 6.8 vote membership")
    A("")
    A("The S3 vote set of SPY, QQQ, SMH and SOXL carries 1.66 to 1.74 effective "
      "independent votes out of four, stable across all five average lengths and "
      "all three window bases. The vote count distribution is bimodal, with 66.4 "
      "percent of sessions unanimous bull and 11.7 percent unanimous bear at the "
      "200-session average. Under simple majority, decision 6.7, removing SOXL "
      "changes the classification on 12 of 3,935 sessions, 0.30 percent, against "
      "412 for SMH, 408 for SPY and 404 for QQQ. Substituting TLT for SOXL "
      "raises the effective independent votes to 2.29 to 2.38 on its native "
      "window and 2.21 to 2.39 restricted to the S3 window; KMLM raises it to "
      "1.78 to 2.18 on a window beginning 2021; dropping SOXL leaves 1.47 to "
      "1.54 out of three.")
    A("")

    # ------------------------------------------------------------ flags
    A("## Results that contradict an expectation stated in DECISIONS-OPEN-v2.md")
    A("")
    A("Flagged, not reconciled.")
    A("")
    A("### 6.8 states that SOXL and SMH votes are near-duplicates. They are the "
      "least duplicative equity pair in the set.")
    A("")
    A("The register gives as the reason for adding a non-equity leg that "
      "\"SOXL and SMH votes are near-duplicates\". Measured, SOXL and SMH are "
      "the **least** similar of the three equity-equity pairings at every "
      "average length from 100 sessions upward, and SPY and QQQ are the most "
      "similar throughout.")
    A("")
    A("| SMA | SMH/SOXL agreement | SPY/QQQ agreement | SMH/SOXL correlation | "
      "SPY/QQQ correlation |")
    A("|---|---|---|---|---|")
    for n in [50, 100, 150, 200, 250]:
        sa = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
                & (d7.sma_length == n) & (d7.metric == "pairwise_agreement")]
        sc = d7[(d7.vote_set == "S3_current") & (d7.window_basis == "native")
                & (d7.sma_length == n) & (d7.metric == "pairwise_correlation")]
        g = lambda df, a, b: df[(df.key1 == a) & (df.key2 == b)].value.iloc[0]
        A(f"| {n} | {g(sa,'SMH','SOXL'):.4f} | {g(sa,'SPY','QQQ'):.4f} | "
          f"{g(sc,'SMH','SOXL'):.4f} | {g(sc,'SPY','QQQ'):.4f} |")
    A("")
    A("At the canonical 200-session average, SMH and SOXL agree on 86.9 percent "
      "of sessions with a vote correlation of 0.709, while SPY and QQQ agree on "
      "94.5 percent with a correlation of 0.789. The stated premise is "
      "contradicted by the measurement.")
    A("")
    A("The conclusion the register draws from that premise, that SOXL "
      "contributes little, is separately supported by the leave-one-out result: "
      "removing SOXL changes the majority classification on 12 of 3,935 "
      "sessions, against 412 for SMH. But the mechanism is not duplication of "
      "SMH. SOXL is the "
      "*least* correlated vote in the set and is still nearly inert, because it "
      "is almost never on the winning side of a split decision. These are "
      "different facts and they point to different remedies.")
    A("")
    A("### 6.9's framing assumes the two panels are comparable. Their windows "
      "differ by two years.")
    A("")
    A("S1's eleven names support a common window only from 2012-04-11, bounded "
      "by QQQE, while T11's five support one from 2010-03-04, bounded by TQQQ. "
      "The 2010 to 2012 period, which contains a 20 percent QQQ drawdown, is in "
      "one panel's window and not the other's. Firing rates quoted side by side "
      "are not measured on the same sample.")
    A("")
    A("### 1.12's tolerance is not the binding constraint on distribution "
      "quality.")
    A("")
    A("The register treats 1.12 as a tolerance to be set. No tolerance in the "
      "plausible range separates anything in this panel: the worst ticker is at "
      "4.05 basis points per annum and the median is at 0.06. The diagnostic as "
      "specified passes everything. The actual distribution defect found in this "
      "session, SMH's missing HOLDRS-era distributions, is invisible to it at "
      "any tolerance, because both sides of the comparison read the same feed.")
    A("")

    # ------------------------------------------------------------ limits
    A("## Limitations")
    A("")
    A("- The final bar of every series is a live intraday print, as described "
      "under Provenance.")
    A("- Leveraged and inverse funds in this panel have had their stated daily "
      "multiples changed during their listed lives, including the Direxion "
      "change of 31 March 2020 covered by open decision 3.11. No multiple "
      "schedule was applied. Divergences measured here therefore blend the "
      "mechanical effects of daily reset and financing with any multiple change "
      "inside the window.")
    A("- The stress-regime subsets in Step 6 are small, between 224 and 951 "
      "sessions and between 5 and 23 matched crossovers per pair.")
    A("- Crossover matching uses a fixed 60-session window and a nearest-first "
      "one-to-one rule. Unmatched events are reported but not otherwise "
      "attributed.")
    A("- Effective independent counts from the eigenvalue method are computed on "
      "the full window and assume a stable correlation structure through it.")
    A("- Policy-rate levels referenced in the Step 4 discussion are not pulled "
      "in this session and are used only qualitatively. Decision 2.4 fixes FRED "
      "DFF as the source when a rate series is required.")
    A("")
    A("## Files written")
    A("")
    A("| file | contents |")
    A("|---|---|")
    A("| `outputs/session-00c/panel-coverage.csv` | per-ticker rows, first and "
      "last date, action counts, download status |")
    A("| `outputs/session-00c/etf-manifest.csv` | SHA-256, bytes, rows, dates, "
      "pull timestamp, yfinance version |")
    A("| `outputs/session-00c/pull-metadata.json` | versions and pull parameters |")
    A("| `outputs/session-00c/distribution-coverage.csv` | Step 2, all 35 "
      "tickers |")
    A("| `outputs/session-00c/smh-continuity.md` | Step 3, full inspection |")
    A("| `outputs/session-00c/rsi-leveraged-divergence.csv` | Step 4, pooled and "
      "by year |")
    A("| `outputs/session-00c/rsi-inverse-relationship.csv` | Step 5, pooled and "
      "by year, plus inverse against inverse |")
    A("| `outputs/session-00c/sma-crossover-divergence.csv` | Step 6, both "
      "scopes, three directions |")
    A("| `outputs/session-00c/vote-structure.csv` | Step 7, four sets, three "
      "window bases |")
    A("| `outputs/session-00c/overbought-panel-structure.csv` | Step 8, two "
      "panels, three RSI periods |")
    A("| `data/raw/etf/*.parquet` | frozen raw pulls, 35 files |")
    A("| `data/interim/etf-panel.parquet` | long panel, total return and "
      "adjusted close |")
    A("")

    (OUT / "REPORT.md").write_text("\n".join(L) + "\n")
    print(f"REPORT.md written, {len('\n'.join(L)):,} characters, "
          f"{len(L):,} lines")


if __name__ == "__main__":
    main()
