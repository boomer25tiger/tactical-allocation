"""M1 final. Positive control at session 19's chunk, then the mechanical null.

POSITIVE CONTROL CHUNK, stated before running. The chunk is pinned to 514,
the value session 19 used, rather than derived from a ceiling. That is
required rather than cosmetic, because scripts/s19_step4.py line 143 computes
n_is = float(mc[0] @ nvec), taking the in-sample session count from the first
combination of each chunk. The chunk boundaries therefore enter the emitted
figures and reproducing them requires reproducing the chunk. The chunk is a
harness parameter and not a measurement parameter, and it is stated here
rather than hidden.

TOLERANCES AND SEEDS, FIXED BEFORE THE COMPARISONS THEY GOVERN.
  TOL_PC    = 1e-12 absolute on the four positive-control figures, read from
              outputs/session-19/pbo.csv rather than hardcoded.
  TOL_MARG  = 1e-10 absolute on the full-window naive Sharpe before against
              after permutation.
  NULL_SEED = 20260822, fixed before drawing. Replication r draws NULL_SEED+r.
  MEM_CEILING_GB = 4.0. Two earlier attempts at 5.0 and 2.0 drove the machine
              into swap and were killed; both are recorded in the report.

NULL COUNT. The null uses the EXACT per-combination and per-specification
session count, since permuting blocks makes the merged counts specification
dependent. The observed comparator is therefore the exact-count slope from
outputs/session-19_6/m1-nis-correction.csv, and the emitted slope is carried
alongside it.
"""
from __future__ import annotations
import csv, itertools, json, math, resource, sys, time
from pathlib import Path
import numpy as np

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S      # noqa: E402

G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-19_6"
TOL_PC, TOL_MARG, NULL_SEED, MEM_CEILING_GB = 1e-12, 1e-10, 20260822, 4.0
PC_CHUNK, NULL_CHUNK = 514, 257
NBLK, NSHARD, S_PRIMARY = 48, 8, 16
TOTAL = S.grid_size(); ANN = math.sqrt(252.0)
WALL_BUDGET_S = 1800.0
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


TARGET = {}
for r in csv.DictReader(open(ROOT / "outputs/session-19/pbo.csv")):
    if (r["table"] == "pbo" and r["S"] == "16" and r["pass_label"] == "primary"
            and r["restriction"] == "full_grid"
            and r["metric"] in ("pbo", "degradation_slope", "degradation_intercept",
                                "degradation_r_squared")):
        TARGET[r["metric"]] = float(r["value"])
EXACT = {}
for r in csv.DictReader(open(OUT / "m1-nis-correction.csv")):
    if r["table"] == "correction":
        EXACT[r["metric"]] = float(r["value"])

raw = np.concatenate([np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64
                                  ).reshape(-1, 2 * NBLK) for k in range(NSHARD)])
ids = np.concatenate([np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
                      for k in range(NSHARD)])
raw = np.ascontiguousarray(raw[np.argsort(ids)])
MOM = raw.reshape(TOTAL, NBLK, 2)
BLK = np.load(G / "block-sizes.npy").astype(np.float64)
del raw
g = NBLK // S_PRIMARY
half = S_PRIMARY // 2
NCOMB = math.comb(S_PRIMARY, half)
M = np.zeros((NCOMB, S_PRIMARY))
for i, c in enumerate(itertools.combinations(range(S_PRIMARY), half)):
    M[i, list(c)] = 1.0
add("setup", item="n_combinations", value=NCOMB, note="full enumeration of C(16,8)")
add("setup", item="n_specifications", value=TOTAL, note="from src/config.py via s17_common")
add("setup", item="pc_chunk", value=PC_CHUNK, note="pinned to session 19's value")
add("setup", item="null_chunk", value=NULL_CHUNK)
add("setup", item="mem_ceiling_gb", value=MEM_CEILING_GB, note="stated before running")
add("setup", item="null_seed", value=NULL_SEED, note="fixed before drawing")
add("setup", item="wall_budget_seconds", value=WALL_BUDGET_S,
    note="stated before choosing the replication count")


