"""Session 28 phase C. The Lo estimator at holdout sample length.

Mirrors the session 20 D1 construction exactly, being a permutation null that
preserves each row's marginal distribution and destroys its ordering, 300 draws
per row. LO_SEED is the same 20260820 session 20 used and is fixed before drawing,
so the only difference between the two nulls is the sample.

No new holdout pass runs. The series come from
outputs/session-27/_holdout_line_returns.parquet, written in the session 27 read.
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

OUT = ROOT / "outputs" / "session-28"
LO_SEED, NPERM, Q = 20260820, 300, 252
QS = (1, 5, 21, 63, 126, 252)
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def lo_at(x, q):
    mu, sd = x.mean(), x.std(ddof=1)
    if sd == 0:
        return float("nan"), float("nan"), float("nan")
    xc = x - mu
    den = float(np.dot(xc, xc))
    acf = 0.0
    for k in range(1, q):
        acf += (q - k) * float(np.dot(xc[:-k], xc[k:])) / den
    scale = q + 2.0 * acf
    if scale <= 0:
        return float("nan"), acf, scale
    return (mu / sd) * q / math.sqrt(scale) * math.sqrt(252.0 / q), acf, scale


df = pd.read_parquet(ROOT / "outputs" / "session-27" / "_holdout_line_returns.parquet")
rf = bt.rf_per_session(df.index).reindex(df.index).fillna(0.0)
series = {ln: (df[ln] - rf).dropna().to_numpy() for ln in df.columns}
n = len(series["STRATEGY"])
add("meta", item="seed", value=LO_SEED, note="the same seed session 20 used, fixed "
    "before drawing, so the only difference between the two nulls is the sample")
add("meta", item="draws", value=NPERM)
add("meta", item="q", value=Q)
add("meta", item="n_sessions", value=n, note="against 2472 in the primary window")
add("meta", item="q_over_n", value=repr(Q / n),
    note="against 252/2472, being " + repr(252 / 2472))
add("meta", item="construction",
    note="permutation of the excess-return series, preserving the marginal "
         "distribution and destroying the ordering, mirroring session 20 D1")

NEG = -Q / 2.0
add("meta", item="negative_variance_threshold", value=NEG,
    note="the Lo scale q plus twice the weighted autocorrelation sum turns non-positive "
         "at this value. It depends on q alone and not on n, so it is the same "
         "threshold the primary window carried")

print(f"holdout n {n}, q {Q}, q/n {Q/n:.4f}")
inside_ct = 0
fac_of = {}
for ln, x in series.items():
    obs_lo, obs_acf, obs_scale = lo_at(x, Q)
    naive = x.mean() / x.std(ddof=1) * math.sqrt(252.0)
    obs_f = obs_lo / naive
    fac_of[ln] = float(obs_f)
    rng = np.random.default_rng(LO_SEED)
    facs, acfs = [], []
    for _ in range(NPERM):
        p = rng.permutation(x)
        v, a, _s = lo_at(p, Q)
        nv = p.mean() / p.std(ddof=1) * math.sqrt(252.0)
        facs.append(v / nv); acfs.append(a)
    facs, acfs = np.array(facs), np.array(acfs)
    p05, p95 = float(np.percentile(facs, 5)), float(np.percentile(facs, 95))
    inside = bool(p05 <= obs_f <= p95)
    inside_ct += int(inside)
    add("lo_null", item=ln, value=repr(float(obs_f)), naive=repr(float(naive)),
        lo=repr(float(obs_lo)), acf_sum=repr(float(obs_acf)),
        null_mean=repr(float(facs.mean())), null_sd=repr(float(facs.std(ddof=1))),
        null_p05=repr(p05), null_p95=repr(p95), inside_own_null=int(inside),
        acf_null_sd=repr(float(acfs.std(ddof=1))),
        distance_to_negative_variance=repr(float(obs_acf - NEG)),
        distance_to_negative_variance_sd=repr(
            float((obs_acf - NEG) / acfs.std(ddof=1))))
    print(f"  {ln:<34} factor {obs_f:.4f} null [{p05:.4f}, {p95:.4f}] inside {inside}")
add("summary", item="rows_inside_own_null", value=inside_ct,
    note=f"of {len(series)} ladder rows at holdout length, against 9 of 12 at primary "
         f"length recorded at 9.37")

st = next(r for r in rows if r["table"] == "lo_null" and r["item"] == "STRATEGY")
add("strategy", item="observed_factor", value=st["value"],
    note="being the Lo-corrected Sharpe divided by the naive Sharpe over the holdout")
add("strategy", item="null_mean_at_holdout_length", value=st["null_mean"],
    note="against the session 20 figure at n equal to 2472 of 1.1129")
add("strategy", item="null_p95_at_holdout_length", value=st["null_p95"],
    note="against the session 20 figure at n equal to 2472 of 1.4783")
add("strategy", item="inside_own_null", value=st["inside_own_null"],
    note="the verdict on whether the holdout Lo factor is distinguishable from what a "
         "permutation of the same returns produces at this sample length")
z = (float(st["value"]) - float(st["null_mean"])) / float(st["null_sd"])
add("strategy", item="standard_deviations_above_the_null_mean", value=repr(z))

# ---- the q sweep over the holdout ladder -------------------------------------------
for q in QS:
    vals = {}
    for ln, x in series.items():
        v, a, s_ = lo_at(x, q)
        vals[ln] = v
        add("q_sweep", item=ln, q=q, value=repr(float(v)), acf_sum=repr(float(a)))
    order = sorted(vals, key=lambda k: -vals[k])
    for rk, ln in enumerate(order, 1):
        add("q_rank", item=ln, q=q, value=rk)
    add("q_strategy", item="rank", q=q, value=order.index("STRATEGY") + 1,
        note=f"of {len(order)}")
sr = [next(r["value"] for r in rows if r["table"] == "q_strategy" and r["q"] == q)
      for q in QS]
add("summary", item="strategy_rank_range_across_q",
    value=f"{min(sr)} to {max(sr)}",
    note="q values " + " ".join(f"q{q}={r}" for q, r in zip(QS, sr)) +
         ", against a primary-window range of 6 to 7 at 9.37")
chg = 0
for ln in series:
    rr = {next(r["value"] for r in rows if r["table"] == "q_rank"
               and r["item"] == ln and r["q"] == q) for q in QS}
    if len(rr) > 1:
        chg += 1
add("summary", item="rows_changing_rank_across_q", value=chg,
    note=f"of {len(series)}, against 9 of 12 at primary length")

fn = ["table", "item", "q", "value", "naive", "lo", "acf_sum", "null_mean", "null_sd",
      "null_p05", "null_p95", "inside_own_null", "acf_null_sd",
      "distance_to_negative_variance", "distance_to_negative_variance_sd", "note"]
with open(OUT / "lo-holdout-null.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote lo-holdout-null.csv, {len(rows)} rows")
print(f"  rows inside their own null: {inside_ct} of {len(series)}")
print(f"  strategy rank across q: {sr}")
