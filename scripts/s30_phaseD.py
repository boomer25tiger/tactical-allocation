"""Session 30 phase D. The holdout nulls.

The timing-shuffle and turnover-matched constructions are READ FROM
scripts/s14_nulls.py rather than rewritten. The module's definitions are executed
up to its own driver loop, so run_strategy, ret_matrix, episodes_and_cost,
draw_returns and lo_sharpe_fast are the pre-registered ones and the RNG carries
the session 22 seed convention of 20260818 unchanged. Only the window the driver
walks is the holdout instead of the primary window.
"""
from __future__ import annotations

import csv
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"
os.environ["S22_NULLS_ONLY"] = "1"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s22_vm as VM                            # noqa: E402
import subprocess                                      # noqa: E402

OUT = ROOT / "outputs" / "session-30"
BOUNDARY = bt.HOLDOUT_BOUNDARY
N_DRAWS, SEED = 10000, 20260818
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
    add("machine_at_phase_D", item=k, value=v)

# ---- execute the session 14 definitions, stopping before its own driver ------------
SRC = (ROOT / "scripts" / "s14_nulls.py").read_text()
CUT = SRC.index('for conv in (("o2o",) if _NULLS_ONLY else ("o2o", "c2c")):')
NS = {"__name__": "s14_nulls_defs", "__file__": str(ROOT / "scripts" / "s14_nulls.py")}
print("executing the session 14 null definitions")
exec(compile(SRC[:CUT], "scripts/s14_nulls.py", "exec"), NS)
run_strategy = NS["run_strategy"]; ret_matrix = NS["ret_matrix"]
episodes_and_cost = NS["episodes_and_cost"]; draw_returns = NS["draw_returns"]
lo_sharpe_fast = NS["lo_sharpe_fast"]
add("construction", item="source", value="scripts/s14_nulls.py",
    note="the module's definitions are executed up to its own driver loop, so the "
         "constructions are the pre-registered ones rather than rewritten")
add("construction", item="seed", value=SEED,
    note="the session 22 seed convention, unchanged. scripts/s14_nulls.py sets "
         "RNG = np.random.default_rng(20260818) at module level")
add("construction", item="n_draws", value=N_DRAWS,
    note="matching the 10,000 replications session 22 raised the primary-window nulls to")

conv = "o2o"
acc = run_strategy(conv)
R = ret_matrix(conv)
comps, lens, cost_frac = episodes_and_cost(acc, conv)
daily = acc["daily"]
rate = float(daily["transition"].mean())
cal = NS["cal"]
off = len(cal) - len(daily)
add("null_setup", item="n_episodes", value=len(comps))
add("null_setup", item="mean_episode_len", value=q(lens.mean()))
add("null_setup", item="median_episode_len", value=q(np.median(lens)))
add("null_setup", item="measured_transition_rate_per_session", value=q(rate))
add("null_setup", item="mean_cost_frac_per_transition", value=q(cost_frac))

sl = daily["ret"].loc[daily.index >= BOUNDARY].dropna()
dates = sl.index
n = len(dates)
i0 = list(daily.index).index(dates[0]) + off
Rw = R[i0:i0 + n]
rf = bt.rf_per_session(dates).fillna(0.0).to_numpy()[1:]
nn = n - 1
add("window", item="holdout_sessions", value=n,
    note=f"{dates.min().date()} to {dates.max().date()}")


def stats(r):
    s = np.asarray(r)[1:]
    ann = float(np.prod(1 + s) ** (252 / nn) - 1)
    ex = s - rf
    naive = float(ex.mean() / ex.std(ddof=1) * math.sqrt(252.0))
    return ann, naive, lo_sharpe_fast(ex)


obs_ann, obs_naive, obs_lo = stats(sl.to_numpy())
# equality control against the reference estimator before any draw is read
rf_ctl = bt.rf_per_session(dates).fillna(0.0)
ctl_fast = lo_sharpe_fast((sl - rf_ctl).dropna().to_numpy())
ctl_ref = bt.lo_sharpe((sl - rf_ctl).dropna())
add("lo_sharpe_control", item="fast", value=q(ctl_fast), target=q(ctl_ref),
    note=f"absolute gap {float(abs(ctl_fast-ctl_ref))!r}, checked before any null draw "
         f"is read")
