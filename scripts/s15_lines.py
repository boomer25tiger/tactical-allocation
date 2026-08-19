"""Session 15 shared ladder-line builders and the completed metric set.

The line builders reproduce session 14's step-1 construction. The step-3
positive control checks that reproduction against session 14's ladder.csv
to four decimals before any new metric is emitted.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
import scripts.s14_common as C
from src import config
from src.portfolio import SLEEVE_ORDER, sleeve_label

INVERSE = {"SQQQ", "PSQ", "SH", "TECS", "SOXS"}
MEAN_EFF_EXPOSURE = 1.70
# Newey-West lag fixed before the run: 21 sessions, one trading month,
# matching the block length session 14 used for the Romano-Wolf bootstrap
# and the cap lookback. Andrews automatic bandwidth reported alongside.
NW_LAG = 21


def build_env():
    return C.build_env(verbose=False)


# ---------------------------------------------------------------------------
# Line builders (session 14 step 1 construction)
# ---------------------------------------------------------------------------

def rows_from_weights(wseq, always_emit=False):
    out, prev = [], None
    for i in sorted(wseq):
        t = wseq[i]
        changed = always_emit or (prev is None) or (set(t) != set(prev)) or \
            any(abs(t[k] - prev.get(k, 0)) > 1e-12 for k in t)
        out.append({"i": i, "changed": changed, "targets": dict(t) if changed else None})
        if changed:
            prev = dict(t)
    return out


def first_fillable(panel, tickers, start_i, cal):
    arrs = {t: panel[t].raw_close.reindex(cal).to_numpy() for t in tickers}
    for i in range(max(start_i, config.WARMUP_SESSIONS), len(cal)):
        if all(not math.isnan(arrs[t][i]) for t in tickers):
            return i
    return len(cal) - 1


def make_lines(cal):
    def buy_and_hold(ticker):
        def f(panel, srows, i0):
            return rows_from_weights({first_fillable(panel, [ticker], i0, cal):
                                      {ticker: 1.0}})
        return f

    def daily_constant(ticker, weight):
        def f(panel, srows, i0):
            j = first_fillable(panel, [ticker], i0, cal)
            return rows_from_weights({i: {ticker: weight} for i in range(j, len(cal))},
                                     always_emit=True)
        return f

    def vol_targeted(panel, srows, i0):
        j = first_fillable(panel, ["TQQQ"], i0, cal)
        r = panel["QQQ"].ret_total.reindex(cal)
        rv = r.rolling(60).std() * math.sqrt(252)
        raw = (1.0 / rv).replace([np.inf, -np.inf], np.nan).shift(1)
        scale = MEAN_EFF_EXPOSURE / raw.iloc[j:].mean()
        eff = (raw * scale).clip(0.0, 3.0)
        return rows_from_weights({i: {"TQQQ": float(eff.iloc[i] / 3.0)}
                                  for i in range(j, len(cal))
                                  if not math.isnan(eff.iloc[i])}, always_emit=True)

    def naive_fast(panel, srows, i0):
        j = first_fillable(panel, ["TQQQ"], i0, cal)
        r = panel["QQQ"].ret_total.reindex(cal).shift(1)
        return rows_from_weights({i: ({"TQQQ": 1.0} if (r.iloc[i] or 0) > 0 else {})
                                  for i in range(j, len(cal))})

    def equal_weight(panel, srows, i0):
        tk = [t for t in ra.TARGET_TICKERS if t in panel.frames]
        j = first_fillable(panel, tk, i0, cal)
        w = 1.0 / len(tk)
        return rows_from_weights({j: {t: w for t in tk}})

    def sleeve_standalone(k):
        def f(panel, srows, i0):
            seq = {r["i"]: dict(r["sleeves"][k]) for r in srows
                   if r["sleeves"][k] is not None}
            return rows_from_weights(seq)
        return f

    def long_legs_only(panel, srows, i0):
        seq, cur = {}, {}
        for r in srows:
            if r["changed"] and r["targets"] is not None:
                cur = {t: w for t, w in r["targets"].items() if t not in INVERSE}
            seq[r["i"]] = dict(cur)
        return rows_from_weights(seq)

    lines = {
        "buy_hold_QQQ": (buy_and_hold("QQQ"), "window_entry"),
        "buy_hold_TQQQ": (buy_and_hold("TQQQ"), "window_entry"),
        "vol_targeted_QQQ_matched": (vol_targeted, "window_entry"),
        "naive_fast_1d_momentum": (naive_fast, "window_entry"),
        "matched_exposure_levered_QQQ_1.70":
            (daily_constant("TQQQ", MEAN_EFF_EXPOSURE / 3.0), "window_entry"),
        "long_legs_only": (long_legs_only, "strategy_stream"),
        "equal_weight_universe": (equal_weight, "window_entry"),
    }
    for k in SLEEVE_ORDER:
        lines[f"sleeve_{k}_standalone"] = (sleeve_standalone(k), "strategy_stream")
    return lines


# ---------------------------------------------------------------------------
# Metric set
# ---------------------------------------------------------------------------

def _dd_series(r: pd.Series) -> pd.Series:
    g = (1 + r).cumprod()
    return g / g.cummax() - 1.0


def drawdown_metrics(r: pd.Series) -> dict:
    dd = _dd_series(r)
    g = (1 + r).cumprod()
    peak = g.cummax()
    in_dd = dd < -1e-12
    out = {"max_drawdown": float(dd.min())}
    # episodes
    eps, start = [], None
    for i, (d, flag) in enumerate(zip(dd.index, in_dd.to_numpy())):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            eps.append((start, i - 1))
            start = None
    if start is not None:
        eps.append((start, len(dd) - 1))
    depths = [float(dd.iloc[a:b + 1].min()) for a, b in eps]
    durs = [b - a + 1 for a, b in eps]
    deep = [(d, u) for d, u in zip(depths, durs) if d <= -0.20]
    out["n_drawdowns_gt_20pct"] = len(deep)
    out["mean_duration_drawdowns_gt_20pct_sessions"] = \
        float(np.mean([u for _, u in deep])) if deep else np.nan
    if eps:
        k = int(np.argmin(depths))
        a, b = eps[k]
        out["max_dd_duration_sessions"] = int(b - a + 1)
        out["max_dd_duration_calendar_days"] = int((dd.index[b] - dd.index[a]).days)
        trough = int(dd.iloc[a:b + 1].idxmin() == dd.index) if False else None
        t_idx = dd.iloc[a:b + 1].idxmin()
        rec = dd.loc[t_idx:]
        recovered = rec[rec >= -1e-12]
        if len(recovered):
            out["time_to_recovery_sessions"] = int(
                list(dd.index).index(recovered.index[0]) - list(dd.index).index(t_idx))
            out["recovered_within_window"] = True
        else:
            out["time_to_recovery_sessions"] = np.nan
            out["recovered_within_window"] = False
    ulcer = float(np.sqrt(np.mean((dd * 100.0) ** 2)))
    out["ulcer_index"] = ulcer
    n = len(r)
    ann = float((1 + r).prod() ** (252 / n) - 1)
    out["pain_ratio"] = ann / (ulcer / 100.0) if ulcer > 0 else np.nan
    return out


def standalone_metrics(r: pd.Series, nav: pd.Series | None = None,
                       orders: pd.DataFrame | None = None) -> dict:
    r = r.dropna()
    n = len(r)
    rf = bt.rf_per_session(r.index).fillna(0.0)
    ex = (r - rf).dropna()
    g = (1 + r).cumprod()
    ann = float(g.iloc[-1] ** (252 / n) - 1)
    vol = float(r.std(ddof=1) * math.sqrt(252))
    dd = _dd_series(r)
    mdd = float(dd.min())
    m = {"n_sessions": n, "total_return": float(g.iloc[-1] - 1), "ann_return": ann,
         "ann_vol": vol,
         "sharpe_naive": float(ex.mean() / ex.std(ddof=1) * math.sqrt(252)),
         "sharpe_lo": bt.lo_sharpe(ex),
         "max_drawdown": mdd,
         "calmar": ann / abs(mdd) if mdd < 0 else np.nan,
         "arith_mean_excess_ann": float(ex.mean() * 252)}
    if orders is not None and nav is not None and len(orders):
        od = orders[(orders["date"] >= r.index.min()) & (orders["date"] <= r.index.max())]
        navw = nav.reindex(r.index)
        m["ann_turnover"] = float(od["value"].sum() / 2 / navw.mean() / (n / 252)) \
            if len(od) else 0.0
    else:
        m["ann_turnover"] = 0.0
    # distributional
    down = ex[ex < 0]
    dsd = float(down.std(ddof=1) * math.sqrt(252)) if len(down) > 1 else np.nan
    m["downside_deviation_ann"] = dsd
    m["sortino_mar_dtb3"] = float(ex.mean() * 252 / dsd) if dsd and dsd > 0 else np.nan
    m["skewness"] = float(r.skew())
    m["excess_kurtosis"] = float(r.kurtosis())
    for q, lab in ((0.05, "95"), (0.01, "99")):
        v = float(np.percentile(r, q * 100))
        cv = float(r[r <= v].mean())
        m[f"var_{lab}_daily"] = v
        m[f"cvar_{lab}_daily"] = cv
        m[f"var_{lab}_annualised"] = v * math.sqrt(252)
        m[f"cvar_{lab}_annualised"] = cv * math.sqrt(252)
    m.update(drawdown_metrics(r))
    # stability
    roll = r.rolling(252)
    rs = (roll.mean() - rf.reindex(r.index).rolling(252).mean()) / roll.std(ddof=1) * math.sqrt(252)
    rs = rs.dropna()
    m["rolling_12m_sharpe_min"] = float(rs.min()) if len(rs) else np.nan
    m["rolling_12m_sharpe_max"] = float(rs.max()) if len(rs) else np.nan
    m["rolling_12m_sharpe_frac_below_zero"] = float((rs < 0).mean()) if len(rs) else np.nan
    mo = (1 + r).resample("ME").prod() - 1
    m["pct_positive_months"] = float((mo > 0).mean())
    h = len(r) // 2
    for lab, seg in (("first", r.iloc[:h]), ("second", r.iloc[h:])):
        exs = (seg - rf.reindex(seg.index)).dropna()
        m[f"split_half_{lab}_sharpe_lo"] = bt.lo_sharpe(exs) if len(exs) > 260 else np.nan
        m[f"split_half_{lab}_ann_return"] = float(
            (1 + seg).prod() ** (252 / len(seg)) - 1)
    # implementation
    tvr = m["ann_turnover"]
    m["return_per_unit_turnover"] = ann / tvr if tvr > 0 else np.nan
    m["turnover_adjusted_sharpe"] = m["sharpe_lo"] / tvr if tvr > 0 else np.nan
    return m


def newey_west_t(y: np.ndarray, X: np.ndarray, lag: int) -> tuple:
    """OLS with Newey-West standard errors; returns (coef, t, se)."""
    n = len(y)
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    S = (X * resid[:, None]).T @ (X * resid[:, None])
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        u = X[L:] * resid[L:, None]
        v = X[:-L] * resid[:-L, None]
        G = u.T @ v
        S += w * (G + G.T)
    cov = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(cov))
    return beta, beta / se, se


def andrews_bandwidth(resid: np.ndarray) -> float:
    """Andrews (1991) automatic bandwidth for the Bartlett kernel from an
    AR(1) approximation."""
    x = resid[:-1]
    y = resid[1:]
    denom = float(np.dot(x, x))
    rho = float(np.dot(x, y) / denom) if denom > 0 else 0.0
    rho = max(min(rho, 0.97), -0.97)
    a1 = 4 * rho ** 2 / ((1 - rho) ** 2 * (1 + rho) ** 2)
    return float(1.1447 * (a1 * len(resid)) ** (1 / 3))


def relative_metrics(strategy: pd.Series, benchmark: pd.Series) -> dict:
    j = pd.DataFrame({"s": strategy, "b": benchmark}).dropna()
    if len(j) < 60:
        return {}
    rf = bt.rf_per_session(j.index).fillna(0.0)
    y = (j["s"] - rf).to_numpy()
    x = (j["b"] - rf).to_numpy()
    X = np.column_stack([np.ones(len(x)), x])
    beta, tstat, se = newey_west_t(y, X, NW_LAG)
    yhat = X @ beta
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    d = j["s"] - j["b"]
    te = float(d.std(ddof=1) * math.sqrt(252))
    alpha_ann = float(beta[0] * 252)
    up = j[j["b"] > 0]
    dn = j[j["b"] < 0]
    return {"alpha_ann": alpha_ann,
            "beta": float(beta[1]),
            "tracking_error_ann": te,
            "information_ratio": float(d.mean() * 252 / te) if te > 0 else np.nan,
            "r_squared": 1 - ss_res / ss_tot if ss_tot > 0 else np.nan,
            "alpha_t_newey_west": float(tstat[0]),
            "newey_west_lag": NW_LAG,
            "andrews_bandwidth": andrews_bandwidth(y - yhat),
            "up_capture": float(up["s"].mean() / up["b"].mean())
            if len(up) and up["b"].mean() != 0 else np.nan,
            "down_capture": float(dn["s"].mean() / dn["b"].mean())
            if len(dn) and dn["b"].mean() != 0 else np.nan,
            "n_up_days": int(len(up)), "n_down_days": int(len(dn))}


STANDALONE_KEYS = None   # filled by the driver from a sample metric dict
