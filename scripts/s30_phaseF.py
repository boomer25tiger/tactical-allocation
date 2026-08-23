"""Session 30 phase F. Interval estimates by the stationary block bootstrap.

CONTENTION CHECK before launching, per the precedent at 9.47. If the one-minute
load average exceeds twice the core count the phase halts and reports rather than
starting a resampling pass.

BLOCK LENGTH RULE, stated before running. Mean block length is 21 sessions, being
the Newey-West lag 8.11 already fixes for this study's serial dependence. Tying
the bootstrap's dependence horizon to the one the register already carries avoids
selecting a second horizon after seeing a result. Block lengths are geometric with
that mean, which is the stationary bootstrap of Politis and Romano, so the
resampled series is stationary and the choice of starting point carries no edge
effect. Holdout excess kurtosis at 5.223157724383093 is why an iid resample would
understate the standard error and why blocks are used at all.

REPLICATIONS 10,000. SEED 20260823, fixed before drawing.
WALL LIMIT 1800 seconds, stated before launching. Termination on that limit alone.
MEMORY CEILING 3.0 GB peak resident, stated before launching.
"""
from __future__ import annotations

import csv
import math
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s22_vm as VM                            # noqa: E402

OUT = ROOT / "outputs" / "session-30"
S27 = ROOT / "outputs" / "session-27"
BOUNDARY = bt.HOLDOUT_BOUNDARY
NREP, SEED, MEAN_BLOCK = 10000, 20260823, 21
WALL_LIMIT, MEM_CEILING_GB = 1800.0, 3.0
ANN = math.sqrt(252.0)
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


cores = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True,
                           text=True).stdout)
l = [float(x) for x in subprocess.run(["sysctl", "-n", "vm.loadavg"],
     capture_output=True, text=True).stdout.strip().strip("{} ").split()]
s0 = VM.sample()
for k, v in (("load_1min", l[0]), ("load_5min", l[1]), ("cores", cores),
             ("compressor_gib", s0["compressor_gib"]),
             ("swap_used_mb", s0["swap_used_mb"]),
             ("swap_free_mb", s0["swap_free_mb"])):
    add("machine_at_phase_F", item=k, value=v)
add("preregistration", item="wall_limit_seconds", value=WALL_LIMIT,
    note="stated before launching. Termination on this limit alone")
add("preregistration", item="memory_ceiling_gb", value=MEM_CEILING_GB,
    note="stated before launching, read as peak resident set size")
add("preregistration", item="replications", value=NREP)
add("preregistration", item="seed", value=SEED, note="fixed before drawing")
add("preregistration", item="mean_block_length", value=MEAN_BLOCK,
    note="the Newey-West lag 8.11 already fixes for this study's serial dependence, so "
         "the bootstrap carries the same dependence horizon the register already "
         "records rather than a second one chosen here. Block lengths are geometric "
         "with that mean, being the stationary bootstrap of Politis and Romano")
add("contention_check", item="threshold", value=cores * 2,
    note="twice the core count, the precedent at 9.47")
add("contention_check", item="load_1min", value=l[0])
halt = l[0] > cores * 2
add("contention_check", item="verdict", value="HALT" if halt else "PROCEED")
if halt:
    with open(OUT / "bootstrap-intervals.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table", "item", "window", "value", "note"],
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"phase F HALTED, load {l[0]} against {cores*2}")
    sys.exit(0)
print(f"phase F proceeding, load {l[0]} against {cores*2}")

# ---- the series -------------------------------------------------------------------
hl = pd.read_parquet(S27 / "_holdout_line_returns.parquet")
cl = pd.read_parquet(S27 / "_combined_line_returns.parquet")
LINES = ["STRATEGY", "buy_hold_QQQ", "matched_exposure_levered_QQQ_1.70"]
H = hl[LINES].dropna()
P = cl[LINES].loc[cl.index < BOUNDARY].dropna()
rfh = bt.rf_per_session(H.index).reindex(H.index).fillna(0.0)
rfp = bt.rf_per_session(P.index).reindex(P.index).fillna(0.0)
EH = H.sub(rfh, axis=0).to_numpy()
EP = P.sub(rfp, axis=0).to_numpy()

# the factor block, open to open, matching phase E
MF = list(csv.DictReader(open(OUT / "multi-factor.csv")))
FAC = [r["item"] for r in MF if r["table"] == "factor" and r["value"] == "1"]
INSTR = {r["item"]: r["instrument"] for r in MF if r["table"] == "factor"}
import scripts.s14_common as C                          # noqa: E402
env = C.build_env(verbose=False)
o2o = env["o2o"]
FH = []
for f in FAC:
    tk = INSTR[f]
    if tk in o2o.frames:
        v = o2o[tk].ret_total
    else:
        fr = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{tk}.parquet")
        fr.index = pd.DatetimeIndex(fr.index).tz_localize(None).normalize()
        ratio = (fr["Adj Close"] / fr["Close"]) if "Adj Close" in fr.columns else 1.0
        ao = fr["Open"].astype(float) * ratio
        v = ao / ao.shift(1) - 1.0
    FH.append((v.reindex(H.index).fillna(0.0) - rfh).to_numpy())
