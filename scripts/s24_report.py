"""Session 24 phase G. Write outputs/session-24/REPORT.md from the emitted CSVs."""
from __future__ import annotations
import csv
from pathlib import Path
R=Path("/Users/GualyCr/Downloads/tactical-allocation")
def rd(p): return list(csv.DictReader(open(R/p)))
C=rd("outputs/session-24/claim-sources.csv"); W=rd("outputs/session-24/withdrawn-sources.csv")
F=rd("outputs/session-24/figure-spec.csv"); P=rd("outputs/session-24/phaseF-relaunch.csv")
def pv(item,f="value"):
    for r in P:
        if r["item"]==item: return r[f]
    return None
L=[];A=L.append
A("# Session 24, the claim freeze")
A("")
A("2026-08-22. Seven phases. One commit, at phase G.")
A("")
A("## What this session did")
A("")
A(f"The claim set is frozen. `docs/CLAIMS.md` carries {len(C)} claims with the "
  f"limitations written into the same file, `docs/WITHDRAWN.md` carries {len(W)} "
  f"withdrawals, and `outputs/session-24/figure-spec.csv` specifies {len(F)} figures "
  f"without drawing any of them. The gated housekeeping pass ran and returned a "
  f"substantive result the session did not expect.")
A("")
A("## Phase A and C, the frozen claim set")
A("")
A(f"{len(C)} claims, being {sum(1 for c in C if c['tier']=='primary')} primary and "
  f"{sum(1 for c in C if c['tier']=='supporting')} supporting. "
  f"{sum(1 for c in C if c['category']=='strategy')} concern the strategy and "
  f"{sum(1 for c in C if c['category']=='grid')} the grid, while "
  f"{sum(1 for c in C if c['category']=='apparatus')} concern the measurement "
  f"apparatus. Each carries a statement, a source file, the literal emitted value, a "
  f"register item and the condition that would overturn it.")
A("")
A("Every figure was read from an emitted CSV with the path carried beside it. Two "
  "figures were corrected during the write. Claim 14 had said the three ladder rows "
  "outside their own no-autocorrelation null were the rows that outrank the strategy, "
  "and the file shows five rows outrank it while the three outside are its top three on "
  "the Lo-corrected Sharpe. Four values had been carried with a numpy repr wrapper "
  "around them rather than as the file emits them.")
A("")
A("The limitations sit under the claim each qualifies. They cover the ten config "
  "parameters with no consumer and the two read but never invoked, `crash_threshold` "
  "fixed after a measurement on its own axis, the seven of nine axis closures with no "
  "session attribution, the SVIX and UVIX path that will not execute at the holdout "
  "read, D16, D23, the unregistered Lo lag parameter, the ladder drop from fourteen "
  "lines to twelve, and the outstanding measurement.")
A("")
A("## Phase B, the withdrawn set")
A("")
A(f"{len(W)} withdrawals, of which "
  f"{sum(1 for x in W if x['measurement_or_argument'].startswith('measurement'))} "
  f"followed from a measurement and "
  f"{sum(1 for x in W if x['measurement_or_argument'].startswith('argument'))} from an "
  f"argument about construction. Three concern the measurement apparatus rather than "
  f"the strategy, and two of those, being the resource diagnosis in its first and "
  f"second forms, were successive wrong answers to the same question in opposite "
  f"directions.")
A("")
A("## Phase D, the figure specification")
A("")
nd=[r for r in F if r.get("drawable_from_committed")=="0"]
A(f"{len(F)} rows against the scaffold's eight. **No figure is drawn.** "
  f"{len(nd)} are not drawable from committed artifacts, being the null distribution "
  f"histograms, which need per-draw arrays the nulls file does not carry, and effective "
  f"exposure by decile, which has the mean and two named deciles rather than a "
  f"ten-decile series. Plotting will use the standard-library SVG path at "
  f"`scripts/s19_svg.py`, since matplotlib is absent and the offline constraint rules "
  f"out installing it.")
A("")
A("## Phase E, the volatility terminal")
A("")
A("The file existed from session 22 and was read rather than recomputed. The T10 "
  "terminal fires 1114 sessions holding SVXY and the S3 terminal 519 holding UVXY "
  "across the primary window, both tickers list 2022-03-30 inside the holdout span, and "
  "both load on neither panel. The finding is carried into the limitations. "
  "`bt.LEVERED` is not modified.")
