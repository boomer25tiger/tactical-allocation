"""Session 21 phases E and F."""
from __future__ import annotations
import csv, math, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
import scripts.s17_common as S      # noqa: E402
import scripts.s17_grid_worker as W  # noqa: E402
OUT = ROOT / "outputs" / "session-21"
EULER = 0.5772156649015329
t0 = time.time()


def ncdf(x): return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))
def nppf(p):
    a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,
       1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00]
    b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,
       6.680131188771972e+01,-1.328068155288572e+01]
    c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,
       -2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00]
    d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,3.754408661907416e+00]
    pl,ph=0.02425,1-0.02425
    if p<pl:
        q=math.sqrt(-2*math.log(p))
        x=(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p>ph:
        q=math.sqrt(-2*math.log(1-p))
        x=-(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    else:
        q=p-0.5; r=q*q
        x=(((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    e=ncdf(x)-p; u=e*math.sqrt(2*math.pi)*math.exp(x*x/2)
    return x-u/(1+x*u/2)
def emax_z(n): return (1.0-EULER)*nppf(1.0-1.0/n)+EULER*nppf(1.0-1.0/(n*math.e))

# ============================ PHASE E ======================================
rows = []
met = np.concatenate([np.fromfile(ROOT/f"outputs/session-17/grid/metrics-{k:02d}.f64",
                                  dtype=np.float64).reshape(-1, W.N_MET) for k in range(8)])
met = met[np.argsort(met[:,0].astype(np.int64))]
base = 1+len(S.AXES)
nv = met[:, base+W.METRIC_ORDER.index("sharpe_naive")]
lo = met[:, base+W.METRIC_ORDER.index("sharpe_lo")]
canon = S.index_of(S.canonical_values()); best = int(np.argmax(nv))
rows.append({"table":"grounds","item":"deflated_sharpe_removed",
             "note":"The deflated Sharpe assumes every trial has true Sharpe zero while "
                    "the grid's cross-sectional naive mean is 0.6199013071365644, so the "
                    "null is misspecified at every N. The incoherence is visible at the "
                    "participation-ratio count, where session 20 reported an expected "
                    "maximum of 0.4285 that falls below the mean of the draws it "
                    "maximises over. Removed on the misspecified null rather than on an "
                    "unfavourable result. Effective N is retained as its own finding, "
                    "since it is the reason for the removal"})
rows.append({"table":"method","item":"recentring",
             "note":"the comparison is against the grid's own cross-sectional "
                    "distribution rather than against a zero-Sharpe null"})
for nm, arr in (("sharpe_naive", nv), ("sharpe_lo", lo)):
    mu, sd = float(arr.mean()), float(arr.std(ddof=1))
    for lab, i in (("canonical", canon), ("in_sample_best", best)):
        z = (float(arr[i])-mu)/sd
        pct = float((arr <= arr[i]).mean()*100.0)
        rows += [{"table":"recentred","item":f"{lab}_{nm}_value","value":float(arr[i])},
                 {"table":"recentred","item":f"{lab}_{nm}_z_from_grid_mean","value":z},
                 {"table":"recentred","item":f"{lab}_{nm}_percentile","value":pct},
                 {"table":"recentred","item":f"{lab}_{nm}_rank",
                  "value":int((arr > arr[i]).sum())+1}]
    rows += [{"table":"recentred","item":f"grid_{nm}_mean","value":mu},
             {"table":"recentred","item":f"grid_{nm}_sd","value":sd}]
print(f"E canonical naive z {(nv[canon]-nv.mean())/nv.std(ddof=1):.4f}, "
      f"percentile {(nv<=nv[canon]).mean()*100:.2f}")

en = list(csv.DictReader(open(ROOT/"outputs/session-20/effective-n.csv")))
def eff(nm): return float([r["in_N"] for r in en if r["table"]=="effective_n"
                           and r["axis"]==nm][0])
PR, VT, SE = eff("participation_ratio"), eff("variance_threshold_95"), eff("spectral_entropy")
rows.append({"table":"correlation_method","item":"method_1_empirical",
             "note":"the grid's own empirical distribution already embeds the "
                    "correlation among specifications, so the percentile needs no "
                    "adjustment. This method makes no independence assumption at all"})
rows.append({"table":"correlation_method","item":"method_2_effective_count",
             "note":"compare the canonical's z against the expected maximum z of that "
                    "many independent standard normal draws, using session 20's "
                    "effective counts from the subsample eigenvalue spectrum"})
z_can = (float(nv[canon])-float(nv.mean()))/float(nv.std(ddof=1))
z_best = (float(nv[best])-float(nv.mean()))/float(nv.std(ddof=1))
for nm, n in (("participation_ratio",PR),("spectral_entropy",SE),
              ("variance_threshold_95",VT),("nominal_121500",float(len(nv)))):
    ez = emax_z(max(n,2.0))
    rows += [{"table":"expected_max","item":f"{nm}_effective_count","value":n},
             {"table":"expected_max","item":f"{nm}_expected_max_z","value":ez},
             {"table":"expected_max","item":f"{nm}_canonical_exceeds",
              "value":int(z_can>ez)},
             {"table":"expected_max","item":f"{nm}_in_sample_best_exceeds",
              "value":int(z_best>ez)}]
    print(f"  N_eff {nm} {n:.2f}: expected max z {ez:.4f}, canonical z {z_can:.4f} "
          f"{'exceeds' if z_can>ez else 'does not exceed'}")
with open(OUT/"recentred-comparison.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","item","value","note"],extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'recentred-comparison.csv'} with {len(rows)} rows")

# ============================ PHASE F ======================================
fr = []
cs = pd.read_csv(ROOT/"outputs/session-20/rebuilt/cost-sweep-designated.csv")
bps = sorted(cs.slippage_bp.dropna().unique())
fr.append({"table":"F1","item":"sweep_range_bp","note":f"{min(bps):g} to {max(bps):g}",
           "value":len(bps)})
lad = pd.read_csv(ROOT/"outputs/session-20/rebuilt/metrics-full.csv")
lad = lad[(lad.table=="metrics")&(lad.panel=="realized")&(lad.convention=="o2o")
          &(lad.window=="primary")].set_index("line")
strat = cs[(cs.slippage_bp.notna())&(cs.line.astype(str).str.contains("STRATEGY",na=False))]
if not len(strat):
    strat = cs[cs.slippage_bp.notna()].copy()
for metric in ("sharpe_lo","sharpe_naive"):
    ser = strat.groupby("slippage_bp")[metric].first().sort_index()
    for line in lad.index:
        if line == "STRATEGY":
            continue
        tgt = float(lad.loc[line, metric])
        cross, inside = None, None
        xs = ser.index.to_numpy(); ys = ser.to_numpy()
        for i in range(1, len(xs)):
            if (ys[i-1]-tgt)*(ys[i]-tgt) <= 0 and ys[i-1] != ys[i]:
                cross = float(xs[i-1]+(tgt-ys[i-1])*(xs[i]-xs[i-1])/(ys[i]-ys[i-1]))
                inside = True; break
        if cross is None:
            cross = float("nan"); inside = False
        fr.append({"table":"F1","item":f"{line}|{metric}","value":cross,
                   "note":"inside the swept range" if inside else
                          "no crossing inside the swept range, so any figure would be an "
                          "extrapolation"})
qq = [r for r in fr if r["item"].startswith("buy_hold_QQQ|sharpe_lo")]
print(f"\nF1 crossings computed over {len(bps)} sweep points "
      f"{min(bps):g} to {max(bps):g} bp")

loo_files = sorted(ROOT.glob("outputs/*/leave-one-out.csv")) + \
            sorted(ROOT.glob("outputs/*/loo-*.csv"))
fr.append({"table":"F2","item":"files","note":" ".join(str(f.relative_to(ROOT)) for f in loo_files)})
fr.append({"table":"F2","item":"rebuilt_in_session_20",
           "value":int(any((ROOT/"outputs/session-20/rebuilt"/f.name).exists() for f in loo_files)),
           "note":"phase C of session 20 rebuilt s14_ladder, s14_nulls, s15_metrics and "
                  "s15_rest only, so the leave-one-out artifacts were NOT rebuilt and "
                  "carry the superseded boundary"})
for f in loo_files:
    try:
        d = pd.read_csv(f)
    except Exception:
        continue
    if "n_estimates" in d.columns and d.n_estimates.notna().any():
        fr.append({"table":"F2","item":f"{f.name}|n_estimates",
                   "value":float(d.n_estimates.dropna().iloc[0])})
    if "sharpe_lo" in d.columns and d.sharpe_lo.notna().any():
        v = d.sharpe_lo.dropna()
        fr.append({"table":"F2","item":f"{f.name}|sharpe_lo_range",
                   "note":f"{v.min():.4f} to {v.max():.4f}", "value":len(v)})
    if "n_sessions" in d.columns and d.n_sessions.notna().any():
        fr.append({"table":"F2","item":f"{f.name}|n_sessions_values",
                   "note":" ".join(map(str, sorted(set(d.n_sessions.dropna().astype(int)))))})
fr.append({"table":"F2","item":"1.5636_agreement",
           "note":"the 2011 leave-one-out estimate and the 2012-start strip arm both "
                  "read 1.5636. They are computed differently, since a leave-one-out "
                  "drops one calendar year from the return series while a strip arm "
                  "starts the window later and keeps every subsequent year, so the "
                  "agreement at four decimals is coincidental rather than structural"})

ax = pd.read_csv(ROOT/"outputs/session-17/axis-adoption.csv")
tot = ax[ax.table=="totals"].set_index("axis")["cardinality"].to_dict()
fr.append({"table":"F3","item":"18225_times_15",
           "value":18225*15,
           "note":"18,225 times 15 is 273,375, the v1/v2 total. With N corrected to "
                  "121,500 that arithmetic still describes the historical reconciliation "
                  "of the enumerated space and no longer describes N"})
for k,v in tot.items():
    fr.append({"table":"F3","item":k,"value":float(v)})
fr.append({"table":"F3","item":"what_each_total_now_refers_to",
           "note":"273,375 is the superseded v1/v2 enumerated space, 364,500 is the "
                  "current enumerated space across ten axes, and 121,500 is both the "
                  "evaluated count and, since session 20, N"})

for lbl, p in (("original", ROOT/"outputs/session-14/nulls.csv"),
               ("rebuilt", ROOT/"outputs/session-20/rebuilt/nulls.csv")):
    d = pd.read_csv(p); nd = d[d.table=="null_distribution"]
    des = nd[(nd.convention=="o2o")&(nd.window=="primary")]
    for _, r in des.iterrows():
        n = float(r.n_draws)
        for col, lab in (("p_value_ann_one_sided","annualised return"),
                         ("p_value_sharpe_one_sided","Lo-corrected Sharpe")):
            pv = float(r[col])
            fr.append({"table":"F4","item":f"{lbl}|{r['null']}|{lab}","value":pv,
                       "note":f"{int(round(pv*n))} exceedances of {int(n)} draws"})
fr.append({"table":"F4","item":"gate_defect",
           "note":"clearing p below 0.001 at 1,000 draws requires zero exceedances, so "
                  "the gate turns on a single draw. The session 20 gate specification "
                  "carries that defect and the gate outcome is unresolved rather than "
                  "settled. No null is re-run in this session"})

ja = list(csv.DictReader(open(ROOT/"outputs/session-20/jan2013-attribution.csv")))
wins = [(r["date"], r["item"], float(r["contribution"])) for r in ja
        if r["table"]=="drawdown_window"]
env = C.build_env(verbose=False)
cal = env["cal"]
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
r_all = acc["daily"]["ret"].loc[acc["daily"].index >= C.PRIMARY_START].dropna()
g = (1.0+r_all).values; idx = r_all.index; Wd = 14
cw = np.array([np.prod(g[i:i+Wd])-1.0 for i in range(len(g)-Wd+1)])
hits = [(i, cw[i]) for i in range(len(cw)) if cw[i] < -0.15]
hits.sort(key=lambda t: t[1])
chosen, used = [], set()
for i, v in hits:
    if any(j in used for j in range(i, i+Wd)):
        continue
    chosen.append((i, v)); used |= set(range(i, i+Wd))
chosen.sort(key=lambda t: t[1])
jan_rank = None
for k, (i, v) in enumerate(chosen, 1):
    a, b = idx[i], idx[i+Wd-1]
    if a <= pd.Timestamp("2013-01-22") and b >= pd.Timestamp("2013-01-02"):
        jan_rank = k
fr += [{"table":"F5","item":"overlapping_windows_below_threshold","value":len(hits)},
       {"table":"F5","item":"distinct_non_overlapping_episodes","value":len(chosen),
        "note":"greedy selection taking the most negative window first and excluding "
               "any window sharing a session with one already chosen"},
       {"table":"F5","item":"january_2013_rank_among_episodes","value":jan_rank}]
for k,(i,v) in enumerate(chosen[:8],1):
    fr.append({"table":"F5_episode","item":f"{idx[i].date()}|{idx[i+Wd-1].date()}",
               "value":float(v),"note":f"rank {k}"})
print(f"F5 {len(hits)} overlapping windows collapse to {len(chosen)} distinct episodes, "
      f"January 2013 ranks {jan_rank}")
with open(OUT/"reads.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","item","value","note"],extrasaction="ignore")
    w.writeheader(); w.writerows(fr)
print(f"wrote {OUT/'reads.csv'} with {len(fr)} rows")
print(f"phases E and F {time.time()-t0:.1f}s")
