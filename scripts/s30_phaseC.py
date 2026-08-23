"""Session 30 phase C. The disposition and one restatement.

C1 records the three options with their consequences as measured and adopts none,
since the choice is a research decision. C2 restates session 28's G3 comparison on
one convention at a time.
"""
from __future__ import annotations

import csv
import hashlib
import math
import os
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402

OUT = ROOT / "outputs" / "session-30"
S27 = ROOT / "outputs" / "session-27"
BOUNDARY = bt.HOLDOUT_BOUNDARY
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


SW = list(csv.DictReader(open(OUT / "corporate-action-sweep.csv")))


def sw(t, i, w=None):
    for r in SW:
        if r["table"] == t and r["item"] == i and (w is None or r["window"] == w):
            return r
    return {}


# ================================ C1 ==============================================
breaks = [(r["item"], r["date"]) for r in SW
          if r["table"] == "break_classification" and r["value"] == "1"]
add("measured_facts", item="breaks_found", value=len(breaks),
    note="; ".join(f"{t} {d}" for t, d in breaks))
add("measured_facts", item="SVXY_2018-02-06_is_a_proxy_limitation", value=1,
    note="it is classified a break by the conjunction of the two screens while the "
         "underlying event is the February 2018 volatility spike. The frozen "
         "constant-maturity thirty-day series understates a front-month move, so the "
         "volatility proxy cannot discriminate a real spike from an adjustment there, "
         "which the sweep pre-registered as a known limitation")
add("measured_facts", item="the_only_unexplained_break", value="SOXS 2026-05-26",
    note="the residual reads -0.8113452842932015 against a registered multiple of -3.0 "
         "and an SMH return of 0.04480151130636223, with no corporate action in the "
         "frozen record")
for w in ("holdout", "primary"):
    r = sw("B2_summary", "cumulative_flagged_contribution", w)
    add("measured_facts", item="cumulative_flagged_contribution", window=w,
        value=r.get("value"), note=r.get("note"))
    m = sw("B2_summary", "instruments_material_under_the_gate", w)
    add("measured_facts", item="instruments_material", window=w, value=m.get("value"),
        note=m.get("note"))
add("measured_facts", item="contaminated_sessions_coinciding_with_a_firing",
    value=sw("B3_summary",
             "contaminated_sessions_coinciding_with_a_terminal_firing").get("value"))
add("measured_facts", item="gate_B_verdict", value=sw("gate_B", "verdict").get("value"),
    note=sw("gate_B", "verdict").get("note"))

# ---- option one, repair the frozen input --------------------------------------------
SOXS_P = ROOT / "data" / "raw" / "etf" / "SOXS.parquet"
h = hashlib.sha256(SOXS_P.read_bytes()).hexdigest()
add("option_1_repair", item="file_that_changes", value="data/raw/etf/SOXS.parquet",
    note=f"its current SHA-256 is {h}")
man = []
for p in sorted(ROOT.glob("outputs/session-*/*manifest*.csv")):
    try:
        txt = p.read_text(errors="ignore")
    except Exception:
        continue
    if "SOXS" in txt:
        man.append(str(p.relative_to(ROOT)))
add("option_1_repair", item="manifest_entries_that_change", value=len(man),
    note="; ".join(man))
sessions = sorted({p.parent.name for p in ROOT.glob("outputs/session-*/*.csv")
                   if "input-verification" in p.name or "gates" in p.name})
add("option_1_repair", item="prior_sessions_whose_integrity_check_would_not_reproduce",
    value=len(sessions), note="; ".join(sessions) +
    ". Each verified 339 hashed inputs against the manifests and each would fail on the "
    "repaired file until its manifest is rewritten too")
add("option_1_repair", item="the_holdout_has_already_been_read", value=1,
    note="the repair would change an input after the single read the study's design "
         "permits, so the holdout figures would no longer be the ones the frozen record "
         "produced")
add("option_1_repair", item="measured_effect_on_the_holdout", value="0.0",
    note="SOXS carries zero weight across 2026-05-18 to 2026-06-05, so the repaired "
         "series changes no holdout return through the position path")

# ---- option two, disclose unrepaired ------------------------------------------------
add("option_2_disclose", item="impact_bound", window="holdout",
    value=sw("B2_summary", "cumulative_flagged_contribution", "holdout").get("value"),
    note="the cumulative contribution of every flagged session in the window, which "
         "bounds the whole class rather than the one instance")
add("option_2_disclose", item="known_defective_series_remains", value=1,
    note="SOXS stays inside the study with a session the record cannot explain")
add("option_2_disclose", item="no_hash_changes", value=1)

# ---- option three, register and add a permanent check ---------------------------------
add("option_3_permanent_check", item="what_implementing_it_involves",
    value="one script and one call site",
    note="the screen is scripts/s30_phaseB.py section B1, which reads src/schedule.py "
         "for the registered multiple and a frozen proxy for the underlying and "
         "compares the tracking residual against a fixed tolerance. Lifting it into a "
         "standalone module and calling it beside scripts/s195_verify_inputs.py is the "
         "whole of the work")
