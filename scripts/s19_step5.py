"""Session 19 step 5: PBO within structural strata.

REPLACES the smooth-axis restriction. That restriction holds all six
structural axes at canonical and varies only the three smooth axes, which
spans 3 x 3 x 3 = 27 specifications. A 27-point PBO is not comparable to a
121,500-point figure, so the restriction is replaced rather than run.

The purpose the restriction served was to separate overfitting arising from
parameter search WITHIN one strategy shape from overfitting arising from
search ACROSS shapes. Stratification serves that purpose at usable sample
sizes. Holding one structural axis at one value fixes the strategy shape
that axis controls and leaves the remaining eight axes free, so the PBO
measured inside a stratum is the parameter-search component alone.

PRE-REGISTERED, identical to step 4 so the figures are comparable.
  S = 16. Naive Sharpe. COMBO_CAP 20000 at COMBO_SEED 20260821.
  MEM_CEILING_GB 2.0.
"""
from __future__ import annotations

import csv
import itertools
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
S18 = ROOT / "outputs" / "session-18"
OUT = ROOT / "outputs" / "session-19"
OUT.mkdir(parents=True, exist_ok=True)

S_PRIMARY = 16
MEM_CEILING_GB = 2.0
COMBO_CAP = 20000
COMBO_SEED = 20260821
NBLK, NSHARD = 48, 8
TOTAL = S.grid_size()
ANN = math.sqrt(252.0)
rows = []


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


raw = np.concatenate([
    np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64).reshape(-1, 2 * NBLK)
    for k in range(NSHARD)])
ids = np.concatenate([np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
                      for k in range(NSHARD)])
order = np.argsort(ids)
raw = np.ascontiguousarray(raw[order])
assert np.array_equal(ids[order], np.arange(TOTAL))
MOM = raw.reshape(TOTAL, NBLK, 2)
BLK = np.load(G / "block-sizes.npy").astype(np.float64)
print(f"moment array {MOM.shape} {MOM.dtype} {MOM.nbytes/1e6:.1f} MB")

idx = pd.read_csv(S18 / "spec-index-augmented.csv")
assert len(idx) == TOTAL
CANON = S.index_of(S.canonical_values())
CV = S.canonical_values()

STRUCTURAL = [a for a in S.AXIS_NAMES if idx[f"class_{a}"].iloc[0] == "structural"]
SMOOTH = [a for a in S.AXIS_NAMES if idx[f"class_{a}"].iloc[0] == "smooth"]
print(f"structural axes {STRUCTURAL}")
print(f"smooth axes     {SMOOTH}")

# the replaced restriction, recorded rather than run
smooth_n = 1
for a in SMOOTH:
    smooth_n *= len(S.AXIS_VALUES[S.AXIS_NAMES.index(a)])
rows.append({"table": "replacement", "axis": "smooth_axis_restriction",
             "n_specifications": smooth_n,
             "note": "NOT RUN. All six structural axes held at canonical leaves "
                     f"{' x '.join(str(len(S.AXIS_VALUES[S.AXIS_NAMES.index(a)])) for a in SMOOTH)}"
                     f" = {smooth_n} specifications, which is not comparable to a "
                     "121,500-point PBO. Replaced by the stratification below"})
rows.append({"table": "preregistration", "axis": "S", "n_specifications": S_PRIMARY,
             "note": "identical to step 4 so the stratified and full-grid figures compare"})
rows.append({"table": "preregistration", "axis": "performance_metric",
             "note": "naive Sharpe, not Lo-corrected, because autocovariance is not "
                     "additive across disjoint blocks"})
rows.append({"table": "preregistration", "axis": "combination_seed",
             "n_specifications": COMBO_SEED})


def merge(nblk_target):
    g = NBLK // nblk_target
    Sb = MOM[:, :, 0].reshape(TOTAL, nblk_target, g).sum(axis=2)
    Qb = MOM[:, :, 1].reshape(TOTAL, nblk_target, g).sum(axis=2)
    nb = BLK.reshape(nblk_target, g).sum(axis=1)
    return np.ascontiguousarray(Sb), np.ascontiguousarray(Qb), nb


def combos(nb, rng):
    half = nb // 2
    full = math.comb(nb, half)
    if full <= COMBO_CAP:
        m = np.zeros((full, nb), dtype=np.float64)
        for i, c in enumerate(itertools.combinations(range(nb), half)):
            m[i, list(c)] = 1.0
        return m, full, False
    m = np.zeros((COMBO_CAP, nb), dtype=np.float64)
    seen = set()
    i = 0
    while i < COMBO_CAP:
        c = tuple(sorted(rng.choice(nb, size=half, replace=False).tolist()))
        if c in seen:
            continue
        seen.add(c); m[i, list(c)] = 1.0; i += 1
    return m, full, True


