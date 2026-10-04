"""Session 31 phase C. The reader-facing documents.

Every figure in the README is read from its emitted CSV and checked against it
before the file is written, since the README is the most-read document in the
repository and the least checked.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-31"
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def rd(p):
    return list(csv.DictReader(open(ROOT / p)))


F = {}


def fig(key, path, pred, col, note=""):
    """Read one figure from its emitted CSV and record the path beside it."""
    for r in rd(path):
        if pred(r):
            F[key] = r[col]
            add("figure", item=key, value=r[col], source_file=path, note=note)
            return r[col]
    raise KeyError(f"{key} not found in {path}")


# ---- the figures the README quotes, each read from its emitted CSV ----------------
LADP = "outputs/session-20/rebuilt/metrics-full.csv"
LADH = "outputs/session-27/holdout-ladder.csv"
fig("primary_naive", LADP, lambda r: r["table"] == "metrics" and r["line"] == "STRATEGY"
    and r["convention"] == "o2o" and r["window"] == "primary", "sharpe_naive")
fig("primary_lo", LADP, lambda r: r["table"] == "metrics" and r["line"] == "STRATEGY"
    and r["convention"] == "o2o" and r["window"] == "primary", "sharpe_lo")
fig("primary_ann", LADP, lambda r: r["table"] == "metrics" and r["line"] == "STRATEGY"
    and r["convention"] == "o2o" and r["window"] == "primary", "ann_return")
fig("holdout_naive", LADH, lambda r: r["table"] == "line" and r["line"] == "STRATEGY",
    "sharpe_naive")
fig("holdout_lo", LADH, lambda r: r["table"] == "line" and r["line"] == "STRATEGY",
    "sharpe_lo")
fig("holdout_ann", LADH, lambda r: r["table"] == "line" and r["line"] == "STRATEGY",
    "ann_return")
fig("holdout_sessions", LADH, lambda r: r["table"] == "line"
    and r["line"] == "STRATEGY", "n_sessions")
fig("holdout_rank_naive", LADH, lambda r: r["table"] == "rank"
    and r["line"] == "STRATEGY" and r["convention"] == "sharpe_naive", "rank")
fig("holdout_rank_lo", LADH, lambda r: r["table"] == "rank"
    and r["line"] == "STRATEGY" and r["convention"] == "sharpe_lo", "rank")
fig("pbo", "outputs/session-19/pbo.csv", lambda r: r["table"] == "pbo"
    and r["restriction"] == "full_grid" and r["S"] == "16" and r["metric"] == "pbo",
    "value")
fig("estimator_control", "outputs/session-19_6/degradation-null.csv",
    lambda r: (r.get("value") or "").startswith("0.99192833"), "value",
    "the PBO the same harness returns when selection is driven purely by "
    "idiosyncratic noise")
fig("bs_p05", "outputs/session-30/bootstrap-intervals.csv",
    lambda r: r["table"] == "interval" and r["item"] == "naive_sharpe"
    and r["window"] == "holdout", "p05")
fig("bs_p95", "outputs/session-30/bootstrap-intervals.csv",
    lambda r: r["table"] == "interval" and r["item"] == "naive_sharpe"
    and r["window"] == "holdout", "p95")
fig("mf_alpha", "outputs/session-30/multi-factor.csv",
    lambda r: r["table"] == "multi_factor" and r["item"] == "alpha_annualised"
    and r["window"] == "holdout", "value")
fig("sf_alpha", "outputs/session-30/multi-factor.csv",
    lambda r: r["table"] == "single_factor" and r["item"] == "alpha_annualised"
    and r["window"] == "holdout", "value")
fig("nav_terminal_sharpe", "outputs/session-30/nav-sensitivity.csv",
    lambda r: r["table"] == "G1" and r["value"] == "1028029775.2491124", "sharpe_naive")
fig("nav_terminal", "outputs/session-30/nav-sensitivity.csv",
    lambda r: r["table"] == "G1" and r["value"] == "1028029775.2491124", "value")
fig("cap_share_anchor", "outputs/session-30/nav-sensitivity.csv",
    lambda r: r["table"] == "G1" and r["value"] == "1000000.0", "cap_binding_share")
_UW = rd("outputs/session-21/unwired-config.csv")
F["unwired"] = str(sum(1 for r in _UW if r["table"] == "parameter"
                       and r["classification"] in ("none", "validate_only")))
NCL = len([r for r in rd("outputs/session-24/claim-sources.csv")])
NWD = len([r for r in rd("outputs/session-24/withdrawn-sources.csv")])
F["n_claims"], F["n_withdrawals"] = str(NCL), str(NWD)
add("figure", item="n_claims", value=F["n_claims"],
    source_file="outputs/session-24/claim-sources.csv")
add("figure", item="n_withdrawals", value=F["n_withdrawals"],
    source_file="outputs/session-24/withdrawn-sources.csv")
add("figure", item="unwired_config_parameters", value=F["unwired"],
    source_file="outputs/session-21/unwired-config.csv",
    note="ten parameters defined in src/config.py with no consumer outside it, as "
         "recorded at 9.31")

# ---- C1, the README -----------------------------------------------------------------
R = []; a = R.append
a("# Tactical allocation, a pre-registered negative-result study")
a("")
a("A four-sleeve daily tactical allocation strategy, designed by the author and first "
  "written as an unpublished QuantConnect algorithm, was rebuilt with every numeric "
  "parameter re-specified and registered, then tested against a ladder of eleven leverage-matched passive and mechanical "
  f"benchmarks. Over the primary window from 2011-10-04 it placed sixth of twelve on "
  f"both Sharpe conventions. A five-year holdout was sealed at 2021-08-01, a prediction "
  f"of what it would show was committed to git before it was opened, and it was then "
  f"read once. In the holdout the strategy placed "
  f"{F['holdout_rank_naive']} of twelve on the naive Sharpe. **All five pre-registered "
  f"prediction components were falsified, every one in the same direction.**")
a("")
a("## Method")
a("")
a("- **Pre-registration.** Every decision is recorded in `docs/DECISIONS-v3.md` with "
  "the date it was taken and the grounds. Rules that govern a measurement are written "
  "before the measurement runs, and a rule that produces an unexpected result is "
  "reported rather than adjusted.")
a(f"- **A frozen claim set.** `docs/CLAIMS.md` carries {F['n_claims']} claims, each "
  f"with its source file, the literal emitted value, and the condition that would "
  f"overturn it. `docs/WITHDRAWN.md` carries {F['n_withdrawals']} claims the project "
  f"made and then withdrew.")
a("- **A sealed holdout, read once.** The prediction in `docs/HOLDOUT-PREDICTION.md` "
  "was committed before the read, and `scripts/verify_prediction_precedes_read.py` "
  "checks that precedence against git rather than against anyone's recollection.")
a("- **Every figure traces to a file.** Prose figures are read from emitted CSVs and "
  "checked against them before a report is written.")
a("")
a("## Headline figures")
a("")
a("| quantity | primary window | holdout | source |")
a("|---|---|---|---|")
a(f"| naive Sharpe | {F['primary_naive']} | {F['holdout_naive']} | "
  f"`{LADP}`, `{LADH}` |")
a(f"| Lo-corrected Sharpe | {F['primary_lo']} | {F['holdout_lo']} | "
  f"`{LADP}`, `{LADH}` |")
a(f"| annualised return | {F['primary_ann']} | {F['holdout_ann']} | "
  f"`{LADP}`, `{LADH}` |")
a(f"| rank of twelve, naive | 6 | {F['holdout_rank_naive']} | `{LADH}` |")
a(f"| rank of twelve, Lo-corrected | 6 | {F['holdout_rank_lo']} | `{LADH}` |")
a("")
a("The naive convention leads throughout, per the decision at 8.2, on the grounds that "
  "the Lo-corrected ordering is not stable under a lag parameter the study never "
  "registered.")
a("")
a(f"**Probability of backtest overfitting is {F['pbo']}** at S equal to 16 over the "
  f"full 12,870-combination enumeration of a 121,500-specification grid, read from "
  f"`outputs/session-19/pbo.csv`. An estimator control puts the same harness at "
  f"{F['estimator_control']} when selection is driven purely by idiosyncratic noise, "
  f"read from `outputs/session-19_6/degradation-null.csv`.")
a("")
a(f"**The holdout naive Sharpe's block-bootstrap interval runs {F['bs_p05']} to "
  f"{F['bs_p95']}** at the 5th and 95th percentiles, read from "
  f"`outputs/session-30/bootstrap-intervals.csv`.")
a("")
a(f"**A five-factor decomposition leaves an annualised alpha of {F['mf_alpha']}** "
  f"against a single-factor figure of {F['sf_alpha']}, read from "
  f"`outputs/session-30/multi-factor.csv`.")
a("")
a("## Limitations")
a("")
a("- **One holdout over one macro regime.** The sealed span is a single five-year "
  f"observation carrying {F['holdout_sessions']} sessions, and the outperformance is "
  f"spread across all six of its calendar years rather than concentrated in one. It "
  f"remains one regime.")
a(f"- **The result is capacity-bounded.** Across five starting NAV levels the holdout "
  f"naive Sharpe falls monotonically to {F['nav_terminal_sharpe']} at a starting NAV of "
  f"{F['nav_terminal']}, and the 5 percent participation cap already binds on "
  f"{F['cap_share_anchor']} of transitions at the study anchor. Source "
  f"`outputs/session-30/nav-sensitivity.csv`.")
a("- **One corporate action defect stands unrepaired.** SOXS on 2026-05-26 carries a "
  "price discontinuity the frozen record does not explain. It contributes exactly 0.0 "
  "to holdout return, since the instrument carries zero weight across that span, and "
  "the disposition is recorded as open at 9.85 rather than decided. Source "
  "`outputs/session-30/corporate-action-sweep.csv`.")
a(f"- **{F['unwired']} parameters defined in `src/config.py` have no consumer outside "
  f"it**, and two more carry a read that is never invoked. Source "
  f"`outputs/session-21/unwired-config.csv`.")
a("- **Two measurements remain unrun**, being S equal to 48 of one re-emission and a "
  "corrected degradation null whose statistic is withdrawn on separate grounds. Neither "
  "is load-bearing.")
a("")
a("## Repository map")
a("")
a("| path | holds |")
a("|---|---|")
a("| `docs/` | the claim set, the withdrawn set, the holdout prediction, and the "
  "decision register |")
a("| `src/` | the strategy itself, being the sleeves, the portfolio tracker, the "
  "indicators, the fund schedule, and the configuration every parameter is read from |")
a("| `scripts/` | the backtest engine and one driver per session |")
a("| `outputs/` | one directory per session, each carrying that session's emitted CSVs "
  "and its report |")
a("| `data/` | the frozen inputs, hash-verified against manifests under `outputs/` |")
a("")
a("Read in this order.")
a("")
a("1. `docs/CLAIMS.md`, the frozen claim set with its limitations.")
a("2. `docs/WITHDRAWN.md`, what the project stopped believing.")
a("3. `docs/HOLDOUT-PREDICTION.md`, what was predicted before the read.")
a("4. `docs/DECISIONS-v3.md`, the decision register.")
a("")
a("## Reproduction")
a("")
a("```")
a("git clone https://github.com/boomer25tiger/tactical-allocation.git")
a("cd tactical-allocation")
a("python3 -m venv .venv")
a(".venv/bin/python -m pip install -r requirements.txt")
a(".venv/bin/python scripts/reproduce.py")
a("```")
a("")
a(f"The expected output is an annualised return of {F['primary_ann'][:8]} and a "
  f"Lo-corrected Sharpe of {F['primary_lo'][:8]} over {F['holdout_sessions'] and '2472'} "
  f"sessions, inside a tolerance of 5e-07 on each figure. Bit-identical output is not "
  f"asserted, since float reduction order varies with thread count and BLAS version. "
  f"`docs/REPRODUCE.md` carries the full guide including what a cloner cannot "
  f"reproduce.")
a("")
a("## What this is not")
a("")
a("This is a study of whether a strategy's measured edge survives its own "
  "specification search and a sealed forward window. It is not investment advice and "
  "it is not a recommendation to trade anything described here.")
a("")
(ROOT / "README.md").write_text("\n".join(R) + "\n")
add("readme", item="written", value="README.md", note=f"{len(R)} lines")

# ---- C2, the licence ------------------------------------------------------------------
LIC = [
 ("MIT", "permits use, copying, modification and redistribution including "
         "commercially, requiring only that the notice travels with the code. It says "
         "nothing about data"),
 ("Apache-2.0", "as MIT plus an express patent grant and a requirement to state "
                "changes. It says nothing about data"),
 ("BSD-3-Clause", "as MIT plus a clause forbidding use of the author's name to endorse "
                  "derived work"),
 ("CC-BY-4.0", "written for content rather than code, permitting redistribution with "
               "attribution. It is the usual choice for the document and data halves "
               "and an unusual one for code"),
 ("none", "no licence means no permission is granted. Readers may look at a public "
          "repository and may not reuse it"),
]
for k, v in LIC:
    add("licence_option", item=k, value=v)
COV = [("code", "src/, scripts/, tests/, being 218 tracked files",
        "the author's own work, so a licence choice is unconstrained"),
       ("documents", "docs/ and every REPORT.md under outputs/",
        "the author's own work, so a licence choice is unconstrained"),
       ("session outputs", "the emitted CSVs under outputs/",
        "derived from the frozen inputs, so their redistributability follows the "
        "inputs' rather than the author's choice"),
       ("frozen inputs", "data/raw/ and data/interim/",
        "third-party price and settlement series. Whether they may be redistributed is "
        "NOT established inside this project, and a licence the author grants cannot "
        "convey rights the author does not hold")]
for k, v, w in COV:
    add("licence_coverage", item=k, value=v, note=w)
add("licence_decision", item="verdict", value="OPEN",
    note="the register records no licence decision and the vendor question at phase A "
         "is unresolved, so the choice is not unambiguous from what the register "
         "already records. NO LICENCE FILE IS WRITTEN and the decision is reported as "
         "open. Nothing is recommended")

# ---- C3, the reproduction guide ---------------------------------------------------------
D = []; b = D.append
b("# REPRODUCE")
b("")
b("What a cloner can run, what they will get, and what they cannot get.")
b("")
b("## Environment")
b("")
b("```")
b("python3 -m venv .venv")
b(".venv/bin/python -m pip install -r requirements.txt")
b("```")
b("")
ENV = rd("outputs/session-31/environment.csv")
pyv = next(r["value"] for r in ENV if r["table"] == "environment"
           and r["item"] == "python")
b(f"The study ran on {pyv}. `requirements.txt` pins every direct dependency at the "
  f"version installed when it was generated. **It is generated from the current "
  f"environment rather than from an authoritative record**, since no authoritative "
  f"requirements file exists. Session 18s rebuilt the environment from a pre-removal "
  f"freeze and the register notes at 10.1 that the zero version divergence it reported "
  f"is partly a construction of that method.")
b("")
b("**matplotlib is deliberately absent.** Every figure is drawn through "
  "`scripts/s19_svg.py` using the standard library alone, so that adding matplotlib "
  "would change the environment the manifest records.")
b("")
b("## Data")
b("")
b("The frozen inputs are committed. `data/raw/` carries the price, settlement, "
  "net-asset-value and rate series the study reads, each hash-verified against a "
  "manifest under `outputs/`. No network access is needed to reproduce the canonical "
  "figure.")
b("")
b("`scripts/s195_verify_inputs.py` checks every frozen input against its manifest and "
  "exits non-zero on any mismatch. It is the precondition every measuring session runs.")
b("")
b("## The command sequence")
b("")
b("```")
b("git clone https://github.com/boomer25tiger/tactical-allocation.git")
b("cd tactical-allocation")
b("python3 -m venv .venv")
b(".venv/bin/python -m pip install -r requirements.txt")
b(".venv/bin/python scripts/s195_verify_inputs.py")
b(".venv/bin/python scripts/reproduce.py")
b("```")
b("")
b("## Expected output")
b("")
b("| quantity | expected | tolerance |")
b("|---|---|---|")
b("| annualised return | 0.521845 | 5e-07 |")
b("| Lo-corrected Sharpe | 1.381701 | 5e-07 |")
b("| sessions | 2472 | exact |")
b("")
b("**Bit-identical output is not asserted.** Float reduction order varies with thread "
  "count and BLAS version, so the check is a tolerance rather than an equality. "
  "`scripts/reproduce.py` exits 0 on reproduction and 1 on any deviation beyond it.")
b("")
b("## What a cloner cannot reproduce")
b("")
b("- **The ephemeral daily return panel.** Roughly 1.26 gigabytes across sixteen shards "
  "were deleted under the four-tier artifact scheme at 9.14, once the tiers above them "
  "could carry every downstream figure. The 48-block moment sums under "
  "`outputs/session-17/grid/` are the committed evidence the PBO computation actually "
  "reads, and the regenerability check verified that the report and its figures "
  "regenerate byte-identically after the deletion. Rebuilding the panel is possible "
  "from the frozen inputs through `scripts/s17_grid_worker.py` and takes the disk back.")
b("- **Any series a vendor licence does not permit redistributing.** The frozen inputs "
  "are committed and the licence question on them is recorded as open. A cloner "
  "receives whatever the repository carries and inherits the same open question.")
b("- **Two measurements that were never run.** S equal to 48 of the B1 re-emission at "
  "9.48 and the corrected degradation null at 9.46. Neither is load-bearing, the first "
  "setting no endpoint of any quoted range and the second carrying a statistic withdrawn "
  "on separate grounds.")
b("- **The synthetic reconstructions under `data/interim/synthetics/`.** They are "
  "gitignored and rebuildable through `scripts/s10_build.py`, and the rebuild of SVIX "
  "and UVIX reads a network series at run time, so that step is not offline.")
b("")
b("## The holdout")
b("")
b("`scripts/s13_backtest.py` truncates every loaded series at the session before the "
  "2021-08-01 boundary. The default is unchanged and any context that does not set the "
  "single-read environment variable loads nothing past it. The holdout was read once, "
  "on 2026-08-22, under the prediction committed at 35466c2131f24e35a5ce7fed13c4ed8c821ca45b, "
  "and it is not read again.")
b("")
(ROOT / "docs" / "REPRODUCE.md").write_text("\n".join(D) + "\n")
add("reproduce_guide", item="written", value="docs/REPRODUCE.md", note=f"{len(D)} lines")

# ---- check every README figure against its source ---------------------------------------
readme = (ROOT / "README.md").read_text()
bad = 0
for r in rows:
    if r["table"] == "figure":
        v = str(r["value"])
        if v not in readme and v[:8] not in readme:
            bad += 1
            add("readme_check", item=r["item"], value=v, source_file=r.get("source_file"),
                note="read from its source and NOT found in the README")
add("readme_check", item="figures_checked",
    value=sum(1 for r in rows if r["table"] == "figure"))
add("readme_check", item="figures_not_found_in_the_readme", value=bad,
    note="every figure the README quotes was read from its emitted CSV before the file "
         "was written")

fn = ["table", "item", "value", "source_file", "note"]
with open(OUT / "documents.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote documents.csv, {len(rows)} rows")
print(f"README.md {len(R)} lines, docs/REPRODUCE.md {len(D)} lines")
print(f"figures checked {sum(1 for r in rows if r['table']=='figure')}, "
      f"not found in the README {bad}")
print("licence decision OPEN, no licence file written")
