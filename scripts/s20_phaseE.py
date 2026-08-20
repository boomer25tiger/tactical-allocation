"""Session 20 phase E. Search-space accounting.

EFFECTIVE-COUNT DEFINITIONS, STATED BEFORE COMPUTING.
  D1 participation ratio, N_eff = (sum lambda)^2 / sum(lambda^2), the standard
     effective number of independent factors in a correlation spectrum.
  D2 variance threshold, the smallest k whose top-k eigenvalues carry at least
     95 percent of total variance.
  D3 spectral entropy, N_eff = exp(-sum p log p) over lambda normalised to sum
     to one.
Reporting three makes the choice visible rather than buried.
"""
from __future__ import annotations
import csv, math, resource, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
import scripts.s17_common as S      # noqa: E402
from src import config              # noqa: E402
OUT = ROOT / "outputs" / "session-20"
S18 = ROOT / "outputs" / "session-18"
t0 = time.time()
ANN = math.sqrt(252.0)
EULER = 0.5772156649015329


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def ncdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


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


def psr(sr_d, star, T, sk, ek):
    den = 1.0 - sk*sr_d + ((ek+3.0)-1.0)/4.0*sr_d**2
    if den <= 0: return float("nan")
    return ncdf((sr_d-star)*math.sqrt(T-1.0)/math.sqrt(den))


def emax(sigma, n):
    return sigma*((1.0-EULER)*nppf(1.0-1.0/n)+EULER*nppf(1.0-1.0/(n*math.e)))


rows = []

# ---- E1, the axis census --------------------------------------------------
ax = list(csv.DictReader(open(ROOT / "outputs/session-17/axis-adoption.csv")))
searched = [r for r in ax if r["table"] == "nine_axis_searched"]
for r in searched:
    rows.append({"table": "census", "axis": r["axis"], "register": r["register_id"],
                 "source": r["source"], "status": "searched",
                 "in_N": 1, "note": f"{r['cardinality']} values"})
rows.append({"table": "census", "axis": "tier_two_offset", "register": "7.4",
             "source": "register 7.4, status informed", "status": "held at canonical",
             "in_N": 0,
             "note": "held at 10 on every specification, no maximum taken across it, so "
                     "it does not enter N"})
CURVE = [("panel","9.11","searched as a reported sensitivity",1),
         ("convention","9.11","searched as a reported sensitivity",1),
         ("window","9.11","searched as a reported sensitivity",1),
         ("commission_arm","9.11","searched as a reported sensitivity",1),
         ("slippage_model","9.11","searched as a reported sensitivity",1),
         ("financing_spread","9.11","assumed, D16 open",0),
         ("smh_accrual","9.11 and 9.8","never varied until phase E2",0),
         ("sizing_mode","9.11","never varied, and unwired, see below",0),
         ("completion_rule","9.11","never varied, provisional rather than closed",0),
         ("starting_nav","D20 session 16","added to the curve, not to the grid",0),
         ("participation_cap","added session 19","ADDED WITHOUT RECORD, see below",0)]
for a, reg, st, inn in CURVE:
    rows.append({"table": "curve_axis", "axis": a, "register": reg, "status": st,
                 "in_N": inn})
rows.append({"table": "discrepancy", "axis": "participation_cap",
             "note": "session 19 added it to the curve axis list without recording the "
                     "addition, giving eleven where 9.11 plus NAV gives ten. Searched as "
                     "a sensitivity, not part of N"})
rows.append({"table": "discrepancy", "axis": "ladder_fourteen_to_twelve",
             "note": "session 14's ladder carried fourteen lines and the twelve-row "
                     "ladder dropped the intraday-only and overnight-only hold "
                     "universes. Recorded nowhere and never run through Romano-Wolf at "
                     "thirteen. Not part of N, since the ladder is a comparison set "
                     "rather than a search"})
rows.append({"table": "discrepancy", "axis": "lo_q",
             "note": "on no axis, a Python default at scripts/s13_backtest.py:609, never "
                     "swept before phase D1. Belongs in N only if the paper reports a "
                     "figure selected across q, which it does not"})
