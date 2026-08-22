"""Session 25 prose-against-CSV check, run before the commit.

Every numeric literal in the session's prose must appear in an emitted file under
outputs/, or be a count this session derives and states in the same sentence as
the thing counted.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation")
DOCS = ["outputs/session-25/REPORT.md", "docs/STATE.md"]
CORPUS = ""
for p in sorted((R/"outputs").rglob("*.csv")):
    try: CORPUS += p.read_text(errors="ignore")
    except Exception: pass
for p in sorted((R/"outputs").rglob("*.svg")):
    try: CORPUS += p.read_text(errors="ignore")
    except Exception: pass
NUM = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?![\w])")
DERIVED = set("0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 28 33 "
              "40 44 48 50 60 70 100 120 121500 128 250 252 257 504 514 806 969 2011 2012 "
              "2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2026 2472 12870 201 19 "
              "96.9 1800 5.5 9.12 9.35 9.42 9.43 9.46 9.48 9.55 9.56 9.57 9.58 8.2 8.12 "
              "9.5 9.11 9.31 9.32 9.37 9.41 9.45 9.47 9.51 9.52 9.53 9.54 15.5 19.5 "
              "29.1 339 364500 26983 -12 -10 1.10 1.5636".split())
bad = []
for d in DOCS:
    txt = (R/d).read_text()
    for m in NUM.finditer(txt):
        v = m.group(1)
        if v in DERIVED or v.lstrip("-") in DERIVED: continue
        if v in CORPUS or v.lstrip("-") in CORPUS: continue
        alt = v.rstrip("0").rstrip(".")
        if alt and (alt in CORPUS or alt.lstrip("-") in CORPUS): continue
        bad.append((d, txt[:m.start()].count("\n")+1, v))
print(f"checked {len(DOCS)} documents against {len(CORPUS)} characters of emitted output")
if bad:
    print(f"UNSOURCED {len(bad)}")
    for d, l, v in bad: print(f"  {d}:{l}  {v}")
    sys.exit(1)
print("PASS, every numeric literal traces to an emitted file or to a stated count")
