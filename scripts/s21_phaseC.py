"""Session 21 phase C. Subsample representativeness.

TESTS AND SEEDS, STATED BEFORE RUNNING.
  PRIMARY, a resampling null. 2,000 random subsets of size equal to the
  subsample's own size are drawn without replacement from the 121,500
  evaluated specifications at RESAMPLE_SEED, and the observed subsample's
  mean naive Sharpe is placed in that distribution. This makes no
  distributional assumption and respects the finite population exactly.
  SECONDARY, a two-sample Kolmogorov-Smirnov statistic against the full
  grid. Its assumptions are independent draws from continuous
  distributions, and BOTH are imperfect here, since the subsample is a
  subset of the population it is compared against and specifications are
  correlated by construction. It is reported as a descriptive distance
  rather than as a test with a valid p value, and that is stated rather
  than left implicit.
  RESAMPLE_SEED = 20260821, fixed before drawing.
  BALANCE_TOL, an axis value is called balanced when its subsample count
  lies inside a 99 percent binomial interval around the expected count.
"""
from __future__ import annotations
import csv, math, resource, subprocess, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S       # noqa: E402
import scripts.s17_grid_worker as W  # noqa: E402
OUT = ROOT / "outputs" / "session-21"; G = ROOT / "outputs" / "session-17" / "grid"
S18 = ROOT / "outputs" / "session-18"
RESAMPLE_SEED, NRESAMPLE = 20260821, 2000
t0 = time.time(); rows = []

vm = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
ps = int(re.search(r"page size of (\d+)", vm).group(1))
fr = sum(int(m.group(1))*ps for m in [re.search(rf"{k}:\s+(\d+)", vm) for k in
        ("Pages free","Pages inactive","Pages purgeable")] if m)
sw = subprocess.run(["sysctl","-n","vm.swapusage"],capture_output=True,text=True).stdout.strip()
CEIL = 0.6
rows += [{"table":"machine","item":"free_plus_inactive_gib","value":round(fr/2**30,2)},
         {"table":"machine","item":"swap","note":sw},
         {"table":"machine","item":"memory_ceiling_gb","value":CEIL,
          "note":"stated before the load. The metric shards total about 70 MB, well "
                 "inside it, so no phase here approaches the constraint"}]
print(f"free+inactive {fr/2**30:.2f} GiB, ceiling {CEIL} GB")

met = np.concatenate([np.fromfile(G/f"metrics-{k:02d}.f64", dtype=np.float64
                                  ).reshape(-1, W.N_MET) for k in range(8)])
met = met[np.argsort(met[:,0].astype(np.int64))]
base = 1 + len(S.AXES)
naive_all = met[:, base + W.METRIC_ORDER.index("sharpe_naive")]
lo_all = met[:, base + W.METRIC_ORDER.index("sharpe_lo")]
axis_vals = met[:, 1:1+len(S.AXES)]
ids = np.load(S18/"subsample-ids.npy")
canon = S.index_of(S.canonical_values())
inside = bool(np.isin(canon, ids))
naive_s, lo_s = naive_all[ids], lo_all[ids]
rows += [{"table":"positive_control","item":"canonical_in_subsample","value":int(inside),
          "note":"reproduces session 19 step 3's control"},
         {"table":"positive_control","item":"subsample_size","value":int(len(ids))},
         {"table":"positive_control","item":"grid_size","value":int(len(naive_all))}]
print(f"subsample {len(ids)} of {len(naive_all)}, canonical inside {inside}")

EMIT_MEAN, EMIT_SD = 0.6199013071365644, 0.45197782372194695
for nm, sub, full in (("sharpe_naive", naive_s, naive_all), ("sharpe_lo", lo_s, lo_all)):
    for lab, arr in (("subsample", sub), ("full_grid", full)):
        rows.append({"table":"distribution","item":f"{nm}_{lab}_mean","value":float(arr.mean())})
        rows.append({"table":"distribution","item":f"{nm}_{lab}_sd","value":float(arr.std(ddof=1))})
        for q in (5,50,95):
            rows.append({"table":"distribution","item":f"{nm}_{lab}_p{q:02d}",
                         "value":float(np.percentile(arr,q))})
rows.append({"table":"reconciliation","item":"full_grid_naive_mean_recomputed",
             "value":float(naive_all.mean()), "target":EMIT_MEAN,
             "abs_gap":abs(float(naive_all.mean())-EMIT_MEAN),
             "note":"against outputs/session-19/deflated-sharpe.csv"})
