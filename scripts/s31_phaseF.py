"""Session 31 phase F. The publication instruction.

NOTHING HERE CHANGES VISIBILITY. The steps are reported as an instruction.
"""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-31"
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def rd(p):
    return list(csv.DictReader(open(OUT / p)))


def g(rows_, t, i, f="value"):
    for r in rows_:
        if r["table"] == t and r["item"] == i:
            return r[f]
    return None


AU, CC, HS, DC = (rd("publication-audit.csv"), rd("clean-clone.csv"),
                  rd("history-sweep.csv"), rd("documents.csv"))

# ---- the gates ---------------------------------------------------------------------
GATES = [("A, credentials and keys", g(AU, "gate_A", "verdict"),
          g(AU, "gate_A", "credentials_or_keys_found") + " credential or key patterns "
          "matched across every tracked text file"),
         ("D, the clean-clone reproduction", g(CC, "summary", "gate_D"),
          g(CC, "summary", "gate_D", "note"))]
for name, verdict, note in GATES:
    add("gate", item=name, value=verdict, note=note)
allclear = all(v in ("PROCEED", "PASS") for _, v, _ in GATES)
add("gate", item="all_gates_cleared", value=int(allclear))

# ---- the publication steps, reported rather than executed ------------------------------
STEPS = [
 ("1", "Decide the licence.",
  "The decision is recorded as OPEN at phase C. A public repository with no licence "
  "grants no reuse rights, which may be the intent. The vendor question on the frozen "
  "inputs is also open and a licence the author grants cannot convey rights the author "
  "does not hold"),
 ("2", "Decide whether the personal identifiers stay.",
  "1028 commit-and-path pairs carry an absolute home path and 20 carry an email "
  "address, both across committed history. Removing either requires a full history "
  "rewrite that changes every commit SHA including the one establishing the prediction "
  "predates the read"),
 ("3", "Decide whether CLAUDE.md stays.",
  "It is tracked at the repository root and describes the working discipline the "
  "sessions ran under. It goes public with everything else unless it is removed first"),
 ("4", "Change the visibility.",
  "gh repo edit boomer25tiger/tactical-allocation --visibility public --accept-visibility-change-consequences"),
 ("5", "Or through the web interface.",
  "github.com/boomer25tiger/tactical-allocation, Settings, then General, then Danger "
  "Zone, then Change repository visibility"),
 ("6", "Verify afterwards.",
  "clone the public URL into a scratch directory and run the sequence in "
  "docs/REPRODUCE.md, which is the same sequence phase D verified"),
]
for n, what, how in STEPS:
    add("publication_step", item=n, value=what, note=how)
add("publication_step", item="executed_in_this_session", value=0,
    note="the repository stays private. Nothing in this session changes visibility")

# ---- what a first-time visitor sees --------------------------------------------------------
readme = (ROOT / "README.md").read_text().split("\n")
add("first_visit", item="readme_title", value=readme[0].lstrip("# "))
add("first_visit", item="readme_opening", value=readme[2][:400])
add("first_visit", item="root_listing",
    value=", ".join(sorted(p.name for p in ROOT.iterdir()
                           if not p.name.startswith(".")
                           and p.name not in ("__pycache__",))),
    note="the entries a visitor sees at the repository root")
loc = {}
for p in ROOT.rglob("*"):
    if not p.is_file() or ".git" in p.parts or ".venv" in p.parts:
        continue
    loc[p.suffix or "none"] = loc.get(p.suffix or "none", 0) + p.stat().st_size
top = sorted(loc.items(), key=lambda kv: -kv[1])[:6]
add("first_visit", item="languages_github_will_detect", value="Python",
    note="GitHub's linguist counts source files and excludes data and documentation by "
         "default, and the only source language present is Python. By bytes on disk the "
         "largest extensions are " +
         ", ".join(f"{k} at {v/1048576:.1f} MB" for k, v in top))

# ---- the resume-facing summary -----------------------------------------------------------
def fig(item):
    return g(DC, "figure", item)


ONE = (f"Pre-registered study of a four-sleeve tactical allocation strategy against "
       f"eleven leverage-matched benchmarks, with a five-year holdout sealed at "
       f"2021-08-01, a prediction committed to git before the read, and all five "
       f"prediction components falsified when it was opened once.")
THREE = [
 f"A four-sleeve daily tactical allocation strategy was reconstructed with every "
 f"parameter registered and tested against eleven leverage-matched benchmarks, placing "
 f"sixth of twelve on both Sharpe conventions over the primary window.",
 f"A five-year holdout was sealed at 2021-08-01 and a falsifiable prediction of what it "
 f"would show was committed to git before it was opened, with a verification hook that "
 f"checks that precedence against git rather than against recollection.",
 f"The holdout was read once. The strategy placed {fig('holdout_rank_naive')} of twelve "
 f"on the naive Sharpe at {fig('holdout_naive')}, all five prediction components were "
 f"falsified, and the result is capacity-bounded, the same figure falling to "
 f"{fig('nav_terminal_sharpe')} at a starting NAV of {fig('nav_terminal')}.",
]
add("summary_one_line", item="text", value=ONE)
for i, t in enumerate(THREE, 1):
    add("summary_three_line", item=str(i), value=t)
add("summary", item="carries_the_holdout_result", value=1)
add("summary", item="carries_the_preregistration_discipline", value=1)
add("summary", item="carries_the_sealed_single_read", value=1)
add("summary", item="characterisation", value=0,
    note="neither form calls any figure good or bad and neither describes the strategy "
         "as one anybody should trade")

fn = ["table", "item", "value", "note"]
with open(OUT / "publication.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote publication.csv, {len(rows)} rows")
for name, v, _ in GATES:
    print(f"  gate {name:36s} {v}")
print(f"  all gates cleared: {allclear}")
print()
print("ONE LINE:"); print(" ", ONE)
print("THREE LINE:")
for t in THREE:
    print(" ", t)
