"""Session 00b, step 5. Quantify the VX settlement-timestamp mismatch.

Best construction from step 4 is B (S&P roll): highest correlation against VIXY,
VXX and VIXY NAV. The daily return difference against VIXY market price is
described conditional on decile of absolute VIXY return, and split at the
documented Cboe settlement-time change of 2020-10-26.

No strategy return, Sharpe ratio or performance statistic is computed.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00b"

REGIME_CHANGE = pd.Timestamp("2020-10-26")   # Cboe notice C2020092202


def decile_table(df, label):
    d = df.copy()
    d["decile"] = pd.qcut(d["abs_vixy_ret"], 10, labels=False, duplicates="drop") + 1
    g = d.groupby("decile")
    t = pd.DataFrame({
        "n": g.size(),
        "abs_vixy_ret_lo": g["abs_vixy_ret"].min(),
        "abs_vixy_ret_hi": g["abs_vixy_ret"].max(),
        "mean_diff": g["diff"].mean(),
        "sd_diff": g["diff"].std(),
        "mean_abs_diff": g["abs_diff"].mean(),
        "median_abs_diff": g["abs_diff"].median(),
        "p95_abs_diff": g["abs_diff"].quantile(0.95),
        "max_abs_diff": g["abs_diff"].max(),
    }).reset_index()
    t.insert(0, "block", label)
    return t


def main():
    b = pd.read_parquet(INTERIM / "vx-cm30-b.parquet")
    vixy = pd.read_parquet(INTERIM / "vixy-yfinance-raw-s00b.parquet")
    vixy = vixy[["Date", "Adj Close"]].rename(
        columns={"Date": "trade_date", "Adj Close": "vixy_px"})

    m = b[["trade_date", "cdr", "front_contract", "second_contract",
           "w1", "w2", "d1", "d2"]].merge(vixy, on="trade_date", how="inner")
    m = m.sort_values("trade_date")
    m["vixy_ret"] = m["vixy_px"].pct_change()
    m = m.dropna(subset=["cdr", "vixy_ret"]).reset_index(drop=True)
    m["diff"] = m["cdr"] - m["vixy_ret"]
    m["abs_diff"] = m["diff"].abs()
    m["abs_vixy_ret"] = m["vixy_ret"].abs()
    m["regime"] = np.where(m["trade_date"] < REGIME_CHANGE,
                           "pre_1615ET", "post_1600ET")

    pre = m[m["regime"] == "pre_1615ET"]
    post = m[m["regime"] == "post_1600ET"]
    print(f"overlap {len(m)} sessions {m['trade_date'].min().date()} .. "
          f"{m['trade_date'].max().date()}")
    print(f"  pre  (VX settle 16:15 ET): n={len(pre)} "
          f"corr={pre['cdr'].corr(pre['vixy_ret']):.6f} "
          f"mean|diff|={pre['abs_diff'].mean():.5f}")
    print(f"  post (VX settle 16:00 ET): n={len(post)} "
          f"corr={post['cdr'].corr(post['vixy_ret']):.6f} "
          f"mean|diff|={post['abs_diff'].mean():.5f}")

    blocks = [decile_table(m, "all"),
              decile_table(pre, "pre_20201026_settle_1615ET"),
              decile_table(post, "post_20201026_settle_1600ET")]
    dec = pd.concat(blocks, ignore_index=True)

    # ---- top 20 sessions by absolute difference ----------------------------
    panel = pd.read_parquet(INTERIM / "vx-panel.parquet")
    px = panel[panel["settle_idx"] > 0].set_index(
        ["trade_date", "contract"])["settle_idx"]
    px = px[~px.index.duplicated()]
    sessions = list(m["trade_date"])
    prev_of = {t: sessions[i - 1] for i, t in enumerate(sessions) if i > 0}

    top = m.nlargest(20, "abs_diff").copy()
    for lab, col in (("front", "front_contract"), ("second", "second_contract")):
        top[f"{lab}_settle_t"] = [px.get((r.trade_date, getattr(r, col)))
                                  for r in top.itertuples()]
        top[f"{lab}_settle_prev"] = [
            px.get((prev_of.get(r.trade_date), getattr(r, col)))
            for r in top.itertuples()]
    top["prev_session"] = [prev_of.get(t) for t in top["trade_date"]]
    top = top.sort_values("abs_diff", ascending=False)

    cols = ["trade_date", "prev_session", "regime", "cdr", "vixy_ret", "diff",
            "abs_diff", "front_contract", "front_settle_prev", "front_settle_t",
            "second_contract", "second_settle_prev", "second_settle_t",
            "w1", "w2", "d1", "d2"]
    top_out = top[cols]
    top_out.to_csv(OUT / "timestamp-top20-sessions.csv", index=False)

    stacked = pd.concat([dec, top_out.assign(block="top20_session")],
                        ignore_index=True)
    stacked.to_csv(OUT / "timestamp-diagnostics.csv", index=False)

    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print("\n=== decile of |VIXY return|, all sessions ===")
        print(blocks[0].round(5).to_string(index=False))
        print("\n=== pre 2020-10-26 (VX settle 16:15 ET) ===")
        print(blocks[1].round(5).to_string(index=False))
        print("\n=== post 2020-10-26 (VX settle 16:00 ET) ===")
        print(blocks[2].round(5).to_string(index=False))
        print("\n=== top 20 sessions by |difference| ===")
        print(top_out[["trade_date", "regime", "cdr", "vixy_ret", "diff",
                       "front_contract", "front_settle_prev", "front_settle_t",
                       "second_contract", "second_settle_prev",
                       "second_settle_t"]].round(5).to_string(index=False))

    # concentration summary
    for lab, sub in (("all", m), ("pre", pre), ("post", post)):
        d9 = sub[sub["abs_vixy_ret"] >= sub["abs_vixy_ret"].quantile(0.9)]
        share = d9["abs_diff"].sum() / sub["abs_diff"].sum()
        print(f"\n{lab}: top decile of |VIXY ret| holds "
              f"{share:.3f} of total absolute difference "
              f"({len(d9)}/{len(sub)} sessions = {len(d9)/len(sub):.3f})")


if __name__ == "__main__":
    main()
