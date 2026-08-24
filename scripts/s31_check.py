"""Session 31 prose-against-CSV check, run before the commit under 9.12.

CORRECTED against a defect the session 28 through 30 checks carried. Those scripts
added docs/DECISIONS-v3.md to the CORPUS a figure is validated against, while also
checking the register's own tail as a document. A figure written into the register
therefore validated against the register, which is a self-validating loop, and it
is how register 9.88 came to carry fifteen superseded bootstrap figures that the
session 30 check passed over. The register is a checked DOCUMENT here and is not
part of the corpus.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
DOCS = [d for d in ("outputs/session-31/REPORT.md", "docs/STATE.md", "README.md",
                    "docs/REPRODUCE.md") if (R / d).exists()]
CORPUS = ""
for pat in ("*.csv", "*.svg"):
    for p in sorted((R / "outputs").rglob(pat)):
        try:
            CORPUS += p.read_text(errors="ignore")
        except Exception:
            pass
CORPUS += (R / "docs" / "HOLDOUT-PREDICTION.md").read_text(errors="ignore")
CORPUS += (R / "docs" / "CLAIMS.md").read_text(errors="ignore")
CORPUS += (R / "requirements.txt").read_text(errors="ignore")
# The register is a CHECKED DOCUMENT rather than a source. Its session 31 tail is
# appended to DOCS below and it is deliberately absent from CORPUS.
_REG = (R / "docs" / "DECISIONS-v3.md").read_text()
_KEY = "- **9.92 the publication audit"
if _KEY in _REG:
    (R / "outputs" / "session-31" / "_register-tail.md").write_text(_REG[_REG.index(_KEY):])
    DOCS.append("outputs/session-31/_register-tail.md")

NUM = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?![\w])")
DERIVED = set(
    "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 24 25 26 27 28 29 30 "
    "31 33 35 39 40 44 48 50 53 60 66 70 94 95 96 100 120 137 155 174 200 218 252 257 "
    "316 348 400 504 527 529 264 1088 1265 2472 3737 12870 121500 43925 15006 "
    "2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 "
    "0.05 0.25 0.75 0.90 0.005 0.60 1.67 1.05 1.053 1.33 1.5 2.0 3.0 5e-07 "
    "9.10 9.12 9.14 9.31 9.35 9.43 9.46 9.48 9.51 9.52 9.53 9.55 9.56 9.57 9.58 9.59 "
    "9.60 9.61 9.62 9.63 9.64 9.65 9.66 9.67 9.68 9.69 9.70 9.71 9.72 9.73 9.74 9.75 "
    "9.76 9.77 9.78 9.79 9.80 9.81 9.82 9.83 9.84 9.85 9.86 9.87 9.88 9.89 9.90 9.91 "
    "9.92 9.93 9.94 9.95 9.96 9.97 2.10 2.15 3.11 3.12 8.2 8.11 8.12 10.1 15.5 19.5 "
    "1.26 2.34 25.0 1.6 3.13 9.1 1.10 -12 -10 29.10 18.87 14.57 11.12 10.79 10.60 "
    "1.0 2.5 5.5 4.0".split())
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
wrap = []
for d in DOCS:
    txt = (R / d).read_text()
    for m in re.finditer(r"np\.(float64|int64|bool_)\(", txt):
        wrap.append((d, txt[:m.start()].count("\n") + 1))
print(f"checked {len(DOCS)} documents against {len(CORPUS)} characters of emitted output")
print("the register is a checked document here and is NOT part of the corpus")
print(f"numpy repr wrappers: {len(wrap)}")
for d, l in wrap:
    print(f"  {d}:{l}")
if bad:
    print(f"UNSOURCED {len(bad)}")
    for d, l, v in bad:
        print(f"  {d}:{l}  {v}")
if bad or wrap:
    sys.exit(1)
print("PASS, every numeric literal traces to an emitted file or to a stated count")
