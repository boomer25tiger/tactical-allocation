"""Session 21 phase A. The unwired-config sweep.

The class is the inverse of session 20's B3. B3 found literals duplicating a
config value. This finds config values with no consumer.

TOLERANCE, STATED BEFORE THE COMPARISON IT GOVERNS.
  TOL_CANON = 5e-7 absolute on the standing positive control.

Classification of a read.
  engine        a read inside the return-generating path, being the sleeve
                logic, the loader, the indicators, the execution and portfolio
                layers, the schedule, the spread estimators, or the backtest
                engine and the modules the canonical run imports.
  harness       a read in a session script that builds panels or metrics but is
                not itself the return-generating path.
  validate_only a read that occurs only inside config.validate.
  none          no read anywhere outside config.py.
"""
from __future__ import annotations
import ast, csv, re, resource, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
import scripts.s17_common as S      # noqa: E402
from src import config              # noqa: E402
OUT = ROOT / "outputs" / "session-21"; OUT.mkdir(parents=True, exist_ok=True)
TOL = 5e-7
t0 = time.time()
rows = []

ENGINE = {"src/sleeves.py", "src/portfolio.py", "src/execution.py", "src/data.py",
          "src/indicators.py", "src/schedule.py", "src/spread.py",
          "scripts/s13_backtest.py", "scripts/s14_common.py", "scripts/s15_lines.py"}

# ---- standing positive control -------------------------------------------
env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]
acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
d = acc["daily"]
r_can = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
m = L.standalone_metrics(r_can, d["nav"], acc["orders"])
ok = (abs(m["ann_return"] - 0.521845) <= TOL and abs(m["sharpe_lo"] - 1.381701) <= TOL
      and len(r_can) == 2472)
for k, v, tgt in (("ann_return", m["ann_return"], 0.521845),
                  ("sharpe_lo", m["sharpe_lo"], 1.381701),
                  ("n_sessions", float(len(r_can)), 2472.0)):
    rows.append({"table": "positive_control", "param": k, "value": v, "target": tgt,
                 "abs_gap": abs(v - tgt)})
rows.append({"table": "positive_control", "param": "tolerance", "value": TOL,
             "note": "stated before comparing"})
rows.append({"table": "positive_control", "param": "verdict",
             "note": "PASS" if ok else "FAIL"})
print(f"standing positive control {'PASS' if ok else 'FAIL'}: "
      f"{m['ann_return']:.6f} {m['sharpe_lo']:.6f} n={len(r_can)}")

# ---- every config parameter and who reads it -----------------------------
cfg_src = (ROOT / "src" / "config.py").read_text()
tree = ast.parse(cfg_src)
params = []
for n in tree.body:
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name) and t.id.isupper():
                params.append((t.id, n.lineno))
# names referenced inside config.validate only
val_fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "validate"]
val_names = set()
if val_fn:
    val_names = {x.id for x in ast.walk(val_fn[0]) if isinstance(x, ast.Name)}

files = sorted(list((ROOT / "scripts").glob("*.py")) + list((ROOT / "src").glob("*.py")))
text = {}
for p in files:
    rel = str(p.relative_to(ROOT))
    if rel == "src/config.py":
        continue
    text[rel] = p.read_text()

AXIS_ATTRS = {a[2] for a in S.AXES}
GRID_ATTRS = {a[1] for a in S.AXES} | {u[1] for u in S.UNSEARCHED_AXES}
# A read is a code reference, not prose. Regex over raw lines counted
# docstring text such as "SIZING_MODE selects fractional shares" as a read, so
# detection is done on the abstract syntax tree instead. A read is either
# config.NAME as an attribute, or a bare NAME where the module imported it
# directly from src.config.
def reads_in(txt):
    try:
        t = ast.parse(txt)
    except SyntaxError:
        return {}
    direct = set()
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.module in ("src.config", "config"):
            direct |= {a.asname or a.name for a in n.names}
    out = {}
    for n in ast.walk(t):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                and n.value.id in ("config", "cfg") :
            out.setdefault(n.attr, []).append(n.lineno)
        elif isinstance(n, ast.Name) and n.id in direct:
            out.setdefault(n.id, []).append(n.lineno)
    return out


