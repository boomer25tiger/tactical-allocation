"""Session 27 phase E. The frozen claims against the holdout.

Claims are not amended. A contradiction is reported and left standing.

A claim is marked as bearing on the holdout only where phase C's single pass
produced a holdout counterpart for the quantity the claim states. Where a claim
concerns the strategy but its quantity would need a measurement outside that pass,
being a null, a sweep, a leave-one-out or a regression, it is marked as bearing on
the holdout and not evaluated, since running it here would be a second read.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-27"
CL = {r["n"]: r for r in csv.DictReader(
    open(ROOT / "outputs" / "session-24" / "claim-sources.csv"))}
LAD = {r["line"]: r for r in csv.DictReader(open(OUT / "holdout-ladder.csv"))
       if r["table"] == "line"}
RANK = [r for r in csv.DictReader(open(OUT / "holdout-ladder.csv"))
        if r["table"] == "rank"]
COMB = {r["line"]: r for r in csv.DictReader(open(OUT / "combined-window.csv"))
        if r["table"] == "line"}
rows = []


def rank_of(line, conv):
    r = next(x for x in RANK if x["line"] == line and x["convention"] == conv)
    return int(r["rank"]), int(r["of"])


def add(n, bears, holdout_value, contradicts, note, primary_value=None):
    c = CL[n]
    rows.append({"claim": n, "tier": c["tier"], "category": c["category"],
                 "statement": c["statement"],
                 "primary_window_value": primary_value if primary_value is not None
                 else c["literal_value"],
                 "holdout_value": holdout_value,
                 "bears_on_the_holdout": bears,
                 "contradicted": contradicts, "note": note})


nr, nof = rank_of("STRATEGY", "sharpe_naive")
lr, _ = rank_of("STRATEGY", "sharpe_lo")
s = LAD["STRATEGY"]; q = LAD["buy_hold_QQQ"]
gap_n = float(s["sharpe_naive"]) - float(q["sharpe_naive"])
gap_l = float(s["sharpe_lo"]) - float(q["sharpe_lo"])
add("1", "yes",
    f"rank {nr} of {nof} on the naive Sharpe and {lr} of {nof} on the Lo-corrected; "
    f"STRATEGY naive {s['sharpe_naive']} lo {s['sharpe_lo']}; buy_hold_QQQ naive "
    f"{q['sharpe_naive']} lo {q['sharpe_lo']}; naive gap {gap_n!r} lo gap {gap_l!r}",
    "no",
    "the claim is scoped to the designated cell over the primary window, so a forward "
    "span does not contradict it as written. The holdout value differs from the claim's "
    "value on both conventions and on the sign of both gaps, and that difference is "
    "reported here rather than resolved")

cw = COMB["STRATEGY"]; cq = COMB["buy_hold_QQQ"]
cn, _ = rank_of("STRATEGY", "sharpe_naive")
rows.append({"claim": "1", "tier": "primary", "category": "strategy",
             "statement": "the same claim against the combined window",
             "primary_window_value": CL["1"]["literal_value"],
             "holdout_value": f"combined naive {cw['sharpe_naive']} lo {cw['sharpe_lo']}; "
                              f"buy_hold_QQQ naive {cq['sharpe_naive']} lo "
                              f"{cq['sharpe_lo']}",
             "bears_on_the_holdout": "descriptive only",
             "contradicted": "not applicable",
             "note": "the combined window contains the sample the specification was "
                     "chosen on, so it is not an out-of-sample measurement and carries "
                     "no verdict"})

NOT_EVAL = {
    "2": "the randomization nulls are a primary-window construction and running them on "
         "the holdout is a measurement outside the single pass",
    "3": "the Romano-Wolf family is a primary-window construction and running it on the "
         "holdout is a measurement outside the single pass",
    "11": "the beta decomposition is a regression outside the single pass",
    "12": "the timing decomposition across four estimation windows is outside the "
          "single pass",
    "13": "leave-one-out over the holdout's calendar years is outside the single pass",
    "14": "the Lo q sweep and the no-autocorrelation nulls are outside the single pass",
    "15": "the cost sweep across six slippage levels is outside the single pass",
}
for n, why in NOT_EVAL.items():
    add(n, "yes", "not evaluated", "not evaluated", why)

NO_BEARING = {
    "4": "probability of backtest overfitting is a property of the grid search over the "
         "primary window and a forward span does not test it",
    "5": "the estimator control is a property of the CSCV harness",
    "6": "the within-stratum PBO comparison is a property of the grid",
    "7": "the canonical's own stratum PBO is a property of the grid",
    "8": "the canonical's rank in the specification curve is a property of the grid",
    "9": "the recentred comparison is against the grid's own cross-sectional "
         "distribution",
    "10": "the effective number of independent trials is a property of the grid's "
          "correlation structure",
}
for n, why in NO_BEARING.items():
    add(n, "no", "not applicable", "no", why)

rows.sort(key=lambda r: (int(r["claim"]), r["bears_on_the_holdout"]))
fn = ["claim", "tier", "category", "statement", "primary_window_value",
      "holdout_value", "bears_on_the_holdout", "contradicted", "note"]
with open(OUT / "claims-vs-holdout.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
n_bear = sum(1 for r in rows if r["bears_on_the_holdout"] == "yes")
n_eval = sum(1 for r in rows if r["holdout_value"] not in
             ("not evaluated", "not applicable")
             and r["bears_on_the_holdout"] == "yes")
n_contra = sum(1 for r in rows if r["contradicted"] == "yes")
print(f"wrote claims-vs-holdout.csv, {len(rows)} rows")
print(f"  claims the holdout bears on: {n_bear}")
print(f"  of those, evaluated in this session: {n_eval}")
print(f"  claims the holdout does not bear on: "
      f"{sum(1 for r in rows if r['bears_on_the_holdout']=='no')}")
print(f"  claims contradicted: {n_contra}")
