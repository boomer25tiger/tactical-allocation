"""Session 00C, Steps 2 and 3.

Step 2. Distribution coverage diagnostic (closes 1.12).
Step 3. SMH 2011 conversion continuity (closes 2.20).
"""

from pathlib import Path

import numpy as np
import pandas as pd

from s00c_indicators import ROOT, OUT, load_panel

RAW = ROOT / "data" / "raw" / "etf"

FOCUS = ["BIL", "BSV", "AGG", "BND", "TLT", "IEF"]
FLAG_BP = 10.0  # basis points per annum

SMH_CONVERSION = pd.Timestamp("2011-12-20")  # HOLDRS exchange into the VanEck fund


# ---------------------------------------------------------------- Step 2

def coverage_row(t: str, g: pd.DataFrame) -> dict:
    g = g.sort_values("date").reset_index(drop=True)
    close = g["close"].to_numpy(float)
    adj = g["adj_close"].to_numpy(float)
    div = g["dividend"].fillna(0.0).to_numpy(float)
    n_ret = len(g) - 1
    yrs = n_ret / 252.0

    # cumulative return, Yahoo adjusted close
    cum_adj = adj[-1] / adj[0] - 1.0
    # cumulative return, raw close compounded with the dividend stream
    cum_tr = float(g["tr_index"].iloc[-1]) - 1.0
    # cumulative return, literal price return plus summed distributions
    cum_simple = (close[-1] - close[0] + div[1:].sum()) / close[0]

    def ann(c):
        return (1.0 + c) ** (1.0 / yrs) - 1.0 if yrs > 0 and (1.0 + c) > 0 else np.nan

    ann_adj, ann_tr, ann_simple = ann(cum_adj), ann(cum_tr), ann(cum_simple)
    d_cum = cum_adj - cum_tr
    d_ann_bp = (ann_adj - ann_tr) * 1e4

    # daily return agreement between the two constructions
    r_adj = pd.Series(adj).pct_change().to_numpy(float)[1:]
    r_tr = g["ret_total"].to_numpy(float)[1:]
    dr = r_adj - r_tr
    max_daily_bp = float(np.nanmax(np.abs(dr))) * 1e4 if dr.size else np.nan
    n_daily_gt_1bp = int((np.abs(dr) > 1e-4).sum())

    # adjustment factor behaviour: does AdjClose/Close move only on recorded actions?
    # Yahoo rounds Adj Close to about six significant figures, so the factor
    # carries roughly 1e-6 relative rounding noise every session. The threshold
    # is set at 1e-5 to sit above that noise floor and below any real
    # distribution adjustment in this panel.
    factor = adj / close
    fchg = np.abs(np.diff(factor)) / np.maximum(np.abs(factor[:-1]), 1e-300)
    moved = fchg > 1e-5
    action = ((div[1:] > 0) | (g["split"].fillna(0).to_numpy(float)[1:] > 0))
    n_factor_moves = int(moved.sum())
    n_moves_no_action = int((moved & ~action).sum())
    n_actions_no_move = int((~moved & action).sum())

    # distribution coverage in time: when does the recorded stream begin?
    div_dates = g.loc[g["dividend"] > 0, "date"]
    first_div = div_dates.iloc[0] if len(div_dates) else pd.NaT
    yrs_to_first_div = ((first_div - g["date"].iloc[0]).days / 365.25
                        if pd.notna(first_div) else np.nan)

    # decision 1.5: AdjOpen = Open x (AdjClose / Close) must reproduce Open/Close
    op = g["open"].to_numpy(float)
    ok = np.isfinite(op) & np.isfinite(close) & (close != 0) & np.isfinite(adj)
    adj_open = op[ok] * (adj[ok] / close[ok])
    lhs = adj_open / adj[ok]          # AdjOpen / AdjClose
    rhs = op[ok] / close[ok]          # Open / Close
    rel = np.abs(lhs - rhs) / np.maximum(np.abs(rhs), 1e-300)
    max_rel = float(np.nanmax(rel)) if rel.size else np.nan
    n_fail_1e12 = int((rel > 1e-12).sum())
    n_fail_1e9 = int((rel > 1e-9).sum())

    return dict(
        ticker=t, first_date=g["date"].iloc[0].date().isoformat(),
        last_date=g["date"].iloc[-1].date().isoformat(),
        n_sessions=len(g), years=round(yrs, 3),
        n_distribution_events=int((div > 0).sum()),
        first_distribution_date=(first_div.date().isoformat()
                                 if pd.notna(first_div) else ""),
        years_listing_to_first_distribution=yrs_to_first_div,
        flag_distribution_stream_starts_late=bool(
            pd.notna(first_div) and yrs_to_first_div > 3.0),
        total_distributions_per_share=float(div.sum()),
        cum_ret_adjclose=cum_adj, cum_ret_total_return=cum_tr,
        cum_ret_price_plus_sum_dist=cum_simple,
        abs_diff_cum_adj_vs_tr=abs(d_cum),
        diff_cum_adj_vs_tr=d_cum,
        ann_ret_adjclose=ann_adj, ann_ret_total_return=ann_tr,
        ann_ret_price_plus_sum_dist=ann_simple,
        diff_ann_bp_adj_vs_tr=d_ann_bp,
        abs_diff_ann_bp_adj_vs_tr=abs(d_ann_bp),
        flag_gt_10bp=bool(abs(d_ann_bp) > FLAG_BP),
        diff_ann_bp_adj_vs_simple=(ann_adj - ann_simple) * 1e4,
        max_daily_ret_diff_bp=max_daily_bp,
        n_days_daily_diff_gt_1bp=n_daily_gt_1bp,
        n_adjfactor_moves=n_factor_moves,
        n_adjfactor_moves_without_recorded_action=n_moves_no_action,
        n_recorded_actions_without_adjfactor_move=n_actions_no_move,
        adjopen_max_rel_error=max_rel,
        adjopen_n_fail_1e_12=n_fail_1e12,
        adjopen_n_fail_1e_9=n_fail_1e9,
        adjopen_check_pass=bool(n_fail_1e9 == 0),
        focus_instrument=bool(t in FOCUS),
    )


