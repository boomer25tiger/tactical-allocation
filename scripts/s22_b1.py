"""Session 22 phase F payload, launched by phase A as the relaunch test.

Re-emits the three regression figures at every S session 19 ran, under the
per-combination session count the session 20 B1 repair installed. Chunk is
taken from argv so the relaunch test controls it.
"""
from __future__ import annotations
import csv, itertools, math, resource, sys, time
from pathlib import Path
import numpy as np
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S      # noqa: E402
G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-22"
CHUNK = int(sys.argv[1])
COMBO_CAP, COMBO_SEED, NBLK, NSHARD = 20000, 20260821, 48, 8
TOTAL = S.grid_size(); ANN = math.sqrt(252.0)

raw = np.concatenate([np.fromfile(G/f"moments-{k:02d}.f64", dtype=np.float64
                                  ).reshape(-1, 2*NBLK) for k in range(NSHARD)])
ids = np.concatenate([np.fromfile(G/f"index-{k:02d}.i64", dtype=np.int64)
                      for k in range(NSHARD)])
raw = np.ascontiguousarray(raw[np.argsort(ids)])
MOM = raw.reshape(TOTAL, NBLK, 2)
BLK = np.load(G/"block-sizes.npy").astype(np.float64)
del raw
print(f"loaded {MOM.shape} chunk {CHUNK}", flush=True)


def sharpe(s_, q_, n_):
    mean = s_/n_
    var = (q_ - s_*s_/n_)/(n_-1.0)
    np.maximum(var, 1e-300, out=var)
    return (mean/np.sqrt(var))*ANN


def combos(nb, rng):
    half = nb//2; full = math.comb(nb, half)
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


def one(nb, Sb, Qb, nv, per_spec):
    SbT, QbT = Sb.T.copy(), Qb.T.copy()
    M, full, samp = combos(nb, np.random.default_rng(COMBO_SEED))
    NC = M.shape[0]; is_s, os_s, rk = [], [], []
    for a in range(0, NC, CHUNK):
        mc = M[a:a+CHUNK]; oc = 1.0-mc
        if per_spec:
            n_is = (mc @ nv)[:, None]; n_os = (oc @ nv)[:, None]
        else:
            n_is = float(mc[0] @ nv); n_os = float(oc[0] @ nv)
        ish = sharpe(mc @ SbT, mc @ QbT, n_is)
        osh = sharpe(oc @ SbT, oc @ QbT, n_os)
        b = np.argmax(ish, axis=1); r = np.arange(len(b))
        is_s.append(ish[r, b]); sel = osh[r, b]; os_s.append(sel)
        rk.append((osh < sel[:, None]).sum(axis=1)+1)
        del ish, osh
    is_s = np.concatenate(is_s); os_s = np.concatenate(os_s); rk = np.concatenate(rk)
    om = rk/(TOTAL+1.0)
    sl, ic = np.polyfit(is_s, os_s, 1)
    pred = sl*is_s+ic
    r2 = 1-float(((os_s-pred)**2).sum())/float(((os_s-os_s.mean())**2).sum())
    return dict(slope=float(sl), intercept=float(ic), r2=r2,
                pbo=float((np.log(om/(1-om)) < 0).mean()), nc=NC, full=full, samp=samp)


rows = []
prev = {}
for r in csv.DictReader(open(ROOT/"outputs/session-19/pbo.csv")):
    if r["table"] == "pbo" and r["restriction"] == "full_grid":
        prev.setdefault(r["S"], {})[r["metric"]] = r["value"]

for nb in (16, 8, 12, 24, 48):
    t = time.time(); g = NBLK//nb
    Sb = np.ascontiguousarray(MOM[:, :, 0].reshape(TOTAL, nb, g).sum(axis=2))
    Qb = np.ascontiguousarray(MOM[:, :, 1].reshape(TOTAL, nb, g).sum(axis=2))
    nv = BLK.reshape(nb, g).sum(axis=1)
    new = one(nb, Sb, Qb, nv, True)
    old = one(nb, Sb, Qb, nv, False)
    el = time.time()-t
    for key, k2 in (("degradation_slope","slope"),("degradation_intercept","intercept"),
                    ("degradation_r_squared","r2"),("pbo","pbo")):
        rows.append({"table":"regression","S":nb,"metric":key,
                     "corrected":new[k2],"as_emitted_recomputed":old[k2],
                     "session19_value":prev.get(str(nb),{}).get(key,""),
                     "shift":abs(new[k2]-old[k2]),
                     "n_combinations":new["nc"],
                     "note":("sampled of %d"%new["full"]) if new["samp"] else "full enumeration"})
    rows.append({"table":"regression","S":nb,"metric":"seconds","corrected":round(el,1)})
    print(f"  S={nb:<3} {el:6.1f}s slope {new['slope']:.10f} vs {old['slope']:.10f} "
          f"shift {abs(new['slope']-old['slope']):.3e} pbo {new['pbo']:.10f}", flush=True)
    del Sb, Qb

rows.append({"table":"resources","metric":"peak_rss_gb",
             "corrected":round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9,3)})
rows.append({"table":"resources","metric":"chunk","corrected":CHUNK})
rows.append({"table":"note","metric":"disposition",
             "note":"the degradation slope is removed from the paper at 9.35 regardless "
                    "of this re-emission, so the correction closes the defect rather "
                    "than restoring a reported figure"})
with open(OUT/"pbo-regression-corrected.csv","w",newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table","S","metric","corrected",
                                       "as_emitted_recomputed","session19_value","shift",
                                       "n_combinations","note"], extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'pbo-regression-corrected.csv'} with {len(rows)} rows", flush=True)
