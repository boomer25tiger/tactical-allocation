"""Session 24 phases A, B and C. Write docs/CLAIMS.md and docs/WITHDRAWN.md."""
from __future__ import annotations
import csv
from pathlib import Path
R=Path("/Users/GualyCr/Downloads/tactical-allocation"); OUT=R/"outputs"/"session-24"
def rd(p): return list(csv.DictReader(open(R/p)))
C=rd("outputs/session-24/claim-sources.csv")
W=rd("outputs/session-24/withdrawn-sources.csv")
F=rd("outputs/session-24/figure-spec.csv")
unw=rd("outputs/session-21/unwired-config.csv")
prov=rd("outputs/session-21/canonical-provenance.csv")
vol=rd("outputs/session-22/volatility-terminal-resolution.csv")
def val(rows,pred,f="value"):
    for r in rows:
        if pred(r): return r.get(f)
    return None
un=[r["param"] for r in unw if r["table"]=="parameter" and r["classification"] in ("none","validate_only")]
dead=[r["param"] for r in unw if r["table"]=="dead_read"]

L=[];A=L.append
A("# CLAIMS")
A("")
A("The frozen set of claims this project makes, together with the limitations that")
A("qualify them. Frozen means no claim is added after 2026-08-20 without a dated")
A("register entry recording the addition and its grounds.")
A("")
A("Every figure below is the literal value in the emitted CSV named beside it. The")
A("claim-to-artifact map is `outputs/session-24/claim-sources.csv`, so each claim is")
A("traceable to a committed file. Claims withdrawn during the project are in")
A("`docs/WITHDRAWN.md` rather than removed silently.")
A("")
A("Both Sharpe conventions are reported throughout with the naive figure leading, per")
A("the 8.2 decision, on the grounds recorded in claim 14 as narrowed at 9.61.")
A("")
A("**Amendments since the freeze.** Claim 4's scope phrase was narrowed on 2026-08-22 to")
A("name only the block counts re-emitted on repaired code, recorded at 9.59 as a wording")
A("repair. No quoted figure moved and no claim was added or removed.")
A("")
A(f"**{len(C)} claims**, being {sum(1 for c in C if c['tier']=='primary')} primary and "
  f"{sum(1 for c in C if c['tier']=='supporting')} supporting. "
  f"{sum(1 for c in C if c['category']=='strategy')} concern the strategy and "
  f"{sum(1 for c in C if c['category']=='grid')} the grid, while "
  f"{sum(1 for c in C if c['category']=='apparatus')} concern the measurement "
  f"apparatus. **The contribution sits mostly in that last group.**")
A("")
for c in C:
    A(f"## Claim {c['n']}, {c['tier']}, about the {c['category']}")
    A("")
    A(c["statement"])
    A("")
    A(f"- Source `{c['source_file']}`")
    A(f"- Emitted {c['literal_value']}")
    A(f"- Register {c['register_item']}")
    A(f"- Overturned by {c['overturned_by']}")
    A("")
A("# LIMITATIONS")
A("")
A("Each limitation sits beside the claim it qualifies rather than in a section a reader")
A("skips.")
A("")
A("## On the percentile claim, claim 8")
A("")
A(f"**One of the nine axis values was fixed after a measurement on its own axis.** "
  f"`crash_threshold` carried the source value of minus 12, session 04 closed an "
  f"absolute threshold at minus 10 after session 03 measured all three estimator forms "
  f"failing, and session 09 re-closed at the canonical value citing session 06's "
  f"firing-rate measurement. The register marks it a stipulation. What those "
  f"measurements compared was estimator form and firing rate rather than performance "
  f"across levels, and the percentile claim is weakened on that axis alone.")
A("")
A(f"**Seven of the nine closures carry no session attribution in the register**, so "
  f"their ordering relative to any measurement rests on the entries' source-derived "
  f"phrasing rather than on a dated record. That is a documentation gap rather than "
  f"evidence of tuning. Source `outputs/session-21/canonical-provenance.csv`, register "
  f"9.32.")
A("")
A("## On every claim that reads a config parameter")
A("")
A(f"**Ten parameters defined in `src/config.py` have no consumer outside it**, being "
  f"{', '.join(un)}. **Two more carry a read that is never invoked**, being "
  f"{' and '.join(dead)}, each read by `src/execution.py` as a default argument of a "
  f"`size_position` the return-generating path never calls, while the engine hardcodes "
  f"`math.trunc`. Source `outputs/session-21/unwired-config.csv`, register 9.31.")
A("")
A("`SLIPPAGE_MODEL` and `SLIPPAGE_MODELS` have no consumer while `slippage_model` is a "
  "specification-curve axis, so the curve is real and was varied through function "
  "selection rather than through the config value, which 9.11 does not record. "
  "`GRID_TOTAL_SPECIFICATIONS` and `GRID_SEARCHED_SPECIFICATIONS` are read only inside "
  "`validate`, so the counts 7.10 relies on are checked but never consumed by a "
  "measurement.")
