"""Session 19 step 6: the deflated Sharpe.

N. The register's 8.7 amendment at session 16b set N to 131,220 from the
construction-alone axis values. Session 17 adopted the docs/HANDOFF.md
ranges, which carries the enumerated space to 364,500, and evaluated
121,500 of them with the 7.4 tier-two offset held at its canonical value of
10 rather than sampled. N is the size of the search space the study
enumerated rather than the count of points evaluated, so N is 364,500 and
121,500 is the evaluated count. Both are recorded, and the deflated Sharpe
is recomputed at 121,500 as the sensitivity.

METRIC. The probabilistic and deflated Sharpe are defined by Bailey and
Lopez de Prado on the NAIVE Sharpe with an explicit skewness and kurtosis
adjustment. The Lo correction addresses autocorrelation instead, so
substituting it would mix two corrections. The naive Sharpe is primary here
and the same figures computed on the Lo-corrected Sharpe are reported as a
disclosed sensitivity rather than as the headline.

ESTIMATION CAVEAT. The cross-sectional standard deviation of Sharpe enters
the expected maximum under the no-skill null. It is estimated from the
121,500 evaluated specifications, which is a subset of the 364,500
enumerated, so the dispersion of the unevaluated remainder is assumed equal
to the dispersion of the evaluated subset and is not measured.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S           # noqa: E402
import scripts.s17_grid_worker as W      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
S18 = ROOT / "outputs" / "session-18"
OUT = ROOT / "outputs" / "session-19"
OUT.mkdir(parents=True, exist_ok=True)

NSHARD = 8
TOTAL = S.grid_size()
N_ENUMERATED = S.enumerated_size()
ANN = math.sqrt(252.0)
EULER = 0.5772156649015329
rows = []


def ncdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def nppf(p):
    """Inverse standard normal, Acklam's rational approximation refined by
    one Halley step against erf, so the tail values the expected maximum
    needs are accurate at p of order 1 - 1/364500."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    else:
        q = p - 0.5
        r = q * q
        x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    e = ncdf(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def psr(sr_daily, sr_star_daily, T, skew, exkurt):
    """Probabilistic Sharpe. sr in per-period units, T observations,
    exkurt is EXCESS kurtosis so kurtosis is exkurt + 3."""
    denom = 1.0 - skew * sr_daily + ((exkurt + 3.0) - 1.0) / 4.0 * sr_daily ** 2
    if denom <= 0:
        return float("nan"), float("nan")
    z = (sr_daily - sr_star_daily) * math.sqrt(T - 1.0) / math.sqrt(denom)
    return ncdf(z), z


def expected_max_sharpe(sigma_sr_daily, n_trials):
    """Bailey and Lopez de Prado expected maximum Sharpe under a no-skill
    null, in the same per-period units as sigma."""
    a = nppf(1.0 - 1.0 / n_trials)
    b = nppf(1.0 - 1.0 / (n_trials * math.e))
    return sigma_sr_daily * ((1.0 - EULER) * a + EULER * b), a, b


# --- load the metric set ---------------------------------------------------
met = np.concatenate([
    np.fromfile(G / f"metrics-{k:02d}.f64", dtype=np.float64).reshape(-1, W.N_MET)
    for k in range(NSHARD)])
met = met[np.argsort(met[:, 0].astype(np.int64))]
assert np.array_equal(met[:, 0].astype(np.int64), np.arange(TOTAL))
base = 1 + len(S.AXES)


def col(name):
    return met[:, base + W.METRIC_ORDER.index(name)]


sh_naive = col("sharpe_naive")
sh_lo = col("sharpe_lo")
skew_all = col("skewness")
exk_all = col("excess_kurtosis")
nsess_all = col("n_sessions")
ann_ret = col("ann_return")

CANON = S.index_of(S.canonical_values())
BEST = int(np.argmax(sh_naive))
T = float(nsess_all[CANON])
assert float(nsess_all[BEST]) == T, "sample length differs between the two points"

# --- cross-sectional distribution -----------------------------------------
sd_daily = float(np.std(sh_naive / ANN, ddof=1))
rows.append({"table": "cross_section", "metric": "sharpe_naive_ann_mean",
             "value": float(sh_naive.mean())})
rows.append({"table": "cross_section", "metric": "sharpe_naive_ann_sd",
             "value": float(sh_naive.std(ddof=1))})
for q in (5, 50, 95):
    rows.append({"table": "cross_section", "metric": f"sharpe_naive_ann_p{q:02d}",
                 "value": float(np.percentile(sh_naive, q))})
rows.append({"table": "cross_section", "metric": "sharpe_lo_ann_mean",
             "value": float(sh_lo.mean())})
rows.append({"table": "cross_section", "metric": "sharpe_lo_ann_sd",
             "value": float(sh_lo.std(ddof=1))})
for q in (5, 50, 95):
    rows.append({"table": "cross_section", "metric": f"sharpe_lo_ann_p{q:02d}",
                 "value": float(np.percentile(sh_lo, q))})
rows.append({"table": "cross_section", "metric": "sharpe_naive_daily_sd",
             "value": sd_daily,
             "note": "the dispersion the expected maximum uses, estimated from the "
                     "121,500 evaluated specifications; the dispersion of the "
                     "unevaluated remainder of the 364,500 enumerated is assumed "
                     "equal to it and is not measured"})
rows.append({"table": "n", "metric": "n_enumerated", "value": N_ENUMERATED,
             "note": "the search space the study enumerated, ten axes; primary N"})
rows.append({"table": "n", "metric": "n_evaluated", "value": TOTAL,
             "note": "the points the grid evaluated, nine searched axes, with 7.4 "
                     "held at its canonical value of 10 rather than sampled"})
rows.append({"table": "n", "metric": "n_register_8_7_before", "value": 131220,
             "note": "the session 16b amendment, superseded by session 17 adopting "
                     "the HANDOFF ranges"})

print(f"grid {TOTAL:,} evaluated of {N_ENUMERATED:,} enumerated, T={T:.0f} sessions")
print(f"cross-sectional naive Sharpe, annualised: mean {sh_naive.mean():.4f} "
      f"sd {sh_naive.std(ddof=1):.4f} p05 {np.percentile(sh_naive,5):.4f} "
      f"p50 {np.percentile(sh_naive,50):.4f} p95 {np.percentile(sh_naive,95):.4f}")

# --- the two points --------------------------------------------------------
POINTS = [("canonical", CANON, "pre-registered, not selected"),
          ("in_sample_best", BEST, "the grid maximum on the naive Sharpe over the "
                                   "full primary window, a selected point")]

for which, sid, note in POINTS:
    for metric_name, arr in (("sharpe_naive", sh_naive), ("sharpe_lo", sh_lo)):
        sr_ann = float(arr[sid])
        sr_d = sr_ann / ANN
        sk = float(skew_all[sid]); ek = float(exk_all[sid])
        primary = metric_name == "sharpe_naive"
        p0, z0 = psr(sr_d, 0.0, T, sk, ek)
        rows.append({"table": "point", "which": which, "spec_id": sid,
                     "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                     "metric": "sharpe_annualised", "value": sr_ann, "note": note})
        rows.append({"table": "point", "which": which, "spec_id": sid,
                     "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                     "metric": "skewness", "value": sk})
        rows.append({"table": "point", "which": which, "spec_id": sid,
                     "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                     "metric": "excess_kurtosis", "value": ek})
        rows.append({"table": "point", "which": which, "spec_id": sid,
                     "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                     "metric": "n_sessions", "value": T})
        rows.append({"table": "point", "which": which, "spec_id": sid,
                     "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                     "metric": "probabilistic_sharpe_vs_zero", "value": p0,
                     "note": f"z {z0:.4f}; benchmark Sharpe zero"})
        for label, n_tr in (("N_364500", N_ENUMERATED), ("N_121500", TOTAL)):
            sr_star, a, b = expected_max_sharpe(sd_daily, n_tr)
            pd_, zd = psr(sr_d, sr_star, T, sk, ek)
            rows.append({"table": "point", "which": which, "spec_id": sid,
                         "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                         "metric": f"expected_max_sharpe_ann_{label}",
                         "value": sr_star * ANN,
                         "note": f"no-skill null at N={n_tr:,}; z quantiles {a:.4f} and {b:.4f}"})
            rows.append({"table": "point", "which": which, "spec_id": sid,
                         "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                         "metric": f"probabilistic_sharpe_vs_expected_max_{label}",
                         "value": pd_, "note": f"z {zd:.4f}"})
            rows.append({"table": "point", "which": which, "spec_id": sid,
                         "sharpe_metric": metric_name, "is_primary_metric": int(primary),
                         "metric": f"deflated_sharpe_{label}", "value": pd_,
                         "note": "the deflated Sharpe is the probabilistic Sharpe "
                                 "evaluated against the expected maximum under the "
                                 "no-skill null" + (" ; PRIMARY" if primary and label == "N_364500" else "")})
    print(f"{which} spec {sid:,}: naive Sharpe {sh_naive[sid]:.4f} ann, "
          f"skew {skew_all[sid]:.4f}, excess kurtosis {exk_all[sid]:.4f}")

srs, _, _ = expected_max_sharpe(sd_daily, N_ENUMERATED)
srs2, _, _ = expected_max_sharpe(sd_daily, TOTAL)
print(f"expected max Sharpe under the no-skill null, annualised: "
      f"{srs*ANN:.4f} at N=364,500 and {srs2*ANN:.4f} at N=121,500")
for which, sid, _ in POINTS:
    sr_d = float(sh_naive[sid]) / ANN
    p, _ = psr(sr_d, srs, T, float(skew_all[sid]), float(exk_all[sid]))
    print(f"  deflated Sharpe, {which}, naive, N=364,500: {p:.6f}")

rows.append({"table": "definition", "metric": "in_sample_best_rule",
             "note": "argmax of the naive Sharpe across the 121,500 evaluated "
                     "specifications on the full primary window; this is the grid "
                     "maximum rather than the CSCV per-combination selection"})
rows.append({"table": "definition", "metric": "metric_choice",
             "note": "the probabilistic and deflated Sharpe are computed on the naive "
                     "Sharpe as primary, since the formula carries its own skewness and "
                     "kurtosis adjustment while the Lo correction addresses "
                     "autocorrelation; the Lo-corrected figures are reported alongside "
                     "as a disclosed sensitivity"})
rows.append({"table": "canonical_rank", "metric": "sharpe_naive_rank",
             "value": int((sh_naive > sh_naive[CANON]).sum()) + 1,
             "note": f"of {TOTAL:,}, rank 1 is the highest"})
rows.append({"table": "canonical_rank", "metric": "sharpe_lo_rank",
             "value": int((sh_lo > sh_lo[CANON]).sum()) + 1,
             "note": f"of {TOTAL:,}, rank 1 is the highest"})
rows.append({"table": "canonical_rank", "metric": "ann_return_rank",
             "value": int((ann_ret > ann_ret[CANON]).sum()) + 1,
             "note": f"of {TOTAL:,}, rank 1 is the highest"})

COLS = ["table", "which", "spec_id", "sharpe_metric", "is_primary_metric",
        "metric", "value", "note"]
with open(OUT / "deflated-sharpe.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {OUT/'deflated-sharpe.csv'} with {len(rows)} rows")