add("option_3_permanent_check", item="where_it_would_sit",
    value="beside the input-integrity check",
    note="scripts/s195_verify_inputs.py runs as a precondition in every session that "
         "measures. The implied-multiple screen answers a question the hash check "
         "cannot, being whether a series the hash confirms unchanged is also internally "
         "consistent with its own registered terms")
add("option_3_permanent_check", item="no_hash_changes", value=1)
add("option_3_permanent_check", item="cost_per_session_seconds", value="",
    note="the sweep screened 43925 instrument-sessions in this session inside the same "
         "environment build every measuring session already performs, so the marginal "
         "cost is the screen itself rather than a new environment build")

add("disposition", item="adopted", value="none",
    note="the choice is a research decision and this session records the three options "
         "with their measured consequences without adopting any")

# ================================ C2 ==============================================
hl = pd.read_parquet(S27 / "_holdout_line_returns.parquet")
cl = pd.read_parquet(S27 / "_combined_line_returns.parquet")
prim = cl["STRATEGY"].loc[cl.index < BOUNDARY].dropna()
hold = hl["STRATEGY"].dropna()


def lo_sharpe(x, qq=252):
    mu, sd = x.mean(), x.std(ddof=1)
    xc = x - mu
    den = float(np.dot(xc, xc))
    acf = sum((qq - k) * float(np.dot(xc[:-k], xc[k:])) / den for k in range(1, qq))
    scale = qq + 2.0 * acf
    if scale <= 0:
        return float("nan")
    return float((mu / sd) * qq / math.sqrt(scale) * math.sqrt(252.0 / qq))


for wname, ser in (("holdout", hold), ("primary", prim)):
    rf = bt.rf_per_session(ser.index).reindex(ser.index).fillna(0.0)
    years = sorted({d.year for d in ser.index})
    base_x = (ser - rf).dropna().to_numpy()
    base_n = float(base_x.mean() / base_x.std(ddof=1) * math.sqrt(252.0))
    base_l = lo_sharpe(base_x)
    add("C2_base", item=wname, sharpe_naive=q(base_n), sharpe_lo=q(base_l),
        n_sessions=len(base_x), note="the window unmodified")
    est = {}
    for y in years:
        idx = ser.index[ser.index.year != y]
        x = (ser.reindex(idx) - rf.reindex(idx)).dropna().to_numpy()
        nv, lv = float(x.mean() / x.std(ddof=1) * math.sqrt(252.0)), lo_sharpe(x)
        est[y] = (nv, lv)
        add("C2_estimate", item=str(y), window=wname, sharpe_naive=q(nv),
            sharpe_lo=q(lv), n_sessions=len(x),
            note="the window with that calendar year removed")
    for conv, ix in (("naive", 0), ("lo", 1)):
        vals = {y: est[y][ix] for y in years}
        lo_y = min(vals, key=lambda k: vals[k]); hi_y = max(vals, key=lambda k: vals[k])
        base = base_n if conv == "naive" else base_l
        mv = max(vals, key=lambda k: abs(vals[k] - base))
        add("C2_range", item=conv, window=wname,
            value=f"{vals[lo_y]!r} to {vals[hi_y]!r}", n_sessions=len(years),
            note=f"minimum when {lo_y} is removed and maximum when {hi_y} is removed, "
                 f"against a base of {base!r}")
        add("C2_mover", item=conv, window=wname, value=mv,
            note=f"removing it moves the estimate by {vals[mv]-base!r}")
add("C2_construction", item="series_drop_rather_than_rebuild", value=1,
    note="each estimate here removes the calendar year's sessions from the committed "
         "return series. The primary-window Lo range session 28 quoted, being "
         "1.287076427656795 to 1.6183359759194622, comes from session 22's leave-one-out "
         "REBUILD at outputs/session-22/rebuilt/leave-one-out.csv, which re-ran the "
         "strategy with the year dropped. The two constructions are not the same "
         "quantity, which is a second reason the session 28 comparison does not hold")
add("C2_correction", item="session_28_G3_mixed_conventions", value=1,
    note="session 28's G3 compared the holdout's naive range of 1.4608187196166473 to "
         "1.7121151693407555 against the primary window's Lo range of "
         "1.287076427656795 to 1.6183359759194622, which are different conventions. "
         "Both windows are restated on each convention above. "
         "outputs/session-28/REPORT.md is not edited and the correction stands here")

fn = ["table", "item", "window", "value", "sharpe_naive", "sharpe_lo", "n_sessions",
      "note"]
with open(OUT / "disposition.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote disposition.csv, {len(rows)} rows")
for r in rows:
    if r["table"] in ("C2_range", "gate_B") or r["item"] == "gate_B_verdict":
        print(f"  {r['table']:12s} {r['item']:10s} {r.get('window',''):9s} {r['value']}")
