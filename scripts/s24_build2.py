"""Session 24 phases B and D. Withdrawn set and figure specification."""
from __future__ import annotations
import csv, pickle
from pathlib import Path
import pandas as pd
R=Path("/Users/GualyCr/Downloads/tactical-allocation"); OUT=R/"outputs"/"session-24"
def rd(p): return list(csv.DictReader(open(R/p)))
def val(rows,pred,f="value"):
    for r in rows:
        if pred(r): return r.get(f)
    return None

# ---------------- phase B, the withdrawn set ----------------
W=[]
def w(n, claim, grounds, basis, session, source, value):
    W.append({"n":n,"withdrawn_claim":claim,"grounds":grounds,
              "measurement_or_argument":basis,"session":session,
              "source_file":source,"literal_value":value})
rec=rd("outputs/session-21/recentred-comparison.csv")
efn=rd("outputs/session-20/effective-n.csv")
w(1,"The deflated Sharpe, reported at 0.000660 for the canonical at N equal to 364,500 "
    "and later at 0.001979 at N equal to 121,500.",
  "The statistic assumes every trial has true Sharpe zero while the grid's "
  "cross-sectional naive mean is 0.6199013071365644, so the null is misspecified at "
  "every N. The incoherence is visible at the participation-ratio count where the "
  "expected maximum falls below the mean of the draws it maximises over.",
  "argument, from the construction rather than from a result","21, at 8.7",
  "outputs/session-21/recentred-comparison.csv",
  val(rec,lambda r:r["table"]=="grounds" and r["item"]=="deflated_sharpe_removed","note")[:120])
w(2,"The performance degradation slope, reported at -1.0663023854544191 and corrected "
    "to -1.0666200132036998.",
  "No valid null exists for it. Session 19.6's null permuted block ordering "
  "independently per specification, which destroyed the common time structure every "
  "specification shares, so its z-scores tested that structure rather than overfitting. "
  "The corrected construction was never run.",
  "argument, with the corrected null still unrun","21, at 9.35",
  "outputs/session-19_6/m1-nis-correction.csv","corrected slope -1.0666200132036998")
ws=rd("outputs/session-19_5/window-strip.csv")
w(3,"The session 19.5 window strip, reporting the strategy's rank as unstable across six "
    "start dates.",
  "The strip compared a nested strategy against re-initialised benchmarks, since the "
  "strategy was built once and sliced while each benchmark line was rebuilt per arm. "
  "Seven of the eleven benchmark lines carry state, so the comparison is not like for "
  "like.",
  "argument, from the construction","21, at 9.36",
  "outputs/session-20/jan2013-attribution.csv","seven of eleven lines carry state")
bw=rd("outputs/session-22/beta-window-sensitivity.csv")
def bwv(win,item):
    return val(bw,lambda r:r["window"]==str(win) and r["item"]==item)
w(4,"The exposure-matched line reaching a higher naive Sharpe than the strategy at "
    "1.108581.",
  "Measured at a single 60-session window. Across 120, 252 and 504 sessions the matched "
  "line reads lower at each step and falls below the strategy, so the finding holds only "
  "at the shortest and noisiest window.",
  "measurement","22, at 9.42","outputs/session-22/beta-window-sensitivity.csv",
  f"120 {bwv(120,'sharpe_naive')}; 252 {bwv(252,'sharpe_naive')}; 504 {bwv(504,'sharpe_naive')}")
ja=rd("outputs/session-20/jan2013-attribution.csv")
w(5,"January 2013 as an exceptional event.",
  "The 69 overlapping fourteen-session windows below minus 0.15 collapse to 16 distinct "
  "non-overlapping episodes, and January 2013 ranks 11 among them rather than being "
  "singular.",
  "measurement","21 phase F5 and 20 phase F","outputs/session-21/reads.csv",
  f"distinct episodes {val(rd('outputs/session-21/reads.csv'),lambda r:r['table']=='F5' and r['item']=='distinct_non_overlapping_episodes')}, "
  f"rank {val(rd('outputs/session-21/reads.csv'),lambda r:r['table']=='F5' and r['item']=='january_2013_rank_among_episodes')}")
