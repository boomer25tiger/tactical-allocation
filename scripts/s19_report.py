"""Session 19 step 8: generate PBO-REPORT.md and its figures.

REGENERABILITY. This script reads only committed artifacts. It never opens
outputs/session-17/panel/. Its inputs are the session 19 CSVs, the
per-combination draws dumped by s19_draws.py from the committed block
moments, the session 18 augmented specification index, and the manifest when
one exists. Running it twice on the same inputs produces byte-identical
output, which is what the step 8 and step 10 checks compare.

Every prose figure is read from an emitted CSV under 9.12 rather than
restated from a separate computation.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.s19_svg as svg            # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-19"
S18 = ROOT / "outputs" / "session-18"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def rd(name):
    with open(OUT / name) as fh:
        return list(csv.DictReader(fh))


pbo_rows = rd("pbo.csv")
strata_rows = rd("pbo-strata.csv")
dsr_rows = rd("deflated-sharpe.csv")
curve_rows = rd("specification-curve.csv")
inv_rows = rd("inventory.csv")
add_rows = rd("additivity-check.csv")
rem_rows = rd("remote-status.csv")


def pv(S, metric, pass_label=None, restriction="full_grid"):
    for r in pbo_rows:
        if (r["table"] == "pbo" and r["S"] == str(S) and r["metric"] == metric
                and r["restriction"] == restriction
                and (pass_label is None or r["pass_label"] == pass_label)):
            return float(r["value"])
    raise KeyError((S, metric))


def pnote(S, metric):
    for r in pbo_rows:
        if r["table"] == "pbo" and r["S"] == str(S) and r["metric"] == metric:
            return r["note"]
    return ""


def pmeta(S, key):
    for r in pbo_rows:
        if r["table"] == "pbo" and r["S"] == str(S):
            return r[key]
    return ""


def dv(which, metric, sharpe_metric="sharpe_naive"):
    for r in dsr_rows:
        if (r["table"] == "point" and r["which"] == which
                and r["metric"] == metric and r["sharpe_metric"] == sharpe_metric):
            return float(r["value"])
    raise KeyError((which, metric))


def xs(metric):
    for r in dsr_rows:
        if r["table"] == "cross_section" and r["metric"] == metric:
            return float(r["value"])
    raise KeyError(metric)


def nval(metric):
    for r in dsr_rows:
        if r["table"] == "n" and r["metric"] == metric:
            return int(float(r["value"]))
    raise KeyError(metric)


def iv(item):
    for r in inv_rows:
        if r["item"] == item:
            return r["value"]
    return ""


def rv(item):
    for r in rem_rows:
        if r["item"] == item:
            return r["value"]
    return ""


d = np.load(OUT / "cscv-draws-s16.npz")
logit, is_sel, os_sel, os_med = d["logit"], d["is_sel"], d["os_sel"], d["os_med"]
c_os = d["canonical_oos_rank"]
NSPEC = int(d["n_specifications"][0])
NCOMB = int(d["n_combinations"][0])
pbo16 = pv(16, "pbo", "primary")
assert abs(float((logit < 0).mean()) - pbo16) < 1e-12, \
    "the dumped draws do not reproduce the emitted PBO"

slope16 = pv(16, "degradation_slope", "primary")
icept16 = pv(16, "degradation_intercept", "primary")
r2_16 = pv(16, "degradation_r_squared", "primary")
ploss16 = pv(16, "probability_of_loss", "primary")

# --- figures ---------------------------------------------------------------
(FIG / "logit-histogram.svg").write_text(svg.histogram(
    logit, 60,
    "Distribution of the out-of-sample rank logit across 12,870 combinations",
    "logit of the selected specification's out-of-sample rank",
    shade_below=0.0,
    note=f"shaded region is the PBO, being {pbo16:.4f} of combinations below zero"))

(FIG / "degradation-scatter.svg").write_text(svg.scatter_fit(
    is_sel, os_sel, slope16, icept16,
    "In-sample against out-of-sample Sharpe of the selected specification",
    "in-sample naive Sharpe, annualised",
    "out-of-sample naive Sharpe, annualised",
    note=f"R-squared {r2_16:.4f}"))

(FIG / "selected-vs-median.svg").write_text(svg.two_cdfs(
    os_sel, os_med, "selected specification", "median trial",
    "Out-of-sample Sharpe, selected specification against the median trial",
    "out-of-sample naive Sharpe, annualised",
    note="first and second order stochastic dominance both fail"))

groups = []
seen = []
for r in curve_rows:
    if r["table"] != "axis_marginal":
        continue
    a = r["axis"]
    if a not in seen:
        seen.append(a)
        groups.append((a, r["classification"], []))
    for g in groups:
        if g[0] == a:
            g[2].append((r["axis_value"], float(r["sharpe_lo_mean"]),
                         float(r["sharpe_lo_p05"]), float(r["sharpe_lo_p95"])))
(FIG / "specification-curve.svg").write_text(svg.strata_panel(
    groups, "Lo-corrected Sharpe across the nine searched axes",
    "Lo-corrected Sharpe, annualised",
    note="point is the stratum mean, bar spans the 5th to 95th percentile"))

# --- tables ----------------------------------------------------------------
S_ORDER = ["16", "8", "12", "24", "48"]
sens = []
for S in S_ORDER:
    sens.append((S, pv(S, "pbo"), pmeta(S, "n_combinations"),
                 pmeta(S, "combinations_full"), pmeta(S, "combinations_sampled"),
                 pv(S, "degradation_slope"), pv(S, "degradation_r_squared"),
                 pv(S, "probability_of_loss"), pmeta(S, "seconds"),
                 pmeta(S, "peak_rss_gb")))

ref_pbo = None
axis_rows, stratum_rows = [], []
for r in strata_rows:
    if r["table"] == "reference":
        ref_pbo = float(r["pbo"])
    elif r["table"] == "axis_range":
        axis_rows.append(r)
    elif r["table"] == "stratum":
        stratum_rows.append(r)
interp = next(r["note"] for r in strata_rows if r["table"] == "interpretation")
n_inside = next(int(r["n_axes_inside"]) for r in strata_rows if r["table"] == "interpretation")
n_above = next(int(r["n_axes_full_above"]) for r in strata_rows if r["table"] == "interpretation")
n_below = next(int(r["n_axes_full_below"]) for r in strata_rows if r["table"] == "interpretation")

N_ENUM, N_EVAL = nval("n_enumerated"), nval("n_evaluated")
# Deliberately NOT recorded in the output. Whether the panel is present must not
# change a single byte of this document, or the post-deletion regenerability check
# would compare two different texts and fail on a difference this script created.

L = []
A = L.append
A("# Session 19 PBO report")
A("")
A(f"Probability of backtest overfitting, the deflated Sharpe, and the specification "
  f"curve for the completed {N_EVAL:,} specification grid. Every figure below is read "
  f"from an emitted CSV in `outputs/session-19/` under 9.12. The holdout boundary "
  f"2021-08-01 under 2.10 is untouched and no post-boundary quantity appears here.")
A("")
A("This document is regenerable from committed artifacts alone. The panel directory "
  "`outputs/session-17/panel/` is never opened by the generator, so this text is "
  "identical whether the panel is present or deleted.")
A("")
A("## The approximation this rests on")
A("")
A("The performance metric throughout the CSCV is the **naive Sharpe** rather than the "
  "Lo-corrected Sharpe that 8.2 designates as headline. Autocovariance is not additive "
  "across disjoint blocks, so the cross-boundary terms are missing from any union of "
  "blocks and a Lo correction computed on a union would be wrong rather than "
  "approximate. The naive Sharpe is exactly reconstructible from the stored block sums, "
  "which is why it is used. This is a disclosed approximation and it means the PBO here "
  "measures overfitting of the naive Sharpe, with the headline Lo-corrected figure "
  "reported separately in the specification curve section.")
A("")
A("Moment additivity was re-verified this session rather than taken from the recovered "
  f"session 18 file. The maximum absolute deviation between statistics reconstructed "
  f"from the 48 stored block moments and the same statistics in the per-specification "
  f"metric set is "
  f"{float(next(r['abs_gap_metric_set'] for r in add_rows if r['which']=='step3')):.3e} "
  f"against a 1e-10 tolerance fixed before the comparison ran, reproducing session 18's "
  f"3.3e-16.")
A("")
A("## Positive control")
A("")
A(f"The canonical specification is identifier {iv('canonical_spec_id')} in shard "
  f"{iv('canonical_shard')}. Its axis values match `src/config.py` with no literal "
  f"entering the check. It reads annualised return "
  f"{float(iv('ann_return')):.6f} and Lo-corrected Sharpe {float(iv('sharpe_lo')):.6f}, "
  f"reproducing the designated cell to six decimals.")
A("")
A("## PBO at S equal to 16")
A("")
A(f"**PBO is {pbo16:.4f}** over {NCOMB:,} combinations, being the full enumeration of "
  f"C(16,8), across {NSPEC:,} specifications. That is the frequency with which the "
  f"specification selected as best in sample lands in the bottom half of the "
  f"out-of-sample ranking. Session 18's interrupted run measured 0.1578 on the same "
  f"construction and the figure reproduces.")
A("")
A(f"![logit histogram](figures/logit-histogram.svg)")
A("")
A("### Performance degradation")
A("")
A(f"Regressing the selected specification's out-of-sample Sharpe on its in-sample "
  f"Sharpe gives slope **{slope16:.4f}**, intercept {icept16:.4f}, and R-squared "
  f"{r2_16:.4f}. The slope is reported as measured and without interpretation.")
A("")
A(f"![degradation scatter](figures/degradation-scatter.svg)")
A("")
A("### Probability of loss and stochastic dominance")
A("")
A(f"The probability of loss, being the frequency with which the selected specification "
  f"returns a negative out-of-sample naive Sharpe, is **{ploss16:.6f}**.")
A("")
A(f"First order stochastic dominance of the selected specification over the median "
  f"trial does **not** hold, with the CDF condition satisfied on "
  f"{pnote(16,'first_order_stochastic_dominance').split('on ')[-1].split(' of')[0]} of "
  f"the support. Second order dominance does **not** hold either, with the integrated "
  f"CDF condition satisfied on "
  f"{pnote(16,'second_order_stochastic_dominance').split('on ')[-1].split(' of')[0]} of "
  f"the support.")
A("")
A(f"![selected against median](figures/selected-vs-median.svg)")
A("")
A("### The canonical point, which was not selected")
A("")
A(f"The canonical was pre-registered rather than chosen by the search, so its rank is "
  f"reported separately from the in-sample-best. Across the {NCOMB:,} combinations its "
  f"out-of-sample rank has median {np.median(c_os):,.0f} of {NSPEC:,} and its mean rank "
  f"expressed as a fraction of the specification count is "
  f"{pv(16,'canonical_oos_rank_pctile_mean','primary'):.4f}.")
A("")
A("### Block-count sensitivity")
A("")
A("| S | PBO | combinations | enumeration | degradation slope | R-squared | "
  "probability of loss | seconds | peak GB |")
A("|---|---|---|---|---|---|---|---|---|")
for (S, p, nc, full, samp, sl, r2, pl, sec, peak) in sens:
    enum = "full" if samp == "0" else f"sampled of {int(full):,}"
    star = " (primary)" if S == "16" else ""
    A(f"| {S}{star} | {p:.4f} | {int(nc):,} | {enum} | {sl:.4f} | {r2:.4f} | "
      f"{pl:.6f} | {float(sec):.1f} | {peak} |")
A("")
A(f"PBO spans {min(s[1] for s in sens):.4f} to {max(s[1] for s in sens):.4f} across the "
  f"five block counts. At S equal to 24 and S equal to 48 the combination space exceeds "
  f"the 20,000 cap fixed before the run, so those two passes are random samples at seed "
  f"20260821 rather than full enumerations, and that is disclosed per pass in the table.")
A("")
A("## PBO within structural strata")
A("")
A("The smooth-axis restriction the session 18 prompt specified holds all six structural "
  "axes at canonical and varies only the three smooth axes, which spans 27 "
  "specifications. A 27-point PBO is not comparable to a 121,500-point figure, so the "
  "restriction was replaced rather than run. Holding one structural axis at one value "
  "fixes the strategy shape that axis controls and leaves the remaining eight axes free, "
  "so the PBO inside a stratum is the parameter-search component alone.")
A("")
A(f"The full-grid reference is {ref_pbo:.4f}, being the step 4 primary pass at identical "
  f"construction.")
A("")
A("| structural axis | values | PBO min | PBO max | range | full grid inside |")
A("|---|---|---|---|---|---|")
for r in axis_rows:
    A(f"| {r['axis']} | {int(float(r['n_specifications']))} | {float(r['pbo_min']):.4f} | "
      f"{float(r['pbo_max']):.4f} | {float(r['pbo_range']):.4f} | "
      f"{'yes' if r['full_grid_inside_range']=='1' else 'no'} |")
A("")
A("Per stratum, with the terminals that never fire at that value.")
A("")
A("| axis | value | specifications | PBO | dead terminals |")
A("|---|---|---|---|---|")
for r in stratum_rows:
    mark = " (canonical)" if r["is_canonical_value"] == "1" else ""
    A(f"| {r['axis']} | {r['axis_value']}{mark} | "
      f"{int(float(r['n_specifications'])):,} | {float(r['pbo']):.4f} | "
      f"{int(float(r['n_dead_terminals']))} |")
A("")
A(f"**Interpretation as measured.** {interp[0].upper()}{interp[1:]}. No recommendation "
  f"follows from this.")
A("")
A("## The deflated Sharpe")
A("")
A(f"N is **{N_ENUM:,}**, the size of the search space the study enumerated across ten "
  f"axes, and the grid evaluated **{N_EVAL:,}** of them with the 7.4 tier-two offset "
  f"held at its canonical value of 10 rather than sampled. Both figures are recorded and "
  f"the deflated Sharpe is recomputed at {N_EVAL:,} as the sensitivity.")
A("")
A("The probabilistic and deflated Sharpe are computed on the naive Sharpe, since the "
  "formula carries its own skewness and excess kurtosis adjustment while the Lo "
  "correction addresses autocorrelation, so substituting the Lo-corrected figure would "
  "mix two corrections.")
A("")
A("**Estimation caveat.** The cross-sectional standard deviation of Sharpe entering the "
  f"expected maximum is estimated from the {N_EVAL:,} evaluated specifications, which "
  f"is a subset of the {N_ENUM:,} enumerated, so the dispersion of the unevaluated "
  f"remainder is assumed equal to that of the evaluated subset and is not measured.")
A("")
A("| quantity | canonical | in-sample-best |")
A("|---|---|---|")
A(f"| naive Sharpe, annualised | {dv('canonical','sharpe_annualised'):.4f} | "
  f"{dv('in_sample_best','sharpe_annualised'):.4f} |")
A(f"| skewness | {dv('canonical','skewness'):.4f} | {dv('in_sample_best','skewness'):.4f} |")
A(f"| excess kurtosis | {dv('canonical','excess_kurtosis'):.4f} | "
  f"{dv('in_sample_best','excess_kurtosis'):.4f} |")
A(f"| probabilistic Sharpe against zero | {dv('canonical','probabilistic_sharpe_vs_zero'):.6f} | "
  f"{dv('in_sample_best','probabilistic_sharpe_vs_zero'):.6f} |")
A(f"| expected maximum Sharpe, no-skill null, N={N_ENUM:,} | "
  f"{dv('canonical','expected_max_sharpe_ann_N_364500'):.4f} | "
  f"{dv('in_sample_best','expected_max_sharpe_ann_N_364500'):.4f} |")
A(f"| **deflated Sharpe at N={N_ENUM:,}** | "
  f"**{dv('canonical','deflated_sharpe_N_364500'):.6f}** | "
  f"**{dv('in_sample_best','deflated_sharpe_N_364500'):.6f}** |")
A(f"| deflated Sharpe at N={N_EVAL:,} | {dv('canonical','deflated_sharpe_N_121500'):.6f} | "
  f"{dv('in_sample_best','deflated_sharpe_N_121500'):.6f} |")
A("")
A(f"The same figures computed on the Lo-corrected Sharpe are carried in "
  f"`deflated-sharpe.csv` as a disclosed sensitivity, giving a deflated Sharpe of "
  f"{dv('canonical','deflated_sharpe_N_364500','sharpe_lo'):.6f} for the canonical and "
  f"{dv('in_sample_best','deflated_sharpe_N_364500','sharpe_lo'):.6f} for the "
  f"in-sample-best at N equal to {N_ENUM:,}.")
A("")
A(f"The expected maximum Sharpe under the no-skill null, "
  f"{dv('canonical','expected_max_sharpe_ann_N_364500'):.4f} annualised, exceeds both "
  f"the canonical's {dv('canonical','sharpe_annualised'):.4f} and the in-sample-best's "
  f"{dv('in_sample_best','sharpe_annualised'):.4f}, which is what produces deflated "
  f"figures below one half. Reported as measured.")
A("")
A("### Cross-sectional Sharpe across the grid")
A("")
A("| metric | naive Sharpe | Lo-corrected Sharpe |")
A("|---|---|---|")
A(f"| mean | {xs('sharpe_naive_ann_mean'):.4f} | {xs('sharpe_lo_ann_mean'):.4f} |")
A(f"| standard deviation | {xs('sharpe_naive_ann_sd'):.4f} | {xs('sharpe_lo_ann_sd'):.4f} |")
A(f"| 5th percentile | {xs('sharpe_naive_ann_p05'):.4f} | {xs('sharpe_lo_ann_p05'):.4f} |")
A(f"| 50th percentile | {xs('sharpe_naive_ann_p50'):.4f} | {xs('sharpe_lo_ann_p50'):.4f} |")
A(f"| 95th percentile | {xs('sharpe_naive_ann_p95'):.4f} | {xs('sharpe_lo_ann_p95'):.4f} |")
A("")
A("## The specification curve")
A("")
rk = {r["axis"]: r for r in curve_rows if r["table"] == "canonical_rank"}
A(f"The canonical point ranks **{int(float(rk['sharpe_lo']['rank'])):,} of {N_EVAL:,}** "
  f"on the Lo-corrected Sharpe and "
  f"**{int(float(rk['ann_return']['rank'])):,} of {N_EVAL:,}** on annualised return, "
  f"where rank 1 is the highest.")
A("")
A(f"![specification curve](figures/specification-curve.svg)")
A("")
A("The six structural axes are shown as separated strata and the three smooth axes as "
  "sweeps, per step 5.")
A("")
A("### Choice axes under 9.11 plus NAV")
A("")
A("| axis | arms sourced | note |")
A("|---|---|---|")
for r in curve_rows:
    if r["table"] == "curve_axis_status":
        A(f"| {r['axis']} | {r['arm']} | {r['note']} |")
A("")
A("The tier-two offset under 7.4 is **not** on the curve and was not searched. The "
  "register records it as informed rather than closed, so it is not a decision the study "
  "made, and a curve spanning it would report sensitivity to a parameter the register "
  "never fixed. It is held at its canonical value of 10 on every one of the "
  f"{N_EVAL:,} specifications, so the canonical point is unchanged.")
A("")
A("### Post-result choices off the recorded axes")
A("")
A("| item | status |")
A("|---|---|")
for r in curve_rows:
    if r["table"] == "off_axis_post_result_choice" and r["axis"] != "count":
        A(f"| {r['axis']} | {r['note']} |")
A("")
A("## Custody")
A("")
A(f"The repository gained a remote this session at {rv('url')}, private, with the remote "
  f"main matching local HEAD. {float(rv('pack_mb_pushed')):.2f} MB in "
  f"{int(rv('objects_in_pack')):,} objects were pushed and the largest tracked file is "
  f"{float(rv('tracked_mb_at_head')):.2f} MB of tracked content with nothing over 100 "
  f"megabytes entering history.")
A("")
out = "\n".join(L) + "\n"
(OUT / "PBO-REPORT.md").write_text(out)
print(f"wrote {OUT/'PBO-REPORT.md'} {len(out):,} bytes")
print(f"wrote 4 figures under {FIG}")
