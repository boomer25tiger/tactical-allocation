"""h03. Engine and benchmark ladder by window (slides 3, 4, 6, 11, 12, 15, 18, 21).

Reads the frozen twelve-line ladder (outputs/session-27/_combined_line_returns.parquet,
daily returns of the canonical engine and eleven comparison lines) and the
canonical account (_canonical_daily.parquet, _canonical_orders.parquet) and
measures them on P11, P12 and H with the metric set in common.metrics.

Writes to outputs/hw2/
    ladder-windows.csv   every metric and its rank among the twelve lines, by window
    ladder-misc.json     turnover, mean effective exposure, concentration,
                         leave-one-year-out Sharpe, the P12 bootstrap of the
                         naive-Sharpe gap to QQQ, and fourth-quarter 2011 returns
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, WINDOWS, P12, H, metrics, sl, stationary_blocks  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scripts.s13_backtest as bt  # noqa: E402

S27, S28 = ROOT / "outputs" / "session-27", ROOT / "outputs" / "session-28"
cl = pd.read_parquet(S27 / "_combined_line_returns.parquet")
cl.index = pd.DatetimeIndex(cl.index)
rf = bt.rf_per_session(cl.index).fillna(0.0)

rows = []
for wn, w in WINDOWS.items():
    for c in cl.columns:
        rows.append({"window": wn, "line": c, **metrics(sl(cl[c], w), rf)})
L = pd.DataFrame(rows)
for k in ("sharpe_naive", "sharpe_lo", "sortino", "calmar", "ann_return"):
    L["rank_" + k] = L.groupby("window")[k].rank(ascending=False).astype(int)
L.to_csv(OUT / "ladder-windows.csv", index=False)

misc = {}
cd = pd.read_parquet(S27 / "_canonical_daily.parquet"); cd.index = pd.DatetimeIndex(cd.index)
od = pd.read_parquet(S27 / "_canonical_orders.parquet"); od["date"] = pd.to_datetime(od["date"])
for wn, w in WINDOWS.items():
    r, nav = sl(cd["ret"], w), sl(cd["nav"], w)
    o = od[(od.date >= w[0]) & (od.date <= w[1])]
    misc[f"turnover_{wn}"] = float(o["value"].sum() / 2 / nav.mean() / (len(r) / 252))
    misc[f"canonical_ann_return_{wn}"] = metrics(r, rf)["ann_return"]
    s = sl(cl["STRATEGY"], w).dropna()
    c = s.sort_values(ascending=False).cumsum()
    misc[f"sessions_for_half_arithmetic_return_{wn}"] = int((c < s.sum() / 2).sum() + 1)
misc["nav_at_2021_07_30_close"] = float(cd["nav"].loc["2021-07-30"])
misc["nav_at_2026_08_14_close"] = float(cd["nav"].iloc[-1])
ee = pd.read_parquet(S28 / "_effective_exposure.parquet"); ee.index = pd.DatetimeIndex(ee.index)
for wn, w in WINDOWS.items():
    misc[f"mean_effective_exposure_{wn}"] = float(sl(ee["eff_exposure"], w).mean())

# Leave one calendar year out, on both Sharpe conventions, P12 and the holdout.
for wn, w in (("P12", P12), ("H", H)):
    ex = (sl(cl["STRATEGY"], w) - rf).dropna()
    for name, f in (("naive", lambda x: x.mean() / x.std(ddof=1) * math.sqrt(252)),
                    ("lo", bt.lo_sharpe)):
        vals = {int(y): float(f(ex[ex.index.year != y])) for y in sorted(set(ex.index.year))}
        misc[f"loyo_{name}_{wn}"] = {"base": float(f(ex)), "min": min(vals.values()),
                                     "max": max(vals.values()), "by_year_removed": vals}

# Stationary bootstrap of the P12 naive-Sharpe gap to QQQ, with the session-30
# settings: mean block 21 sessions, 10,000 draws, seed 20260823.
P = sl(cl[["STRATEGY", "buy_hold_QQQ"]], P12).dropna()
E = P.sub(rf.reindex(P.index), axis=0).to_numpy()
rng = np.random.default_rng(20260823)
def sr(x): return x.mean(0) / x.std(0, ddof=1) * math.sqrt(252)
d_sr, d_gap = [], []
for _ in range(10000):
    s_ = sr(E[stationary_blocks(rng, len(E), 21)])
    d_sr.append(s_[0]); d_gap.append(s_[0] - s_[1])
pt = sr(E)
misc["bootstrap_P12"] = {"sharpe": float(pt[0]), "sharpe_p05": float(np.percentile(d_sr, 5)),
                         "sharpe_p95": float(np.percentile(d_sr, 95)), "gap": float(pt[0] - pt[1]),
                         "gap_p05": float(np.percentile(d_gap, 5)), "gap_p95": float(np.percentile(d_gap, 95))}

q4 = sl(cl, ("2011-10-04", "2011-12-30"))
misc["q4_2011"] = {c: float((1 + q4[c]).prod() - 1) for c in ("STRATEGY", "buy_hold_QQQ", "buy_hold_TQQQ")}

json.dump(misc, open(OUT / "ladder-misc.json", "w"), indent=1)
pd.set_option("display.width", 220)
print(L[L.line.isin(["STRATEGY", "buy_hold_QQQ", "buy_hold_TQQQ"])][
    ["window", "line", "ann_return", "sharpe_naive", "sharpe_lo", "sortino", "calmar", "max_dd",
     "rank_sharpe_naive", "rank_sharpe_lo", "rank_sortino", "rank_calmar"]].round(5).to_string(index=False))
print(json.dumps({k: v for k, v in misc.items() if not k.startswith("loyo")}, indent=1))
for k, v in misc.items():
    if k.startswith("loyo"):
        print(k, {kk: round(vv, 3) for kk, vv in v.items() if kk != "by_year_removed"})
