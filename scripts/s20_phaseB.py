"""Session 20 phase B. Three defect class sweeps under 9.13, diagnosis pass."""
from __future__ import annotations
import ast, csv, re, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
from src import config          # noqa: E402
import src.sleeves as SL        # noqa: E402
OUT = ROOT / "outputs" / "session-20"
PYFILES = sorted(list((ROOT / "scripts").glob("*.py")) + list((ROOT / "src").glob("*.py")))


def w(name, rows, cols):
    with open(OUT / name, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        wr.writeheader(); wr.writerows(rows)
    print(f"wrote {OUT/name} with {len(rows)} rows")


# ---------- B1, the chunk-first-element class -------------------------------
b1 = []
PAT = re.compile(r"(\w+)\[0\]")
CHUNKY = ("mc", "oc", "chunk", "batch", "shard", "group", "block", "grp", "sub", "part")
for p in PYFILES:
    for i, line in enumerate(p.read_text().split("\n"), 1):
        s = line.strip()
        if s.startswith("#") or "[0]" not in s:
            continue
        for m in PAT.finditer(s):
            var = m.group(1)
            if var not in CHUNKY:
                continue
            b1.append({"table": "site", "file": str(p.relative_to(ROOT)), "line": i,
                       "code": s[:120], "variable": var,
                       "quantity": "session count from the first combination"
                                   if "nvec" in s else "unclassified",
                       "varies_within_collection": 1 if "nvec" in s else "unknown"})
b1.append({"table": "scope", "file": "", "line": len(PYFILES),
           "code": f"{len(PYFILES)} python files scanned under scripts/ and src/",
           "quantity": "chunk, batch, shard, group, block first-element scalars"})
for r in [x for x in b1 if x["table"] == "site"]:
    print(f"  B1 site {r['file']}:{r['line']}  {r['code'][:80]}")
b1.append({"table": "immunity_argument", "file": "outputs/session-19/pbo-strata.csv",
           "code": "confirmed by reasoning rather than by re-running",
           "quantity": "within a chunk the substituted count is one scalar applied to "
                       "every specification, so it multiplies every specification's "
                       "Sharpe by the same factor and preserves the ordering the rank "
                       "and the argmax read. PBO and every stratified PBO are functions "
                       "of that ordering alone, so they are immune. Session 19.6 "
                       "measured a PBO gap of exactly 0.0e+00 at chunk 128, 257 and 514, "
                       "which is the empirical half of the same argument. The strata "
                       "pass is therefore not re-run"})
b1.append({"table": "register", "file": "docs/DECISIONS-v3.md",
           "code": "8.12 records that no arithmetic depends on the chunk size",
           "quantity": "falsified by this sweep; the three regression figures do. "
                       "Recorded as a correctness repair"})
w("chunk-scalar-sweep.csv", b1,
  ["table", "file", "line", "code", "variable", "quantity", "varies_within_collection"])

# ---------- B2, the vacuous-check class -------------------------------------
b2 = []
CHECKS = [
    ("scripts/s19_step10.py", "required-artifact check",
     "ok = all(p.exists() and p.stat().st_size > 0 for p in paths)",
     "all() over an empty list is True, so an empty glob reports PRESENT",
     "assert a minimum count per artifact class before the predicate"),
    ("scripts/s19_step10.py", "regenerability figure count",
     "for f in sorted((OUT / 'figures').glob('*.svg')): h.update(f.read_bytes())",
     "zero figures on both runs still hash equal, so the check passes on an empty "
     "figure set", "assert the figure count equals the number the generator writes"),
    ("scripts/check_report_figures.py", "prose figure check",
     "return 0 if not unmatched else 2",
     "a report with zero decimal figures yields an empty unmatched set and exits 0",
     "assert a minimum prose figure count and a minimum CSV numeric count"),
    ("scripts/s19_step3.py", "additivity accumulator",
     "worst_add, worst_pan = 0.0, 0.0",
     "the accumulators initialise at the passing value, so zero comparisons pass",
     "assert a minimum comparison count before the verdict"),
    ("scripts/s19_step2.py", "per-shard parse consistency",
     "ok = mo.shape[0] == me.shape[0] == ix.size",
     "an empty shard gives 0 == 0 == 0 and reports consistent",
     "assert a positive row count per shard"),
]
for f, name, assertion, why, fix in CHECKS:
    b2.append({"table": "check", "file": f, "item": name, "assertion_before": assertion,
               "passes_on_empty": 1, "why": why, "repair": fix})
b2.append({"table": "scope", "file": "", "item": "checks_examined", "passes_on_empty": len(CHECKS)})
w("vacuous-check-sweep.csv", b2,
  ["table", "file", "item", "assertion_before", "assertion_after", "floor", "basis",
   "passes_on_empty", "why", "repair", "note"])

# ---------- B3, the hardcoded literal class ---------------------------------
b3 = []
AUTH = {}
for nm in dir(config):
    if nm.isupper():
        AUTH[nm] = getattr(config, nm)
HELD = set()
tree = ast.parse((ROOT / "src" / "sleeves.py").read_text())
for n in ast.walk(tree):
    if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict):
        for k in n.value.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                HELD.add(k.value)
    if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant) \
            and isinstance(n.value.value, str) and re.fullmatch(r"[A-Z]{2,5}", n.value.value):
        HELD.add(n.value.value)

