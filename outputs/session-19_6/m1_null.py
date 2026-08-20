"""M1, the mechanical null under the degradation slope.

WHAT THE NULL IS AND WHY, recorded before running.

  In CSCV the in-sample and out-of-sample halves are complements of one
  fixed sample. A specification sitting above its own full-window mean on
  one half must sit below it on the other, so regressing out-of-sample
  Sharpe on in-sample Sharpe carries a negative component that is
  partition arithmetic rather than degradation. The size of that component
  is unmeasured, and the byte-identical canonical rank marginals together
  with the -0.902 pairing correlation are the same structure showing
  through.

  CONSTRUCTION. The 48 stored blocks are permuted independently per
  specification, then merged to 16 by the same adjacent-triple reduction
  the observed pass uses. Each specification keeps its own 48 block
  moments exactly, so every full-window marginal Sharpe is preserved to
  float summation order, while the alignment of which calendar blocks are
  strong across specifications is destroyed. What survives is the
  complementary-half arithmetic and nothing else.

  The per-block session counts are permuted with the moments, so the
  merged super-block counts become specification-dependent. That is
  carried exactly rather than approximated by the shared count vector.

  TOLERANCES AND SEEDS, FIXED HERE BEFORE ANY COMPARISON RUNS.
    TOL_PC    = 1e-12 absolute on the four positive-control figures,
                which are read from outputs/session-19/pbo.csv rather
                than hardcoded. The arithmetic is identical, so anything
                above this is a harness difference rather than rounding.
    TOL_MARG  = 1e-10 absolute on the full-window naive Sharpe before
                against after permutation, which bounds float summation
                order over 48 addends.
    NULL_SEED = 20260822, fixed before drawing. Replication r draws from
                NULL_SEED + r.
    MEM_CEILING_GB = 2.0 on an 8 GB machine.

  This reuses the stored moment array. No grid is re-executed.
"""
from __future__ import annotations

import csv
import itertools
import json
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
P19 = ROOT / "outputs" / "session-19" / "pbo.csv"

TOL_PC, TOL_MARG = 1e-12, 1e-10
NULL_SEED = 20260822
MEM_CEILING_GB = 0.5
S_PRIMARY, NBLK, NSHARD = 16, 48, 8
COMBO_SEED = 20260821          # the seed session 19 fixed, reused unchanged
TOTAL = S.grid_size()          # from config, no literal
ANN = math.sqrt(252.0)
rows = []


def add(table, **kw):
    rows.append({"table": table, **kw})


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


# ---- targets read from the emitted file, never hardcoded -------------------
TARGET = {}
for r in csv.DictReader(open(P19)):
    if (r["table"] == "pbo" and r["S"] == str(S_PRIMARY)
            and r["pass_label"] == "primary" and r["restriction"] == "full_grid"
            and r["metric"] in ("pbo", "degradation_slope", "degradation_intercept",
                                "degradation_r_squared")):
        TARGET[r["metric"]] = float(r["value"])
assert len(TARGET) == 4, TARGET
print("targets read from outputs/session-19/pbo.csv:")
for k, v in TARGET.items():
    print(f"  {k:<24} {v!r}")

# ---- load the stored moment array -----------------------------------------
t0 = time.time()
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
del raw
t_load = time.time() - t0
print(f"\nmoment array {MOM.shape} {MOM.dtype} {MOM.nbytes/1e6:.1f} MB in {t_load:.1f}s")
add("load", item="shape", note=f"{MOM.shape[0]} x {MOM.shape[1]} x {MOM.shape[2]}")
add("load", item="dtype", note=str(MOM.dtype))
add("load", item="mb", value=round(MOM.nbytes / 1e6, 1))
add("load", item="seconds", value=round(t_load, 2))
add("load", item="reuse_note",
    note="the stored 48-block moment array is reused; no grid is re-executed")


# ---- machinery copied verbatim from scripts/s19_step4.py -------------------
def merge(nblk_target):
    g = NBLK // nblk_target
    Sb = MOM[:, :, 0].reshape(TOTAL, nblk_target, g).sum(axis=2)
    Qb = MOM[:, :, 1].reshape(TOTAL, nblk_target, g).sum(axis=2)
    nb = BLK.reshape(nblk_target, g).sum(axis=1)
    return np.ascontiguousarray(Sb), np.ascontiguousarray(Qb), nb


def combos(nb, rng):
    half = nb // 2
    full = math.comb(nb, half)
    m = np.zeros((full, nb), dtype=np.float64)
    for i, c in enumerate(itertools.combinations(range(nb), half)):
        m[i, list(c)] = 1.0
    return m, full, False