A("")
A("## Phase F, the gated housekeeping")
A("")
A(f"`scripts/s23_phaseA.py` contains only a halt branch, so run unchanged on a quiet "
  f"machine it would have written a passed positive control and no pass. "
  f"`scripts/s24_phaseF.py` reuses its pre-registered rule verbatim and adds the launch "
  f"branch. No orphaned worker was present, so the kill step had nothing to terminate.")
A("")
A(f"The pass launched at a one-minute load of {pv('load_1min')} against the halt "
  f"threshold of {pv('halt_threshold')} and ran to the wall limit at "
  f"{pv('wall_clock_seconds')} seconds, peak resident {pv('peak_rss_gb')} GB, return "
  f"code {pv('return_code')}. It reached {pv('stages_completed')} of five block counts.")
A("")
A("| S | re-emitted PBO | reported PBO | reproduces | corrected slope | shift from the defective value |")
A("|---|---|---|---|---|---|")
for S in ("8","12","16","24"):
    pb=pv(f"S={S}_pbo_reemitted"); nb=[r for r in P if r["item"]==f"S={S}_pbo_reemitted"][0]["note"]
    rep=nb.split("reported ")[1].split(" at chunk")[0]
    sl=pv(f"S={S}_slope_corrected"); sn=[r for r in P if r["item"]==f"S={S}_slope_corrected"][0]["note"]
    sh=sn.split("shift ")[1].split(";")[0]
    A(f"| {S} | {pb} | {rep} | yes | {sl} | {sh} |")
A("")
A("**The chunk-first-element defect did not touch PBO.** All four re-emitted values "
  "reproduce the reported figures exactly on repaired code at a chunk size of 257 "
  "rather than the 514 most were first run at, so claim 4 stands on repaired code at "
  "both of its stated range endpoints, which are S equal to 8 and S equal to 12. The "
  "degradation slope does move, and its removal at 9.35 makes that moot.")
A("")
A("**The wall limit was mis-derived and the halt reflects the limit rather than the "
  "machine.** 969 seconds was taken as ten times a 96.9 second single-chunk pass, while "
  "the sweep it had to cover measured 2424.37 seconds across its five stages when first "
  "run. Load ran between 5.09 and 13.05 across 33 samples and each completed stage beat "
  "its original, S=16 at 417.4 seconds against 775.01 and S=24 at 506.1 against 598.24. "
  "Recording this as a contention halt would repeat the class at 9.47 of naming a "
  "mechanism the evidence does not reach.")
A("")
A("**The contention diagnosis gains its first supporting completion observation.** Four "
  "stages completed at a load-to-core ratio of 1.90 at launch, against 4.9463 when "
  "session 22's pass failed to complete and 8.9288 when session 23 halted before "
  "launch. It is support rather than proof, since the three runs differ in wall limit "
  "as well as in load.")
A("")
A("## What remains outstanding")
A("")
A("S equal to 48 of the B1 re-emission, which sets neither endpoint of claim 4's stated "
  "range, and the corrected degradation null, whose slope is withdrawn at 9.35 "
  "regardless. Neither is load-bearing and no claim depends on either.")
A("")
A("## Register")
A("")
A("9.48 the partial re-emission and the amendment to 8.12. 9.49 the mis-derived wall "
  "limit. 9.50 the completion observation extending 9.47. 9.51 the frozen claim set. "
  "9.52 the withdrawn set. 9.53 the figure specification and the plotting decision. "
  "9.54 the volatility terminal read. The measurement-phase closure note is amended to "
  "one outstanding item from two.")
A("")
A("## Artifacts")
A("")
for f in ("claim-sources.csv","withdrawn-sources.csv","figure-spec.csv",
          "phaseF-relaunch.csv","f.log","b1.log"):
    A(f"- `outputs/session-24/{f}`")
A("- `docs/CLAIMS.md`")
A("- `docs/WITHDRAWN.md`")
A("")
(R/"outputs/session-24/REPORT.md").write_text("\n".join(L)+"\n")
print("wrote REPORT.md")