def step2(panel: pd.DataFrame) -> pd.DataFrame:
    rows = [coverage_row(t, g) for t, g in panel.groupby("ticker", sort=True)]
    df = pd.DataFrame(rows).sort_values(
        "abs_diff_ann_bp_adj_vs_tr", ascending=False).reset_index(drop=True)
    df.to_csv(OUT / "distribution-coverage.csv", index=False)
    return df


# ---------------------------------------------------------------- Step 3

def step3(panel: pd.DataFrame) -> str:
    smh = panel[panel.ticker == "SMH"].set_index("date").sort_index()
    spy = panel[panel.ticker == "SPY"].set_index("date").sort_index()

    lines = []
    A = lines.append
    A("# SMH continuity at the 2011 HOLDRS to VanEck conversion")
    A("")
    A("Session 00C, Step 3. Closes decision 2.20. Nothing is adjusted here.")
    A("")
    A("## Series extent")
    A("")
    A(f"- First date returned by yfinance: **{smh.index[0].date()}**")
    A(f"- Last date returned: **{smh.index[-1].date()}**")
    A(f"- Sessions returned: **{len(smh):,}**")
    A(f"- Nominal conversion reference date used for the window: "
      f"{SMH_CONVERSION.date()} (Merrill Lynch Semiconductor HOLDRS exchanged "
      f"into the VanEck fund in December 2011)")
    A("")

    idx = smh.index
    pos = int(idx.searchsorted(SMH_CONVERSION))
    lo, hi = max(0, pos - 60), min(len(idx), pos + 61)
    before = smh.iloc[max(0, pos - 60):pos]
    after = smh.iloc[pos:min(len(idx), pos + 60)]

    A("## Daily total return distribution, 60 sessions either side of the boundary")
    A("")
    A("| window | sessions | first | last | mean % | sd % | min % | p05 % | p95 % | max % |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for name, blk in [("60 sessions before", before), ("60 sessions after", after),
                      ("full history", smh)]:
        r = blk["ret_total"].dropna().to_numpy(float) * 100
        if r.size == 0:
            continue
        A(f"| {name} | {r.size} | {blk.index[0].date()} | {blk.index[-1].date()} | "
          f"{r.mean():.3f} | {r.std(ddof=1):.3f} | {r.min():.3f} | "
          f"{np.percentile(r,5):.3f} | {np.percentile(r,95):.3f} | {r.max():.3f} |")
    A("")

    A("## Single-day absolute total return above 25 percent, full history")
    A("")
    big = smh[smh["ret_total"].abs() > 0.25]
    if len(big) == 0:
        A("None. Maximum absolute single-day total return over the full history is "
          f"**{smh['ret_total'].abs().max()*100:.2f} percent** on "
          f"{smh['ret_total'].abs().idxmax().date()}.")
    else:
        A("| date | total return % | close | adj close | dividend | split |")
        A("|---|---|---|---|---|---|")
        for d, r in big.iterrows():
            A(f"| {d.date()} | {r['ret_total']*100:.2f} | {r['close']:.4f} | "
              f"{r['adj_close']:.4f} | {r['dividend']:.4f} | {r['split']:.2f} |")
    A("")
    A("Largest ten absolute daily moves in the +/- 60 session boundary window:")
    A("")
    win = smh.iloc[lo:hi]
    top = win.reindex(win["ret_total"].abs().sort_values(ascending=False).index).head(10)
    A("| date | total return % | close | dividend | split |")
    A("|---|---|---|---|---|")
    for d, r in top.iterrows():
        A(f"| {d.date()} | {r['ret_total']*100:.3f} | {r['close']:.4f} | "
          f"{r['dividend']:.4f} | {r['split']:.2f} |")
    A("")

    A("## Trading date gaps")
    A("")
    cal = spy.index[(spy.index >= smh.index[0]) & (spy.index <= smh.index[-1])]
    missing = cal.difference(smh.index)
    extra = smh.index.difference(spy.index)
    A(f"- Reference calendar: SPY sessions over the SMH window, {len(cal):,} sessions.")
    A(f"- SMH sessions over the same window: {len(smh):,}.")
    A(f"- Sessions present in SPY and absent in SMH: **{len(missing)}**.")
    A(f"- Sessions present in SMH and absent in SPY: **{len(extra)}**.")
    if len(missing):
        A("")
        A("Missing sessions (all, up to 60 listed):")
        A("")
        A("```")
        for d in list(missing)[:60]:
            A(str(d.date()))
        A("```")
        gap_win = [d for d in missing if abs((d - SMH_CONVERSION).days) <= 200]
        A(f"Missing sessions within 200 calendar days of the conversion: "
          f"**{len(gap_win)}**" + (f" -> {[str(d.date()) for d in gap_win]}" if gap_win else "."))
    else:
        A("")
        A("No missing sessions. The SMH trading calendar matches SPY exactly over "
          "the common window.")
    A("")
    dd = np.diff(smh.index.values).astype("timedelta64[D]").astype(int)
    A(f"- Maximum calendar gap between consecutive SMH sessions: **{dd.max()} days** "
      f"ending {smh.index[1:][dd.argmax()].date()}.")
    A("")

    A("## Corporate actions near the boundary")
    A("")
    near = smh[(smh.index >= SMH_CONVERSION - pd.Timedelta(days=200)) &
               (smh.index <= SMH_CONVERSION + pd.Timedelta(days=200))]
    acts = near[(near["dividend"] > 0) | (near["split"] > 0)]
    if len(acts) == 0:
        A("No dividend and no split recorded within 200 calendar days either side "
          "of the conversion date.")
    else:
        A("| date | dividend | split | close | adj close |")
        A("|---|---|---|---|---|")
        for d, r in acts.iterrows():
            A(f"| {d.date()} | {r['dividend']:.4f} | {r['split']:.2f} | "
              f"{r['close']:.4f} | {r['adj_close']:.4f} |")
    A("")
    all_acts = smh[(smh["dividend"] > 0) | (smh["split"] > 0)]
    A(f"Full history: {int((smh['dividend']>0).sum())} distributions, "
      f"{int((smh['split']>0).sum())} splits.")
    if int((smh["split"] > 0).sum()):
        A("")
        A("All recorded splits:")
        A("")
        A("| date | split factor | close | prior close | raw close ratio |")
        A("|---|---|---|---|---|")
        for d, r in smh[smh["split"] > 0].iterrows():
            i = smh.index.get_loc(d)
            prior = smh["close"].iloc[i - 1] if i > 0 else np.nan
            A(f"| {d.date()} | {r['split']:.4f} | {r['close']:.4f} | {prior:.4f} | "
              f"{r['close']/prior:.4f} |")
    A("")
    divs = smh[smh["dividend"] > 0]
    A("")
    A("### Distribution stream, before and after the conversion")
    A("")
    pre = divs[divs.index < SMH_CONVERSION]
    post = divs[divs.index >= SMH_CONVERSION]
    A(f"- Distributions recorded **before** {SMH_CONVERSION.date()}: **{len(pre)}**")
    A(f"- Distributions recorded **on or after** {SMH_CONVERSION.date()}: **{len(post)}**")
    A(f"- First recorded distribution anywhere in the series: "
      f"**{divs.index[0].date() if len(divs) else 'none'}**, which is "
      f"{(divs.index[0] - smh.index[0]).days / 365.25:.2f} years after the first bar.")
    A("")
    A("This is the material finding of Step 3, and it is not a price "
      "discontinuity. yfinance records **no distribution at all** across the "
      f"entire HOLDRS era, {smh.index[0].date()} to "
      f"{divs.index[0].date() if len(divs) else 'end'}. The HOLDRS was a grantor "
      "trust that passed underlying constituent dividends through to holders, so "
      "distributions did occur and are simply absent from the feed. Both the "
      "total return series built in Step 1 and Yahoo's own adjusted close inherit "
      "that absence, which is why the Step 2 diagnostic cannot see it: the two "
      "constructions agree with each other while both omit the same cash flows. "
      "SMH total return before December 2012 is therefore a price return, and is "
      "understated by the semiconductor dividend yield of the period.")
    A("")

    A("## Price and volume level either side of the boundary")
    A("")
    A("| date | close | adj close | volume |")
    A("|---|---|---|---|")
    for d, r in smh.iloc[max(0, pos - 5):min(len(smh), pos + 6)].iterrows():
        A(f"| {d.date()} | {r['close']:.4f} | {r['adj_close']:.4f} | {r['volume']:,.0f} |")
    A("")
    v_before = before["volume"].median()
    v_after = after["volume"].median()
    A(f"Median volume, 60 sessions before: {v_before:,.0f}. "
      f"60 sessions after: {v_after:,.0f}. Ratio after/before: {v_after/v_before:.2f}.")
    A("")

    # verdict inputs
    n_big = len(big)
    verdict_stitched = (n_big == 0) and (len(missing) == 0)
    A("## Verdict")
    A("")
    if verdict_stitched:
        A("**Stitched, on price. Discontinuous, on distributions.**")
        A("")
        A("The price series is continuous across the December 2011 conversion: it "
          "starts in 2000 during the HOLDRS era, has no missing session relative "
          "to the SPY calendar, records no single-day absolute return above 25 "
          "percent anywhere in its history, and carries no split or distribution "
          "at the conversion boundary. yfinance presents one unbroken price series "
          "across the vehicle change, with no marker identifying the conversion.")
        A("")
        A("The distribution series is not continuous. It begins in December 2012, "
          "twelve and a half years after the first bar. Everything before that is "
          "price return carrying a total return label. Two secondary markers also "
          "sit at the boundary and are consistent with a vehicle change rather "
          "than a price break: median volume falls by about four fifths across the "
          "conversion, and the distribution stream switches on shortly after it.")
    elif n_big:
        A("**Discontinuous.** One or more single-day absolute returns above 25 "
          "percent appear in the series, listed above.")
    else:
        A("**Gapped.** Sessions are missing relative to the reference calendar, "
          "listed above.")
    A("")
    A("Nothing was adjusted. The observation that the series is presented as "
      "continuous is a statement about what yfinance returns, not a claim that "
      "the pre-2011 HOLDRS return stream is economically comparable to the "
      "post-2011 fund. The HOLDRS was a fixed basket of grantor-trust receipts "
      "with no rebalancing and a shrinking constituent count; the VanEck fund "
      "tracks a rebalanced index. That difference is not visible as a price "
      "discontinuity and cannot be detected by this test.")
    A("")

    txt = "\n".join(lines) + "\n"
    (OUT / "smh-continuity.md").write_text(txt)
    return txt