w(6,"The handoff's section 4 inference about 2022 holdout behaviour.",
  "The inference rested on the SVIX and UVIX branches activating from their 2022-03-30 "
  "listing. Those tickers load on neither panel and the availability switch resolves "
  "them away, so the branch will not execute at the holdout read under the current "
  "loader and no 2022 inference follows from it.",
  "measurement, by tracing the code path","20 at 9.20 and 22 at 9.43",
  "outputs/session-22/volatility-terminal-resolution.csv",
  "SVIX and UVIX in bt.LEVERED: 0")
rr=rd("outputs/session-23/resource-record.csv")
w(7,"The resource diagnosis in its first form, being that passes were blocked on memory.",
  "Every terminated pass was killed by hand after slowing, with no completion attempt "
  "allowed and no operating-system kill. Peak resident reached 1.133 GB against 3.561 GB "
  "that had completed, with page-outs low and the compressor flat.",
  "measurement, under a pre-registered rule","22, correcting 9.35 and 8.12",
  "outputs/session-23/resource-record.csv",
  val(rr,lambda r:r["table"]=="history" and r["item"]=="1_session_21","note")[:110])
w(8,"The resource diagnosis in its second form, being that the passes would have "
    "completed had they not been killed.",
  "A pre-registered 1800 second attempt did not complete, so the passes genuinely do not "
  "finish under contention. The claim ran ahead of the evidence in the opposite "
  "direction to the first.",
  "measurement","22, and again at 23","outputs/session-23/resource-record.csv",
  val(rr,lambda r:r["table"]=="history" and r["item"]=="2_correction","note")[:110])
loor=rd("outputs/session-22/loo-rebuilt.csv")
w(9,"The concern that the leave-one-out artifacts carried the superseded 2011-10-03 "
    "boundary.",
  "The rebuild produced a base estimate identical to the original at 1.3817013060, which "
  "is the corrected value, because session 16 made the correction and the leave-one-out "
  "script ran after it. The rebuild confirmed rather than repaired.",
  "measurement","22, at 9.41","outputs/session-22/loo-rebuilt.csv",
  f"abs_gap {val(loor,lambda r:r['table']=='premise_check' and r['item']=='abs_gap')}")
w(10,"The claim that the 1.5636 agreement between the 2011 leave-one-out estimate and "
     "the 2012-start strip arm was coincidental.",
  "The two operations are not independent. The primary window begins 2011-10-04, so "
  "dropping calendar 2011 removes very nearly the sessions that starting at the first "
  "2012 session removes, and the estimates agree to 8.326e-07 rather than to four "
  "decimals.",
  "measurement","22, at 9.41","outputs/session-22/loo-rebuilt.csv",
  f"abs_gap {val(loor,lambda r:r['table']=='agreement' and r['item']=='abs_gap')}")
with open(OUT/"withdrawn-sources.csv","w",newline="") as fh:
    wr=csv.DictWriter(fh,fieldnames=["n","withdrawn_claim","grounds",
        "measurement_or_argument","session","source_file","literal_value"])
    wr.writeheader(); wr.writerows(W)
print(f"withdrawn-sources.csv: {len(W)} withdrawals")
print(f"  by measurement {sum(1 for x in W if x['measurement_or_argument'].startswith('measurement'))}, "
      f"by argument {sum(1 for x in W if x['measurement_or_argument'].startswith('argument'))}")

# ---------------- phase D, the figure specification ----------------
F=[]
def fig(n,name,content,source,cols,drawable,note):
    F.append({"n":n,"figure":name,"content":content,"source_file":source,
              "columns_needed":cols,"drawable_from_committed":drawable,"note":note})
pkl=R/"outputs/session-20/rebuilt/_ladder_returns.pkl"
d=pickle.load(open(pkl,"rb"))
has=("buy_hold_QQQ","o2o","primary") in d["lines"] and \
    ("matched_exposure_levered_QQQ_1.70","o2o","primary") in d["lines"]
