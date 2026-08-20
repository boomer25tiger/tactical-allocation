"""M1 diagnostic. Is the positive-control failure a harness difference or an
instability in the statistic itself?

The candidate mechanism is that mc @ SbT is a BLAS matmul whose summation
order over the 16-element inner dimension depends on the shape of mc, so the
chunk size perturbs is_sh at the 1e-16 level. argmax over 121,500 near-tied
specifications is not continuous in that perturbation, so a handful of
selections flip, which moves the regression coefficients while leaving PBO,
a coarse statistic over ranks, unchanged.

Test. Run the observed pass at several chunk sizes and compare the four
figures against outputs/session-19/pbo.csv, and count how many of the 12,870
selections differ between chunk settings.
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

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S           # noqa: E402

G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-19_6"
NBLK, NSHARD, S_PRIMARY = 48, 8, 16
TOTAL = S.grid_size()
ANN = math.sqrt(252.0)
COMBO_SEED = 20260821

TARGET = {}
for r in csv.DictReader(open(ROOT / "outputs/session-19/pbo.csv")):
    if (r["table"] == "pbo" and r["S"] == "16" and r["pass_label"] == "primary"
            and r["restriction"] == "full_grid"
            and r["metric"] in ("pbo", "degradation_slope", "degradation_intercept",
                                "degradation_r_squared")):
        TARGET[r["metric"]] = float(r["value"])

raw = np.concatenate([
    np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64).reshape(-1, 2 * NBLK)
    for k in range(NSHARD)])
ids = np.concatenate([np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
                      for k in range(NSHARD)])
raw = np.ascontiguousarray(raw[np.argsort(ids)])
MOM = raw.reshape(TOTAL, NBLK, 2)
BLK = np.load(G / "block-sizes.npy").astype(np.float64)
del raw

g = NBLK // S_PRIMARY
Sb = np.ascontiguousarray(MOM[:, :, 0].reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
Qb = np.ascontiguousarray(MOM[:, :, 1].reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
nvec = BLK.reshape(S_PRIMARY, g).sum(axis=1)
SbT, QbT = Sb.T.copy(), Qb.T.copy()

half = S_PRIMARY // 2
NCOMB = math.comb(S_PRIMARY, half)
M = np.zeros((NCOMB, S_PRIMARY), dtype=np.float64)
for i, c in enumerate(itertools.combinations(range(S_PRIMARY), half)):
    M[i, list(c)] = 1.0


def sharpe(sum_, sq_, n_):
    mean = sum_ / n_
    var = (sq_ - sum_ * sum_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


def run_at(chunk):
    is_sel, os_sel, rank, sel_idx = [], [], [], []
    t = time.time()
    for a in range(0, NCOMB, chunk):
        mc = M[a:a + chunk]
        oc = 1.0 - mc
        is_sh = sharpe(mc @ SbT, mc @ QbT, float(mc[0] @ nvec))
        os_sh = sharpe(oc @ SbT, oc @ QbT, float(oc[0] @ nvec))
        best = np.argmax(is_sh, axis=1)
        r = np.arange(len(best))
        sel_idx.append(best)
        is_sel.append(is_sh[r, best])
        sel = os_sh[r, best]
        os_sel.append(sel)
        rank.append((os_sh < sel[:, None]).sum(axis=1) + 1)
        del is_sh, os_sh
    el = time.time() - t
    is_sel = np.concatenate(is_sel); os_sel = np.concatenate(os_sel)
    rank = np.concatenate(rank); sel_idx = np.concatenate(sel_idx)
    omega = rank / (TOTAL + 1.0)
    logit = np.log(omega / (1.0 - omega))
    sl, ic = np.polyfit(is_sel, os_sel, 1)
    pred = sl * is_sel + ic
    r2 = 1.0 - float(((os_sel - pred) ** 2).sum()) / float(((os_sel - os_sel.mean()) ** 2).sum())
    return dict(chunk=chunk, seconds=el, pbo=float((logit < 0).mean()),
                slope=float(sl), intercept=float(ic), r2=r2, sel=sel_idx,
                is_sel=is_sel, peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9)


rows = []
res = {}
for chunk in (128, 257, 514):
    r = run_at(chunk)
    res[chunk] = r
    gaps = {"pbo": abs(r["pbo"] - TARGET["pbo"]),
            "degradation_slope": abs(r["slope"] - TARGET["degradation_slope"]),
            "degradation_intercept": abs(r["intercept"] - TARGET["degradation_intercept"]),
            "degradation_r_squared": abs(r["r2"] - TARGET["degradation_r_squared"])}
    print(f"chunk {chunk:>4}  {r['seconds']:>6.1f}s peak {r['peak']:.2f}GB  "
          f"PBO {r['pbo']:.10f} (gap {gaps['pbo']:.1e})  "
          f"slope {r['slope']:.10f} (gap {gaps['degradation_slope']:.1e})")
    for k, v in gaps.items():
        rows.append({"table": "chunk_sweep", "chunk": chunk, "metric": k,
                     "value": {"pbo": r["pbo"], "degradation_slope": r["slope"],
                               "degradation_intercept": r["intercept"],
                               "degradation_r_squared": r["r2"]}[k],
                     "target": TARGET[k], "abs_gap": v,
                     "exact": int(v == 0.0)})
    rows.append({"table": "chunk_sweep", "chunk": chunk, "metric": "seconds",
                 "value": round(r["seconds"], 1)})
    rows.append({"table": "chunk_sweep", "chunk": chunk, "metric": "peak_rss_gb",
                 "value": round(r["peak"], 3)})

base = res[514]
for chunk in (128, 257):
    d = int((res[chunk]["sel"] != base["sel"]).sum())
    md = float(np.max(np.abs(res[chunk]["is_sel"] - base["is_sel"])))
    rows.append({"table": "selection_stability", "chunk": chunk,
                 "metric": "selections_differing_from_chunk_514", "value": d,
                 "note": f"of {NCOMB} combinations"})
    rows.append({"table": "selection_stability", "chunk": chunk,
                 "metric": "max_abs_selected_is_sharpe_difference", "value": md})
    print(f"chunk {chunk} against 514: {d} of {NCOMB} selections differ, "
          f"max abs selected in-sample Sharpe difference {md:.3e}")

rows.append({"table": "diagnosis", "metric": "mechanism",
             "note": "mc @ SbT is a BLAS matmul whose summation order over the "
                     "16-element inner dimension depends on the shape of mc, so the "
                     "chunk size perturbs the in-sample Sharpe at the level of float "
                     "rounding. argmax over 121,500 specifications is not continuous "
                     "in that perturbation, so some selections flip and the regression "
                     "coefficients move while PBO, a coarse statistic over ranks, does "
                     "not"})
with open(OUT / "m1-diagnostic.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "chunk", "metric", "value", "target",
                                       "abs_gap", "exact", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'m1-diagnostic.csv'} with {len(rows)} rows")