FH = np.column_stack(FH)
add("setup", item="holdout_sessions", value=len(H))
add("setup", item="primary_sessions", value=len(P))
add("setup", item="factors", value=",".join(FAC))
add("setup", item="returns_are_excess_of_the_risk_free_rate", value=1,
    note="every statistic here is computed on the excess return series, so the "
         "annualised return reported below is an annualised EXCESS return. That is why "
         "the holdout point estimate reads lower than the 0.8287111594113898 at "
         "outputs/session-27/holdout-ladder.csv and the primary one lower than "
         "0.5218447451814521, both of which are total annualised returns. The interval "
         "and the point estimate are computed the same way, so the interval is "
         "internally consistent")


def lo_sharpe(x, qq=252):
    mu, sd = x.mean(), x.std(ddof=1)
    if sd == 0:
        return float("nan")
    xc = x - mu
    den = float(np.dot(xc, xc))
    acf = sum((qq - k) * float(np.dot(xc[:-k], xc[k:])) / den for k in range(1, qq))
    sc = qq + 2.0 * acf
    return float("nan") if sc <= 0 else float(
        (mu / sd) * qq / math.sqrt(sc) * math.sqrt(252.0 / qq))


def alpha_of(y, X):
    Xd = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    return float(b[0] * 252.0)


def blocks(rng, n, mean_block):
    """Stationary bootstrap index vector, geometric block lengths."""
    p = 1.0 / mean_block
    idx = np.empty(n, dtype=np.int64)
    i = 0
    while i < n:
        start = rng.integers(n)
        L = min(int(rng.geometric(p)), n - i)
        idx[i:i + L] = (start + np.arange(L)) % n
        i += L
    return idx


def point_stats(E, F=None, Fsingle=None):
    st = E[:, 0]
    out = {"naive_sharpe": float(st.mean() / st.std(ddof=1) * ANN),
           "lo_sharpe": lo_sharpe(st),
           "ann_return": float(np.prod(1 + E[:, 0]) ** (252 / len(E)) - 1),
           "gap_vs_buy_hold_QQQ": float(st.mean() / st.std(ddof=1) * ANN
                                        - E[:, 1].mean() / E[:, 1].std(ddof=1) * ANN),
           "gap_vs_matched_exposure": float(st.mean() / st.std(ddof=1) * ANN
                                            - E[:, 2].mean() / E[:, 2].std(ddof=1) * ANN)}
    if Fsingle is not None:
        out["single_factor_alpha"] = alpha_of(st, Fsingle.reshape(-1, 1))
    if F is not None:
        out["multi_factor_alpha"] = alpha_of(st, F)
    return out


rng = np.random.default_rng(SEED)
t0 = time.time()
res = {}
for wname, E, F, Fs in (("holdout", EH, FH, EH[:, 1]),
                        ("primary", EP, None, EP[:, 1])):
    pt = point_stats(E, F, Fs)
    draws = {k: [] for k in pt}
    n = len(E)
    for r in range(NREP):
        if time.time() - t0 > WALL_LIMIT:
            add("result", item="terminated_on_the_wall_limit", window=wname, value=r,
                note=f"of {NREP} replications")
            break
        ix = blocks(rng, n, MEAN_BLOCK)
        Eb = E[ix]
        Fb = F[ix] if F is not None else None
        d = point_stats(Eb, Fb, Eb[:, 1])
        for k, v in d.items():
            draws[k].append(v)
    for k, v in pt.items():
        arr = np.array([x for x in draws[k] if x == x])
        st = E[:, 0]
        # the iid approximate standard error for the two Sharpe forms
        se = ""
        if k == "naive_sharpe":
            se = q(math.sqrt((1 + 0.5 * v * v) / n) * math.sqrt(252.0 / 252.0))
        elif k == "ann_return":
            se = q(float(st.std(ddof=1) * ANN / math.sqrt(n)))
        add("interval", item=k, window=wname, value=q(v),
            p05=q(float(np.percentile(arr, 5))),
            p50=q(float(np.percentile(arr, 50))),
            p95=q(float(np.percentile(arr, 95))),
            bootstrap_sd=q(float(arr.std(ddof=1))),
            iid_standard_error=se, n_draws=len(arr),
            note="the iid approximate standard error uses the Lo 1994 form for the "
                 "naive Sharpe and the ordinary mean standard error for the annualised "
                 "return, and is blank where no closed form applies"
                 if se else "no closed-form iid standard error applies")
        res[(wname, k)] = (v, float(np.percentile(arr, 5)),
                           float(np.percentile(arr, 95)))
    print(f"  {wname} done at {time.time()-t0:.1f}s, peak {rss():.3f} GB")

g = res.get(("holdout", "gap_vs_buy_hold_QQQ"))
add("verdict", item="holdout_gap_vs_buy_hold_QQQ_excludes_zero_at_the_5th_percentile",
    value=int(g[1] > 0) if g else "",
    note=f"the 5th percentile reads {g[1]!r} against a point estimate of {g[0]!r}"
         if g else "")
s1 = VM.sample()
add("machine_at_phase_F_end", item="peak_rss_gb", value=q(rss()),
    note=f"against the {MEM_CEILING_GB} GB ceiling stated before launching")
add("machine_at_phase_F_end", item="compressor_gib", value=s1["compressor_gib"])
add("machine_at_phase_F_end", item="swap_used_mb", value=s1["swap_used_mb"])
add("machine_at_phase_F_end", item="seconds", value=q(time.time() - t0),
    note=f"against the {WALL_LIMIT} second limit stated before launching")

fn = ["table", "item", "window", "value", "p05", "p50", "p95", "bootstrap_sd",
      "iid_standard_error", "n_draws", "note"]
with open(OUT / "bootstrap-intervals.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote bootstrap-intervals.csv, {len(rows)} rows")