rows.append({"table": "authoritative_count", "axis": "searched_degrees_of_freedom",
             "in_N": len(searched),
             "note": "the nine grid axes are the searched degrees of freedom that enter "
                     "N. The curve axes are reported sensitivities rather than a search "
                     "over which a maximum was taken"})
print(f"E1 authoritative searched degrees of freedom: {len(searched)}")

# ---- E2, sourcing the three open axes ------------------------------------
env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]


def canonical_metrics():
    a = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                       slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
    r = a["daily"]["ret"].loc[a["daily"].index >= C.PRIMARY_START].dropna()
    return L.standalone_metrics(r, a["daily"]["nav"], a["orders"])


base = canonical_metrics()
rows.append({"table": "axis_arm", "axis": "canonical", "status": "reference",
             "ann_return": base["ann_return"], "sharpe_naive": base["sharpe_naive"],
             "sharpe_lo": base["sharpe_lo"]})
print(f"E2 canonical reference ann {base['ann_return']:.6f} lo {base['sharpe_lo']:.6f}")

orig = config.SMH_PRE2013_ACCRUAL_PCT
for arm in config.SMH_ACCRUAL_GRID:
    config.SMH_PRE2013_ACCRUAL_PCT = float(arm)
    e2 = C.build_env(verbose=False)
    s2 = e2["sigs"]["realized"]
    a = bt.run_account(s2["sig"], e2["o2o"], s2["rows"], C.ANCHOR,
                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                       slip_fn=C.slip_class_premium(), cap_fn=e2["cap_fn"])
    r = a["daily"]["ret"].loc[a["daily"].index >= C.PRIMARY_START].dropna()
    m = L.standalone_metrics(r, a["daily"]["nav"], a["orders"])
    rows.append({"table": "axis_arm", "axis": "smh_accrual", "arm": str(arm),
                 "status": "measured", "ann_return": m["ann_return"],
                 "sharpe_naive": m["sharpe_naive"], "sharpe_lo": m["sharpe_lo"],
                 "note": f"SMH_PRE2013_ACCRUAL_PCT {arm}, canonical is {orig}"})
    print(f"  smh_accrual {arm}: ann {m['ann_return']:.6f} lo {m['sharpe_lo']:.6f}")
config.SMH_PRE2013_ACCRUAL_PCT = orig

rows.append({"table": "axis_unsourceable", "axis": "sizing_mode",
             "status": "NOT SOURCED, the axis is unwired",
             "note": "config.SIZING_MODE is defined at src/config.py:78 and validated at "
                     "line 333, but the engine hardcodes math.trunc(alloc / px) at "
                     "scripts/s13_backtest.py:528 and never calls "
                     "src.execution.size_position nor reads config.SIZING_MODE. Setting "
                     "the config to fractional changes nothing in the return-generating "
                     "path, so the axis cannot be measured without a code change, which "
                     "is a specification change rather than a measurement. This is a new "
                     "instance of the phase B3 hardcoded-literal class"})
rows.append({"table": "axis_unsourceable", "axis": "completion_rule",
             "status": "NOT SOURCED, no alternative arm exists",
             "note": "scripts/s13_backtest.py lines 18 to 24 record the unavailable-fill "
                     "completion rule as PROVISIONAL and explicitly not a register "
                     "closure, and no switch implements an alternative. Sourcing it "
                     "requires implementing a second arm, which is a specification "
                     "change rather than a measurement"})
print("E2 sizing_mode and completion_rule NOT SOURCED, both need code changes")

# ---- E3, effective N ------------------------------------------------------
ids = np.load(S18 / "subsample-ids.npy")
ret = np.load(S18 / "subsample-returns.npy").astype(np.float64)
canon = S.index_of(S.canonical_values())
inside = bool(np.isin(canon, ids))
rows.append({"table": "effective_n", "axis": "subsample_size", "in_N": int(len(ids))})
rows.append({"table": "effective_n", "axis": "canonical_in_subsample", "in_N": int(inside),
             "note": "session 19 step 3's positive control"})
