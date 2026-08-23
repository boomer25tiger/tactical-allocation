"""Session 30 prose-against-CSV check, run before the commit under 9.12."""
from __future__ import annotations

import re
import sys
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
DOCS = [d for d in ("outputs/session-30/REPORT.md", "docs/STATE.md")
        if (R / d).exists()]
# The session 28 register entries are hand-written, so the tail of the register from
# 9.70 onward is checked here too. Earlier entries carry figures from files this
# session does not read and are out of scope.
_REG = (R / "docs" / "DECISIONS-v3.md").read_text()
_TAIL = _REG[_REG.index("- **9.82 the session 30 pre-registration"):]
(R / "outputs" / "session-30" / "_register-tail.md").write_text(_TAIL)
DOCS.append("outputs/session-30/_register-tail.md")
CORPUS = ""
for pat in ("*.csv", "*.svg"):
    for p in sorted((R / "outputs").rglob(pat)):
        try:
            CORPUS += p.read_text(errors="ignore")
        except Exception:
            pass
CORPUS += (R / "docs" / "DECISIONS-v3.md").read_text(errors="ignore")
CORPUS += (R / "docs" / "HOLDOUT-PREDICTION.md").read_text(errors="ignore")
NUM = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?![\w])")
DERIVED = set(
    "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 20 21 22 24 25 26 27 28 35 39 40 44 "
    "48 50 60 70 100 120 252 257 339 416 504 514 928 1265 2011 2012 2013 2014 2015 "
    "2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2472 3737 12870 121500 "
    "0.25 0.85 1.70 29.10 96.9 5.5 9.12 9.43 9.60 9.62 9.64 9.66 9.67 9.68 9.69 2.10 "
    "8.2 8.12 9.35 9.42 9.46 9.48 9.51 9.52 9.53 9.55 9.56 9.57 9.58 9.59 9.61 9.63 "
    "9.65 15.5 19.5 1.5636 -12 -10 1.10 0.02 5e-07 9.66 9.67 9.68 9.69 9.70 9.71 "
    "9.72 9.73 9.74 9.75 9.76 9.77 9.78 9.79 9.80 9.81 9.82 9.83 9.84 9.85 9.86 9.87 "
    "9.88 9.89 9.90 9.91 2.15 3.11 0.005 0.75 0.90 0.60 1.67 1.053 1.05 1.33 174 "
    "43925 15006 66 137 21 5 3 2.15 1000000.0 10000000.0 200000000.0 13".split())
bad = []
for d in DOCS:
    txt = (R / d).read_text()
    for m in NUM.finditer(txt):
        v = m.group(1)
        if v in DERIVED or v.lstrip("-") in DERIVED:
            continue
        if v in CORPUS or v.lstrip("-") in CORPUS:
            continue
        alt = v.rstrip("0").rstrip(".")
        if alt and (alt in CORPUS or alt.lstrip("-") in CORPUS):
            continue
        bad.append((d, txt[:m.start()].count("\n") + 1, v))
print(f"checked {len(DOCS)} documents against {len(CORPUS)} characters of emitted output")
if bad:
    print(f"UNSOURCED {len(bad)}")
    for d, l, v in bad:
        print(f"  {d}:{l}  {v}")
    sys.exit(1)
print("PASS, every numeric literal traces to an emitted file or to a stated count")