READS = {rel: reads_in(txt) for rel, txt in text.items()}


# Some modules read config dynamically through getattr(config, "NAME"), which no
# attribute walk can see. s17_common stores each axis's grid-tuple name as a
# string and resolves it that way, so string constants in a module that calls
# getattr on config count as reads of the names they spell.
def dynamic_reads(txt):
    try:
        t = ast.parse(txt)
    except SyntaxError:
        return set()
    uses_getattr = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                       and n.func.id == "getattr" and n.args
                       and isinstance(n.args[0], ast.Name) and n.args[0].id == "config"
                       for n in ast.walk(t))
    if not uses_getattr:
        return set()
    return {c.value for c in ast.walk(t)
            if isinstance(c, ast.Constant) and isinstance(c.value, str)
            and c.value.isupper()}


DYN = {rel: dynamic_reads(txt) for rel, txt in text.items()}
LINES = {rel: txt.split("\n") for rel, txt in text.items()}

unread, engine_read, harness_read = [], [], []
for name, lineno in params:
    sites = []
    for rel, rmap in READS.items():
        for ln in rmap.get(name, []):
            sites.append((rel, ln, LINES[rel][ln - 1].strip()[:90]))
    for rel, names in DYN.items():
        if name in names and not any(s2[0] == rel for s2 in sites):
            sites.append((rel, 0, f"resolved dynamically through getattr(config, "
                                  f"\"{name}\")"))
    eng = [s for s in sites if s[0] in ENGINE]
    cls = "engine" if eng else ("harness" if sites else
                                ("validate_only" if name in val_names else "none"))
    first = (eng or sites or [("", "", "")])[0]
    rows.append({"table": "parameter", "param": name, "config_line": lineno,
                 "classification": cls, "n_reading_files": len({s[0] for s in sites}),
                 "reading_site": f"{first[0]}:{first[1]}" if first[0] else "",
                 "reading_code": first[2],
                 "on_grid_axis": int(name in AXIS_ATTRS),
                 "is_axis_grid_tuple": int(name in GRID_ATTRS),
                 "reads_all_files": " ".join(sorted({s[0] for s in sites}))})
    if cls in ("none", "validate_only"):
        unread.append(name)
    elif cls == "engine":
        engine_read.append(name)
    else:
        harness_read.append(name)

# a read inside an engine file but in a function the canonical run never calls
DEAD = []
for nm in ("SIZING_MODE", "EXECUTION_MODE"):
    called = any("size_position" in LINES[f][i - 1] and not LINES[f][i - 1].strip().startswith("#")
                 for f in ("scripts/s13_backtest.py", "src/portfolio.py") if f in LINES
                 for i in range(1, len(LINES[f]) + 1))
    if not called:
        DEAD.append(nm)
        rows.append({"table": "dead_read", "param": nm,
                     "classification": "read in an engine file, never invoked",
                     "note": "src/execution.py reads it as a default argument of "
                             "size_position, and no module in the return-generating path "
                             "calls size_position. The engine hardcodes math.trunc at "
                             "scripts/s13_backtest.py:528, so the parameter has a read "
                             "site but no influence on any result"})

print(f"\nparameters {len(params)}: engine {len(engine_read)}, harness "
      f"{len(harness_read)}, unread or validate-only {len(unread)}")
print(f"  unread or validate-only: {unread}")
print(f"  read but never invoked: {DEAD}")

# ---- claims made about unread parameters ---------------------------------
CLAIM_FILES = ([ROOT / "docs/DECISIONS-v3.md"] + sorted(ROOT.glob("outputs/*/REPORT*.md"))
               + sorted(ROOT.glob("outputs/*/MANIFEST.json")))
