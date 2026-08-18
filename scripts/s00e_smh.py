"""Session 00e, step 2. SMH pre-2013 return basis effect. Informs 3.12.

Two bases over 2006-01-01 to 2013-12-31:
  PR    price return, the series as the feed provides it (ret_price)
  TR(y) price return with a constant assumed annual dividend yield accrued
        daily on a 252-day basis:  ret_tr = ret_price + y/252

The yields are ASSUMPTIONS, not measured distributions. See REPORT.md.

Indicators use the Session 00C library unchanged: Wilder RSI with alpha = 1/n and
an SMA seed (decision 1.6), SMA with min_periods = n.

Nothing here is a strategy return, allocation or performance statistic. RSI
values, SMA comparisons and vote classifications are properties of price series.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s00c_indicators import sma, wilder_rsi          # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00e"

BUILD_START, BUILD_END = "2006-01-01", "2013-12-31"
MEAS_START, MEAS_END = "2007-01-01", "2012-12-31"

YIELDS = [0.010, 0.015, 0.020]
RSI_PERIODS = [7, 14, 28]
SMA_LENGTHS = [50, 100, 150, 200, 250]
OB_THRESHOLDS = [70, 80]        # RSI >= t
OS_THRESHOLDS = [30, 20]        # RSI <= t
VOTE_MEMBERS = ["SPY", "QQQ", "SMH", "SOXL"]
VOTE_SMA = 200
VOTE_THRESHOLD = 3


def build_bases(panel):
    s = panel[panel.ticker == "SMH"].sort_values("date")
    s = s[(s.date >= BUILD_START) & (s.date <= BUILD_END)].set_index("date")
    r = s["ret_price"].astype(float).copy()
    r.iloc[0] = 0.0                       # anchor the index at 1.0
    bases = {"PR": (1.0 + r).cumprod()}
    for y in YIELDS:
        rt = r + y / 252.0
        rt.iloc[0] = 0.0
        bases[f"TR{y*100:.1f}"] = (1.0 + rt).cumprod()
    return s, bases


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_parquet(INTERIM / "etf-panel.parquet")
    panel["date"] = pd.to_datetime(panel["date"])

    smh, bases = build_bases(panel)
    pr = bases["PR"]
    win = (pr.index >= MEAS_START) & (pr.index <= MEAS_END)
    print(f"build window {pr.index.min().date()} .. {pr.index.max().date()} "
          f"({len(pr)} sessions)")
    print(f"measurement window {pr.index[win].min().date()} .. "
          f"{pr.index[win].max().date()} ({int(win.sum())} sessions)")

    # actual distributions inside the build window, for the record
    div = smh[smh["dividend"].fillna(0) != 0]
    print(f"actual SMH distributions in build window: {len(div)} "
          f"{[d.date().isoformat() for d in div.index]}")

    rows = []

    def add(**kw):
        rows.append(kw)

    # ---------------- RSI ----------------------------------------------------
    rsi = {(b, n): wilder_rsi(s, n) for b, s in bases.items() for n in RSI_PERIODS}
    for y in YIELDS:
        tag = f"TR{y*100:.1f}"
        for n in RSI_PERIODS:
            a, b = rsi[("PR", n)], rsi[(tag, n)]
            ok = a.notna() & b.notna() & win
            d = (a[ok] - b[ok]).abs()
            add(metric="mean_abs_rsi_difference", assumed_yield_pct=y * 100,
                rsi_period=n, sma_length="", threshold="",
                value=float(d.mean()), n_sessions=int(ok.sum()),
                disagree_sessions="")
            add(metric="max_abs_rsi_difference", assumed_yield_pct=y * 100,
                rsi_period=n, sma_length="", threshold="",
                value=float(d.max()), n_sessions=int(ok.sum()),
                disagree_sessions="")
            for t in OB_THRESHOLDS + OS_THRESHOLDS:
                fa = (a[ok] >= t) if t in OB_THRESHOLDS else (a[ok] <= t)
                fb = (b[ok] >= t) if t in OB_THRESHOLDS else (b[ok] <= t)
                dis = int((fa != fb).sum())
                add(metric="rsi_threshold_crossing_agreement",
                    assumed_yield_pct=y * 100, rsi_period=n, sma_length="",
                    threshold=t, value=float((fa == fb).mean()),
                    n_sessions=int(ok.sum()), disagree_sessions=dis)
                add(metric="rsi_threshold_fired_PR", assumed_yield_pct=y * 100,
                    rsi_period=n, sma_length="", threshold=t,
                    value=float(fa.sum()), n_sessions=int(ok.sum()),
                    disagree_sessions="")
                add(metric="rsi_threshold_fired_TR", assumed_yield_pct=y * 100,
                    rsi_period=n, sma_length="", threshold=t,
                    value=float(fb.sum()), n_sessions=int(ok.sum()),
                    disagree_sessions="")

    # ---------------- SMA ----------------------------------------------------
    above = {(b, n): (s > sma(s, n)) for b, s in bases.items() for n in SMA_LENGTHS}
    valid = {(b, n): sma(s, n).notna() for b, s in bases.items() for n in SMA_LENGTHS}
    for y in YIELDS:
        tag = f"TR{y*100:.1f}"
        for n in SMA_LENGTHS:
            ok = valid[("PR", n)] & valid[(tag, n)] & win
            fa, fb = above[("PR", n)][ok], above[(tag, n)][ok]
            dis = int((fa != fb).sum())
            add(metric="sma_above_below_agreement", assumed_yield_pct=y * 100,
                rsi_period="", sma_length=n, threshold="",
                value=float((fa == fb).mean()), n_sessions=int(ok.sum()),
                disagree_sessions=dis)
            add(metric="sma_above_PR", assumed_yield_pct=y * 100, rsi_period="",
                sma_length=n, threshold="", value=float(fa.sum()),
                n_sessions=int(ok.sum()), disagree_sessions="")
            add(metric="sma_above_TR", assumed_yield_pct=y * 100, rsi_period="",
                sma_length=n, threshold="", value=float(fb.sum()),
                n_sessions=int(ok.sum()), disagree_sessions="")

    # ---------------- S3 vote ------------------------------------------------
    # Only SMH's basis varies. SPY, QQQ, SOXL use the panel total return index.
    others = {}
    for t in VOTE_MEMBERS:
        if t == "SMH":
            continue
        g = panel[panel.ticker == t].sort_values("date").set_index("date")
        others[t] = g["tr_index"].astype(float)

    def vote_bull(smh_series):
        cols = {}
        for t, s in others.items():
            m = sma(s, VOTE_SMA)
            cols[t] = (s > m)[m.notna()]
        m = sma(smh_series, VOTE_SMA)
        cols["SMH"] = (smh_series > m)[m.notna()]
        j = pd.concat(cols, axis=1, join="inner").dropna().astype(bool)
        j = j[(j.index >= MEAS_START) & (j.index <= MEAS_END)]
        return (j[VOTE_MEMBERS].to_numpy(bool).sum(axis=1) >= VOTE_THRESHOLD), j.index

    base_bull, base_idx = vote_bull(bases["PR"])
    print(f"\nS3 vote window inside measurement span: "
          f"{base_idx.min().date()} .. {base_idx.max().date()} "
          f"({len(base_idx)} sessions)")
    print(f"  SOXL first panel date {panel[panel.ticker=='SOXL'].date.min().date()}"
          f" -> SMA{VOTE_SMA} warm-up truncates the vote window")

    for y in YIELDS:
        tag = f"TR{y*100:.1f}"
        b2, idx2 = vote_bull(bases[tag])
        assert idx2.equals(base_idx)
        dis = int((base_bull != b2).sum())
        add(metric="s3_vote_bull_differs", assumed_yield_pct=y * 100,
            rsi_period="", sma_length=VOTE_SMA, threshold=VOTE_THRESHOLD,
            value=float(dis), n_sessions=len(base_idx), disagree_sessions=dis)
        add(metric="s3_vote_bull_frac_PR", assumed_yield_pct=y * 100,
            rsi_period="", sma_length=VOTE_SMA, threshold=VOTE_THRESHOLD,
            value=float(base_bull.mean()), n_sessions=len(base_idx),
            disagree_sessions="")
        add(metric="s3_vote_bull_frac_TR", assumed_yield_pct=y * 100,
            rsi_period="", sma_length=VOTE_SMA, threshold=VOTE_THRESHOLD,
            value=float(b2.mean()), n_sessions=len(base_idx),
            disagree_sessions="")
        print(f"  yield {y*100:.1f}%: bull classification differs on {dis} "
              f"of {len(base_idx)} sessions")

    res = pd.DataFrame(rows)
    res.insert(0, "measurement_window", f"{MEAS_START}..{MEAS_END}")
    res.insert(0, "build_window", f"{BUILD_START}..{BUILD_END}")
    res.to_csv(OUT / "smh-return-basis.csv", index=False)
    print(f"\nwrote {OUT/'smh-return-basis.csv'} ({len(res)} rows)")

    with pd.option_context("display.width", 220):
        print("\n=== mean abs RSI difference ===")
        p = res[res.metric == "mean_abs_rsi_difference"].pivot(
            index="rsi_period", columns="assumed_yield_pct", values="value")
        print(p.round(4).to_string())
        print("\n=== SMA above/below disagreement sessions ===")
        p = res[res.metric == "sma_above_below_agreement"].pivot(
            index="sma_length", columns="assumed_yield_pct",
            values="disagree_sessions")
        print(p.to_string())


if __name__ == "__main__":
    main()