def sharpe(sum_, sq_, n_):
    mean = sum_ / n_
    var = (sq_ - sum_ * sum_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


# verify the three bodies are the ones in s19_step4.py rather than a rewrite
src4 = (ROOT / "scripts" / "s19_step4.py").read_text()
for probe in ("Sb = MOM[:, :, 0].reshape(TOTAL, nblk_target, g).sum(axis=2)",
              "var = (sq_ - sum_ * sum_ / n_) / (n_ - 1.0)",
              "np.maximum(var, 1e-300, out=var)"):
    assert probe in src4, probe
add("provenance", item="machinery",
    note="merge and sharpe copied verbatim from scripts/s19_step4.py and asserted "
         "present in that file; sharpe broadcasts over an array-valued n, so the "
         "null path uses the same function unmodified")

rng_c = np.random.default_rng(COMBO_SEED)
M, NCOMB, _ = combos(S_PRIMARY, rng_c)
print(f"combinations {NCOMB:,}, full enumeration of C({S_PRIMARY},{S_PRIMARY//2})")


def regress(is_, os_):
    sl, ic = np.polyfit(is_, os_, 1)
    pred = sl * is_ + ic
    ss_res = float(((os_ - pred) ** 2).sum())
    ss_tot = float(((os_ - os_.mean()) ** 2).sum())
    return float(sl), float(ic), (1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"))


def cscv_pass(Sb, Qb, nvec, label, chunk_div):
    """nvec is either a length-16 vector shared by all specifications, the
    observed case, or a (TOTAL, 16) array, the permuted case."""
    per_spec = nvec.ndim == 2
    chunk = max(1, int(MEM_CEILING_GB * 1e9 / (TOTAL * 8 * chunk_div)))
    chunk = min(chunk, NCOMB)
    SbT, QbT = Sb.T.copy(), Qb.T.copy()
    NbT = nvec.T.copy() if per_spec else None
    is_sel, os_sel, rank = [], [], []
    t = time.time(); peak = 0.0
    nchunk = (NCOMB + chunk - 1) // chunk
    for ci, a in enumerate(range(0, NCOMB, chunk)):
        if ci % 20 == 0:
            print(f"    [{label}] chunk {ci+1}/{nchunk} t={time.time()-t:.0f}s "
                  f"rss={rss_gb():.2f}GB", flush=True)
        mc = M[a:a + chunk]
        oc = 1.0 - mc
        if per_spec:
            n_is = mc @ NbT
            n_os = oc @ NbT
        else:
            n_is = float(mc[0] @ nvec)
            n_os = float(oc[0] @ nvec)
        is_sh = sharpe(mc @ SbT, mc @ QbT, n_is)
        os_sh = sharpe(oc @ SbT, oc @ QbT, n_os)
        peak = max(peak, rss_gb())
        best = np.argmax(is_sh, axis=1)
        r = np.arange(len(best))
        is_sel.append(is_sh[r, best])
        sel = os_sh[r, best]
        os_sel.append(sel)
        rank.append((os_sh < sel[:, None]).sum(axis=1) + 1)
        del is_sh, os_sh, n_is, n_os
    el = time.time() - t
    is_sel = np.concatenate(is_sel); os_sel = np.concatenate(os_sel)
    rank = np.concatenate(rank)
    omega = rank / (TOTAL + 1.0)
    logit = np.log(omega / (1.0 - omega))
    pbo = float((logit < 0).mean())
    sl, ic, r2 = regress(is_sel, os_sel)
    print(f"  [{label}] chunk={chunk} {el:.1f}s peak {peak:.2f} GB  "
          f"PBO={pbo:.6f} slope={sl:.6f} icept={ic:.6f} R2={r2:.6f}")
    return dict(pbo=pbo, slope=sl, intercept=ic, r2=r2, seconds=el, peak=peak,
                chunk=chunk)


# ===========================================================================
print("\n== M1 positive control, unmodified S=16 machinery ==")
add("tolerance", item="TOL_PC", value=TOL_PC, note="stated before comparing")
add("tolerance", item="TOL_MARG", value=TOL_MARG, note="stated before comparing")
add("tolerance", item="NULL_SEED", value=NULL_SEED, note="fixed before drawing")
add("tolerance", item="MEM_CEILING_GB", value=MEM_CEILING_GB,
    note="stated before running, 8 GB machine")

Sb0, Qb0, nv0 = merge(S_PRIMARY)
obs = cscv_pass(Sb0, Qb0, nv0, "observed", 4)
gaps = {"pbo": abs(obs["pbo"] - TARGET["pbo"]),
        "degradation_slope": abs(obs["slope"] - TARGET["degradation_slope"]),
        "degradation_intercept": abs(obs["intercept"] - TARGET["degradation_intercept"]),
        "degradation_r_squared": abs(obs["r2"] - TARGET["degradation_r_squared"])}
pc_ok = all(v <= TOL_PC for v in gaps.values())
for k, v in gaps.items():
    got = {"pbo": obs["pbo"], "degradation_slope": obs["slope"],
           "degradation_intercept": obs["intercept"],
           "degradation_r_squared": obs["r2"]}[k]
    add("positive_control", item=k, value=got, target=TARGET[k], abs_gap=v,
        within=int(v <= TOL_PC))
    print(f"    {k:<24} got {got!r} target {TARGET[k]!r} gap {v:.3e}")
add("positive_control", item="verdict", note="PASS" if pc_ok else "FAIL")
add("positive_control", item="seconds", value=round(obs["seconds"], 1))
add("positive_control", item="peak_rss_gb", value=round(obs["peak"], 3))
print(f"  positive control {'PASS' if pc_ok else 'FAIL'}")
if not pc_ok:
    with open(OUT / "degradation-null.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "target",
                                           "abs_gap", "within", "note"],
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    raise SystemExit("M1 halted, positive control failed")

# ---- marginal-preservation control ----------------------------------------
full_S = MOM[:, :, 0].sum(axis=1)
full_Q = MOM[:, :, 1].sum(axis=1)
n_full = float(BLK.sum())
sh_full = sharpe(full_S.copy(), full_Q.copy(), n_full)


def permuted(rep):
    rng = np.random.default_rng(NULL_SEED + rep)
    perm = np.argsort(rng.random((TOTAL, NBLK)), axis=1)
    Sp = np.take_along_axis(MOM[:, :, 0], perm, axis=1)
    Qp = np.take_along_axis(MOM[:, :, 1], perm, axis=1)
    Np = np.take_along_axis(np.broadcast_to(BLK, (TOTAL, NBLK)), perm, axis=1)
    g = NBLK // S_PRIMARY
    Sb = np.ascontiguousarray(Sp.reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
    Qb = np.ascontiguousarray(Qp.reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
    Nb = np.ascontiguousarray(Np.reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
    marg = float(np.max(np.abs(sharpe(Sb.sum(axis=1), Qb.sum(axis=1),
                                      Nb.sum(axis=1)) - sh_full)))
    del Sp, Qp, Np, perm
    return Sb, Qb, Nb, marg


print("\n== M1 pilot replication ==")
Sb1, Qb1, Nb1, marg1 = permuted(0)
add("marginal_control", item="max_abs_sharpe_deviation", value=marg1,
    within=int(marg1 <= TOL_MARG),
    note="full-window naive Sharpe after permutation against before, bounding "
         "float summation order over 48 addends")
add("marginal_control", item="merged_count_min", value=float(Nb1.min()))
add("marginal_control", item="merged_count_max", value=float(Nb1.max()))
add("marginal_control", item="shared_count_min", value=float(merge(S_PRIMARY)[2].min()))
add("marginal_control", item="shared_count_max", value=float(merge(S_PRIMARY)[2].max()))
print(f"  marginal Sharpe preserved to {marg1:.3e} against tolerance {TOL_MARG:g}")
print(f"  merged super-block counts span {Nb1.min():.0f} to {Nb1.max():.0f} "
      f"against the shared vector's {merge(S_PRIMARY)[2].min():.0f} to "
      f"{merge(S_PRIMARY)[2].max():.0f}")
rep0 = cscv_pass(Sb1, Qb1, Nb1, "null rep 0", 12)
add("pilot", item="slope", value=rep0["slope"])
add("pilot", item="intercept", value=rep0["intercept"])
add("pilot", item="r_squared", value=rep0["r2"])
add("pilot", item="pbo", value=rep0["pbo"])
add("pilot", item="seconds", value=round(rep0["seconds"], 1))
add("pilot", item="peak_rss_gb", value=round(rep0["peak"], 3))
add("pilot", item="chunk", value=rep0["chunk"])
del Sb1, Qb1, Nb1

json.dump({"pilot_seconds": rep0["seconds"], "observed_seconds": obs["seconds"],
           "peak": max(obs["peak"], rep0["peak"])},
          open(OUT / "_m1_pilot.json", "w"))
with open(OUT / "_m1_rows.json", "w") as fh:
    json.dump(rows, fh)
print(f"\npilot wall clock {rep0['seconds']:.1f}s, peak {max(obs['peak'], rep0['peak']):.3f} GB")
print("stage 1 complete, replication count not yet chosen")