rows.append({"table":"reconciliation","item":"full_grid_naive_sd_recomputed",
             "value":float(naive_all.std(ddof=1)), "target":EMIT_SD,
             "abs_gap":abs(float(naive_all.std(ddof=1))-EMIT_SD)})
print(f"  naive: subsample mean {naive_s.mean():.6f} sd {naive_s.std(ddof=1):.6f} | "
      f"grid mean {naive_all.mean():.6f} sd {naive_all.std(ddof=1):.6f}")

rng = np.random.default_rng(RESAMPLE_SEED)
means = np.empty(NRESAMPLE)
for i in range(NRESAMPLE):
    means[i] = naive_all[rng.choice(len(naive_all), size=len(ids), replace=False)].mean()
obs = float(naive_s.mean())
pct = float((means <= obs).mean()*100.0)
two_sided = 2*min(pct, 100-pct)/100.0
rows += [{"table":"resampling_null","item":"seed","value":RESAMPLE_SEED,
          "note":"fixed before drawing"},
         {"table":"resampling_null","item":"draws","value":NRESAMPLE},
         {"table":"resampling_null","item":"observed_subsample_mean","value":obs},
         {"table":"resampling_null","item":"null_mean","value":float(means.mean())},
         {"table":"resampling_null","item":"null_sd","value":float(means.std(ddof=1))},
         {"table":"resampling_null","item":"null_p05","value":float(np.percentile(means,5))},
         {"table":"resampling_null","item":"null_p95","value":float(np.percentile(means,95))},
         {"table":"resampling_null","item":"observed_percentile","value":pct},
         {"table":"resampling_null","item":"two_sided_p","value":two_sided,
          "note":"the exact finite-population comparison, no distributional assumption"}]
print(f"  resampling null: observed {obs:.6f} at percentile {pct:.2f}, two-sided p {two_sided:.4f}")

a = np.sort(naive_s); b = np.sort(naive_all)
grid = np.unique(np.concatenate([a,b]))
ks = float(np.max(np.abs(np.searchsorted(a,grid,side="right")/len(a)
                         - np.searchsorted(b,grid,side="right")/len(b))))
rows.append({"table":"ks","item":"statistic","value":ks,
             "note":"descriptive distance only. Both KS assumptions fail here, since the "
                    "subsample is a subset of the population it is compared against and "
                    "specifications are correlated by construction, so no p value is quoted"})
print(f"  KS statistic {ks:.6f}, reported as a distance rather than a test")

nb = 0; nax = 0
for k, axis in enumerate(S.AXIS_NAMES):
    for v in S.AXIS_VALUES[k]:
        exp = len(ids)/len(S.AXIS_VALUES[k])
        got = int((axis_vals[ids,k] == float(v)).sum())
        sd = math.sqrt(exp*(1-1/len(S.AXIS_VALUES[k])))
        z = (got-exp)/sd if sd else 0.0
        ok = abs(z) <= 2.576
        nax += 1; nb += int(ok)
        rows.append({"table":"axis_balance","item":f"{axis}={v}","value":got,
                     "target":exp,"abs_gap":abs(got-exp),
                     "note":f"z {z:+.3f}, balanced {ok}"})
rows.append({"table":"axis_balance_summary","item":"values_balanced","value":nb,
             "target":nax,"note":"inside a 99 percent binomial interval around the "
                                 "expected count under uniform sampling"})
print(f"  axis balance: {nb} of {nax} values inside the 99 percent interval")

representative = (two_sided > 0.05) and (nb == nax) and inside
rows.append({"table":"gate_C","item":"representative","value":int(representative),
             "note":"the resampling null does not reject, every axis value is balanced, "
                    "and the canonical is present" if representative else
                    "at least one condition fails"})
rows.append({"table":"gate_C","item":"verdict",
             "note":"PASS, phase E is licensed" if representative else
                    "HALT before phase E"})
rows.append({"table":"licence","item":"what_this_licenses",
             "note":"a representative subsample licenses session 20's effective-N figures "
                    "and this session's phase E recentred comparison. A non-representative "
                    "one would invalidate both"})
print(f"\ngate C: {'PASS' if representative else 'HALT'}")
with open(OUT/"subsample-representativeness.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","item","value","target","abs_gap","note"],
                     extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'subsample-representativeness.csv'} with {len(rows)} rows")
print(f"phase C peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9:.3f} GB, "
      f"{time.time()-t0:.1f}s")
