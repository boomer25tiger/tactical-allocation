"""h06. Risk and portfolio statistics against QQQ (slide 7).

For the fund gross of fees, the fund after 2% and 20% fees, and buy-and-hold
QQQ, over P12 and the holdout. QQQ is the twelve-line ladder's buy_hold_QQQ
series, the same one behind slide 6.

Definitions (daily returns r, QQQ daily returns q, T-bill rf):
    beta, alpha    OLS of (r - rf) on (q - rf); alpha annualised x 252
    correlation    of daily r and q; R-squared is its square
    tracking error sd(r - q) x sqrt(252)
    information    mean(r - q) x 252 / tracking error
    capture        monthly, arithmetic mean of the fund's return in months
                   QQQ rose (fell) over QQQ's mean in those months
    skewness       of daily returns; excess kurtosis likewise (normal = 0)
    VaR, CVaR      historical one-day 95%, as positive losses: the 5th
                   percentile of daily returns and the mean below it
    months         calendar months compounded from daily returns; the last
                   holdout month (August 2026) is partial
    underwater     longest span from a NAV high to the next new high, in
                   sessions; a span still open at the window end counts to it

Writes outputs/hw2/fund-risk-stats.csv.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, P12, H, ANN, overlay, net_of_fees, sl  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scripts.s13_backtest as bt  # noqa: E402

D = pd.read_csv(OUT / "constnav-10m-daily.csv", index_col=0, parse_dates=True)
fund, _ = overlay(D["strat"], D["rf"])
cl = pd.read_parquet(ROOT / "outputs" / "session-27" / "_combined_line_returns.parquet")
cl.index = pd.DatetimeIndex(cl.index)
rfl = bt.rf_per_session(cl.index).fillna(0.0)


def underwater(r):
    g = (1 + r).cumprod().to_numpy()
    peak, start, longest = g[0], 0, 0
    for i, v in enumerate(g):
        if v >= peak:
            longest = max(longest, i - start)
            peak, start = v, i
    return max(longest, len(g) - 1 - start)


def stats(r, q, rf):
    ex, qx = r - rf, q - rf
    b = np.polyfit(qx, ex, 1)
    act = r - q
    te = act.std(ddof=1) * ANN
    rm = (1 + r).groupby([r.index.year, r.index.month]).prod() - 1
    qm = (1 + q).groupby([q.index.year, q.index.month]).prod() - 1
    up, dn = qm > 0, qm < 0
    var = -np.percentile(r, 5)
    corr = float(np.corrcoef(r, q)[0, 1])
    return {"beta": b[0], "alpha_ann": b[1] * 252, "correlation": corr, "r_squared": corr ** 2,
            "tracking_error": te, "information_ratio": act.mean() * 252 / te if te > 0 else np.nan,
            "upside_capture": rm[up].mean() / qm[up].mean(), "downside_capture": rm[dn].mean() / qm[dn].mean(),
            "skewness": float(r.skew()), "excess_kurtosis": float(r.kurt()),
            "var95_1d": var, "cvar95_1d": -r[r <= -var].mean(),
            "worst_day": -r.min(), "worst_month": -rm.min(), "best_month": rm.max(),
            "positive_months": float((rm > 0).mean()), "months": int(len(rm)),
            "longest_underwater_sessions": underwater(r)}


rows = []
for wn, win in (("P12", P12), ("H", H)):
    f = sl(fund, win)
    idx = f.index
    q = cl["buy_hold_QQQ"].reindex(idx).fillna(0.0)
    rf = rfl.reindex(idx).fillna(0.0)
    net = net_of_fees(f, sl(D["rf"], win), 0.02, 0.20)[0]
    for name, s in (("fund_gross", f), ("fund_net_2_20", net), ("qqq", q)):
        rows.append({"window": wn, "line": name, **stats(s, q, rf)})
R = pd.DataFrame(rows)
R.to_csv(OUT / "fund-risk-stats.csv", index=False)
pd.set_option("display.width", 250)
print(R.set_index(["window", "line"]).T.round(4).to_string())
