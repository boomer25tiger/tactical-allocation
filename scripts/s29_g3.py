"""Session 29, the G3 text inspection.

Phases C, D, E, F, G1 and G2 did NOT run, since gate B fired. G3 is a text
inspection of a committed markdown document with no dependence on any price
series, so it is completed here and its scope is stated rather than assumed.
"""
from __future__ import annotations
import csv, re
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = R / "outputs" / "session-29"
rows = []
def add(**kw): rows.append(kw)

add(item="scope", value="text inspection",
    note="G3 reads outputs/session-28/REPORT.md alone. It touches no price series and "
         "computes no quantity, so gate B's halt of the measurement phases does not "
         "reach it. G1 and G2 are measurements on the holdout series and did not run")
T = (R / "outputs" / "session-28" / "REPORT.md").read_text()
pat = re.compile(r"np\.float64\(([^)]*)\)")
hits = list(pat.finditer(T))
add(item="numpy_repr_wrappers_found", value=len(hits),
    note="the scaffold names two and the document carries this many")
for m in hits:
    ln = T[:m.start()].count("\n") + 1
    ctx = T.split("\n")[ln - 1]
    where = ("the corrections item 12 line" if "item 12" in ctx else
             "the timing materiality line" if "timing component is material" in ctx
             else "another line")
    add(item=f"line_{ln}", value=m.group(0), corrected_to=m.group(1), line=ln,
        note=f"{where}. The digits are correct and only the wrapper is spurious")
add(item="cause", value="numpy scalar formatted with repr",
    note="scripts/s15_lines.py standalone_metrics returns numpy scalars, and session 28 "
         "formatted several of them with the repr conversion inside an f-string note, "
         "which the emitted CSV then carried into the report unchanged")
add(item="register_entries_affected", value=0,
    note="the session 28 register entries carry no wrapper, since those figures were "
         "read from the CSV columns rather than from the note text")
add(item="disposition", value="corrected in the register",
    note="outputs/session-28/REPORT.md is NOT edited. The correction stands in the "
         "register, as the scaffold requires")
add(item="guard_added", value=1,
    note="the session 29 prose check screens for the wrapper before writing rather "
         "than after")
fn = ["item", "value", "corrected_to", "line", "note"]
with open(OUT / "instrument-attribution.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote instrument-attribution.csv, {len(rows)} rows, "
      f"{len(hits)} numpy repr wrappers found")
for r in rows:
    if r["item"].startswith("line_"):
        print(f"  line {r['line']}: {r['value']} -> {r['corrected_to']}")
