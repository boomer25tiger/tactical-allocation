"""Session 19 step 3: RE-VERIFY moment additivity across disjoint blocks.

Session 18 step 2 measured this at 3.3e-16 and its output file was then
evicted and recovered. Every CSCV figure rests on the additivity, so this
recomputes rather than trusting the recovered file. Tolerances and seed are
the values session 18 fixed, restated here before any comparison runs.

TOLERANCES, FIXED HERE BEFORE ANY COMPARISON RUNS.

  TOL_ADDITIVITY = 1e-10 absolute, applied to the comparison of a
  statistic reconstructed from the 48 stored block moments against the
  same statistic in the per-specification metric set. Both sides carry a
  float64 lineage and differ only in reduction order, so anything above
  this is a real defect rather than rounding.

  TOL_PANEL = 1e-5 absolute, applied to the comparison against a direct
  computation on the subsample's retained daily series. The panel is
  stored float32, so that side carries roughly 1e-7 relative quantisation
  on each of 2472 values, and the looser bound is the panel's precision
  rather than a weakening of the additivity test.

  STEP2_SEED = 20260820 for the twenty-specification draw.

WHAT IS AND IS NOT RECONSTRUCTIBLE. The shards store, per block, the sum
and the sum of squares of EXCESS returns. Those give the arithmetic mean,
the variance, and the naive Sharpe of any union of blocks exactly. The
GEOMETRIC annualised return is a product rather than a sum and is not
additive across blocks, so it is not reconstructible from these moments
and is checked against the metric set from the retained series instead.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s13_backtest as bt        # noqa: E402
import scripts.s14_common as C           # noqa: E402
import scripts.s17_common as S           # noqa: E402
import scripts.s17_grid_worker as W      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
S18 = ROOT / "outputs" / "session-18"
OUT = ROOT / "outputs" / "session-19"
OUT.mkdir(parents=True, exist_ok=True)

TOL_ADDITIVITY = 1e-10
TOL_PANEL = 1e-5
STEP2_SEED = 20260820
NSESS, NSHARD, NBLK = 2472, 8, 48
TOTAL = S.grid_size()
BOUNDS = [(k * TOTAL // NSHARD, (k + 1) * TOTAL // NSHARD) for k in range(NSHARD)]
rows = []

blk = np.load(G / "block-sizes.npy")
assert blk.sum() == NSESS


def moments_of(spec_id: int) -> np.ndarray:
    for k, (lo, hi) in enumerate(BOUNDS):
        if lo <= spec_id < hi:
            mm = np.memmap(G / f"moments-{k:02d}.f64", dtype=np.float64,
                           mode="r").reshape(-1, 2 * NBLK)
            return np.array(mm[spec_id - lo])
    raise KeyError(spec_id)


def metric_of(spec_id: int, name: str) -> float:
    for k, (lo, hi) in enumerate(BOUNDS):
        if lo <= spec_id < hi:
            mm = np.memmap(G / f"metrics-{k:02d}.f64", dtype=np.float64,
                           mode="r").reshape(-1, W.N_MET)
            r = np.array(mm[spec_id - lo])
            assert int(r[0]) == spec_id
            return float(r[1 + len(S.AXES) + W.METRIC_ORDER.index(name)])
    raise KeyError(spec_id)


def from_moments(m: np.ndarray, use: np.ndarray | None = None):
    """Arithmetic mean, variance and naive Sharpe over a union of blocks."""
    sel = np.ones(NBLK, dtype=bool) if use is None else use
    s = float(m[0::2][sel].sum())
    q = float(m[1::2][sel].sum())
    n = int(blk[sel].sum())
    mean = s / n
    var = (q - s * s / n) / (n - 1)
    sd = math.sqrt(var)
    return mean * 252.0, sd * math.sqrt(252.0), (mean / sd) * math.sqrt(252.0), n


ids = np.load(S18 / "subsample-ids.npy")
ret = np.load(S18 / "subsample-returns.npy")
pos = {int(v): i for i, v in enumerate(ids)}

C.PRIMARY_START = pd.Timestamp("2011-10-04")
env = C.build_env(verbose=False)
cal = env["cal"]
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))
pidx = cal[i0:]
rf = bt.rf_per_session(pidx).fillna(0.0).to_numpy()
assert len(rf) == NSESS

canon = S.index_of(S.canonical_values())
rng = np.random.default_rng(STEP2_SEED)
pick = [canon] + sorted(rng.choice(np.setdiff1d(ids, [canon]), size=20,
                                   replace=False).tolist())

print(f"tolerances fixed before running: additivity {TOL_ADDITIVITY:g}, "
      f"panel {TOL_PANEL:g}, seed {STEP2_SEED}")
print(f"checking the canonical then {len(pick)-1} specifications drawn from the subsample\n")

worst_add, worst_pan = 0.0, 0.0
for j, sid in enumerate(pick):
    m = moments_of(sid)
    am, av, ash, n = from_moments(m)
    # metric-set side, float64 lineage
    m_sh = metric_of(sid, "sharpe_naive")
    m_am = metric_of(sid, "arith_mean_excess_ann")
    d_sh, d_am = abs(ash - m_sh), abs(am - m_am)
    # retained-series side, float32 lineage
    ex = ret[pos[sid]].astype(np.float64) - rf
    p_am = ex.mean() * 252.0
    p_av = ex.std(ddof=1) * math.sqrt(252.0)
    p_sh = ex.mean() / ex.std(ddof=1) * math.sqrt(252.0)
    e_sh, e_am, e_av = abs(ash - p_sh), abs(am - p_am), abs(av - p_av)
    # geometric annualised return, not reconstructible from the moments
    g = float(np.prod(1.0 + ret[pos[sid]].astype(np.float64)) ** (252.0 / n) - 1.0)
    m_g = metric_of(sid, "ann_return")
    worst_add = max(worst_add, d_sh, d_am)
    worst_pan = max(worst_pan, e_sh, e_am, e_av)
    tag = "canonical" if sid == canon else f"draw {j}"
    rows.append({"table": "additivity", "which": tag, "spec_id": sid, "n_sessions": n,
                 "sharpe_naive_from_moments": ash, "sharpe_naive_metric_set": m_sh,
                 "abs_gap_metric_set": d_sh,
                 "arith_mean_excess_ann_from_moments": am,
                 "arith_mean_excess_ann_metric_set": m_am, "abs_gap_mean": d_am,
                 "ann_vol_excess_from_moments": av,
                 "sharpe_naive_from_retained_series": p_sh,
                 "abs_gap_retained_series": e_sh,
                 "ann_return_geometric_retained": g,
                 "ann_return_geometric_metric_set": m_g,
                 "abs_gap_geometric": abs(g - m_g),
                 "within_additivity_tol": int(max(d_sh, d_am) <= TOL_ADDITIVITY),
                 "within_panel_tol": int(max(e_sh, e_am, e_av) <= TOL_PANEL)})
    if sid == canon:
        print(f"  canonical spec {sid:,}, blocks unioned {NBLK}, sessions {n}")
        print(f"    naive Sharpe from moments   {ash:.12f}")
        print(f"    naive Sharpe in metric set  {m_sh:.12f}   gap {d_sh:.2e}")
        print(f"    naive Sharpe from series    {p_sh:.12f}   gap {e_sh:.2e}")
        print(f"    ann arith mean excess       {am:.12f} vs {m_am:.12f}  gap {d_am:.2e}")
        print(f"    ann vol of excess           {av:.12f} vs {p_av:.12f}  gap {e_av:.2e}")
        print(f"    geometric ann return        {g:.12f} vs metric set {m_g:.12f}"
              f"  gap {abs(g-m_g):.2e}  (NOT reconstructible from moments)")

# partition control: disjoint halves must sum to the whole
half = np.zeros(NBLK, dtype=bool); half[:NBLK // 2] = True
m = moments_of(canon)
s_all = float(m[0::2].sum()); s_a = float(m[0::2][half].sum()); s_b = float(m[0::2][~half].sum())
q_all = float(m[1::2].sum()); q_a = float(m[1::2][half].sum()); q_b = float(m[1::2][~half].sum())
d_s, d_q = abs(s_all - (s_a + s_b)), abs(q_all - (q_a + q_b))
print(f"\n  disjoint-partition control on the canonical, first 24 blocks against last 24")
print(f"    sum of returns    whole {s_all:.15e}  parts {s_a + s_b:.15e}  gap {d_s:.2e}")
print(f"    sum of squares    whole {q_all:.15e}  parts {q_a + q_b:.15e}  gap {d_q:.2e}")
rows.append({"table": "partition_control", "which": "canonical", "spec_id": canon,
             "abs_gap_sum": d_s, "abs_gap_sumsq": d_q,
             "within_additivity_tol": int(max(d_s, d_q) <= TOL_ADDITIVITY)})

rows.append({"table": "tolerance", "which": "TOL_ADDITIVITY", "abs_gap_metric_set": TOL_ADDITIVITY,
             "note": "fixed before running; metric-set comparison, float64 both sides"})
rows.append({"table": "tolerance", "which": "TOL_PANEL", "abs_gap_retained_series": TOL_PANEL,
             "note": "fixed before running; retained-series comparison, panel is float32"})
rows.append({"table": "tolerance", "which": "STEP2_SEED", "spec_id": STEP2_SEED,
             "note": "fixed before the twenty-specification draw"})
rows.append({"table": "reconstructibility", "which": "geometric_ann_return",
             "note": "a product rather than a sum, not additive across disjoint blocks, "
                     "not reconstructible from the stored moments; checked against the "
                     "metric set from the retained series instead"})

print(f"\n  maximum absolute deviation, moments against metric set, all {len(pick)}: "
      f"{worst_add:.3e}   tolerance {TOL_ADDITIVITY:g}")
print(f"  maximum absolute deviation, moments against retained series, all {len(pick)}: "
      f"{worst_pan:.3e}   tolerance {TOL_PANEL:g}")
# Session 20 B2 repair. The accumulators initialise at the passing value, so
# zero comparisons passed. A minimum comparison count is asserted.
COMPARISON_FLOOR = 21
ok = (len(pick) >= COMPARISON_FLOOR and worst_add <= TOL_ADDITIVITY
      and worst_pan <= TOL_PANEL and max(d_s, d_q) <= TOL_ADDITIVITY)
rows.append({"table": "session18_comparison", "which": "worst_additivity_session18",
             "abs_gap_metric_set": 3.3e-16,
             "note": "session 18 step 2 reported this maximum deviation; the row above carries this session recomputation"})
rows.append({"table": "verdict", "which": "step3", "abs_gap_metric_set": worst_add,
             "abs_gap_retained_series": worst_pan, "note": "PASS" if ok else "FAIL"})
print(f"\nSTEP 3: {'PASS' if ok else 'FAIL'}")

cols = ["table", "which", "spec_id", "n_sessions", "sharpe_naive_from_moments",
        "sharpe_naive_metric_set", "abs_gap_metric_set",
        "arith_mean_excess_ann_from_moments", "arith_mean_excess_ann_metric_set",
        "abs_gap_mean", "ann_vol_excess_from_moments",
        "sharpe_naive_from_retained_series", "abs_gap_retained_series",
        "ann_return_geometric_retained", "ann_return_geometric_metric_set",
        "abs_gap_geometric", "abs_gap_sum", "abs_gap_sumsq",
        "within_additivity_tol", "within_panel_tol", "note"]
with open(OUT / "additivity-check.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {OUT/'additivity-check.csv'} with {len(rows)} rows")
sys.exit(0 if ok else 1)