for name in unread:
    hits = 0
    for f in CLAIM_FILES:
        try:
            t = f.read_text()
        except Exception:
            continue
        for i, line in enumerate(t.split("\n"), 1):
            if re.search(rf"\b{re.escape(name)}\b", line):
                hits += 1
                rows.append({"table": "claim_on_unread", "param": name,
                             "reading_site": f"{f.relative_to(ROOT)}:{i}",
                             "reading_code": line.strip()[:110]})
    rows.append({"table": "claim_count", "param": name, "value": hits,
                 "note": "documentation sites naming a parameter no code path reads"})

# ---- the two named explicitly --------------------------------------------
for nm in ("FINANCING_SPREAD_BP",):
    sites = [(rel, i, l.strip()[:90]) for rel, txt in text.items()
             for i, l in enumerate(txt.split("\n"), 1)
             if re.search(rf"\b{nm}\b", l) and not l.strip().startswith("#")]
    eng = [s for s in sites if s[0] in ENGINE]
    rows.append({"table": "named_check", "param": nm,
                 "classification": "engine" if eng else ("harness" if sites else "none"),
                 "n_reading_files": len(sites),
                 "reads_all_files": " ".join(sorted({s[0] for s in sites})),
                 "note": "D16 records the financing spread as assumed and treated by the "
                         "cost sweep; this row establishes whether the engine reads it"})
    print(f"  {nm}: {'engine' if eng else ('harness' if sites else 'NO READER')}, "
          f"files {sorted({s[0] for s in sites})}")

comp = [(rel, i, l.strip()[:100]) for rel, txt in text.items()
        for i, l in enumerate(txt.split("\n"), 1)
        if "unavailable_fills.append" in l or "Cannot price" in l]
rows.append({"table": "named_check", "param": "completion_rule",
             "classification": "engine, hardcoded, no config parameter",
             "n_reading_files": len(comp),
             "reads_all_files": " ".join(sorted({c[0] for c in comp})),
             "note": "scripts/s13_backtest.py lines 18 to 24 mark it PROVISIONAL and not "
                     "a register closure while it sits in the return-generating path. It "
                     "is not a config parameter at all, so it cannot be unwired; it is "
                     "unregistered rather than unread"})

# ---- gate A ---------------------------------------------------------------
axis_unread = [a for a in AXIS_ATTRS if a in unread]
grid_unread = [a for a in GRID_ATTRS if a in unread]
rows.append({"table": "gate_A", "param": "axis_attrs_unread", "value": len(axis_unread),
             "note": " ".join(axis_unread) if axis_unread else
                     "every one of the nine grid axis attributes is read by the engine"})
rows.append({"table": "gate_A", "param": "axis_grid_tuples_unread",
             "value": len(grid_unread), "note": " ".join(grid_unread),
             "note2": "the tuples enumerating each axis are read by the grid harness "
                      "rather than by the engine, which is expected since the engine "
                      "consumes the bound value and not the tuple"})
rows.append({"table": "gate_A", "param": "verdict",
             "note": "HALT" if axis_unread else "PASS, session continues"})
rows.append({"table": "curve_or_axis_overlap", "param": "unread_on_curve_or_axis",
             "value": len([u for u in unread if u in AXIS_ATTRS or u in GRID_ATTRS]),
             "note": " ".join([u for u in unread if u in AXIS_ATTRS or u in GRID_ATTRS])})
print(f"\ngate A: {len(axis_unread)} of the nine axis attributes unread -> "
      f"{'HALT' if axis_unread else 'PASS'}")

COLS = ["table", "param", "config_line", "classification", "n_reading_files",
        "reading_site", "reading_code", "on_grid_axis", "is_axis_grid_tuple",
        "reads_all_files", "value", "target", "abs_gap", "note", "note2"]
with open(OUT / "unwired-config.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'unwired-config.csv'} with {len(rows)} rows")
print(f"phase A peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9:.3f} GB, "
      f"{time.time()-t0:.1f}s")