A("")
A("## On the holdout")
A("")
A(f"**SVIX and UVIX appear in weight dictionaries and load on neither panel.** "
  f"`State.available` returns False for a ticker absent from the panel and the switch "
  f"selects the fallback before the dictionary is built, so no weight is dropped, no "
  f"balance goes to cash and no renormalisation occurs. The T10 terminal fires "
  f"{val(vol,lambda r:r['table']=='firing' and r['item']=='t10_vol_short')} times "
  f"holding SVXY and the S3 terminal "
  f"{val(vol,lambda r:r['table']=='firing' and r['item']=='s3_vol')} times holding UVXY "
  f"across the primary window. Both list 2022-03-30, inside the holdout span, so the "
  f"source strategy's guards would activate there while this implementation will not. "
  f"**The loader is left unchanged deliberately**, since adding either ticker would "
  f"execute the branch for the first time inside the single holdout read. Source "
  f"`outputs/session-22/volatility-terminal-resolution.csv`, register 9.43.")
A("")
A("## On the cost model, claim 15")
A("")
A("**D16 stands.** The financing spread is assumed rather than measured, is treated by "
  "the cost sweep, and is **never read by the engine**. Its readers are the synthetics "
  "builder and validator, so the spread reaches results only through the pre-built "
  "reconstructions on the synthetic arm. On the realized arm, which is the designated "
  "cell, the levered funds carry the issuer's own financing inside their price history "
  "and no financing model applies. Register 9.31.")
A("")
A("## On the ladder, claim 1")
A("")
A("**The ladder dropped from fourteen lines to twelve**, removing the intraday-only and "
  "overnight-only hold universes. The drop is recorded nowhere and the Romano-Wolf "
  "family was never run at thirteen comparisons. Register 9.26.")
A("")
A("**Romano-Wolf ran at 1,000 draws** while the two randomization nulls were raised to "
  "10,000, so claim 3 and claim 2 rest on different replication counts.")
A("")
A("## On every Sharpe figure, claim 14")
A("")
A("**The Lo lag parameter q is a Python default at `scripts/s13_backtest.py:609`**, "
  "absent from `config.py`, on no specification-curve axis and on no grid axis, and it "
  "was discovered post hoc. It was never varied when any reported figure was selected. "
  "Register 9.37.")
A("")
A("## On attribution, claim 11")
A("")
A("**D23 stands**, being the portfolio-level per-instrument attribution confound, "
  "corrected in place at session 15.5.")
A("")
A("## Outstanding measurements")
A("")
A("**The B1 re-emission ran on a quiet machine and reached four of its five block "
  "counts**, being 8, 12, 16 and 24, before the pre-registered wall limit fired at "
  "994.2 seconds with 48 unreached. **All four re-emitted PBO values reproduce the "
  "reported figures exactly**, so the chunk-first-element defect did not touch PBO and "
  "claim 4 stands on repaired code at both of its stated range endpoints. The "
  "degradation slope does move, by between 2.448e-04 and 1.080e-02, and it is withdrawn "
  "on separate grounds. Source `outputs/session-24/phaseF-relaunch.csv`, register 9.48.")
A("")
A("**The wall limit was mis-derived and the halt reflects the limit rather than the "
  "machine.** 969 seconds came from ten times a single-chunk 96.9 second pass, while "
  "the sweep it had to cover measured 2424.37 seconds when first run. Load ran between "
  "5.09 and 13.05 throughout and each completed stage beat its original, S=16 at 417.4 "
  "seconds against 775.01 and S=24 at 506.1 against 598.24. Register 9.49.")
A("")
A("**One measurement remains outstanding and it is not load-bearing**, being S=48 of "
  "the B1 re-emission. The corrected degradation null is not run and its slope is "
  "withdrawn at 9.35 regardless. **No claim above depends on either.** Register 9.48 "
  "and 9.46.")
A("")
A("## Figures")
A("")
A(f"Two of the eight specified figures cannot be drawn from committed artifacts alone. "
  f"The null distribution histograms need per-draw arrays the nulls file does not carry, "
  f"and effective exposure by decile has only the mean and two named deciles rather than "
  f"a ten-decile series. Source `outputs/session-24/figure-spec.csv`.")
A("")
(R/"docs/CLAIMS.md").write_text("\n".join(L)+"\n")
print(f"wrote docs/CLAIMS.md, {len(C)} claims")

L=[];A=L.append
A("# WITHDRAWN")
A("")
A("Every claim this project made and then withdrew, with the grounds and the session")
A("that overturned it. A negative-result paper is judged partly on whether its authors")
A("can show what they stopped believing.")
A("")
A(f"**{len(W)} withdrawals**, of which "
  f"{sum(1 for x in W if x['measurement_or_argument'].startswith('measurement'))} "
  f"followed from a measurement and "
  f"{sum(1 for x in W if x['measurement_or_argument'].startswith('argument'))} from an "
  f"argument about construction. The map is `outputs/session-24/withdrawn-sources.csv`.")
A("")
for x in W:
    A(f"## {x['n']}. {x['withdrawn_claim']}")
    A("")
    A(x["grounds"])
    A("")
    A(f"- Withdrawn by {x['measurement_or_argument']}")
    A(f"- Session {x['session']}")
    A(f"- Source `{x['source_file']}`")
    A(f"- Emitted {x['literal_value']}")
    A("")
A("## A note on the pattern")
A("")
A(f"Three of the {len(W)} withdrawals concern the measurement apparatus rather than the")
A("strategy, and two of those, being the resource diagnosis in its first and second")
A("forms, were successive wrong answers to the same question in opposite directions. The")
A("register records the class at 9.47 as an inference stated as a measurement, which has")
A("produced three register corrections across the project.")
A("")
(R/"docs/WITHDRAWN.md").write_text("\n".join(L)+"\n")
print(f"wrote docs/WITHDRAWN.md, {len(W)} withdrawals")
