"""Session 31 phase B. The environment.

requirements.txt is GENERATED FROM THE CURRENT ENVIRONMENT rather than from an
authoritative record, since none exists. Session 18s rebuilt the environment from a
pre-removal freeze and the register notes that the zero version divergence it
reported is partly a construction of that method.
"""
from __future__ import annotations

import ast
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-31"
PY = ROOT / ".venv" / "bin" / "python"
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True,
                          cwd=ROOT).stdout


pyver = sh(f"{PY} -V").strip()
add("environment", item="python", value=pyver)
add("environment", item="interpreter", value=".venv/bin/python")

freeze = [l for l in sh(f"{PY} -m pip freeze").split("\n") if l and "==" in l]
installed = {l.split("==")[0].lower(): l.split("==")[1] for l in freeze}
add("environment", item="installed_packages", value=len(installed))

# every module the codebase imports
IMPORTS = set()
for p in sorted(ROOT.rglob("*.py")):
    if ".venv" in p.parts:
        continue
    try:
        tree = ast.parse(p.read_text(errors="ignore"))
    except Exception:
        continue
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                IMPORTS.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            IMPORTS.add(n.module.split(".")[0])
STDLIB = set(sys.stdlib_module_names)
LOCAL = {"scripts", "src", "tests"}
THIRD = sorted(m for m in IMPORTS if m not in STDLIB and m not in LOCAL)
add("imports", item="modules_imported", value=len(IMPORTS))
add("imports", item="third_party_modules", value=len(THIRD), note=", ".join(THIRD))

# the distribution each third-party module belongs to
DIST = {"yfinance": "yfinance", "numpy": "numpy", "pandas": "pandas",
        "pyarrow": "pyarrow", "requests": "requests", "pytest": "pytest",
        "scipy": "scipy", "matplotlib": "matplotlib", "dateutil": "python-dateutil",
        "bs4": "beautifulsoup4", "lxml": "lxml", "tqdm": "tqdm"}
direct, missing = [], []
for m in THIRD:
    d = DIST.get(m, m).lower()
    if d in installed:
        direct.append((m, DIST.get(m, m), installed[d]))
    else:
        missing.append(m)
for m, d, v in direct:
    add("direct_dependency", item=d, value=v, note=f"imported as {m}")
MISSING_WHY = {
 "AlgorithmImports": "the QuantConnect runtime namespace, imported only by "
                     "docs/source-quantconnect.py, which is the source strategy carried "
                     "as a reference document and is never executed here",
 "s00c_indicators": "a local session 00c module imported by path rather than as a "
                    "package, so it resolves at run time and is not a third-party "
                    "dependency",
 "s00c_rsi": "a local session 00c module imported by path rather than as a package, so "
             "it resolves at run time and is not a third-party dependency",
}
for m in missing:
    add("missing_dependency", item=m, value="ABSENT",
        note=MISSING_WHY.get(m, "imported by the codebase and not present in the "
                                "environment"))
# Runtime requirements nothing imports by name. pandas reads and writes every
# frozen input through read_parquet, whose engine is pyarrow, so a clone carrying
# only the imported set fails on the first data load.
for d, why in (("pyarrow",
                "the parquet engine pandas.read_parquet resolves to. Nothing imports "
                "it by name and every frozen input load needs it"),):
    if d in installed and d not in {x[1].lower() for x in direct}:
        direct.append((d, d, installed[d]))
        add("runtime_requirement", item=d, value=installed[d], note=why)
DIRECT_NAMES = {d.lower() for _, d, _ in direct}
for name, ver in sorted(installed.items()):
    if name not in DIRECT_NAMES:
        add("transitive_or_unused", item=name, value=ver,
            note="present in the environment and imported by nothing in this codebase, "
                 "so it is either a transitive dependency or unused")
add("counts", item="direct_dependencies", value=len(direct))
add("counts", item="missing_from_the_environment", value=len(missing))
add("counts", item="installed_but_not_imported",
    value=len(installed) - len(DIRECT_NAMES))

# ---- write requirements.txt ---------------------------------------------------------
lines = [
    "# Generated from the current environment on 2026-08-23 by session 31.",
    "# NOT an authoritative record. Session 18s rebuilt this environment from a",
    "# pre-removal freeze rather than from a requirements file, and the register",
    "# notes at 10.1 that the zero version divergence it reported is partly a",
    "# construction of that method.",
    "#",
    "# matplotlib is DELIBERATELY ABSENT. The plotting decision at 9.53 draws every",
    "# figure through scripts/s19_svg.py using the standard library alone, so that",
    "# adding matplotlib would change the environment the manifest records.",
    "#",
    f"# {pyver}",
    "",
]
lines += [f"{d}=={v}" for _, d, v in sorted(direct, key=lambda t: t[1].lower())]
(ROOT / "requirements.txt").write_text("\n".join(lines) + "\n")
add("requirements", item="written", value="requirements.txt",
    value_note="", note="pinning every direct dependency at its installed version")
add("requirements", item="generated_from",
    value="the current environment rather than an authoritative record",
    note="no authoritative requirements file exists. requirements-session-00a.txt is a "
         "session 00a artifact and predates the session 18s rebuild")
add("requirements", item="matplotlib_absent", value=1,
    note="deliberately, per the plotting decision at 9.53")
add("requirements", item="pinned_packages", value=len(direct))

fn = ["table", "item", "value", "note"]
with open(OUT / "environment.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote environment.csv, {len(rows)} rows")
print(f"{pyver}, {len(direct)} direct dependencies, {len(missing)} missing, "
      f"{len(installed)-len(DIRECT_NAMES)} installed but not imported")
for _, d, v in sorted(direct, key=lambda t: t[1].lower()):
    print(f"  {d}=={v}")
if missing:
    print("MISSING:", ", ".join(missing))
