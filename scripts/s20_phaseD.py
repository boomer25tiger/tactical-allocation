"""Session 20 phase D. The metric audit, on the corrected boundary.

SEEDS AND TOLERANCES, FIXED BEFORE THE COMPARISONS THEY GOVERN.
  LO_SEED   = 20260820, fixed before drawing, 300 permutations per ladder row.
  The permutation null preserves each row's marginal distribution and destroys
  serial dependence entirely, so the observed Lo factor is compared against a
  null in which there is no autocorrelation at all.

Q values swept are 1, 5, 21, 63, 126 and 252, with q equal to 1 being the naive
Sharpe limit since the Lo scale collapses to sqrt(q) with no lag terms.
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
OUT = ROOT / "outputs" / "session-20"
LO_SEED, NPERM = 20260820, 300
QS = (1, 5, 21, 63, 126, 252)
t0 = time.time()
rows = []


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def lo_at(x, q):
    """Lo (2002) annualised Sharpe at lag horizon q, and its internals."""
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


env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))
acc_s = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                       slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
rf_all = bt.rf_per_session(acc_s["daily"].index)

series = {}
r = acc_s["daily"]["ret"].loc[acc_s["daily"].index >= C.PRIMARY_START].dropna()
series["STRATEGY"] = (r - rf_all.reindex(r.index).fillna(0.0)).dropna().to_numpy()
for ln in ["buy_hold_QQQ", "buy_hold_TQQQ", "vol_targeted_QQQ_matched",
           "naive_fast_1d_momentum", "matched_exposure_levered_QQQ_1.70",
           "long_legs_only", "equal_weight_universe", "sleeve_T10_standalone",
           "sleeve_T11_standalone", "sleeve_S2_standalone", "sleeve_S3_standalone"]:
    a = bt.run_account(sig["sig"], o2o, LINES[ln][0](o2o, sig["rows"], i0), C.ANCHOR,
                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                       slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
    rr = a["daily"]["ret"].loc[a["daily"].index >= C.PRIMARY_START].dropna()
    series[ln] = (rr - rf_all.reindex(rr.index).fillna(0.0)).dropna().to_numpy()
print(f"built {len(series)} excess-return series in {time.time()-t0:.1f}s")

# ---- D1, the q sweep ------------------------------------------------------
print("\n== D1, Lo Sharpe across q ==")
tab = {}
for q in QS:
    vals = {}
    for ln, x in series.items():
        v, acf, scale = lo_at(x, q)
        vals[ln] = v
        rows.append({"table": "q_sweep", "line": ln, "q": q, "value": v,
                     "acf_sum": acf, "scale_sq": scale})
    order = sorted(vals, key=lambda k: -vals[k])
    for rk, ln in enumerate(order, 1):
        rows.append({"table": "q_rank", "line": ln, "q": q, "value": rk})
    tab[q] = (vals, {ln: rk for rk, ln in enumerate(order, 1)})
    print(f"  q={q:<4} strategy {vals['STRATEGY']:.4f} rank {tab[q][1]['STRATEGY']}")
sr = [tab[q][1]["STRATEGY"] for q in QS]
rows.append({"table": "q_summary", "line": "STRATEGY", "value": len(set(sr)),
             "note": "distinct strategy ranks across the sweep, "
                     + " ".join(f"q{q}={tab[q][1]['STRATEGY']}" for q in QS)})
rows.append({"table": "q_summary", "line": "STRATEGY_rank_range",
             "note": f"{min(sr)} to {max(sr)}"})
chg = [QS[i] for i in range(1, len(QS)) if sr[i] != sr[i - 1]]
rows.append({"table": "q_summary", "line": "rank_changes_at_q",
             "note": " ".join(map(str, chg)) if chg else "none"})
nchg = sum(1 for ln in series if len({tab[q][1][ln] for q in QS}) > 1)
rows.append({"table": "q_summary", "line": "rows_changing_rank_across_q", "value": nchg})
print(f"  strategy rank across the sweep {sr}, rows changing rank {nchg} of {len(series)}")

# ---- D1, the permutation null for every row -------------------------------
print("\n== D1, permutation null per row, 300 draws ==")
NEG_THRESHOLD = -252 / 2.0
for ln, x in series.items():
    obs_lo, obs_acf, _ = lo_at(x, 252)
    naive = x.mean() / x.std(ddof=1) * math.sqrt(252.0)
    obs_f = obs_lo / naive
    rng = np.random.default_rng(LO_SEED)
    facs, acfs = [], []
    for _ in range(NPERM):
        p = rng.permutation(x)
        v, a, _s = lo_at(p, 252)
        nv = p.mean() / p.std(ddof=1) * math.sqrt(252.0)
        facs.append(v / nv); acfs.append(a)
    facs, acfs = np.array(facs), np.array(acfs)
    inside = bool(np.percentile(facs, 5) <= obs_f <= np.percentile(facs, 95))
    dist_sd = (obs_acf - NEG_THRESHOLD) / acfs.std(ddof=1)
    rows.append({"table": "lo_null", "line": ln, "value": obs_f,
                 "acf_sum": obs_acf, "naive": naive, "lo": obs_lo,
                 "null_mean": float(facs.mean()), "null_sd": float(facs.std(ddof=1)),
                 "null_p05": float(np.percentile(facs, 5)),
                 "null_p95": float(np.percentile(facs, 95)),
                 "inside_own_null": int(inside),
                 "acf_null_sd": float(acfs.std(ddof=1)),
                 "distance_to_negative_variance_sd": float(dist_sd),
                 "note": f"observed weighted sum {obs_acf:.3f} against the threshold "
                         f"{NEG_THRESHOLD:.1f} at which q + 2*acf turns negative"})
    print(f"  {ln:<34} factor {obs_f:.4f} null [{np.percentile(facs,5):.4f}, "
          f"{np.percentile(facs,95):.4f}] inside {inside}  dist {dist_sd:+.2f} sd")
rows.append({"table": "lo_null_meta", "line": "seed", "value": LO_SEED,
             "note": "fixed before drawing"})
rows.append({"table": "lo_null_meta", "line": "draws", "value": NPERM})
rows.append({"table": "lo_null_meta", "line": "negative_variance_threshold",
             "value": NEG_THRESHOLD,
             "note": "the Lo scale q + 2*acf_sum turns non-positive at this weighted "
                     "autocorrelation sum, at which the estimator returns nan"})
n_in = sum(1 for r in rows if r["table"] == "lo_null" and r["inside_own_null"] == 1)
rows.append({"table": "lo_null_meta", "line": "rows_inside_own_null", "value": n_in,
             "note": f"of {len(series)} ladder rows"})
print(f"  rows whose observed factor falls inside their own no-autocorrelation null: "
      f"{n_in} of {len(series)}")

with open(OUT / "lo-q-sweep.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table", "line", "q", "value", "acf_sum",
                                        "scale_sq", "naive", "lo", "null_mean",
                                        "null_sd", "null_p05", "null_p95",
                                        "inside_own_null", "acf_null_sd",
                                        "distance_to_negative_variance_sd", "note"],
                       extrasaction="ignore")
    wr.writeheader(); wr.writerows(rows)
print(f"\nwrote {OUT/'lo-q-sweep.csv'} with {len(rows)} rows")
print(f"phase D1 peak {rss():.3f} GB, {time.time()-t0:.1f}s")
