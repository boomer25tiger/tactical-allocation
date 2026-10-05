"""h05. Evidence on the fund series itself (slides 1, 3, 6, 7, 11, 12, 13, 16, 18, 21).

The deck presents the 25% volatility-target fund as the product. This script
re-measures on the fund the evidence that h03 and session 30 measure on the
engine: its rank against the eleven comparison lines, holdout calendar years
and concentration, leave-one-year-out Sharpe, the stationary bootstrap of the
holdout Sharpe and of its gap to QQQ, and the single- and five-factor
regressions. It also passes the uniform cost sweep through the overlay and
computes rolling five-year investor outcomes after fees.

PBO, the timing nulls, Romano-Wolf and the holdout prediction test the signal
and stay on the engine; they are not re-run here.

Needs outputs/hw2/constnav-10m-daily.csv (run h01 first). Importing engine
builds the panel for the cost sweep and the factor returns.

Writes to outputs/hw2/
    fund-ladder.csv          fund and the eleven comparison lines by window, with ranks
    fund-holdout-years.csv   calendar-year returns of fund and QQQ in the holdout
    fund-holdout-path.csv    growth of $1 in fund and QQQ over the holdout
    fund-cost-sweep.csv      fund metrics under a uniform round-turn cost of 0 to 50 bp
    fund-rolling-5y.csv      five-year outcomes from every monthly start, both fee classes
    fund-evidence.json       concentration, LOYO, bootstrap, factor regressions, controls,
                             rolling five-year summaries
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (OUT, ROOT, WINDOWS, P12, H, ANN, metrics, overlay,  # noqa: E402
                    net_of_fees, sl, stationary_blocks)
import engine  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

bt, C = engine.bt, engine.C
NW_LAG, NREP, SEED, BLOCK = 21, 10000, 20260823, 21

D = pd.read_csv(OUT / "constnav-10m-daily.csv", index_col=0, parse_dates=True)
r, q, rf = D["strat"], D["qqq"], D["rf"]
fund, w = overlay(r, rf)
ev = {}

# 1. Fund in place of the engine in the twelve-line ladder.
cl = pd.read_parquet(ROOT / "outputs" / "session-27" / "_combined_line_returns.parquet")
cl.index = pd.DatetimeIndex(cl.index)
rfl = bt.rf_per_session(cl.index).fillna(0.0)
rows = []
for wn, win in WINDOWS.items():
    rows.append({"window": wn, "line": "FUND", **metrics(sl(fund, win), sl(rf, win))})
    for c in cl.columns:
        if c != "STRATEGY":
            rows.append({"window": wn, "line": c, **metrics(sl(cl[c], win), rfl)})
L = pd.DataFrame(rows)
for k in ("sharpe_naive", "sharpe_lo", "sortino", "calmar", "ann_return"):
    L["rank_" + k] = L.groupby("window")[k].rank(ascending=False).astype(int)
L.to_csv(OUT / "fund-ladder.csv", index=False)

# 2. Holdout calendar years, growth path and concentration.
fh, qh = sl(fund, H), sl(q, H)
yrs = pd.DataFrame({"fund": (1 + fh).groupby(fh.index.year).prod() - 1,
                    "qqq": (1 + qh).groupby(qh.index.year).prod() - 1,
                    "sessions": fh.groupby(fh.index.year).size()})
yrs["gap_pp"] = (yrs["fund"] - yrs["qqq"]) * 100
yrs.to_csv(OUT / "fund-holdout-years.csv", index_label="year")
pd.DataFrame({"fund": (1 + fh).cumprod(), "qqq": (1 + qh).cumprod()}).to_csv(OUT / "fund-holdout-path.csv")
exh = (fh - sl(rf, H))
srt = fh.sort_values(ascending=False)
c_ = srt.cumsum()
ev["holdout_sessions_for_half_arithmetic_return"] = int((c_ < fh.sum() / 2).sum() + 1)
for k in (5, 10):
    keep = exh.drop(srt.index[:k])
    ev[f"holdout_naive_sharpe_without_best_{k}"] = float(keep.mean() / keep.std(ddof=1) * ANN)
ag = (fh - qh)
ev["holdout_arithmetic_gap_share_by_year"] = {int(y): float(v) for y, v in
                                               (ag.groupby(ag.index.year).sum() / ag.sum()).items()}

# 3. Leave one calendar year out.
for wn, win in (("P12", P12), ("H", H)):
    ex = sl(fund, win) - sl(rf, win)
    for name, f in (("naive", lambda x: x.mean() / x.std(ddof=1) * ANN), ("lo", bt.lo_sharpe)):
        vals = {int(y): float(f(ex[ex.index.year != y])) for y in sorted(set(ex.index.year))}
        ev[f"loyo_{name}_{wn}"] = {"base": float(f(ex)), "min": min(vals.values()),
                                   "max": max(vals.values()), "by_year_removed": vals}

# 4. Stationary bootstrap of the fund Sharpe and of its gap to QQQ, by window.
def sr(x):
    return x.mean(0) / x.std(0, ddof=1) * ANN
for wn, win in (("P12", P12), ("H", H)):
    E = np.column_stack([(sl(fund, win) - sl(rf, win)).to_numpy(),
                         (sl(q, win) - sl(rf, win)).to_numpy()])
    rng = np.random.default_rng(SEED)
    d_sr, d_gap = [], []
    for _ in range(NREP):
        s_ = sr(E[stationary_blocks(rng, len(E), BLOCK)])
        d_sr.append(s_[0]); d_gap.append(s_[0] - s_[1])
    pt = sr(E)
    ev[f"bootstrap_{wn}"] = {"sharpe": float(pt[0]), "sharpe_p05": float(np.percentile(d_sr, 5)),
                             "sharpe_p95": float(np.percentile(d_sr, 95)), "gap": float(pt[0] - pt[1]),
                             "gap_p05": float(np.percentile(d_gap, 5)),
                             "gap_p95": float(np.percentile(d_gap, 95))}

# 5. Factor regressions, open to open, Newey-West with Bartlett weights and 21 lags,
#    as in scripts/s30_phaseE.py. A positive control reruns them on the engine.
def factor(tk):
    if tk in engine.o2o.frames:
        return engine.o2o[tk].ret_total
    fr = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{tk}.parquet")
    fr.index = pd.DatetimeIndex(fr.index).tz_localize(None).normalize()
    ratio = (fr["Adj Close"] / fr["Close"]) if "Adj Close" in fr.columns else 1.0
    ao = fr["Open"].astype(float) * ratio
    return ao / ao.shift(1) - 1.0
FR = {tk: factor(tk) for tk in ("QQQ", "SMH", "XBI", "TLT", "UVXY")}

def ols_nw(y, X, lag=NW_LAG):
    Xd = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    e = y - Xd @ b
    XtXi = np.linalg.inv(Xd.T @ Xd)
    S = (Xd * e[:, None]).T @ (Xd * e[:, None])
    for l in range(1, lag + 1):
        A = (Xd[l:] * e[l:, None]).T @ (Xd[:-l] * e[:-l, None])
        S += (1.0 - l / (lag + 1.0)) * (A + A.T)
    V = XtXi @ S @ XtXi
    r2 = 1 - float((e ** 2).sum()) / float(((y - y.mean()) ** 2).sum())
    return {"alpha_ann": float(b[0] * 252), "t_alpha": float(b[0] / math.sqrt(V[0, 0])),
            "betas": [float(x) for x in b[1:]], "r2": r2}

def regress(series, win):
    idx = sl(series, win).index
    rfx = rfl.reindex(idx).fillna(0.0)
    y = (series.reindex(idx).fillna(0.0) - rfx).to_numpy()
    xq = (cl["buy_hold_QQQ"].reindex(idx).fillna(0.0) - rfx).to_numpy()
    X5 = np.column_stack([(FR[t].reindex(idx).fillna(0.0) - rfx).to_numpy() for t in FR])
    return {"single": ols_nw(y, xq.reshape(-1, 1)), "five": ols_nw(y, X5)}
ev["factor_control_engine_H"] = regress(cl["STRATEGY"], H)
for wn, win in (("P12", P12), ("H", H)):
    ev[f"factor_fund_{wn}"] = regress(fund, win)

# 6. Uniform round-turn cost sweep on the constant-$10M engine, through the overlay.
crow = []
for bp in (0, 5, 10, 20, 35, 50):
    engine.SLIP = C.slip_uniform(bp)
    d, *_ = engine.run(10_000_000.0, reset=True)
    rr = d["ret"]
    rfx = bt.rf_per_session(rr.index).fillna(0.0)
    ff, _ = overlay(rr, rfx)
    for wn in ("P12", "H"):
        win = WINDOWS[wn]
        crow.append({"window": wn, "round_turn_bp": bp,
                     **{f"fund_{k}": v for k, v in metrics(sl(ff, win), sl(rfx, win)).items()},
                     **{f"engine_{k}": v for k, v in metrics(sl(rr, win), sl(rfx, win)).items()}})
    print(f"cost {bp} bp done")
engine.SLIP = C.slip_class_premium()
pd.DataFrame(crow).to_csv(OUT / "fund-cost-sweep.csv", index=False)

# 7. Rolling five-year investor outcomes from the first session of every month,
#    January 2012 to the last month whose fifth anniversary falls inside the data.
f12 = fund[fund.index >= P12[0]]
starts = f12.groupby([f12.index.year, f12.index.month]).head(1).index
starts = [s for s in starts if s + pd.DateOffset(years=5) <= fund.index[-1]]
rrow = []
for s0 in starts:
    x = fund[s0:]
    for cls, mg, ic in (("founders 1.5/15", 0.015, 0.15), ("standard 2/20", 0.02, 0.20)):
        _, tot = net_of_fees(x, rf, mg, ic, nav0=1.0, years=5)
        e = tot["end_date"]
        rrow.append({"start": s0.date(), "end": e.date(), "class": cls, "gross": tot["gross"],
                     "net": tot["net"], "qqq": float((1 + q[s0:e]).prod()),
                     "in_sample_only": bool(e <= pd.Timestamp(P12[1]))})
R = pd.DataFrame(rrow)
R["net_annual"] = R["net"] ** 0.2 - 1
R["qqq_annual"] = R["qqq"] ** 0.2 - 1
R["ahead"] = R["net"] > R["qqq"]
R.to_csv(OUT / "fund-rolling-5y.csv", index=False)
summ = {}
for cls, g in R.groupby("class"):
    for part, gg in (("all", g), ("in_sample_only", g[g.in_sample_only]),
                     ("overlapping_holdout", g[~g.in_sample_only])):
        summ[f"{cls} | {part}"] = {
            "starts": int(len(gg)), "first": str(gg.start.min()), "last": str(gg.start.max()),
            "net_median": float(gg.net.median()), "net_min": float(gg.net.min()),
            "net_max": float(gg.net.max()), "qqq_median": float(gg.qqq.median()),
            "qqq_min": float(gg.qqq.min()), "qqq_max": float(gg.qqq.max()),
            "share_ahead": float(gg.ahead.mean()),
            "net_annual_median": float(gg.net_annual.median()),
            "qqq_annual_median": float(gg.qqq_annual.median())}
ev["rolling_5y"] = summ

json.dump(ev, open(OUT / "fund-evidence.json", "w"), indent=1, default=str)
pd.set_option("display.width", 220)
print(L[L.line.isin(["FUND", "buy_hold_QQQ", "buy_hold_TQQQ"])][
    ["window", "line", "ann_return", "sharpe_naive", "sharpe_lo", "sortino", "calmar", "max_dd",
     "rank_sharpe_naive", "rank_sharpe_lo", "rank_sortino", "rank_calmar"]].round(5).to_string(index=False))
print(yrs.round(4).to_string())
print(pd.DataFrame(crow)[["window", "round_turn_bp", "fund_sharpe_naive", "fund_ann_return",
                          "engine_sharpe_naive"]].round(4).to_string(index=False))
print(json.dumps({k: v for k, v in ev.items() if not k.startswith("loyo")}, indent=1, default=str))
for k, v in ev.items():
    if k.startswith("loyo"):
        print(k, {kk: round(vv, 3) for kk, vv in v.items() if kk != "by_year_removed"})
