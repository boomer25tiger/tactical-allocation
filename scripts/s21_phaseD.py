"""Session 21 phase D. The beta decomposition.

RULES STATED BEFORE RUNNING.
  Benchmark. The investable buy-and-hold QQQ ladder line, charged the same
  cost model, rather than the raw index return, since the decomposition is
  against a line the study actually reports.
  Newey-West lag. 21 sessions, which 8.11 fixes before the run for every
  alpha t-statistic in this project. Not chosen here.
  Rolling window. config.CRASH_HORIZON_SESSIONS, being the only rolling
  lookback the register records for a return-based estimator, read from
  config rather than chosen here.
  Timing form. Excess return is decomposed as
      r_s = beta_bar * r_q + (beta_t - beta_bar) * r_q + e_t
  where beta_bar is the full-window beta and beta_t the rolling beta lagged
  one session so no session uses its own data. The three terms are the
  static exposure component, the timing component, and the residual.
  TOL_PC = 1e-9 on the positive control, being beta 1.0 and alpha 0.0 from
  regressing the benchmark on itself through the same code path.
"""
from __future__ import annotations
import csv, math, resource, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
from src import config              # noqa: E402
OUT = ROOT / "outputs" / "session-21"
NW_LAG = 21
TOL_PC = 1e-9
t0 = time.time(); rows = []
ANN = math.sqrt(252.0)


def sharpes(x):
    """naive and Lo-corrected annualised Sharpe of an excess-return array."""
    mu, sd = x.mean(), x.std(ddof=1)
    if sd == 0:
        return float("nan"), float("nan")
    naive = mu/sd*ANN
    xc = x-mu; den = float(np.dot(xc, xc)); q = 252
    acf = sum((q-k)*float(np.dot(xc[:-k], xc[k:]))/den for k in range(1, q))
    sc = q + 2.0*acf
    return naive, (mu/sd)*q/math.sqrt(sc) if sc > 0 else float("nan")


def ols_nw(y, x, lag):
    X = np.column_stack([np.ones(len(x)), x])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X@b
    ss_tot = float(((y-y.mean())**2).sum())
    r2 = 1.0 - float((resid**2).sum())/ss_tot if ss_tot > 0 else float("nan")
    n, k = X.shape
    XtXi = np.linalg.inv(X.T@X)
    S = (X*resid[:, None]).T@(X*resid[:, None])
    for l in range(1, lag+1):
        w = 1.0 - l/(lag+1.0)
        A = (X[l:]*resid[l:, None]).T@(X[:-l]*resid[:-l, None])
        S += w*(A+A.T)
    V = XtXi@S@XtXi
    return b[0], b[1], r2, resid, b[0]/math.sqrt(V[0, 0])


env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))


def run(rws):
    return bt.run_account(sig["sig"], o2o, rws, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM],
                          slip_fn=C.slip_class_premium(), cap_fn=cap_fn)


acc_s = run(sig["rows"])
acc_q = run(LINES["buy_hold_QQQ"][0](o2o, sig["rows"], i0))
rf_all = bt.rf_per_session(acc_s["daily"].index)
idx = acc_s["daily"].index[acc_s["daily"].index >= C.PRIMARY_START]
rs = acc_s["daily"]["ret"].reindex(idx).fillna(0.0).to_numpy()
rq = acc_q["daily"]["ret"].reindex(idx).fillna(0.0).to_numpy()
rf = rf_all.reindex(idx).fillna(0.0).to_numpy()
ys, yq = rs-rf, rq-rf
rows.append({"table": "setup", "item": "n_sessions", "value": len(ys)})
rows.append({"table": "setup", "item": "newey_west_lag", "value": NW_LAG,
             "note": "fixed by 8.11 before the run, not chosen here"})
rows.append({"table": "setup", "item": "rolling_window",
             "value": config.CRASH_HORIZON_SESSIONS,
             "note": "config.CRASH_HORIZON_SESSIONS, the only rolling lookback the "
                     "register records for a return-based estimator"})

# ---- positive control -----------------------------------------------------
a0, b0, r20, _, t0_ = ols_nw(yq, yq, NW_LAG)
pc_ok = abs(b0-1.0) <= TOL_PC and abs(a0) <= TOL_PC
for k, v, tgt in (("beta", b0, 1.0), ("alpha_daily", a0, 0.0), ("r_squared", r20, 1.0)):
    rows.append({"table": "positive_control", "item": k, "value": v, "target": tgt,
                 "abs_gap": abs(v-tgt)})
rows.append({"table": "positive_control", "item": "tolerance", "value": TOL_PC,
             "note": "stated before comparing"})
rows.append({"table": "positive_control", "item": "verdict",
             "note": "PASS" if pc_ok else "FAIL"})
print(f"positive control {'PASS' if pc_ok else 'FAIL'}: beta {b0:.12f} alpha {a0:.3e}")

# ---- static decomposition -------------------------------------------------
a, beta, r2, resid, t_a = ols_nw(ys, yq, NW_LAG)
# The OLS residual has mean exactly zero when an intercept is fitted, so its
# Sharpe is identically zero and carries no information. The quantity that does
# is the beta-hedged excess return, being the strategy less beta times the
# benchmark with the intercept retained, whose mean is alpha.
hedged = ys - beta * yq
nvR, loR = sharpes(hedged)
g = float(np.prod(1.0 + hedged))
rows.append({"table": "static", "item": "residual_definition",
             "note": "the beta-hedged excess return ys minus beta times yq, retaining "
                     "the intercept. The fitted OLS residual has mean zero by "
                     "construction and its Sharpe is identically zero, which is a "
                     "property of the estimator rather than a result"})
