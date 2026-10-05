"""h04. The fund: 25% volatility target, fees and checks (slides 8, 9, 11, 16 to 19, 21).

Reads outputs/hw2/constnav-10m-daily.csv (run h01 first) and applies the fund
overlay in common.overlay: exposure w = min(1, 0.25 / sigma), sigma the
annualised sd of the last 60 daily engine returns applied two sessions later,
the rest in T-bills, 10 bp per unit change in exposure. Fees follow
common.net_of_fees (daily management fee, incentive fee accrued daily above
the high-water mark and the year's T-bill return, paid at each anniversary).

Writes to outputs/hw2/
    fund-windows.csv       engine, fund gross, fund net at 1/20 over QQQ and at 2/20, QQQ, by window
    fund-start-dates.csv   seven start dates, each ending 2021-07-30
    fund-targets.csv       max drawdown and CAGR by target level and window
    fund-fees.csv          five-year investor outcomes for three start dates and both fee classes
    fund-checks.json       exposure, CAPM, lookbacks, fixed exposure, drawdown episodes,
                           fourth quarter 2011 and the review-rule bootstrap threshold
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (OUT, WINDOWS, P11, P12, H, ANN, metrics, overlay, net_of_fees,  # noqa: E402
                    sl, stationary_blocks, FEE_MGMT, FEE_INC)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

D = pd.read_csv(OUT / "constnav-10m-daily.csv", index_col=0, parse_dates=True)
r, q, rf = D["strat"], D["qqq"], D["rf"]
fund, w = overlay(r, rf)
checks = {}

# Windows.
rows = []
for wn, win in WINDOWS.items():
    x = sl(fund, win); t = sl(rf, win)
    lines = {"engine10m": sl(r, win), "fund_gross": x,
             "fund_net": net_of_fees(x, t, FEE_MGMT, FEE_INC, hurdle=sl(q, win))[0],
             "fund_net_2_20": net_of_fees(x, t, 0.02, 0.20)[0], "qqq": sl(q, win)}
    for k, s in lines.items():
        rows.append({"window": wn, "line": k, **metrics(s, t)})
    checks[f"avg_exposure_{wn}"] = float(sl(w, win).mean())
    for k in ("fund_gross", "fund_net", "fund_net_2_20"):        # CAPM against QQQ, Newey-West lag 8
        y = (lines[k] - t).to_numpy(); xx = (sl(q, win) - t).to_numpy()
        X = np.column_stack([np.ones(len(y)), xx]); b, *_ = np.linalg.lstsq(X, y, rcond=None)
        e = y - X @ b; n = len(y); S = (X * e[:, None]).T @ (X * e[:, None]) / n
        for l in range(1, 9):
            G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None]) / n; S += (1 - l / 9) * (G + G.T)
        Q = np.linalg.inv(X.T @ X / n); V = Q @ S @ Q / n
        checks[f"capm_{k}_{wn}"] = {"beta": float(b[1]), "alpha_ann": float(b[0] * 252),
                                    "t_alpha": float(b[0] / math.sqrt(V[0, 0]))}
checks["avg_exposure_2011-10-04_to_2026-08-14"] = float(sl(w, ("2011-10-04", "2026-08-14")).mean())
pd.DataFrame(rows).to_csv(OUT / "fund-windows.csv", index=False)

# Seven start dates, each ending on the last session before the holdout.
strip = []
for s0 in ("2011-10-04", "2012-01-03", "2012-07-02", "2013-01-02", "2014-01-02", "2015-01-02", "2016-01-04"):
    win = (s0, "2021-07-30"); x = sl(fund, win); t = sl(rf, win)
    g = metrics(x, t); qq = metrics(sl(q, win), t)
    n_ = metrics(net_of_fees(x, t, FEE_MGMT, FEE_INC, hurdle=sl(q, win))[0], t)
    n2 = metrics(net_of_fees(x, t, 0.02, 0.20)[0], t)
    strip.append({"start": s0, **{f"{a}_{k}": v for a, m in (("gross", g), ("net", n_), ("net_2_20", n2), ("qqq", qq))
                                  for k, v in m.items() if k != "n"}})
pd.DataFrame(strip).to_csv(OUT / "fund-start-dates.csv", index=False)

# Target levels: the rule picks the highest round target whose max drawdown
# stays within QQQ's over the in-sample data.
trow = []
for T in (0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
    f_, _ = overlay(r, rf, target=T)
    for wn, win in WINDOWS.items():
        m = metrics(sl(f_, win), sl(rf, win))
        trow.append({"target": T, "window": wn, "max_dd": m["max_dd"], "cagr": m["ann_return"],
                     "qqq_max_dd": metrics(sl(q, win), sl(rf, win))["max_dd"]})
pd.DataFrame(trow).to_csv(OUT / "fund-targets.csv", index=False)

# Lookback sensitivity and fixed exposure at the same average weight.
for wn, win in WINDOWS.items():
    t = sl(rf, win)
    checks[f"lookback_max_dd_{wn}"] = {lb: metrics(sl(overlay(r, rf, lookback=lb)[0], win), t)["max_dd"]
                                       for lb in (20, 60, 120)}
    wbar = float(sl(w, win).mean()); fx = wbar * sl(r, win) + (1 - wbar) * t
    mf, mv = metrics(fx, t), metrics(sl(fund, win), t)
    checks[f"fixed_exposure_{wn}"] = {"weight": wbar, "fixed_cagr": mf["ann_return"], "fixed_max_dd": mf["max_dd"],
                                      "vt_cagr": mv["ann_return"], "vt_max_dd": mv["max_dd"]}

# Drawdown episodes, depth over the engine's peak-to-trough span.
def span(x, a, b):
    g = (1 + x[a:b]).cumprod(); return float((g / g.cummax() - 1).min())
checks["episodes"] = {f"{a} to {b}": {"engine": span(r, a, b), "fund": span(fund, a, b)}
                      for a, b in (("2020-03-03", "2020-03-19"), ("2022-10-13", "2023-01-09"),
                                   ("2024-07-17", "2024-08-05"), ("2025-01-24", "2025-04-07"))}
q4 = ("2011-10-04", "2011-12-30")
checks["q4_2011"] = {"fund": float((1 + sl(fund, q4)).prod() - 1), "engine10m": float((1 + sl(r, q4)).prod() - 1),
                     "qqq_open_to_open": float((1 + sl(q, q4)).prod() - 1)}

# Five-year investor outcomes. QQQ compounds over the same sessions.
frow = []
for label, s0 in (("Jan 2012", "2012-01-03"), ("Aug 2016", "2016-08-01"), ("Aug 2021", "2021-08-02")):
    x = fund[s0:]
    for cls, mg, ic, nav0, hz in (("1/20 over QQQ", FEE_MGMT, FEE_INC, 10e6, q),
                                  ("2/20 over T-bills", 0.02, 0.20, 10e6, None)):
        _, tot = net_of_fees(x, rf, mg, ic, nav0=nav0, years=5, hurdle=hz)
        qv = nav0 * float((1 + q[s0:str(tot["end_date"].date())]).prod())
        frow.append({"start": label, "class": cls, "nav0": nav0, "end_date": tot["end_date"].date(),
                     "gross": tot["gross"], "net": tot["net"], "fees": tot["mgmt_fees"] + tot["incentive_fees"],
                     "net_annual": (tot["net"] / nav0) ** (1 / 5) - 1, "qqq_value": qv,
                     "qqq_annual": (qv / nav0) ** (1 / 5) - 1})
pd.DataFrame(frow).to_csv(OUT / "fund-fees.csv", index=False)

# Review rule. Distribution of a two-year (504-session) Sharpe after fees (1% and 20% over QQQ),
# from a stationary bootstrap of the fund's net daily returns from January 2012
# through the holdout (mean block 21 sessions, 10,000 draws, seed 20260823).
win = (P12[0], H[1]); t = sl(rf, win)
net = net_of_fees(sl(fund, win), t, FEE_MGMT, FEE_INC, hurdle=sl(q, win))[0]
E = (net - t).to_numpy()
rng = np.random.default_rng(20260823)
draws = [E[stationary_blocks(rng, len(E), 21, 504)] for _ in range(10000)]
srs = np.array([d.mean() / d.std(ddof=1) * ANN for d in draws])
checks["review_rule_two_year_net_sharpe"] = {"p05": float(np.percentile(srs, 5)), "p10": float(np.percentile(srs, 10)),
                                             "median": float(np.median(srs)),
                                             "full_period_net_sharpe": float(E.mean() / E.std(ddof=1) * ANN)}

json.dump(checks, open(OUT / "fund-checks.json", "w"), indent=1, default=str)
pd.set_option("display.width", 220)
print(pd.DataFrame(rows).round(5).to_string(index=False))
print(pd.DataFrame(strip)[["start", "gross_sortino", "net_sortino", "qqq_sortino", "gross_calmar",
                           "net_calmar", "qqq_calmar", "gross_sharpe_naive", "net_sharpe_naive",
                           "qqq_sharpe_naive"]].round(3).to_string(index=False))
print(pd.DataFrame(trow).round(4).to_string(index=False))
print(pd.DataFrame(frow).round(4).to_string(index=False))
print(json.dumps(checks, indent=1, default=str))
