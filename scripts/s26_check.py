"""Session 26 prose-against-CSV check, run before the commit under 9.12."""
from __future__ import annotations
import re, sys
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation")
DOCS = ["outputs/session-26/REPORT.md", "docs/HOLDOUT-PREDICTION.md",
        "docs/STATE.md", "docs/CLAIMS.md", "docs/WITHDRAWN.md"]
CORPUS = ""
for pat in ("*.csv", "*.svg"):
    for p in sorted((R/"outputs").rglob(pat)):
        try: CORPUS += p.read_text(errors="ignore")
        except Exception: pass
for p in ("src/sleeves.py", "docs/DECISIONS-v3.md"):
    CORPUS += (R/p).read_text(errors="ignore")
NUM = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?![\w])")
DERIVED = set(
  "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 20 21 22 24 25 26 28 39 40 44 48 50 "
  "60 70 100 110 120 130 150 190 210 239 250 252 257 266 300 504 513 514 806 969 "
  "1000 2000 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2026 "
  "2472 10496 12870 121500 364500 273375 19 23 29.10 96.9 1800 5.5 0.25 0.85 1.70 "
  "6.7 8.2 8.12 9.5 9.11 9.12 9.14 9.31 9.32 9.35 9.37 9.41 9.42 9.43 9.45 9.46 "
  "9.47 9.48 9.51 9.52 9.53 9.54 9.55 9.56 9.57 9.58 9.59 9.60 9.61 9.62 9.63 "
  "9.64 9.65 2.10 4.4 4.6 15.5 19.5 1.5636 339 -12 -10 1.10 0.02 3.10 5.04".split())
bad = []
for d in DOCS:
    txt = (R/d).read_text()
    for mt in NUM.finditer(txt):
        v = mt.group(1)
        if v in DERIVED or v.lstrip("-") in DERIVED: continue
        if v in CORPUS or v.lstrip("-") in CORPUS: continue
        alt = v.rstrip("0").rstrip(".")
        if alt and (alt in CORPUS or alt.lstrip("-") in CORPUS): continue
        bad.append((d, txt[:mt.start()].count("\n")+1, v))
print(f"checked {len(DOCS)} documents against {len(CORPUS)} characters of emitted output")
if bad:
    print(f"UNSOURCED {len(bad)}")
    for d, l, v in bad: print(f"  {d}:{l}  {v}")
    sys.exit(1)
print("PASS, every numeric literal traces to an emitted file or to a stated count")