def sharpe(s_, q_, n_):
    mean = s_ / n_
    var = (q_ - s_ * s_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


def cscv(Sb, Qb, nvec, chunk, label):
    per_spec = nvec.ndim == 2
    SbT, QbT = Sb.T.copy(), Qb.T.copy()
    NbT = nvec.T.copy() if per_spec else None
    is_s, os_s, rk = [], [], []
    t = time.time()
    for a in range(0, NCOMB, chunk):
        mc = M[a:a + chunk]; oc = 1.0 - mc
        if per_spec:
            ni, no = mc @ NbT, oc @ NbT
        else:
            ni, no = float(mc[0] @ nvec), float(oc[0] @ nvec)
        ish = sharpe(mc @ SbT, mc @ QbT, ni)
        osh = sharpe(oc @ SbT, oc @ QbT, no)
        b = np.argmax(ish, axis=1); r = np.arange(len(b))
        is_s.append(ish[r, b]); sel = osh[r, b]; os_s.append(sel)
        rk.append((osh < sel[:, None]).sum(axis=1) + 1)
        del ish, osh
    el = time.time() - t
    is_s = np.concatenate(is_s); os_s = np.concatenate(os_s); rk = np.concatenate(rk)
    om = rk / (TOTAL + 1.0)
    sl, ic = np.polyfit(is_s, os_s, 1)
    pr = sl * is_s + ic
    r2 = 1 - float(((os_s - pr) ** 2).sum()) / float(((os_s - os_s.mean()) ** 2).sum())
    print(f"  [{label}] {el:.1f}s peak {rss():.2f}GB PBO={float((np.log(om/(1-om))<0).mean()):.6f} "
          f"slope={sl:.6f}", flush=True)
    return dict(pbo=float((np.log(om / (1 - om)) < 0).mean()), slope=float(sl),
                intercept=float(ic), r2=r2, seconds=el, peak=rss())


print("== positive control, chunk pinned to 514 ==", flush=True)
Sb0 = np.ascontiguousarray(MOM[:, :, 0].reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
Qb0 = np.ascontiguousarray(MOM[:, :, 1].reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
nv0 = BLK.reshape(S_PRIMARY, g).sum(axis=1)
obs = cscv(Sb0, Qb0, nv0, PC_CHUNK, "observed")
got = {"pbo": obs["pbo"], "degradation_slope": obs["slope"],
       "degradation_intercept": obs["intercept"], "degradation_r_squared": obs["r2"]}
pc_ok = True
for k, v in got.items():
    gp = abs(v - TARGET[k]); pc_ok &= gp <= TOL_PC
    add("positive_control", item=k, value=v, target=TARGET[k], abs_gap=gp,
        within=int(gp <= TOL_PC))
    print(f"    {k:<24} gap {gp:.3e}")
add("positive_control", item="verdict", note="PASS" if pc_ok else "FAIL")
add("positive_control", item="seconds", value=round(obs["seconds"], 1))
add("positive_control", item="peak_rss_gb", value=round(obs["peak"], 3))
print(f"  positive control {'PASS' if pc_ok else 'FAIL'}", flush=True)
if not pc_ok:
    with open(OUT / "degradation-null.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "target",
                                           "abs_gap", "within", "note"],
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    raise SystemExit("M1 halted")

full_S, full_Q = MOM[:, :, 0].sum(axis=1), MOM[:, :, 1].sum(axis=1)
sh_full = sharpe(full_S.copy(), full_Q.copy(), float(BLK.sum()))


def permuted(rep):
    rng = np.random.default_rng(NULL_SEED + rep)
    perm = np.argsort(rng.random((TOTAL, NBLK)), axis=1)
    Sp = np.take_along_axis(MOM[:, :, 0], perm, axis=1)
    Qp = np.take_along_axis(MOM[:, :, 1], perm, axis=1)
    Np = np.take_along_axis(np.broadcast_to(BLK, (TOTAL, NBLK)), perm, axis=1)
    Sb = np.ascontiguousarray(Sp.reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
    Qb = np.ascontiguousarray(Qp.reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
    Nb = np.ascontiguousarray(Np.reshape(TOTAL, S_PRIMARY, g).sum(axis=2))
    marg = float(np.max(np.abs(sharpe(Sb.sum(1), Qb.sum(1), Nb.sum(1)) - sh_full)))
    del Sp, Qp, Np, perm
    return Sb, Qb, Nb, marg


print("\n== null, pilot replication ==", flush=True)
Sb, Qb, Nb, marg = permuted(0)
add("marginal_control", item="max_abs_sharpe_deviation", value=marg,
    within=int(marg <= TOL_MARG),
    note="full-window naive Sharpe after permutation against before")
add("marginal_control", item="merged_count_min_permuted", value=float(Nb.min()))
add("marginal_control", item="merged_count_max_permuted", value=float(Nb.max()))
print(f"  marginals preserved to {marg:.3e} against {TOL_MARG:g}", flush=True)
reps = [cscv(Sb, Qb, Nb, NULL_CHUNK, "null 0")]
del Sb, Qb, Nb
pilot_s = reps[0]["seconds"]
n_more = max(0, int((WALL_BUDGET_S - pilot_s) // pilot_s))
add("pilot", item="seconds", value=round(pilot_s, 1))
add("pilot", item="slope", value=reps[0]["slope"])
add("pilot", item="intercept", value=reps[0]["intercept"])
add("pilot", item="r_squared", value=reps[0]["r2"])
add("pilot", item="pbo", value=reps[0]["pbo"])
add("replication_count", item="chosen", value=1 + n_more,
    note=f"set by a {WALL_BUDGET_S:.0f} s wall-clock budget divided by the pilot's "
         f"{pilot_s:.1f} s, not by a power calculation")
print(f"\n  pilot {pilot_s:.1f}s -> {1+n_more} replications under a "
      f"{WALL_BUDGET_S:.0f}s budget", flush=True)
for rep in range(1, 1 + n_more):
    Sb, Qb, Nb, mg = permuted(rep)
    reps.append(cscv(Sb, Qb, Nb, NULL_CHUNK, f"null {rep}"))
    del Sb, Qb, Nb

arr = {k: np.array([r[k] for r in reps]) for k in ("slope", "intercept", "r2", "pbo")}
OBSV = {"slope": EXACT["degradation_slope"], "intercept": EXACT["degradation_intercept"],
        "r2": EXACT["degradation_r_squared"], "pbo": EXACT["pbo"]}
EMIT = {"slope": TARGET["degradation_slope"], "intercept": TARGET["degradation_intercept"],
        "r2": TARGET["degradation_r_squared"], "pbo": TARGET["pbo"]}
print(f"\n== null distribution over {len(reps)} replications ==")
for k, a in arr.items():
    m, sd = float(a.mean()), float(a.std(ddof=1)) if len(a) > 1 else float("nan")
    p5, p95 = float(np.percentile(a, 5)), float(np.percentile(a, 95))
    z = (OBSV[k] - m) / sd if sd and not math.isnan(sd) and sd > 0 else float("nan")
    pct = float((a <= OBSV[k]).mean() * 100.0)
    add("null", item=k, value=m, note="mean")
    add("null", item=f"{k}_sd", value=sd)
    add("null", item=f"{k}_p05", value=p5)
    add("null", item=f"{k}_p95", value=p95)
    add("null", item=f"{k}_min", value=float(a.min()))
    add("null", item=f"{k}_max", value=float(a.max()))
    add("observed_vs_null", item=k, value=OBSV[k], target=m, abs_gap=abs(OBSV[k] - m),
        note=f"z {z:.4f}, percentile {pct:.2f}, exact-count observed")
    add("observed_vs_null", item=f"{k}_emitted", value=EMIT[k],
        note="the value in outputs/session-19/pbo.csv, computed with the "
             "first-combination session count")
    print(f"  {k:<10} null mean {m: .6f} sd {sd: .6f} p05 {p5: .6f} p95 {p95: .6f} "
          f"| observed {OBSV[k]: .6f} z {z: .3f} pct {pct:.1f}")
for r in reps:
    add("replication", item=f"rep_{reps.index(r)}", value=r["slope"],
        note=f"intercept {r['intercept']:.10f} r2 {r['r2']:.10f} pbo {r['pbo']:.10f} "
             f"seconds {r['seconds']:.1f}")
slope_mean = float(arr["slope"].mean())
add("verdict", item="null_slope_centred_near_minus_one",
    value=int(abs(slope_mean + 1.0) < 0.10),
    note=f"null mean slope {slope_mean:.6f}; a null slope near -1.0 means the observed "
         f"slope carries little information beyond partition arithmetic, a null slope "
         f"near zero means it measures degradation")
add("resources", item="peak_rss_gb", value=round(max(r["peak"] for r in reps + [obs]), 3))
with open(OUT / "degradation-null.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "target", "abs_gap",
                                       "within", "note"], extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"\nwrote {OUT/'degradation-null.csv'} with {len(rows)} rows")
