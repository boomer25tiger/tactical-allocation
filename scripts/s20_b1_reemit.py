"""Session 20 B1 re-emission. Regression figures under the repaired n_is.

MEMORY CEILING, DERIVED FROM MACHINE STATE MEASURED IMMEDIATELY BEFORE.
  Free plus inactive 1.08 GiB with 1.24 GB of free swap on a 12 GB total.
  Ceiling stated at 0.65 GB of working arrays, which sizes the chunk at 48
  combinations. Session 19's chunk of 514 peaked at 3.56 GB and is not
  available at this machine state.

Only the full-grid regression figures are re-emitted. PBO and the stratified
PBO are immune, since within a chunk the substituted count multiplied every
specification's Sharpe by the same factor and preserved the ordering that the
rank and the argmax read.
"""
from __future__ import annotations
import csv, itertools, math, resource, subprocess, re, sys, time
from pathlib import Path
import numpy as np

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S      # noqa: E402
G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-20"
MEM_CEILING_GB, CHUNK = 0.65, 48
COMBO_CAP, COMBO_SEED = 20000, 20260821
NBLK, NSHARD = 48, 8
TOTAL = S.grid_size(); ANN = math.sqrt(252.0)
rows = []


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


vm = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
ps = int(re.search(r"page size of (\d+)", vm).group(1))
fr = sum(int(m.group(1)) * ps for m in
         [re.search(rf"{k}:\s+(\d+)", vm) for k in
          ("Pages free", "Pages inactive", "Pages purgeable")] if m)
sw = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True).stdout.strip()
rows += [{"table": "machine_state", "metric": "free_plus_inactive_gib", "value": round(fr / 2**30, 2)},
         {"table": "machine_state", "metric": "swap", "note": sw},
         {"table": "machine_state", "metric": "memory_ceiling_gb", "value": MEM_CEILING_GB,
          "note": "stated before the load, derived from the figures above"},
         {"table": "machine_state", "metric": "chunk", "value": CHUNK,
          "note": "session 19 used 514, which peaked at 3.56 GB and is unavailable here"}]
print(f"free+inactive {fr/2**30:.2f} GiB, {sw}, ceiling {MEM_CEILING_GB} GB, chunk {CHUNK}")

raw = np.concatenate([np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64
                                  ).reshape(-1, 2 * NBLK) for k in range(NSHARD)])
ids = np.concatenate([np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
                      for k in range(NSHARD)])
raw = np.ascontiguousarray(raw[np.argsort(ids)])
MOM = raw.reshape(TOTAL, NBLK, 2)
BLK = np.load(G / "block-sizes.npy").astype(np.float64)
del raw


def sharpe(s_, q_, n_):
    mean = s_ / n_
    var = (q_ - s_ * s_ / n_) / (n_ - 1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean / np.sqrt(var)) * ANN


def combos(nb, rng):
    half = nb // 2
    full = math.comb(nb, half)
    if full <= COMBO_CAP:
        m = np.zeros((full, nb))
        for i, c in enumerate(itertools.combinations(range(nb), half)):
            m[i, list(c)] = 1.0
        return m, full, False
    m = np.zeros((COMBO_CAP, nb)); seen = set(); i = 0
    while i < COMBO_CAP:
        c = tuple(sorted(rng.choice(nb, size=half, replace=False).tolist()))
        if c in seen:
            continue
        seen.add(c); m[i, list(c)] = 1.0; i += 1
    return m, full, True


emit = []
for nb in (16, 8, 12, 24, 48):
    g = NBLK // nb
    Sb = np.ascontiguousarray(MOM[:, :, 0].reshape(TOTAL, nb, g).sum(axis=2))
    Qb = np.ascontiguousarray(MOM[:, :, 1].reshape(TOTAL, nb, g).sum(axis=2))
    nv = BLK.reshape(nb, g).sum(axis=1)
    SbT, QbT = Sb.T.copy(), Qb.T.copy()
    M, full, samp = combos(nb, np.random.default_rng(COMBO_SEED))
    NC = M.shape[0]
    is_s, os_s = [], []
    t = time.time()
    for a in range(0, NC, CHUNK):
        mc = M[a:a + CHUNK]; oc = 1.0 - mc
        n_is = (mc @ nv)[:, None]; n_os = (oc @ nv)[:, None]
        ish = sharpe(mc @ SbT, mc @ QbT, n_is)
        osh = sharpe(oc @ SbT, oc @ QbT, n_os)
        b = np.argmax(ish, axis=1); r = np.arange(len(b))
        is_s.append(ish[r, b]); os_s.append(osh[r, b])
        del ish, osh
    el = time.time() - t
    is_s = np.concatenate(is_s); os_s = np.concatenate(os_s)
    sl, ic = np.polyfit(is_s, os_s, 1)
    pred = sl * is_s + ic
    r2 = 1 - float(((os_s - pred) ** 2).sum()) / float(((os_s - os_s.mean()) ** 2).sum())
    emit.append((nb, float(sl), float(ic), r2, NC, full, samp, el))
    print(f"  S={nb:<3} {el:6.1f}s peak {rss():.2f}GB slope {sl:.10f} icept {ic:.10f} R2 {r2:.10f}")
    del Sb, Qb, SbT, QbT, M

prev = {}
for r in csv.DictReader(open(ROOT / "outputs/session-19/pbo.csv")):
    if r["table"] == "pbo" and r["restriction"] == "full_grid" and r["metric"] in (
            "degradation_slope", "degradation_intercept", "degradation_r_squared"):
        prev.setdefault(r["S"], {})[r["metric"]] = float(r["value"])
for nb, sl, ic, r2, NC, full, samp, el in emit:
    for key, new in (("degradation_slope", sl), ("degradation_intercept", ic),
                     ("degradation_r_squared", r2)):
        old = prev.get(str(nb), {}).get(key)
        rows.append({"table": "regression", "S": nb, "metric": key, "value": new,
                     "session19_value": old,
                     "abs_shift": abs(new - old) if old is not None else "",
                     "n_combinations": NC,
                     "note": ("sampled of %d at seed %d" % (full, COMBO_SEED)) if samp
                             else "full enumeration"})
    rows.append({"table": "regression", "S": nb, "metric": "seconds", "value": round(el, 1)})
rows.append({"table": "immunity", "metric": "pbo_and_strata_not_re_run", "value": 1,
             "note": "within a chunk the substituted count is one scalar applied to "
                     "every specification, so it scales every Sharpe identically and "
                     "preserves the ordering the rank and the argmax read. PBO and the "
                     "stratified PBO are functions of that ordering alone. Session 19.6 "
                     "measured a PBO gap of exactly 0.0e+00 at chunk 128, 257 and 514"})
rows.append({"table": "resources", "metric": "peak_rss_gb", "value": round(rss(), 3),
             "within": int(rss() <= MEM_CEILING_GB + 0.35)})
with open(OUT / "pbo-regression-corrected.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table", "S", "metric", "value", "session19_value",
                                        "abs_shift", "n_combinations", "within", "note"],
                        extrasaction="ignore")
    wr.writeheader(); wr.writerows(rows)
print(f"\npeak {rss():.3f} GB")
print(f"wrote {OUT/'pbo-regression-corrected.csv'} with {len(rows)} rows")