fig(1,"equity curve","designated cell against buy-and-hold QQQ and the matched-exposure line",
    "outputs/session-20/rebuilt/_ladder_returns.pkl",
    "strategy daily returns and lines[(buy_hold_QQQ,o2o,primary)] and "
    "lines[(matched_exposure_levered_QQQ_1.70,o2o,primary)]", int(has),
    "the pickle carries daily return series for the strategy and all eleven lines. The "
    "1.777 rebuild of the matched-exposure line has no committed daily series, so the "
    "figure uses the 1.70 line and says so")
fig(2,"drawdown series","drawdown of the designated cell",
    "outputs/session-20/rebuilt/_ladder_returns.pkl","strategy daily returns",1,
    "derived from the same series as figure 1")
fig(3,"null distribution histograms","the two randomization nulls with the observed value marked",
    "outputs/session-22/rebuilt/nulls.csv",
    "the per-draw arrays, which the file does not carry",0,
    "NOT DRAWABLE. The file carries null_ann_mean, null_ann_p05, null_ann_p50, "
    "null_ann_p95 and null_ann_max only, so the distribution shape is unavailable. "
    "Drawing it requires re-running the nulls with the draw arrays retained, which is a "
    "new measurement rather than a read")
fig(4,"cost sweep curves","strategy and benchmark Sharpe against round-turn cost with crossings",
    "outputs/session-20/rebuilt/cost-sweep-designated.csv and outputs/session-21/reads.csv",
    "slippage_bp, sharpe_lo, sharpe_naive, and the F1 crossing rows",1,
    "twelve of the twenty-two crossings are extrapolations and must be marked as such")
fig(5,"leave-one-out bars","Lo-corrected Sharpe with each calendar year removed",
    "outputs/session-22/rebuilt/leave-one-out.csv","dropped_year, sharpe_lo",1,"")
fig(6,"hedge intensity curve","short-leg intensity against outcome",
    "outputs/session-15.5/hedge-intensity.csv","the arm and outcome columns",1,
    "carries the 15.5 diagnostic arms, none of which is adopted")
fig(7,"NAV capacity curve","designated cell against starting NAV",
    "outputs/session-15/nav-sweep.csv","nav, ann_return, sharpe_lo, cap_frac_of_target_dollars",1,
    "the session 15 file is on the superseded boundary and was not rebuilt, so the "
    "figure carries that boundary or needs a rebuild first")
fig(8,"effective exposure by decile","mean effective exposure against conditioning decile",
    "outputs/session-16/exposure-reconciliation.csv",
    "mean_effective_exposure, worst_trailing_return_decile, wildest_vol_decile",0,
    "PARTIALLY DRAWABLE. The file carries the mean and two named deciles only, not a "
    "ten-decile series, so a curve across deciles cannot be drawn and a three-point "
    "comparison can")
fig(9,"PBO report figures, overlap check","the four figures scripts/s19_report.py writes",
    "outputs/session-19/figures/","logit-histogram, degradation-scatter, "
    "selected-vs-median, specification-curve",1,
    "none of the four overlaps the eight above. The degradation scatter and the logit "
    "histogram both support a statistic since removed, so two of the four now illustrate "
    "withdrawn claims")
fig(10,"plotting decision","how the eight are drawn","src/config.py environment",
    "matplotlib absence",1,
    "matplotlib is absent from the registered environment and adding it changes the "
    "environment the manifest records. Session 19 drew four figures with "
    "scripts/s19_svg.py using the standard library alone, producing valid SVG at 9.5 KB "
    "to 329.8 KB and deterministic byte-identical output across runs, which the "
    "regenerability check verified. DECISION, the eight are drawn on that path and "
    "matplotlib is not added")
with open(OUT/"figure-spec.csv","w",newline="") as fh:
    wr=csv.DictWriter(fh,fieldnames=["n","figure","content","source_file",
        "columns_needed","drawable_from_committed","note"])
    wr.writeheader(); wr.writerows(F)
nd_=[f for f in F if f["drawable_from_committed"]==0]
print(f"figure-spec.csv: {len(F)} rows, {len(nd_)} not drawable from committed artifacts")
for f in nd_: print(f"  NOT DRAWABLE  {f['figure']}")