print(f"E3 subsample {ret.shape}, canonical inside {inside}")
X = ret - ret.mean(axis=1, keepdims=True)
sd = X.std(axis=1, ddof=1)
keep = sd > 0
X = X[keep] / sd[keep][:, None]
Corr = (X @ X.T) / (X.shape[1] - 1)
lam = np.linalg.eigvalsh(Corr)[::-1]
lam = np.clip(lam, 0, None)
tot = lam.sum()
pr_eff = float(tot**2 / (lam**2).sum())
cum = np.cumsum(lam) / tot
var_eff = int(np.searchsorted(cum, 0.95) + 1)
p = lam / tot; p = p[p > 0]
ent_eff = float(math.exp(-(p * np.log(p)).sum()))
for nm, v, note in (("participation_ratio", pr_eff, "(sum lambda)^2 / sum(lambda^2)"),
                    ("variance_threshold_95", var_eff, "smallest k carrying 95 percent"),
                    ("spectral_entropy", ent_eff, "exp of the spectral entropy")):
    rows.append({"table": "effective_n", "axis": nm, "in_N": v, "note": note})
rows.append({"table": "effective_n", "axis": "top_eigenvalue_share",
             "in_N": float(lam[0] / tot),
             "note": "share of total variance in the first principal component"})
print(f"  participation ratio {pr_eff:.2f}, variance-95 count {var_eff}, "
      f"entropy {ent_eff:.2f}, top eigenvalue share {lam[0]/tot:.4f}")

ds = list(csv.DictReader(open(ROOT / "outputs/session-19/deflated-sharpe.csv")))
def dv(w, m, sm="sharpe_naive"):
    for r in ds:
        if r["table"]=="point" and r["which"]==w and r["metric"]==m and r["sharpe_metric"]==sm:
            return float(r["value"])
def xs(m):
    for r in ds:
        if r["table"]=="cross_section" and r["metric"]==m:
            return float(r["value"])
sigma = xs("sharpe_naive_daily_sd")
T = dv("canonical", "n_sessions")
for nm, n_eff in (("participation_ratio", pr_eff), ("variance_threshold_95", var_eff),
                  ("spectral_entropy", ent_eff), ("preregistered_121500", 121500)):
    star = emax(sigma, max(n_eff, 2.0))
    for which in ("canonical", "in_sample_best"):
        sr = dv(which, "sharpe_annualised"); sk = dv(which, "skewness")
        ek = dv(which, "excess_kurtosis")
        d = psr(sr/ANN, star, T, sk, ek)
        rows.append({"table": "effective_n_deflated", "axis": nm, "arm": which,
                     "in_N": n_eff, "ann_return": star*ANN, "sharpe_naive": sr,
                     "sharpe_lo": d,
                     "note": "expected maximum annualised in ann_return, deflated "
                             "Sharpe in sharpe_lo"})
    print(f"  N_eff {nm} = {n_eff:.2f}: expected max {star*ANN:.4f}, "
          f"canonical DSR {psr(dv('canonical','sharpe_annualised')/ANN, star, T, dv('canonical','skewness'), dv('canonical','excess_kurtosis')):.6f}")
rows.append({"table": "effective_n_disclosure", "axis": "9.10",
             "note": "recorded as a disclosed post-hoc sensitivity. The motivation is "
                     "that the pre-registered N returned a deflated Sharpe near zero and "
                     "the independence assumption underlying the expected maximum is "
                     "violated by construction, since specifications sharing eight of "
                     "nine axis values share most of their return path. Primary remains "
                     "N equal to 121,500"})

with open(OUT / "axis-census.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table","axis","register","source","status",
                                        "in_N","note"], extrasaction="ignore")
    wr.writeheader(); wr.writerows([r for r in rows if r["table"] in
                                    ("census","curve_axis","discrepancy","authoritative_count")])
with open(OUT / "axes-sourced.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table","axis","arm","status","ann_return",
                                        "sharpe_naive","sharpe_lo","note"],
                        extrasaction="ignore")
    wr.writeheader(); wr.writerows([r for r in rows if r["table"] in
                                    ("axis_arm","axis_unsourceable")])
with open(OUT / "effective-n.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table","axis","arm","in_N","ann_return",
                                        "sharpe_naive","sharpe_lo","note"],
                        extrasaction="ignore")
    wr.writeheader(); wr.writerows([r for r in rows if r["table"].startswith("effective_n")])
print(f"\nphase E peak {rss():.3f} GB, {time.time()-t0:.1f}s")
