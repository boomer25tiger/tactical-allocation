"""Session 28 phase H. The beta decomposition over the holdout.

Mirror of session 21 phase D, run over the holdout span so the two windows are
comparable. The Newey-West lag is fixed by 8.11 at 21 and is not chosen here. The
rolling windows are the four session 22 used.
"""
from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s14_common as C                         # noqa: E402
import scripts.s15_lines as L                          # noqa: E402

OUT = ROOT / "outputs" / "session-28"
BOUNDARY = bt.HOLDOUT_BOUNDARY
NW_LAG, TOL_PC, ANN = 21, 1e-10, math.sqrt(252.0)
WINDOWS = (60, 120, 252, 504)
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


def sharpes(x, qq=252):
    mu, sd = x.mean(), x.std(ddof=1)
    nv = float(mu / sd * ANN)
    xc = x - mu
    den = float(np.dot(xc, xc))
    acf = sum((qq - k) * float(np.dot(xc[:-k], xc[k:])) / den for k in range(1, qq))
    scale = qq + 2.0 * acf
    lo = float("nan") if scale <= 0 else float(
        (mu / sd) * qq / math.sqrt(scale) * math.sqrt(252.0 / qq))
    return nv, lo


def ols_nw(y, x, lag):
    X = np.column_stack([np.ones(len(x)), x])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((resid ** 2).sum()) / ss_tot if ss_tot > 0 else float("nan")
    XtXi = np.linalg.inv(X.T @ X)
    S = (X * resid[:, None]).T @ (X * resid[:, None])
    for l in range(1, lag + 1):
        w = 1.0 - l / (lag + 1.0)
        A = (X[l:] * resid[l:, None]).T @ (X[:-l] * resid[:-l, None])
        S += w * (A + A.T)
    V = XtXi @ S @ XtXi
    return b[0], b[1], r2, resid, b[0] / math.sqrt(V[0, 0])


print("building the environment")
env = C.build_env(verbose=False)
cal, sig, o2o, cap_fn = env["cal"], env["sigs"]["realized"], env["o2o"], env["cap_fn"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))


def run(rws):
    return bt.run_account(sig["sig"], o2o, rws, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM],
                          slip_fn=C.slip_class_premium(), cap_fn=cap_fn)


acc_s = run(sig["rows"])
acc_q = run(LINES["buy_hold_QQQ"][0](o2o, sig["rows"], i0))
rf_all = bt.rf_per_session(acc_s["daily"].index)
idx = acc_s["daily"].index[acc_s["daily"].index >= BOUNDARY]
rs = acc_s["daily"]["ret"].reindex(idx).fillna(0.0).to_numpy()
rq = acc_q["daily"]["ret"].reindex(idx).fillna(0.0).to_numpy()
rf = rf_all.reindex(idx).fillna(0.0).to_numpy()
ys, yq = rs - rf, rq - rf
add("setup", item="window", value="holdout",
    note=f"{idx.min().date()} to {idx.max().date()}")
add("setup", item="n_sessions", value=len(ys), note="against 2472 in the primary window")
add("setup", item="newey_west_lag", value=NW_LAG,
    note="fixed by 8.11 before the run, not chosen here")
add("setup", item="rolling_windows", value=",".join(str(w) for w in WINDOWS),
    note="the four session 22 used")

# ---- positive control -------------------------------------------------------------
a0, b0, r20, _, _ = ols_nw(yq, yq, NW_LAG)
pc = abs(b0 - 1.0) <= TOL_PC and abs(a0) <= TOL_PC
for k, v, tgt in (("beta", b0, 1.0), ("alpha_daily", a0, 0.0), ("r_squared", r20, 1.0)):
    add("positive_control", item=k, value=q(v), target=tgt, abs_gap=q(abs(v - tgt)))
add("positive_control", item="tolerance", value=TOL_PC,
    note="stated before comparing")
add("positive_control", item="verdict", value="PASS" if pc else "FAIL",
    note="buy-and-hold QQQ regressed on itself through the same code path")
print(f"positive control {'PASS' if pc else 'FAIL'} beta {b0:.12f} alpha {a0:.3e}")
if not pc:
    sys.exit(1)

# ---- static regression --------------------------------------------------------------
a, beta, r2, resid, t_a = ols_nw(ys, yq, NW_LAG)
hedged = ys - beta * yq
nvR, loR = sharpes(hedged)
g = float(np.prod(1.0 + hedged))
add("static", item="residual_definition",
    note="the beta-hedged excess return, being the strategy less beta times the "
         "benchmark with the intercept retained. The fitted OLS residual has mean zero "
         "by construction and its Sharpe is identically zero, which is a property of "
         "the estimator rather than a result")
for k, v, prim in (("beta", beta, "1.108672858112171"),
                   ("alpha_annualised", a * 252.0, "0.28874420661558875"),
                   ("r_squared", r2, "0.18679426851145753"),
                   ("alpha_t_newey_west", t_a, "2.364283243646891"),
                   ("residual_ann_return", g ** (252.0 / len(hedged)) - 1.0, ""),
                   ("residual_ann_vol", hedged.std(ddof=1) * ANN, ""),
                   ("residual_sharpe_naive", nvR, "0.6558362612960221"),
                   ("residual_sharpe_lo", loR, "0.8649152595612315")):
    add("static", item=k, value=q(v), primary_window=prim,
        note="the primary-window figure is from outputs/session-21/beta-decomposition.csv"
             if prim else "")
print(f"static: beta {beta:.6f} alpha_ann {a*252:.6f} R2 {r2:.6f} t {t_a:.4f}")

