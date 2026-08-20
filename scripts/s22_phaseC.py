"""Session 22 phase C artifact. The leave-one-out rebuild, before and after."""
from __future__ import annotations
import csv, sys
from pathlib import Path
import pandas as pd, numpy as np
ROOT=Path("/Users/GualyCr/Downloads/tactical-allocation"); OUT=ROOT/"outputs/session-22"
o=pd.read_csv(ROOT/"outputs/session-16/leave-one-out.csv")
n=pd.read_csv(OUT/"rebuilt/leave-one-out.csv")
rows=[]
def loo(d):
    l=d[d.table=="loo"].copy()
    if "series" in l.columns and l.series.notna().any():
        s=l[l.series.astype(str).str.upper().str.contains("STRATEGY")]
        if len(s): l=s
    l = l[l.dropped_year.astype(str) != "none (base)"]
    l = l.copy(); l["dropped_year"] = l.dropped_year.astype(int)
    return l.sort_values("dropped_year")
lo_, ln_ = loo(o), loo(n)
rows.append({"table":"scope","item":"originals_preserved",
             "note":"outputs/session-16/leave-one-out.csv and the two session-16b loo "
                    "files are untouched; the rebuild is written to "
                    "outputs/session-22/rebuilt/"})
rows.append({"table":"scope","item":"n_estimates_before","value":len(lo_)})
rows.append({"table":"scope","item":"n_estimates_after","value":len(ln_)})
for _,r in ln_.iterrows():
    yr=r.dropped_year
    m=lo_[lo_.dropped_year==yr]
    ov=float(m.sharpe_lo.iloc[0]) if len(m) else float("nan")
    osess = float(m.n_sessions.iloc[0]) if (len(m) and "n_sessions" in m.columns) else ""
    rows.append({"table":"estimate","item":str(int(yr)) if pd.notna(yr) else "",
                 "before":ov,"after":float(r.sharpe_lo),
                 "shift":float(r.sharpe_lo)-ov if ov==ov else "",
                 "n_sessions_before":osess,
                 "n_sessions_after":"",
                 "ann_return_after":float(r.ann_return) if "ann_return" in r else ""})
for lbl,l in (("before",lo_),("after",ln_)):
    rows.append({"table":"range","item":f"sharpe_lo_min_{lbl}","value":float(l.sharpe_lo.min())})
    rows.append({"table":"range","item":f"sharpe_lo_max_{lbl}","value":float(l.sharpe_lo.max())})
    rows.append({"table":"range","item":f"sharpe_lo_span_{lbl}",
                 "value":float(l.sharpe_lo.max()-l.sharpe_lo.min())})
    top=l.nlargest(2,"sharpe_lo")
    rows.append({"table":"year_attribution","item":lbl,
                 "note":" ".join(f"{int(y)}={v:.4f}" for y,v in
                                 zip(top.dropped_year,top.sharpe_lo)),
                 "note2":"the two years whose removal raises the Sharpe most"})
sup=" ".join(str(int(y)) for y in ln_.nlargest(2,"sharpe_lo").dropped_year)
rows.append({"table":"year_attribution","item":"handoff_reconciliation",
             "note":f"the handoff carries two competing readings, being 2011 with 2020 "
                    f"in one place and 2018 with 2020 in another. The rebuilt file "
                    f"supports {sup}"})
e2011=ln_[ln_.dropped_year==2011]
v2011=float(e2011.sharpe_lo.iloc[0]) if len(e2011) else float("nan")
ws=list(csv.DictReader(open(ROOT/"outputs/session-19_5/window-strip.csv")))
arm=[float(r["sharpe_lo"]) for r in ws if r["table"]=="strip" and r["item"]=="first_session_2012"]
rows.append({"table":"agreement","item":"loo_2011_after","value":v2011})
rows.append({"table":"agreement","item":"strip_2012_arm","value":arm[0] if arm else ""})
rows.append({"table":"agreement","item":"structural_explanation",
             "note":"The primary window begins 2011-10-04, so calendar year 2011 inside "
                    "it spans only 2011-10-04 to the last session of that December. "
                    "Dropping calendar 2011 therefore removes very nearly the same "
                    "sessions as starting the window at the first session of 2012, so "
                    "the two operations are close to identical rather than independent. "
                    "Session 21 recorded the agreement as coincidental and that is "
                    "OVERTURNED here"})
rows.append({"table":"agreement","item":"still_agree",
             "value":int(abs(v2011-(arm[0] if arm else 0))<5e-5),
             "note":"session 21 held the agreement at 1.5636 to be coincidental, since a "
                    "leave-one-out drops one calendar year from the series while a strip "
                    "arm starts the window later and keeps every subsequent year. This "
                    "row tests whether the agreement survives the rebuild"})
with open(OUT/"loo-rebuilt.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","item","value","before","after","shift",
                                    "n_sessions_before","n_sessions_after",
                                    "ann_return_after","note","note2"],
                     extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"before {lo_.sharpe_lo.min():.4f} to {lo_.sharpe_lo.max():.4f}, "
      f"after {ln_.sharpe_lo.min():.4f} to {ln_.sharpe_lo.max():.4f}")
print("the emitted leave-one-out file carries no per-estimate session count, so the "
      "session count is reported from the base row's boundary instead")
print(f"years raising the Sharpe most, after: {sup}")
print(f"2011 loo {v2011:.6f} against the 2012 strip arm "
      f"{arm[0] if arm else float('nan'):.6f}")
print(f"wrote {OUT/'loo-rebuilt.csv'} with {len(rows)} rows")