assert abs(ctl_fast - ctl_ref) < 1e-9, "fast Lo Sharpe diverges from bt.lo_sharpe"
for k, v in (("ann_return", obs_ann), ("sharpe_naive", obs_naive),
             ("sharpe_lo", obs_lo)):
    add("observed", item=k, value=q(v))
add("observed", item="statistic_drops_the_first_session", value=1,
    note="scripts/s14_nulls.py make_stats evaluates on r[1:], so the statistic runs on "
         f"{nn} sessions rather than {n}. That is the pre-registered construction and it "
         "is why the observed naive Sharpe here reads "
         f"{float(obs_naive)!r} against the 1.637799226672021 at "
         "outputs/session-27/holdout-ladder.csv, and the annualised return "
         f"{float(obs_ann)!r} against 0.8287111594113898. The null and the observed value are "
         "computed the same way, so the exceedance counts are internally consistent")
print(f"observed ann {obs_ann:.6f} naive {obs_naive:.6f} lo {obs_lo:.6f} over {n}")

PRIMARY_COUNTS = {}
P22 = ROOT / "outputs" / "session-22" / "rebuilt" / "nulls.csv"
for r in csv.DictReader(open(P22)):
    if r["table"] == "null_distribution" and r["null"]:
        PRIMARY_COUNTS[(r["null"], "ann_return")] = (
            float(r["p_value_ann_one_sided"]) * float(r["n_draws"]),
            float(r["n_draws"]), r["null_ann_mean"], r["strategy_percentile_ann"])
        PRIMARY_COUNTS[(r["null"], "sharpe_lo")] = (
            float(r["p_value_sharpe_one_sided"]) * float(r["n_draws"]),
            float(r["n_draws"]), r["null_sharpe_mean"], r["strategy_percentile_sharpe"])

t0 = time.time()
for mode, label in (("shuffle", "timing_shuffle_block_bootstrap"),
                    ("switch", "turnover_matched_switching")):
    anns, navs, los = [], [], []
    for i in range(N_DRAWS):
        p = draw_returns(comps, lens, Rw, n, cost_frac, mode, rate)
        a, nv, lo = stats(p)
        anns.append(a); navs.append(nv); los.append(lo)
    A = {"ann_return": (np.array(anns), obs_ann),
         "sharpe_naive": (np.array(navs), obs_naive),
         "sharpe_lo": (np.array(los), obs_lo)}
    for metric, (arr, obs) in A.items():
        ex = int((arr >= obs).sum())
        pc = PRIMARY_COUNTS.get((label, metric))
        add("null", item=label, metric=metric, window="holdout",
            exceedances=ex, n_draws=N_DRAWS,
            p_value=q(ex / N_DRAWS),
            percentile=q(float((arr < obs).mean() * 100)),
            observed=q(obs),
            null_mean=q(float(np.nanmean(arr))),
            null_sd=q(float(np.nanstd(arr, ddof=1))),
            null_p95=q(float(np.nanpercentile(arr, 95))),
            null_max=q(float(np.nanmax(arr))),
            primary_exceedances=(f"{pc[0]:.0f} of {pc[1]:.0f}" if pc else
                                 "not reported for this metric at session 22"),
            primary_null_mean=(pc[2] if pc else ""),
            note="exceedance count is the primary form, since one in 1,000 and ten in "
                 "10,000 are the same estimate at different resolution")
        print(f"  {label:36s} {metric:14s} exceedances {ex} of {N_DRAWS}")
    print(f"  [{time.time()-t0:.1f}s]")

_s2 = VM.sample()
add("machine_at_phase_D_end", item="compressor_gib", value=_s2["compressor_gib"])
add("machine_at_phase_D_end", item="swap_used_mb", value=_s2["swap_used_mb"])
add("machine_at_phase_D_end", item="seconds", value=q(time.time() - t0))

fn = ["table", "item", "metric", "window", "value", "target", "exceedances", "n_draws",
      "p_value", "percentile", "observed", "null_mean", "null_sd", "null_p95",
      "null_max", "primary_exceedances", "primary_null_mean", "note"]
with open(OUT / "holdout-nulls.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote holdout-nulls.csv, {len(rows)} rows")