rows += [{"table": "static", "item": "beta", "value": beta},
         {"table": "static", "item": "alpha_annualised", "value": a*252.0},
         {"table": "static", "item": "r_squared", "value": r2},
         {"table": "static", "item": "alpha_t_newey_west", "value": t_a},
         {"table": "static", "item": "residual_ann_return",
          "value": float(g**(252.0/len(hedged))-1.0)},
         {"table": "static", "item": "residual_ann_vol",
          "value": float(hedged.std(ddof=1)*ANN)},
         {"table": "static", "item": "residual_sharpe_naive", "value": nvR},
         {"table": "static", "item": "residual_sharpe_lo", "value": loR}]
print(f"static: beta {beta:.6f} alpha_ann {a*252:.6f} R2 {r2:.6f} t {t_a:.4f}")
print(f"  hedged residual ann {g**(252.0/len(hedged))-1.0:.6f} naive {nvR:.6f} lo {loR:.6f}")

# ---- rolling decomposition ------------------------------------------------
Wn = int(config.CRASH_HORIZON_SESSIONS)
bt_ = np.full(len(ys), np.nan)
for i in range(Wn, len(ys)):
    xs, ysl = yq[i-Wn:i], ys[i-Wn:i]
    v = float(((xs-xs.mean())**2).sum())
    if v > 0:
        bt_[i] = float(((xs-xs.mean())*(ysl-ysl.mean())).sum())/v
ok = ~np.isnan(bt_)
rows += [{"table": "rolling", "item": "window", "value": Wn},
         {"table": "rolling", "item": "beta_mean", "value": float(bt_[ok].mean())},
         {"table": "rolling", "item": "beta_sd", "value": float(bt_[ok].std(ddof=1))},
         {"table": "rolling", "item": "beta_min", "value": float(bt_[ok].min())},
         {"table": "rolling", "item": "beta_max", "value": float(bt_[ok].max())},
         {"table": "rolling", "item": "share_beta_above_1.0",
          "value": float((bt_[ok] > 1.0).mean())},
         {"table": "rolling", "item": "share_beta_above_1.7",
          "value": float((bt_[ok] > 1.7).mean())},
         {"table": "rolling", "item": "n_sessions_with_beta", "value": int(ok.sum())}]
print(f"rolling beta over {Wn}: mean {bt_[ok].mean():.4f} sd {bt_[ok].std(ddof=1):.4f} "
      f"min {bt_[ok].min():.4f} max {bt_[ok].max():.4f}")

# ---- timing decomposition -------------------------------------------------
b_lag = np.roll(bt_, 1); b_lag[0] = np.nan
m = ~np.isnan(b_lag)
static_c = beta*yq[m]
timing_c = (b_lag[m]-beta)*yq[m]
resid_c = ys[m]-static_c-timing_c
for nm, arr in (("static_exposure", static_c), ("timing", timing_c), ("residual", resid_c)):
    nv, lo = sharpes(arr)
    rows.append({"table": "timing_decomposition", "item": f"{nm}_ann_contribution",
                 "value": float(arr.mean()*252.0)})
    rows.append({"table": "timing_decomposition", "item": f"{nm}_sharpe_naive", "value": nv})
    rows.append({"table": "timing_decomposition", "item": f"{nm}_sharpe_lo", "value": lo})
rows.append({"table": "timing_decomposition", "item": "total_ann_check",
             "value": float(ys[m].mean()*252.0),
             "note": "the three components sum to the strategy's own annualised mean "
                     "excess return by construction"})
print(f"timing: static {static_c.mean()*252:+.6f} timing {timing_c.mean()*252:+.6f} "
      f"residual {resid_c.mean()*252:+.6f}")

# ---- exposure-matched null ------------------------------------------------
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
rows += [{"table": "exposure_matched", "item": "ann_return", "value": mm["ann_return"]},
         {"table": "exposure_matched", "item": "ann_vol", "value": mm["ann_vol"]},
         {"table": "exposure_matched", "item": "sharpe_naive", "value": nvm},
         {"table": "exposure_matched", "item": "sharpe_lo", "value": lom},
         {"table": "exposure_matched", "item": "ann_turnover", "value": mm["ann_turnover"]},
         {"table": "exposure_matched", "item": "construction",
          "note": "QQQ held at the canonical's own rolling realised beta lagged one "
                  "session, rebalanced daily, charged the identical cost model"}]
lad = pd.read_csv(ROOT/"outputs/session-20/rebuilt/metrics-full.csv")
lad = lad[(lad.table == "metrics") & (lad.panel == "realized")
          & (lad.convention == "o2o") & (lad.window == "primary")]
for metric, val in (("sharpe_naive", nvm), ("sharpe_lo", lom)):
    better = int((lad[metric] > val).sum())
    rows.append({"table": "exposure_matched", "item": f"ladder_rank_{metric}",
                 "value": better+1,
                 "note": f"position among the twelve rebuilt ladder rows plus this line, "
                         f"so of thirteen"})
print(f"exposure-matched: ann {mm['ann_return']:.6f} naive {nvm:.6f} lo {lom:.6f} "
      f"turnover {mm['ann_turnover']:.2f}")
with open(OUT/"beta-decomposition.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "target", "abs_gap", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'beta-decomposition.csv'} with {len(rows)} rows")
print(f"phase D peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9:.3f} GB, "
      f"{time.time()-t0:.1f}s")