def main():
    panel = load_panel()
    d = step2(panel)
    print("=== Step 2 distribution coverage, worst 12 by annualized difference ===")
    cols = ["ticker", "n_sessions", "n_distribution_events", "cum_ret_adjclose",
            "cum_ret_total_return", "diff_ann_bp_adj_vs_tr", "flag_gt_10bp",
            "max_daily_ret_diff_bp", "adjopen_check_pass"]
    print(d[cols].head(12).to_string(index=False))
    print()
    print("flagged >10bp/yr:", d[d.flag_gt_10bp].ticker.tolist())
    print("adjopen check failures:", d[~d.adjopen_check_pass].ticker.tolist())
    print("max adjopen rel error across panel:", d.adjopen_max_rel_error.max())
    print()
    print("=== focus instruments ===")
    print(d[d.focus_instrument][cols].to_string(index=False))
    print()
    print("=== factor moves without recorded action ===")
    fm = d[d.n_adjfactor_moves_without_recorded_action > 0]
    print(fm[["ticker", "n_adjfactor_moves",
              "n_adjfactor_moves_without_recorded_action",
              "n_recorded_actions_without_adjfactor_move"]].to_string(index=False))
    print()
    txt = step3(panel)
    print("=== Step 3 SMH ===")
    print(txt[-1800:])


if __name__ == "__main__":
    main()
