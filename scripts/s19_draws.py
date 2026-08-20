"""Session 19: dump the per-combination CSCV draws at S=16.

pbo.csv carries summary statistics rather than the per-combination arrays,
and the step 8 figures need the arrays themselves. Recomputing the S=16 pass
inside the report generator would cost about thirteen minutes on every run,
including the two regenerability checks, so the arrays are dumped once here
as a small committed artifact and the generator reads them.

Identical construction to step 4, being S=16 over the full 12,870
enumeration at seed 20260821 on the naive Sharpe, so the PBO recomputed from
these arrays must equal step 4's figure exactly. That equality is asserted.
"""
from __future__ import annotations

import csv
import itertools
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-19"

S_PRIMARY, NBLK, NSHARD = 16, 48, 8
MEM_CEILING_GB, COMBO_SEED = 2.0, 20260821
TOTAL = S.grid_size()
ANN = math.sqrt(252.0)

raw = np.concatenate([
    np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64).reshape(-1, 2 * NBLK)
    for k in range(NSHARD)])
ids = np.concatenate([np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
                      for k in range(NSHARD)])
raw = np.ascontiguousarray(raw[np.argsort(ids)])
MOM = raw.reshape(TOTAL, NBLK, 2)
BLK = np.load(G / "block-sizes.npy").astype(np.float64)

g = NBLK // S_PRIMARY
Sb = np.ascontiguousarray(MOM[:, :, 0].reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
Qb = np.ascontiguousarray(MOM[:, :, 1].reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
nvec = BLK.reshape(S_PRIMARY, g).sum(axis=1)

half = S_PRIMARY // 2
ncomb = math.comb(S_PRIMARY, half)
M = np.zeros((ncomb, S_PRIMARY), dtype=np.float64)
for i, c in enumerate(itertools.combinations(range(S_PRIMARY), half)):
    M[i, list(c)] = 1.0
print(f"S={S_PRIMARY}, {ncomb:,} combinations, full enumeration")

CANON = S.index_of(S.canonical_values())
SbT, QbT = Sb.T.copy(), Qb.T.copy()
chunk = max(1, int(MEM_CEILING_GB * 1e9 / (TOTAL * 8 * 4)))


def sharpe(s_, q_, n_):
    mean = s_ / n_
    var = (q_ - s_ * s_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


is_sel, os_sel, os_med, rank, c_is, c_os = [], [], [], [], [], []
for a in range(0, ncomb, chunk):
    mc = M[a:a + chunk]
    oc = 1.0 - mc
        # Session 20 B1 repair. The count varies across combinations because
        # merged super-block counts are unequal, so it is taken per
        # combination rather than from the chunk's first row.
    is_sh = sharpe(mc @ SbT, mc @ QbT, (mc @ nvec)[:, None])
    os_sh = sharpe(oc @ SbT, oc @ QbT, (oc @ nvec)[:, None])
    best = np.argmax(is_sh, axis=1)
    r = np.arange(len(best))
    is_sel.append(is_sh[r, best])
    sel = os_sh[r, best]
    os_sel.append(sel)
    os_med.append(np.median(os_sh, axis=1))
    rank.append((os_sh < sel[:, None]).sum(axis=1) + 1)
    c_is.append((is_sh < is_sh[:, CANON][:, None]).sum(axis=1) + 1)
    c_os.append((os_sh < os_sh[:, CANON][:, None]).sum(axis=1) + 1)
    del is_sh, os_sh

is_sel = np.concatenate(is_sel); os_sel = np.concatenate(os_sel)
os_med = np.concatenate(os_med); rank = np.concatenate(rank)
c_is = np.concatenate(c_is); c_os = np.concatenate(c_os)
omega = rank / (TOTAL + 1.0)
logit = np.log(omega / (1.0 - omega))
pbo = float((logit < 0).mean())

ref = None
for r0 in csv.DictReader(open(OUT / "pbo.csv")):
    if (r0["table"] == "pbo" and r0["pass_label"] == "primary"
            and r0["restriction"] == "full_grid" and r0["metric"] == "pbo"):
        ref = float(r0["value"]); break
assert ref is not None, "step 4 primary PBO not found"
assert abs(pbo - ref) < 1e-15, f"draws PBO {pbo} does not reproduce step 4 {ref}"
print(f"PBO from the dumped draws {pbo:.10f} reproduces step 4 {ref:.10f} exactly")

np.savez_compressed(OUT / "cscv-draws-s16.npz", is_sel=is_sel, os_sel=os_sel,
                    os_med=os_med, rank=rank, logit=logit,
                    canonical_is_rank=c_is, canonical_oos_rank=c_os,
                    n_specifications=np.array([TOTAL]),
                    n_combinations=np.array([ncomb]), S=np.array([S_PRIMARY]))
sz = (OUT / "cscv-draws-s16.npz").stat().st_size
print(f"wrote {OUT/'cscv-draws-s16.npz'} {sz/1e3:.0f} KB, {ncomb:,} combinations")