def sharpe(sum_, sq_, n_):
    mean = sum_ / n_
    var = (sq_ - sum_ * sum_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


SB16, QB16, NV16 = merge(S_PRIMARY)
_rng = np.random.default_rng(COMBO_SEED)
M16, FULL16, SAMP16 = combos(S_PRIMARY, _rng)
NCOMB = M16.shape[0]
print(f"S={S_PRIMARY}: {NCOMB:,} combinations"
      f"{' sampled of %d' % FULL16 if SAMP16 else ' full enumeration'}")


def cscv_mask(mask, label):
    Sb, Qb = SB16[mask], QB16[mask]
    npec = Sb.shape[0]
    chunk = min(max(1, int(MEM_CEILING_GB * 1e9 / (npec * 8 * 4))), NCOMB)
    SbT, QbT = Sb.T.copy(), Qb.T.copy()
    is_sel, os_sel, rank_acc = [], [], []
    t = time.time(); peak = 0.0
    for a in range(0, NCOMB, chunk):
        mc = M16[a:a + chunk]
        oc = 1.0 - mc
        # Session 20 B1 repair. The count varies across combinations because
        # merged super-block counts are unequal, so it is taken per
        # combination rather than from the chunk's first row.
        n_is = (mc @ NV16)[:, None]; n_os = (oc @ NV16)[:, None]
        is_sh = sharpe(mc @ SbT, mc @ QbT, n_is)
        os_sh = sharpe(oc @ SbT, oc @ QbT, n_os)
        peak = max(peak, rss_gb())
        best = np.argmax(is_sh, axis=1)
        r = np.arange(len(best))
        is_sel.append(is_sh[r, best])
        sel_os = os_sh[r, best]
        os_sel.append(sel_os)
        rank_acc.append((os_sh < sel_os[:, None]).sum(axis=1) + 1)
        del is_sh, os_sh
    el = time.time() - t
    is_sel = np.concatenate(is_sel); os_sel = np.concatenate(os_sel)
    rank = np.concatenate(rank_acc)
    omega = rank / (npec + 1.0)
    logit = np.log(omega / (1.0 - omega))
    pbo = float((logit < 0).mean())
    sl, ic = np.polyfit(is_sel, os_sel, 1)
    pred = sl * is_sel + ic
    ss_res = float(((os_sel - pred) ** 2).sum())
    ss_tot = float(((os_sel - os_sel.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    print(f"  [{label}] specs={npec:,} chunk={chunk} {el:.1f}s peak {peak:.2f} GB  "
          f"PBO={pbo:.4f}")
    return dict(pbo=pbo, npec=npec, chunk=chunk, seconds=el, peak=peak,
                slope=float(sl), intercept=float(ic), r2=float(r2),
                ploss=float((os_sel < 0).mean()),
                os_mean=float(os_sel.mean()), is_mean=float(is_sel.mean()))


# --- full grid reference ---------------------------------------------------
# Read from step 4 rather than recomputed. Step 4's primary pass is already the
# identical construction, being S=16, the same 12,870 full enumeration at the
# same seed, the same naive Sharpe and the same moment array, so recomputing it
# would consume roughly 13 minutes to reproduce a figure bit for bit.
_p4 = pd.read_csv(OUT / "pbo.csv")
_p4 = _p4[(_p4.table == "pbo") & (_p4.pass_label == "primary")
          & (_p4.restriction == "full_grid")]


def _p4v(metric):
    return float(_p4[_p4.metric == metric].iloc[0]["value"])


full = dict(pbo=_p4v("pbo"), npec=TOTAL, chunk=None, seconds=None, peak=None,
            slope=_p4v("degradation_slope"), intercept=_p4v("degradation_intercept"),
            r2=_p4v("degradation_r_squared"), ploss=_p4v("probability_of_loss"),
            os_mean=_p4v("selected_oos_sharpe_mean"),
            is_mean=_p4v("selected_is_sharpe_mean"))
print(f"\n== full-grid reference at S=16, read from step 4 == PBO={full['pbo']:.4f}")
rows.append({"table": "reference", "axis": "full_grid", "axis_value": "",
             "n_specifications": full["npec"], "pbo": full["pbo"],
             "degradation_slope": full["slope"], "degradation_intercept": full["intercept"],
             "degradation_r_squared": full["r2"], "probability_of_loss": full["ploss"],
             "note": "read from outputs/session-19/pbo.csv, the step 4 primary pass; "
                     "identical construction, being S=16 over the full 12,870 enumeration "
                     "at seed 20260821 on the naive Sharpe"})

# --- reachability, which terminals are dead at each stratum value ----------
reach = pd.read_csv(S18 / "reachability.csv")
census = reach[reach.table == "census"]


def dead_terminals(axis, value):
    sub = census[(census.axis == axis) & (census.axis_value == float(value))]
    d = sub[sub["count"] == 0]
    return len(d), "; ".join(sorted(d.terminal.astype(str).tolist()))


# --- strata ---------------------------------------------------------------
print("\n== structural strata ==")
per_axis = {}
for axis in STRUCTURAL:
    vals = S.AXIS_VALUES[S.AXIS_NAMES.index(axis)]
    canon_v = CV[S.AXIS_NAMES.index(axis)]
    col = idx[axis].to_numpy()
    got = []
    print(f"-- {axis}, {len(vals)} values --")
    for v in vals:
        mask = col == float(v)
        res = cscv_mask(mask, f"{axis}={v}")
        nd, dterm = dead_terminals(axis, v)
        rows.append({"table": "stratum", "axis": axis, "axis_value": v,
                     "is_canonical_value": int(float(v) == float(canon_v)),
                     "n_specifications": res["npec"], "pbo": res["pbo"],
                     "degradation_slope": res["slope"],
                     "degradation_intercept": res["intercept"],
                     "degradation_r_squared": res["r2"],
                     "probability_of_loss": res["ploss"],
                     "selected_oos_sharpe_mean": res["os_mean"],
                     "selected_is_sharpe_mean": res["is_mean"],
                     "n_dead_terminals": nd, "dead_terminals": dterm,
                     "seconds": round(res["seconds"], 2),
                     "peak_rss_gb": round(res["peak"], 3)})
        got.append(res["pbo"])
    lo, hi = min(got), max(got)
    inside = bool(lo <= full["pbo"] <= hi)
    per_axis[axis] = (lo, hi, inside)
    rows.append({"table": "axis_range", "axis": axis, "n_specifications": len(vals),
                 "pbo_min": lo, "pbo_max": hi, "pbo_range": hi - lo,
                 "full_grid_pbo": full["pbo"],
                 "full_grid_inside_range": int(inside),
                 "note": "range of stratum PBO across the values of this axis"})
    print(f"   range {lo:.4f} to {hi:.4f}, full-grid {full['pbo']:.4f} "
          f"{'INSIDE' if inside else 'OUTSIDE'}")

n_out_above = sum(1 for a, (lo, hi, ins) in per_axis.items() if not ins and full["pbo"] > hi)
n_out_below = sum(1 for a, (lo, hi, ins) in per_axis.items() if not ins and full["pbo"] < lo)
n_in = sum(1 for a, (lo, hi, ins) in per_axis.items() if ins)
if n_out_above == len(per_axis):
    verdict = ("the full-grid PBO exceeds every within-stratum range, which indicates "
               "search across strategy shapes contributes overfitting beyond parameter "
               "search")
elif n_out_above == 0 and n_in == len(per_axis):
    verdict = ("the full-grid PBO lies inside every within-stratum range and exceeds "
               "none of them, which indicates search across strategy shapes does not "
               "contribute overfitting beyond parameter search")
elif n_out_above == 0:
    verdict = (f"the full-grid PBO exceeds none of the {len(per_axis)} within-stratum "
               f"ranges, lying inside {n_in} of them and below {n_out_below}, which "
               "indicates search across strategy shapes does not contribute overfitting "
               "beyond parameter search, with the one range it falls below indicating "
               "the full grid overfits less than any single stratum of that axis")
else:
    verdict = (f"the full-grid PBO lies inside {n_in} of {len(per_axis)} within-stratum "
               f"ranges, above {n_out_above} and below {n_out_below}, so the two "
               "indications are mixed across axes and no single reading holds")
rows.append({"table": "interpretation", "axis": "full_grid_against_strata",
             "full_grid_pbo": full["pbo"],
             "n_axes_inside": n_in, "n_axes_full_above": n_out_above,
             "n_axes_full_below": n_out_below, "note": verdict})
print(f"\ninterpretation as measured: {verdict}")

COLS = ["table", "axis", "axis_value", "is_canonical_value", "n_specifications",
        "pbo", "pbo_min", "pbo_max", "pbo_range", "full_grid_pbo",
        "full_grid_inside_range", "degradation_slope", "degradation_intercept",
        "degradation_r_squared", "probability_of_loss", "selected_oos_sharpe_mean",
        "selected_is_sharpe_mean", "n_dead_terminals", "dead_terminals",
        "n_axes_inside", "n_axes_full_above", "n_axes_full_below",
        "seconds", "peak_rss_gb", "note"]
with open(OUT / "pbo-strata.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {OUT/'pbo-strata.csv'} with {len(rows)} rows")
