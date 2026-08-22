"""Session 25 phase D. Which two figures the paper's cap best supports.

The criterion is stated in the scaffold, being which two illustrate the largest
number of primary claims between them. It is applied by enumeration over every
pair rather than by preference, and the tie structure is reported whether or not
the criterion resolves. No selection is made.
"""
from __future__ import annotations
import csv, itertools
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT/"outputs"/"session-25"
rows = []
def add(t, **kw): rows.append({"table": t, **kw})

inv = list(csv.DictReader(open(OUT/"figure-inventory.csv")))
cl = {r["n"]: r for r in csv.DictReader(open(ROOT/"outputs/session-24/claim-sources.csv"))}
tier = {n: r["tier"] for n, r in cl.items()}
draw = [r for r in inv if r["table"] == "candidate" and r["disposition"] == "draw"]
FIGS = {r["item"]: {x for x in r["illustrates_claims"].split(",") if x} for r in draw}
PRIM = {f: {c for c in s if tier[c] == "primary"} for f, s in FIGS.items()}
SUPP = {f: {c for c in s if tier[c] == "supporting"} for f, s in FIGS.items()}
add("cap", item="paper_figure_cap", value=2,
    note="the four-tier scheme caps the paper at two figures, with the rest carried by "
         "the PBO report")
for f in sorted(FIGS):
    add("per_figure", item=f, value=len(PRIM[f]),
        primary_claims=",".join(sorted(PRIM[f], key=int)),
        supporting_claims=",".join(sorted(SUPP[f], key=int)),
        carries_literal=next(r["carries_claim_literal"] for r in draw if r["item"] == f))
pairs = []
for a, b in itertools.combinations(sorted(FIGS), 2):
    u = PRIM[a] | PRIM[b]
    pairs.append((len(u), a, b, ",".join(sorted(u, key=int)),
                  len(SUPP[a] | SUPP[b])))
best = max(p[0] for p in pairs)
top = [p for p in pairs if p[0] == best]
for n, a, b, u, s in sorted(pairs, key=lambda p: (-p[0], p[1], p[2])):
    add("pair", item=f"{a} + {b}", value=n, primary_claims=u,
        supporting_claims=str(s), note="highest" if n == best else "")
add("result", item="largest_primary_coverage", value=best,
    note=f"across the {len(pairs)} pairs of the eight figures")
add("result", item="pairs_at_the_maximum", value=len(top),
    note="; ".join(f"{a} + {b}" for _, a, b, _, _ in top))
if len(top) == 1:
    _, a, b, u, _ = top[0]
    add("result", item="criterion_resolves", value=1,
        note=f"the criterion selects one pair, being {a} and {b}, covering primary "
             f"claims {u}. No other pair reaches {best}")
else:
    add("result", item="criterion_resolves", value=0,
        note="the criterion leaves a tie, so it does not select a pair on its own")
add("result", item="selection_made", value=0,
    note="the scaffold requires the analysis and leaves the choice")
add("result", item="second_criterion_if_needed", value="",
    note="three of the eight carry a claim's literal emitted value in the series they "
         "plot, being cost-sweep, leave-one-out and lo-factor-vs-null. The other five "
         "illustrate a claim's subject or a register finding without plotting any figure "
         "the claim quotes, which is a second ordering available if the primary count "
         "leaves a tie")

# ---- the PBO report's figures and the duplication question -------------------
already = [r for r in inv if r["table"] == "already_drawn"]
for r in already:
    add("pbo_report_carries", item=r["item"], value=r["value"],
        primary_claims=r["illustrates_claims"], note=r["note"])
dup = [r["item"] for r in draw
       if r["item"] in {x["item"].replace(".svg", "") for x in already}]
add("duplication", item="figures_in_the_eight_duplicating_a_report_figure", value=len(dup),
    note="none. The three candidates that would have duplicated one were excluded at "
         "phase B, being logit-histogram, is-vs-oos-scatter and specification-curve, so "
         "the eight and the report's four are disjoint")
add("duplication", item="report_figures_illustrating_a_withdrawn_statistic", value=1,
    note="degradation-scatter.svg carries a fitted line for the degradation slope "
         "withdrawn at 9.35. The logit histogram carries the PBO, which is claim 4 and "
         "stands, so the session 24 specification's note that two of the four support a "
         "statistic since removed overstates it by one")

fn = ["table","item","value","primary_claims","supporting_claims","carries_literal","note"]
with open(OUT/"paper-figure-analysis.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
    for r in rows: w.writerow({k: r.get(k,"") for k in fn})
print(f"wrote paper-figure-analysis.csv, {len(rows)} rows")
print(f"maximum primary coverage by a pair {best}, pairs at the maximum {len(top)}")
for _, a, b, u, _ in top: print(f"  {a} + {b}  primary claims {u}")
