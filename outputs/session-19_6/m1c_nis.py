"""Quantify the per-chunk session-count approximation in cscv.

scripts/s19_step4.py computes n_is = float(mc[0] @ nvec), taking the
in-sample session count from the FIRST combination of each chunk and applying
it to every combination in that chunk. Super-block counts are not equal, so
the count varies across combinations and the substitution is an
approximation whose error depends on where the chunk boundaries fall.
"""
from __future__ import annotations
import csv, itertools, math, sys
from pathlib import Path
import numpy as np

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S      # noqa: E402

G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-19_6"
NBLK, NSHARD, S_PRIMARY = 48, 8, 16
TOTAL = S.grid_size(); ANN = math.sqrt(252.0)

raw = np.concatenate([np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64
                                  ).reshape(-1, 2 * NBLK) for k in range(NSHARD)])
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
M = np.zeros((NCOMB, S_PRIMARY))
for i, c in enumerate(itertools.combinations(range(S_PRIMARY), half)):
    M[i, list(c)] = 1.0

n_true = M @ nvec
rows = []
print(f"base block sizes span {BLK.min():.0f} to {BLK.max():.0f}, sum {BLK.sum():.0f}")
print(f"merged super-block counts span {nvec.min():.0f} to {nvec.max():.0f}, "
      f"sum {nvec.sum():.0f}")
print(f"true in-sample session count across {NCOMB:,} combinations spans "
      f"{n_true.min():.0f} to {n_true.max():.0f}, {len(np.unique(n_true))} distinct values")
rows += [{"table": "counts", "metric": "base_block_min", "value": float(BLK.min())},
         {"table": "counts", "metric": "base_block_max", "value": float(BLK.max())},
         {"table": "counts", "metric": "superblock_min", "value": float(nvec.min())},
         {"table": "counts", "metric": "superblock_max", "value": float(nvec.max())},
         {"table": "counts", "metric": "n_is_true_min", "value": float(n_true.min())},
         {"table": "counts", "metric": "n_is_true_max", "value": float(n_true.max())},
         {"table": "counts", "metric": "n_is_distinct_values",
          "value": int(len(np.unique(n_true)))},
         {"table": "counts", "metric": "n_is_spread_fraction",
          "value": float((n_true.max() - n_true.min()) / n_true.mean())}]


def sharpe(s_, q_, n_):
    mean = s_ / n_
    var = (q_ - s_ * s_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


def pass_(chunk, exact_n):
    is_sel, os_sel, rank = [], [], []
    for a in range(0, NCOMB, chunk):
        mc = M[a:a + chunk]; oc = 1.0 - mc
        if exact_n:
            ni = (mc @ nvec)[:, None]; no = (oc @ nvec)[:, None]
        else:
            ni = float(mc[0] @ nvec); no = float(oc[0] @ nvec)
        is_sh = sharpe(mc @ SbT, mc @ QbT, ni)
        os_sh = sharpe(oc @ SbT, oc @ QbT, no)
        b = np.argmax(is_sh, axis=1); r = np.arange(len(b))
        is_sel.append(is_sh[r, b]); sel = os_sh[r, b]; os_sel.append(sel)
        rank.append((os_sh < sel[:, None]).sum(axis=1) + 1)
        del is_sh, os_sh
    is_sel = np.concatenate(is_sel); os_sel = np.concatenate(os_sel)
    rank = np.concatenate(rank)
    om = rank / (TOTAL + 1.0)
    sl, ic = np.polyfit(is_sel, os_sel, 1)
    pred = sl * is_sel + ic
    r2 = 1 - float(((os_sel - pred) ** 2).sum()) / float(((os_sel - os_sel.mean()) ** 2).sum())
    return dict(pbo=float((np.log(om / (1 - om)) < 0).mean()), slope=float(sl),
                intercept=float(ic), r2=r2)


TARGET = {}
for r in csv.DictReader(open(ROOT / "outputs/session-19/pbo.csv")):
    if (r["table"] == "pbo" and r["S"] == "16" and r["pass_label"] == "primary"
            and r["restriction"] == "full_grid"):
        TARGET[r["metric"]] = r["value"]

a = pass_(514, False)
b = pass_(514, True)
print(f"\nas emitted, chunk 514, first-combination count: "
      f"PBO {a['pbo']:.10f} slope {a['slope']:.10f} icept {a['intercept']:.10f} R2 {a['r2']:.10f}")
print(f"exact per-combination count:                     "
      f"PBO {b['pbo']:.10f} slope {b['slope']:.10f} icept {b['intercept']:.10f} R2 {b['r2']:.10f}")
for k in ("pbo", "slope", "intercept", "r2"):
    key = {"pbo": "pbo", "slope": "degradation_slope",
           "intercept": "degradation_intercept", "r2": "degradation_r_squared"}[k]
    rows.append({"table": "correction", "metric": key,
                 "value": b[k], "as_emitted": a[k],
                 "emitted_in_pbo_csv": TARGET.get(key, ""),
                 "abs_gap": abs(b[k] - a[k])})
    print(f"  {key:<24} emitted {a[k]!r}  exact {b[k]!r}  shift {abs(b[k]-a[k]):.3e}")
rows.append({"table": "diagnosis", "metric": "mechanism",
             "note": "n_is = float(mc[0] @ nvec) in scripts/s19_step4.py takes the "
                     "in-sample session count from the first combination of each chunk "
                     "and applies it to every combination in that chunk. Super-block "
                     "counts are unequal, so the count varies across combinations. PBO "
                     "is unaffected because within a chunk the same count scales every "
                     "specification identically and rank ordering is preserved. The "
                     "regression coefficients compare Sharpe levels across combinations "
                     "and are affected, which is why they move with the chunk size while "
                     "PBO does not"})
with open(OUT / "m1-nis-correction.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "metric", "value", "as_emitted",
                                       "emitted_in_pbo_csv", "abs_gap", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'m1-nis-correction.csv'} with {len(rows)} rows")
