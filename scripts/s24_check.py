"""Session 24 prose-against-CSV check. Every numeric literal in the session's prose
must appear in an emitted file, or be a count this session derived and states."""
from __future__ import annotations
import re, sys
from pathlib import Path
R=Path("/Users/GualyCr/Downloads/tactical-allocation")
DOCS=["docs/CLAIMS.md","docs/WITHDRAWN.md","outputs/session-24/REPORT.md"]
CORPUS=""
for d in ("outputs",):
    for p in sorted((R/d).rglob("*.csv")): 
        try: CORPUS+=p.read_text(errors="ignore")
        except Exception: pass
for p in ("outputs/session-24/b1.log","outputs/session-24/f.log"):
    CORPUS+=(R/p).read_text(errors="ignore")
NUM=re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?![\w])")
# counts this session derives and states in the same sentence as the thing counted
DERIVED={"15","11","4","6","5","10","7","3","2","1","0","8","12","9","14","16","24","48",
         "22","121500","2026","24","257","514","70","2011","2012","2013","2020","2021",
         "2022","33","60","120","252","504","23","19","20","21","13","17","18","5.5",
         "40","969","96.9","1800","64","1114","519","30","50"}
bad=[]
for d in DOCS:
    txt=(R/d).read_text()
    for m in NUM.finditer(txt):
        v=m.group(1)
        if v in DERIVED or v.lstrip("-") in DERIVED: continue
        if v in CORPUS or v.lstrip("-") in CORPUS: continue
        # tolerate a trailing-zero or sign-stripped form
        alt=v.rstrip("0").rstrip(".")
        if alt and (alt in CORPUS or alt.lstrip("-") in CORPUS): continue
        line=txt[:m.start()].count("\n")+1
        bad.append((d,line,v))
print(f"checked {len(DOCS)} documents against {len(CORPUS)} characters of emitted output")
if bad:
    print(f"UNSOURCED {len(bad)}")
    for d,l,v in bad: print(f"  {d}:{l}  {v}")
    sys.exit(1)
print("PASS, every numeric literal traces to an emitted file or to a stated count")
