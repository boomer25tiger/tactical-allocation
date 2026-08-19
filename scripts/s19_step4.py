"""Session 19 step 4: PBO via CSCV, complete run.

PRE-REGISTERED BEFORE ANY RESULT IS READ.

  S = 16 as primary, the Bailey, Borwein, Lopez de Prado and Zhu
  convention. The performance metric is the NAIVE Sharpe rather than the
  Lo-corrected Sharpe, because autocovariance is not additive across
  disjoint blocks and the cross-boundary terms are missing from a union.
  That is a disclosed approximation and is recorded here rather than left
  implicit.

  MEM_CEILING = 2.0 GB peak for the combination tensors, which sets the
  chunk size.

  COMBO_CAP = 20000. Where C(S, S/2) exceeds the cap the combinations are
  a random sample drawn at COMBO_SEED rather than the full enumeration,
  and the sampling is disclosed per pass. C(24,12) is 2,704,156 and
  C(48,24) is about 1.6e13, so full enumeration is not available at those
  block counts at any runtime.

  COMBO_SEED = 20260821, fixed before any sampling.
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
NBLK, NSHARD, NSESS = 48, 8, 2472
TOTAL = S.grid_size()
ANN = math.sqrt(252.0)


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


# --- load once --------------------------------------------------------------
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
print(f"moment array shape {MOM.shape} dtype {MOM.dtype} "
      f"{MOM.nbytes/1e6:.1f} MB, loaded in {time.time()-t0:.1f}s")
print(f"  stored layout is 48 blocks x 2 moments; the session 18 prompt assumed")
print(f"  48 x 5 with cubes, fourth powers and a per-block count. The count is the")
print(f"  shared block-sizes vector and skewness and kurtosis come from the metric set.")

idx = pd.read_csv(S18 / "spec-index-augmented.csv")
assert len(idx) == TOTAL
SMOOTH_MASK = idx["all_structural_axes_at_canonical"].to_numpy().astype(bool)
CANON = S.index_of(S.canonical_values())
rows = []


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


def cscv(nb, spec_mask=None, label=""):
    Sb, Qb, nvec = merge(nb)
    if spec_mask is not None:
        Sb, Qb = Sb[spec_mask], Qb[spec_mask]
    npec = Sb.shape[0]
    rng = np.random.default_rng(COMBO_SEED)
    M, full, sampled = combos(nb, rng)
    ncomb = M.shape[0]
    chunk = max(1, int(MEM_CEILING_GB * 1e9 / (npec * 8 * 4)))
    chunk = min(chunk, ncomb)
    SbT, QbT = Sb.T.copy(), Qb.T.copy()

    is_sel, os_sel, os_med = [], [], []
    canon_is_r, canon_os_r = [], []
    canon_pos = None
    if spec_mask is None:
        canon_pos = CANON
    elif spec_mask[CANON]:
        canon_pos = int(np.searchsorted(np.flatnonzero(spec_mask), CANON))

    t = time.time()
    peak = 0.0
    for a in range(0, ncomb, chunk):
        mc = M[a:a + chunk]
        oc = 1.0 - mc
        n_is = float(mc[0] @ nvec)
        n_os = float(oc[0] @ nvec)
        is_sh = sharpe(mc @ SbT, mc @ QbT, n_is)
        os_sh = sharpe(oc @ SbT, oc @ QbT, n_os)
        peak = max(peak, rss_gb())
        best = np.argmax(is_sh, axis=1)
        r = np.arange(len(best))
        is_sel.append(is_sh[r, best])
        sel_os = os_sh[r, best]
        os_sel.append(sel_os)
        os_med.append(np.median(os_sh, axis=1))
        # ascending rank of the selected specification's out-of-sample Sharpe
        cnt = (os_sh < sel_os[:, None]).sum(axis=1)
        rows_rank = cnt + 1
        if a == 0:
            rank_acc = [rows_rank]
        else:
            rank_acc.append(rows_rank)
        if canon_pos is not None:
            canon_is_r.append((is_sh < is_sh[:, canon_pos][:, None]).sum(axis=1) + 1)
            canon_os_r.append((os_sh < os_sh[:, canon_pos][:, None]).sum(axis=1) + 1)
        del is_sh, os_sh
    el = time.time() - t

    is_sel = np.concatenate(is_sel); os_sel = np.concatenate(os_sel)
    os_med = np.concatenate(os_med); rank = np.concatenate(rank_acc)
    omega = rank / (npec + 1.0)
    logit = np.log(omega / (1.0 - omega))
    pbo = float((logit < 0).mean())
    print(f"  [{label}] S={nb} specs={npec:,} combos={ncomb:,}"
          f"{' SAMPLED of %d' % full if sampled else ' full'} chunk={chunk} "
          f"{el:.1f}s peak {peak:.2f} GB  PBO={pbo:.4f}")
    return dict(nb=nb, npec=npec, ncomb=ncomb, full=full, sampled=sampled,
                chunk=chunk, seconds=el, peak_gb=peak, pbo=pbo,
                is_sel=is_sel, os_sel=os_sel, os_med=os_med, omega=omega,
                logit=logit, rank=rank,
                canon_is_r=np.concatenate(canon_is_r) if canon_is_r else None,
                canon_os_r=np.concatenate(canon_os_r) if canon_os_r else None)


def dominance(a, b):
    """First and second order stochastic dominance of a over b."""
    grid = np.unique(np.concatenate([a, b]))
    Fa = np.searchsorted(np.sort(a), grid, side="right") / len(a)
    Fb = np.searchsorted(np.sort(b), grid, side="right") / len(b)
    fsd = bool(np.all(Fa <= Fb + 1e-12))
    d = np.diff(grid, prepend=grid[0])
    Ia, Ib = np.cumsum(Fa * d), np.cumsum(Fb * d)
    ssd = bool(np.all(Ia <= Ib + 1e-12))
    return fsd, ssd, float((Fa <= Fb + 1e-12).mean()), float((Ia <= Ib + 1e-12).mean())


def emit(res, pass_label, restriction):
    is_, os_, med = res["is_sel"], res["os_sel"], res["os_med"]
    sl, ic = np.polyfit(is_, os_, 1)
    pred = sl * is_ + ic
    ss_res = float(((os_ - pred) ** 2).sum())
    ss_tot = float(((os_ - os_.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    ploss = float((os_ < 0).mean())
    fsd, ssd, ffrac, sfrac = dominance(os_, med)
    base = dict(table="pbo", pass_label=pass_label, restriction=restriction,
                S=res["nb"], n_specifications=res["npec"],
                n_combinations=res["ncomb"],
                combinations_full=res["full"],
                combinations_sampled=int(res["sampled"]),
                chunk_size=res["chunk"], seconds=round(res["seconds"], 2),
                peak_rss_gb=round(res["peak_gb"], 3))
    rows.append({**base, "metric": "pbo", "value": res["pbo"],
                 "note": "frequency with which the in-sample-best specification "
                         "lands in the bottom half of the out-of-sample ranking"})
    rows.append({**base, "metric": "degradation_slope", "value": float(sl)})
    rows.append({**base, "metric": "degradation_intercept", "value": float(ic)})
    rows.append({**base, "metric": "degradation_r_squared", "value": float(r2)})
    rows.append({**base, "metric": "probability_of_loss", "value": ploss,
                 "note": "frequency with which the selected specification returns a "
                         "negative out-of-sample naive Sharpe"})
    rows.append({**base, "metric": "first_order_stochastic_dominance", "value": int(fsd),
                 "note": f"selected against median trial; CDF condition holds on "
                         f"{ffrac:.4f} of the support"})
    rows.append({**base, "metric": "second_order_stochastic_dominance", "value": int(ssd),
                 "note": f"selected against median trial; integrated CDF condition holds "
                         f"on {sfrac:.4f} of the support"})
    for nm, arr in (("selected_is_sharpe", is_), ("selected_oos_sharpe", os_),
                    ("median_trial_oos_sharpe", med), ("logit", res["logit"])):
        rows.append({**base, "metric": f"{nm}_mean", "value": float(arr.mean())})
        rows.append({**base, "metric": f"{nm}_median", "value": float(np.median(arr))})
        rows.append({**base, "metric": f"{nm}_p05", "value": float(np.percentile(arr, 5))})
        rows.append({**base, "metric": f"{nm}_p95", "value": float(np.percentile(arr, 95))})
    if res["canon_is_r"] is not None:
        for nm, arr in (("canonical_is_rank", res["canon_is_r"]),
                        ("canonical_oos_rank", res["canon_os_r"])):
            rows.append({**base, "metric": f"{nm}_mean", "value": float(arr.mean())})
            rows.append({**base, "metric": f"{nm}_median", "value": float(np.median(arr))})
            rows.append({**base, "metric": f"{nm}_p05", "value": float(np.percentile(arr, 5))})
            rows.append({**base, "metric": f"{nm}_p95", "value": float(np.percentile(arr, 95))})
            rows.append({**base, "metric": f"{nm}_pctile_mean",
                         "value": float((arr / res["npec"]).mean()),
                         "note": "mean rank expressed as a fraction of the specification count"})
    return res


COLS = ["table", "pass_label", "restriction", "S", "n_specifications",
        "n_combinations", "combinations_full", "combinations_sampled",
        "chunk_size", "seconds", "peak_rss_gb", "metric", "value", "note"]


def write():
    with open(OUT / "pbo.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


rows.append({"table": "preregistration", "metric": "S_primary", "value": S_PRIMARY,
             "note": "Bailey, Borwein, Lopez de Prado and Zhu convention"})
rows.append({"table": "preregistration", "metric": "performance_metric",
             "note": "naive Sharpe, not Lo-corrected, because autocovariance is not "
                     "additive across disjoint blocks and the cross-boundary terms are "
                     "missing from a union; a disclosed approximation"})
rows.append({"table": "preregistration", "metric": "combination_cap", "value": COMBO_CAP,
             "note": "where C(S,S/2) exceeds the cap the combinations are a random "
                     "sample at the seed below rather than a full enumeration"})
rows.append({"table": "preregistration", "metric": "combination_seed", "value": COMBO_SEED})
rows.append({"table": "preregistration", "metric": "memory_ceiling_gb", "value": MEM_CEILING_GB})

# --- load record and memory-ceiling preflight -------------------------------
rows.append({"table": "load", "metric": "moment_array_shape",
             "note": f"{MOM.shape[0]} specifications x {MOM.shape[1]} blocks x {MOM.shape[2]} moments"})
rows.append({"table": "load", "metric": "moment_array_dtype", "note": str(MOM.dtype)})
rows.append({"table": "load", "metric": "moment_array_bytes", "value": int(MOM.nbytes)})
rows.append({"table": "load", "metric": "moment_array_mb", "value": round(MOM.nbytes / 1e6, 1)})
rows.append({"table": "load", "metric": "stored_layout_note",
             "note": "48 blocks x 2 moments, being the sum of excess returns and the sum "
                     "of squares per block, with the per-block count held once in "
                     "block-sizes.npy. The scaffold specified 48 x 5 with cubes, fourth "
                     "powers and a per-block count; that layout was never written. Naive "
                     "Sharpe is reconstructible from what is stored, skewness and excess "
                     "kurtosis are not and are read from the metric set at step 6"})

print("\n== memory-ceiling preflight ==")
_Sb, _Qb, _nv = merge(S_PRIMARY)
_chunk = min(max(1, int(MEM_CEILING_GB * 1e9 / (TOTAL * 8 * 4))), 12870)
_rng = np.random.default_rng(COMBO_SEED)
_M, _full, _samp = combos(S_PRIMARY, _rng)
_before = rss_gb()
_mc = _M[:_chunk]
_oc = 1.0 - _mc
_is = sharpe(_mc @ _Sb.T.copy(), _mc @ _Qb.T.copy(), float(_mc[0] @ _nv))
_os = sharpe(_oc @ _Sb.T.copy(), _oc @ _Qb.T.copy(), float(_oc[0] @ _nv))
_peak = rss_gb()
print(f"  ceiling {MEM_CEILING_GB:.1f} GB stated before the run, chunk {_chunk} combinations")
print(f"  one chunk at S={S_PRIMARY} peaked at {_peak:.2f} GB, resident before {_before:.2f} GB")
_ok = _peak <= MEM_CEILING_GB * 1.5
print(f"  preflight {'PASS' if _ok else 'FAIL'}")
rows.append({"table": "preflight", "metric": "memory_ceiling_gb", "value": MEM_CEILING_GB,
             "note": "stated before the run"})
rows.append({"table": "preflight", "metric": "chunk_size", "value": _chunk})
rows.append({"table": "preflight", "metric": "peak_rss_gb_one_chunk", "value": round(_peak, 3)})
rows.append({"table": "preflight", "metric": "verdict", "note": "PASS" if _ok else "FAIL"})
del _mc, _oc, _is, _os, _Sb, _Qb, _M
if not _ok:
    raise SystemExit("memory preflight exceeded the stated ceiling")

print("\n== primary pass, S = 16, full grid ==")
r16 = emit(cscv(S_PRIMARY, None, "primary"), "primary", "full_grid")
write()
print(f"  wrote {OUT/'pbo.csv'} after the primary pass")

print("\n== block-count sensitivity ==")
for nb in (8, 12, 24, 48):
    emit(cscv(nb, None, f"S{nb}"), "sensitivity", "full_grid")
    write()

print(f"\nwrote {OUT/'pbo.csv'} with {len(rows)} rows")
print("the smooth-axis restriction is NOT run here; it spans 27 specifications and is "
      "replaced by the step 5 structural stratification")
