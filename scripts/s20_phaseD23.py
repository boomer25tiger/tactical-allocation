"""Session 20 phases D2 and D3."""
from __future__ import annotations
import csv, json, re, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-20"
rows = []

# ---- D2, adopt the emitted N = 121,500 sensitivity row --------------------
ds = list(csv.DictReader(open(ROOT / "outputs/session-19/deflated-sharpe.csv")))
def pick(which, metric, sm="sharpe_naive"):
    for r in ds:
        if (r["table"] == "point" and r["which"] == which and r["metric"] == metric
                and r["sharpe_metric"] == sm):
            return r["value"]
    return ""

rows.append({"table": "grounds", "item": "correction_class", "value": "correctness repair",
             "note": "N equal to 364,500 counts the 7.4 tier-two offset axis, which was "
                     "held at its canonical value of 10 on every specification and "
                     "across which no maximum was ever taken. Selection operates only "
                     "over trials actually drawn, so the evaluated count of 121,500 is "
                     "the count the statistic requires. Recorded as a correctness "
                     "repair with the grounds stated, not as a post-hoc sensitivity, "
                     "and no 9.10 entry is opened"})
rows.append({"table": "adoption", "item": "method",
             "note": "the N equal to 121,500 row session 19 already emitted is adopted "
                     "in full rather than recomputed"})
for which in ("canonical", "in_sample_best"):
    for sm in ("sharpe_naive", "sharpe_lo"):
        for metric in ("sharpe_annualised", "skewness", "excess_kurtosis",
                       "probabilistic_sharpe_vs_zero",
                       "expected_max_sharpe_ann_N_121500",
                       "probabilistic_sharpe_vs_expected_max_N_121500",
                       "deflated_sharpe_N_121500", "deflated_sharpe_N_364500"):
            v = pick(which, metric, sm)
            if v:
                rows.append({"table": "corrected_deflated_sharpe", "item": which,
                             "sharpe_metric": sm, "metric": metric, "value": v,
                             "primary": int(sm == "sharpe_naive"
                                            and metric == "deflated_sharpe_N_121500")})
for r in ds:
    if r["table"] == "cross_section":
        rows.append({"table": "cross_section", "item": r["metric"], "value": r["value"]})
print("D2 corrected primary figures, N equal to 121,500, on the naive Sharpe")
print(f"  canonical      {pick('canonical','deflated_sharpe_N_121500')}")
print(f"  in_sample_best {pick('in_sample_best','deflated_sharpe_N_121500')}")
print(f"  superseded, N equal to 364,500, canonical {pick('canonical','deflated_sharpe_N_364500')}")

# ---- D2, propagation sweep -----------------------------------------------
TARGETS = ["docs/STATE.md", "docs/DECISIONS-v3.md", "outputs/session-19/REPORT.md",
           "outputs/session-19/PBO-REPORT.md", "outputs/session-19/MANIFEST.json",
           "outputs/session-16b/REPORT.md", "src/config.py", "scripts/s19_report.py"]
for rel in TARGETS:
    p = ROOT / rel
    if not p.exists():
        continue
    for i, line in enumerate(p.read_text().split("\n"), 1):
        if "364,500" in line or "364500" in line:
            designates = bool(re.search(r"N (is|equal to|at) \*?\*?364", line)) or \
                         "deflated_sharpe_N_364500" in line or \
                         ("deflated Sharpe" in line and "364" in line)
            rows.append({"table": "propagation", "item": rel, "metric": str(i),
                         "value": line.strip()[:110],
                         "note": "DESIGNATES N, requires correction" if designates
                                 else "states the enumerated space size, which remains "
                                      "true and is not corrected"})
n_des = sum(1 for r in rows if r["table"] == "propagation" and "DESIGNATES" in r["note"])
n_tot = sum(1 for r in rows if r["table"] == "propagation")
rows.append({"table": "propagation_summary", "item": "sites_found", "value": n_tot})
rows.append({"table": "propagation_summary", "item": "sites_designating_N", "value": n_des})
rows.append({"table": "propagation_summary", "item": "sites_left_unchanged",
             "value": n_tot - n_des,
             "note": "364,500 remains the correct size of the enumerated space and the "
                     "correct content of MANIFEST.json's grid.n_enumerated field; only "
                     "its use as the deflated Sharpe's N is corrected"})
print(f"D2 propagation: {n_tot} sites carrying the figure, {n_des} designate N")

# ---- D3, the degradation slope disposition -------------------------------
nc = list(csv.DictReader(open(ROOT / "outputs/session-19_6/m1-nis-correction.csv")))
dn = list(csv.DictReader(open(ROOT / "outputs/session-19_6/degradation-null.csv")))
def g(rs, t, i, f="value", key="metric"):
    for r in rs:
        if r["table"] == t and r.get(key) == i:
            return r.get(f)
    return ""
rows.append({"table": "slope_disposition", "item": "status", "value": "UNRESOLVED",
             "note": "no valid null exists for the degradation slope. Session 19.6's "
                     "null permuted block ordering independently per specification, "
                     "which destroys the common time structure every specification "
                     "shares, so its four z-scores measure the presence of that shared "
                     "structure rather than overfitting"})
rows.append({"table": "slope_disposition", "item": "corrected_n_is_slope",
             "value": g(nc, "correction", "degradation_slope"),
             "note": "the B1-corrected value at chunk 514 from "
                     "outputs/session-19_6/m1-nis-correction.csv, carried here since the "
                     "phase B1 re-emission halted on the memory gate"})
rows.append({"table": "slope_disposition", "item": "as_emitted_slope",
             "value": g(nc, "correction", "degradation_slope", "as_emitted")})
rows.append({"table": "slope_disposition", "item": "candidate_for_removal", "value": 1,
             "note": "the statistic is a candidate for removal from the paper. No "
                     "recommendation is made on whether to remove it"})
rows.append({"table": "estimator_control", "item": "pbo_null_mean",
             "value": g(dn, "null", "pbo", key="item"),
             "note": "retained as an estimator control rather than as a test. A harness "
                     "fed selection driven purely by idiosyncratic noise returned "
                     "near-total overfitting, which is a validation of the harness that "
                     "session 19's observed 0.157809 never carried"})
rows.append({"table": "estimator_control", "item": "pbo_observed",
             "value": g(dn, "observed_vs_null", "pbo", key="item")})
print(f"D3 slope recorded UNRESOLVED; PBO null mean {g(dn,'null','pbo',key='item')} "
      f"against observed {g(dn,'observed_vs_null','pbo',key='item')}")

with open(OUT / "deflated-sharpe-corrected.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table", "item", "sharpe_metric", "metric",
                                        "value", "primary", "note"],
                        extrasaction="ignore")
    wr.writeheader(); wr.writerows(rows)
print(f"wrote {OUT/'deflated-sharpe-corrected.csv'} with {len(rows)} rows")