# ---- rolling decomposition ------------------------------------------------------------
PRIM_TIMING = {60: "0.011293050910284682", 120: "0.027230151692897046",
               252: "-0.004075416692355631", 504: "-0.0077512681113622505"}
PRIM_SD = {60: "1.1646116827038935", 120: "0.6992985332538183",
           252: "0.41047564557798377", 504: "0.20922149429810166"}
matched = {}
for W in WINDOWS:
    bt_ = np.full(len(ys), np.nan)
    for i in range(W, len(ys)):
        xs, ysl = yq[i - W:i], ys[i - W:i]
        v = float(((xs - xs.mean()) ** 2).sum())
        if v > 0:
            bt_[i] = float(((xs - xs.mean()) * (ysl - ysl.mean())).sum()) / v
    ok = ~np.isnan(bt_)
    if ok.sum() < 10:
        add("rolling", item="insufficient_sessions", window=W, value=int(ok.sum()),
            note="the holdout is too short to fit this window")
        continue
    for k, v in (("beta_mean", bt_[ok].mean()), ("beta_sd", bt_[ok].std(ddof=1)),
                 ("beta_min", bt_[ok].min()), ("beta_max", bt_[ok].max()),
                 ("n_sessions_with_beta", ok.sum())):
        add("rolling", item=k, window=W, value=q(v),
            primary_window=PRIM_SD[W] if k == "beta_sd" else "",
            note="the primary-window standard deviation is from "
                 "outputs/session-22/beta-window-sensitivity.csv" if k == "beta_sd"
                 else "")
    b_lag = np.roll(bt_, 1); b_lag[0] = np.nan
    m = ~np.isnan(b_lag)
    static_c = beta * yq[m]
    timing_c = (b_lag[m] - beta) * yq[m]
    resid_c = ys[m] - static_c - timing_c
    for nm, arr in (("static_exposure", static_c), ("timing", timing_c),
                    ("residual", resid_c)):
        nv, lo = sharpes(arr)
        add("timing", item=f"{nm}_ann_contribution", window=W, value=q(arr.mean() * 252.0),
            primary_window=PRIM_TIMING[W] if nm == "timing" else "",
            note="the primary-window timing contribution is from "
                 "outputs/session-21/beta-decomposition.csv at 60 sessions and "
                 "outputs/session-22/beta-window-sensitivity.csv beyond it"
                 if nm == "timing" else "")
        add("timing", item=f"{nm}_sharpe_naive", window=W, value=q(nv))
        add("timing", item=f"{nm}_sharpe_lo", window=W, value=q(lo))
    add("timing", item="total_ann_check", window=W, value=q(ys[m].mean() * 252.0),
        note="the three components sum to the strategy's own annualised mean excess "
             "return by construction")
    # exposure-matched line at this window
    bser = pd.Series(b_lag, index=idx).clip(lower=0.0)
    seq = {}
    for i, dte in enumerate(idx):
        if not np.isnan(b_lag[i]):
            j = int(np.searchsorted(cal.to_numpy(), np.datetime64(dte)))
            seq[j] = {"QQQ": float(bser.iloc[i])}
    acc_m = run(L.rows_from_weights(seq, always_emit=True))
    rm = acc_m["daily"]["ret"].reindex(idx).dropna()
    mm = L.standalone_metrics(rm, acc_m["daily"]["nav"], acc_m["orders"])
    nvm, lom = sharpes((rm - rf_all.reindex(rm.index).fillna(0.0)).to_numpy())
    matched[W] = (nvm, lom)
    for k, v in (("ann_return", mm["ann_return"]), ("ann_vol", mm["ann_vol"]),
                 ("sharpe_naive", nvm), ("sharpe_lo", lom),
                 ("ann_turnover", mm["ann_turnover"])):
        add("exposure_matched", item=k, window=W, value=q(v))
    add("exposure_matched", item="beats_the_strategy_on_the_naive_sharpe", window=W,
        value=int(nvm > 1.637799226672021),
        note=f"the matched line reads {nvm!r} against the strategy's 1.637799226672021")
    print(f"  W={W:>3} beta_mean {bt_[ok].mean():+.4f} sd {bt_[ok].std(ddof=1):.4f} "
          f"timing {timing_c.mean()*252:+.6f} matched naive {nvm:.4f}")
add("exposure_matched", item="construction",
    note="QQQ held at the canonical's own rolling realised beta lagged one session, "
         "rebalanced daily, charged the identical cost model. It uses beta estimated "
         "from the strategy's own realised returns, so it is a decomposition rather "
         "than an ex-ante benchmark")

tm = {}
for r in rows:
    if r["table"] == "timing" and r["item"] == "timing_ann_contribution":
        tm[r["window"]] = float(r["value"])
signs = {np.sign(v) for v in tm.values()}
add("timing_summary", item="windows_fitted", value=len(tm))
add("timing_summary", item="timing_contribution_range",
    value=f"{min(tm.values())!r} to {max(tm.values())!r}" if tm else "",
    note="against a primary-window range of -0.0077512681113622505 to "
         "0.027230151692897046 across the same four windows")
add("timing_summary", item="changes_sign_across_the_window", value=int(len(signs) > 1))
add("timing_summary", item="material_over_the_holdout",
    value=int(any(abs(v) > 0.05 for v in tm.values())),
    note="material is recorded when any window's timing contribution exceeds 0.05 "
         "annualised in absolute value, against a strategy annualised excess mean of "
         f"{ys.mean()*252.0!r}. The primary-window finding was that timing contributes "
         f"essentially nothing at any window")

fn = ["table", "item", "window", "value", "target", "abs_gap", "primary_window", "note"]
with open(OUT / "holdout-beta.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote holdout-beta.csv, {len(rows)} rows")
