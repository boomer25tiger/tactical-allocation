"""Session 30 phase E. The multi-factor decomposition.

Motivation as recorded at 9.79 and carried at 9.82. The static single-factor
regression against buy-and-hold QQQ carries an R-squared of 0.12086286064363738,
so 88 percent of holdout variance is unexplained by construction and lands in the
alpha of 0.5637941837318013, while the strategy holds semiconductor, biotechnology,
volatility and Treasury instruments none of which is QQQ.

ENTRY ORDER, stated before running and justified on economic grounds rather than
on fit. Equity market first, since it is the broadest exposure and the single
factor the study already regresses against. Semiconductor second, since SOXL and
SOXS are the largest sector positions the strategy takes. Biotechnology third,
since LABU is the remaining sector position. Long Treasury fourth, since TLT is
the risk-off leg of the T10 branch. Volatility last, since it is the narrowest
exposure and the one the strategy holds least often.
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
import scripts.s22_vm as VM                            # noqa: E402
import subprocess                                      # noqa: E402

OUT = ROOT / "outputs" / "session-30"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
NW_LAG, TOL_PC, ANN = 21, 1e-10, math.sqrt(252.0)
FACTORS = [("equity_market", "QQQ", "the broadest exposure and the single factor the "
            "study already regresses against"),
           ("semiconductor", "SMH", "SOXL and SOXS are the largest sector positions the "
            "strategy takes, and SMH is the ICE Semiconductor tracker their registered "
            "schedule names from 2021-08-25"),
           ("biotechnology", "XBI", "LABU's registered benchmark is the S&P "
            "Biotechnology Select Industry Index, which XBI tracks"),
           ("long_treasury", "TLT", "the risk-off leg of the T10 branch"),
           ("volatility", "UVXY", "the narrowest exposure and the one the strategy "
            "holds least often")]
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


_l = [float(x) for x in subprocess.run(["sysctl", "-n", "vm.loadavg"],
      capture_output=True, text=True).stdout.strip().strip("{} ").split()]
_s = VM.sample()
for k, v in (("load_1min", _l[0]), ("compressor_gib", _s["compressor_gib"]),
             ("swap_used_mb", _s["swap_used_mb"]), ("swap_free_mb", _s["swap_free_mb"])):
    add("machine_at_phase_E", item=k, value=v)


def ols_nw(y, X, lag):
    Xd = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ b
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((resid ** 2).sum()) / ss if ss > 0 else float("nan")
    XtXi = np.linalg.inv(Xd.T @ Xd)
    S = (Xd * resid[:, None]).T @ (Xd * resid[:, None])
    for l in range(1, lag + 1):
        w = 1.0 - l / (lag + 1.0)
        A = (Xd[l:] * resid[l:, None]).T @ (Xd[:-l] * resid[:-l, None])
        S += w * (A + A.T)
    V = XtXi @ S @ XtXi
    return b, r2, resid, b[0] / math.sqrt(V[0, 0])


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


print("building the environment")
env = C.build_env(verbose=False)
cal, sig, o2o, cap_fn = env["cal"], env["sigs"]["realized"], env["o2o"], env["cap_fn"]
panel = env["panels"]["realized"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(PRIMARY)))
acc_s = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                       slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
acc_q = bt.run_account(sig["sig"], o2o, LINES["buy_hold_QQQ"][0](o2o, sig["rows"], i0),
                       C.ANCHOR, commission_fn=C.ARMS[C.CANONICAL_ARM],
                       slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
rf_all = bt.rf_per_session(acc_s["daily"].index)

# The factor returns must carry the SAME convention as the designated cell, being
# open to open. scripts/s14_common.py o2o_panel_from rebuilds ret_total from
# adj_open, and reading a factor's close-to-close ret_total instead correlates
# only 0.2704559414562822 with the traded open-to-open line for QQQ, so a
# close-to-close factor set would not span the strategy's own returns.
FR = {}
for name, tk, why in FACTORS:
    present = tk in o2o.frames
    src = "the open-to-open panel built from the loaded universe"
    if present:
        FR[name] = o2o[tk].ret_total
    else:
        pp = ROOT / "data" / "raw" / "etf" / f"{tk}.parquet"
        if pp.exists():
            fr = pd.read_parquet(pp)
            fr.index = pd.DatetimeIndex(fr.index).tz_localize(None).normalize()
            if "Open" not in fr.columns:
                add("factor", item=name, instrument=tk, value=0,
                    note=why + ". THE FROZEN FILE CARRIES NO OPEN COLUMN, so an "
                               "open-to-open factor cannot be built from it")
                continue
            # the same adjustment ratio the loader applies, being adjusted close over
            # close, carried onto the open so the two conventions stay comparable
            ratio = (fr["Adj Close"] / fr["Close"]) if "Adj Close" in fr.columns else 1.0
            ao = fr["Open"].astype(float) * ratio
            FR[name] = ao / ao.shift(1) - 1.0
            present, src = True, ("frozen input at data/raw/etf, open-to-open built "
                                  "with the loader's own adjustment ratio")
    add("factor", item=name, instrument=tk, value=int(present), source=src,
        note=why + (". NO SUITABLE INSTRUMENT INSIDE THE FROZEN INPUTS" if not present
                    else ""))
    if not present:
        FR.pop(name, None)
add("factor_set", item="convention", value="open-to-open",
    note="matching the designated cell. A close-to-close factor set correlates only "
         "0.2704559414562822 with the traded open-to-open QQQ line and would not span "
         "the strategy's own returns")
add("factor_set", item="factors_available", value=len(FR),
    note="nothing is fetched. Every factor stands for an instrument already inside the "
         "frozen inputs")
add("setup", item="newey_west_lag", value=NW_LAG,
    note="fixed by 8.11 before the run, not chosen here")
add("setup", item="entry_order", value=",".join(n for n, *_ in FACTORS),
    note="stated before running and justified on economic grounds rather than on fit")

for wname, lo_d, hi_d in (("holdout", BOUNDARY, None),
                          ("primary", PRIMARY, BOUNDARY)):
    d = acc_s["daily"]
    m = d.index >= lo_d
    if hi_d is not None:
        m = m & (d.index < hi_d)
    idx = d.index[m]
    ys = (d["ret"].reindex(idx).fillna(0.0)
          - rf_all.reindex(idx).fillna(0.0)).to_numpy()
    rq = (acc_q["daily"]["ret"].reindex(idx).fillna(0.0)
          - rf_all.reindex(idx).fillna(0.0)).to_numpy()
    F = {k: (v.reindex(idx).fillna(0.0)
             - rf_all.reindex(idx).fillna(0.0)).to_numpy() for k, v in FR.items()}
    add("window", item=wname, value=len(idx),
        note=f"{idx.min().date()} to {idx.max().date()}")

    # positive control, each factor regressed on itself
    ok = True
    for k, v in F.items():
        b, r2, _, _ = ols_nw(v, v.reshape(-1, 1), NW_LAG)
        good = abs(b[1] - 1.0) <= TOL_PC and abs(b[0]) <= TOL_PC
        ok &= good
        add("positive_control", item=k, window=wname, beta=q(b[1]),
            alpha_daily=q(b[0]), value=int(good))
    add("positive_control", item="tolerance", window=wname, value=TOL_PC,
        note="stated before comparing")
    add("positive_control", item="verdict", window=wname,
        value="PASS" if ok else "FAIL")
    if not ok:
        print(f"positive control FAIL on {wname}")
        sys.exit(1)

    # single-factor baseline
    b1, r2_1, res1, t1 = ols_nw(ys, rq.reshape(-1, 1), NW_LAG)
    hedged = ys - b1[1] * rq
    nv1, lo1 = sharpes(hedged)
    for k, v in (("beta", b1[1]), ("alpha_annualised", b1[0] * 252.0),
                 ("r_squared", r2_1), ("alpha_t_newey_west", t1),
                 ("residual_sharpe_naive", nv1), ("residual_sharpe_lo", lo1)):
        add("single_factor", item=k, window=wname, value=q(v))
    print(f"{wname} single factor: beta {b1[1]:.6f} alpha {b1[0]*252:.6f} "
          f"R2 {r2_1:.6f} t {t1:.4f}")

    # incremental entry
    names = [n for n, *_ in FACTORS if n in F]
    prev_r2 = 0.0
    for j in range(1, len(names) + 1):
        use = names[:j]
        X = np.column_stack([F[k] for k in use])
        b, r2, resid, t = ols_nw(ys, X, NW_LAG)
        add("incremental", item=use[-1], window=wname, n_factors=j,
            r_squared=q(r2), incremental_r_squared=q(r2 - prev_r2),
            alpha_annualised=q(b[0] * 252.0), alpha_t_newey_west=q(t),
            note="factors entered in the pre-registered economic order")
        prev_r2 = r2
    # the full multi-factor fit
    X = np.column_stack([F[k] for k in names])
    b, r2, resid, t = ols_nw(ys, X, NW_LAG)
    add("multi_factor", item="alpha_annualised", window=wname, value=q(b[0] * 252.0),
        note="against the single-factor figure of 0.5637941837318013 over the holdout")
    add("multi_factor", item="r_squared", window=wname, value=q(r2))
    add("multi_factor", item="alpha_t_newey_west", window=wname, value=q(t))
    for k, coef in zip(names, b[1:]):
        add("loading", item=k, window=wname, value=q(coef))
    # the multi-factor residual, keeping the intercept as session 21 does
    mf_hedged = ys - X @ b[1:]
    nvm, lom = sharpes(mf_hedged)
    g = float(np.prod(1.0 + mf_hedged))
    for k, v in (("residual_ann_return", g ** (252.0 / len(mf_hedged)) - 1.0),
                 ("residual_ann_vol", mf_hedged.std(ddof=1) * ANN),
                 ("residual_sharpe_naive", nvm), ("residual_sharpe_lo", lom)):
        add("multi_factor_residual", item=k, window=wname, value=q(v),
            note="against the single-factor residual naive Sharpe of 1.527991674661622"
                 if k == "residual_sharpe_naive" else "")
    # correlations and variance inflation
    Fm = np.column_stack([F[k] for k in names])
    Cm = np.corrcoef(Fm, rowvar=False)
    for a in range(len(names)):
        for bb in range(a + 1, len(names)):
            add("factor_correlation", item=f"{names[a]}|{names[bb]}", window=wname,
                value=q(Cm[a, bb]))
        others = [c for c in range(len(names)) if c != a]
        _, r2a, _, _ = ols_nw(Fm[:, a], Fm[:, others], NW_LAG)
        add("variance_inflation", item=names[a], window=wname,
            value=q(1.0 / (1.0 - r2a)) if r2a < 1 else "inf",
            note="one over one minus the R-squared of that factor on the others")
    absorbed = (b1[0] - b[0]) * 252.0
    add("verdict", item="alpha_absorbed_by_the_extra_factors", window=wname,
        value=q(absorbed),
        note=f"the single-factor annualised alpha {float(b1[0]*252.0)!r} against the "
             f"multi-factor {float(b[0]*252.0)!r}. A multi-factor alpha materially below the "
             f"single-factor figure means the single-factor figure was measuring sector "
             f"exposure the benchmark omits, and an alpha that survives means it was not")
    add("verdict", item="share_of_the_single_factor_alpha_absorbed", window=wname,
        value=q(absorbed / (b1[0] * 252.0)) if b1[0] else "")
    print(f"{wname} multi factor: alpha {b[0]*252:.6f} R2 {r2:.6f} t {t:.4f}")

fn = ["table", "item", "window", "instrument", "source", "value", "beta", "alpha_daily",
      "n_factors", "r_squared", "incremental_r_squared", "alpha_annualised",
      "alpha_t_newey_west", "note"]
with open(OUT / "multi-factor.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote multi-factor.csv, {len(rows)} rows")