WATCH = {"WARMUP_SESSIONS": config.WARMUP_SESSIONS, "SMA_LONG": config.SMA_LONG,
         "SMA_SHORT": config.SMA_SHORT, "OVERSOLD": config.OVERSOLD,
         "OVERBOUGHT_TIER_1": config.OVERBOUGHT_TIER_1,
         "CRASH_THRESHOLD_PCT": config.CRASH_THRESHOLD_PCT,
         "S3_VOTE_THRESHOLD": config.S3_VOTE_THRESHOLD,
         "CRASH_HORIZON_SESSIONS": config.CRASH_HORIZON_SESSIONS,
         "FINANCING_SPREAD_BP": config.FINANCING_SPREAD_BP}
for p in PYFILES:
    if p.name == "config.py":
        continue
    rel = str(p.relative_to(ROOT))
    txt = p.read_text()
    for i, line in enumerate(txt.split("\n"), 1):
        s = line.strip()
        if s.startswith("#") or not s:
            continue
        for nm, val in WATCH.items():
            if nm in s:
                continue
            if re.search(rf"(?<![\w.]){re.escape(str(val))}(?![\w.])", s) and \
                    re.search(r"=\s*[-\d]", s) and "config" not in s:
                b3.append({"table": "literal", "file": rel, "line": i, "literal": str(val),
                           "authoritative_source": f"config.{nm}", "code": s[:100],
                           "diverged": 0,
                           "note": "value agrees with its source, a latent duplicate"})
                break
    tk = set(re.findall(r'"([A-Z]{2,5})"', txt)) & HELD
    if len(tk) >= 3 and p.name != "sleeves.py":
        missing = sorted(HELD - tk)
        extra = sorted(tk - HELD)
        div = int(bool(missing))
        b3.append({"table": "ticker_list", "file": rel, "line": len(tk),
                   "literal": " ".join(sorted(tk)),
                   "authoritative_source": "src/sleeves.py AST, outputs/session-20/held-universe.csv",
                   "diverged": div,
                   "note": ("diverges, omits " + " ".join(missing)) if missing
                           else "agrees with the derived held set"})
div = [r for r in b3 if r.get("diverged") == 1]
b3.append({"table": "summary", "file": "", "literal": str(len(b3)),
           "note": f"{len(div)} divergent instances, the rest agree with their source "
                   f"and are latent rather than active"})
print(f"\nB3 literal sites {len([r for r in b3 if r['table']=='literal'])}, "
      f"ticker-list sites {len([r for r in b3 if r['table']=='ticker_list'])}, "
      f"divergent {len(div)}")
w("hardcoded-literal-sweep.csv", b3,
  ["table", "file", "line", "literal", "authoritative_source", "code", "diverged", "note"])
