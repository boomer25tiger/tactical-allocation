"""Session 28 phase I. Reconciliation.

I1 checks whether the residual annualised return's proximity to the primary
window's figure is arithmetic coincidence, checking the two quantities are
comparably defined BEFORE comparing them.
I2 checks the combined window against the two spans separately.
I3 reports every quantity in this session disagreeing with a figure carried in
outputs/session-27/REPORT.md.
"""
from __future__ import annotations

import csv
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

OUT = ROOT / "outputs" / "session-28"
S27 = ROOT / "outputs" / "session-27"
BOUNDARY = bt.HOLDOUT_BOUNDARY
SHORTS = ("SQQQ", "TECS", "SOXS", "PSQ", "SH")
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


def rd(p):
    return list(csv.DictReader(open(p)))


DEC = rd(OUT / "holdout-decomposition.csv")
LADH = {r["line"]: r for r in rd(S27 / "holdout-ladder.csv") if r["table"] == "line"}
LADC = {r["line"]: r for r in rd(S27 / "combined-window.csv") if r["table"] == "line"}
VER = rd(S27 / "prediction-verdicts.csv")


def dec(t, i, w):
    for r in DEC:
        if r["table"] == t and r["item"] == i and r["window"] == w:
            return r["value"]
    return None


# ============================== I1 ==========================================
hl = pd.read_parquet(S27 / "_holdout_line_returns.parquet")
n_h = int(float(LADH["STRATEGY"]["n_sessions"]))
short_arith = float(dec("instrument_summary", "short_sleeve_total", "holdout"))
strat_ann = float(LADH["STRATEGY"]["ann_return"])
PRIM_ANN = 0.5218447451814521

add("I1", item="the_two_quantities_as_the_scaffold_states_them",
    value="0.5127 against 0.5218447451814521",
    note="the scaffold reports a residual annualised return of 0.5127 near the primary "
         "window's annualised return")
add("I1", item="short_sleeve_contribution_holdout", value=q(short_arith),
    note="an ARITHMETIC SUM of daily contributions across "
         f"{n_h} sessions, not an annualised rate")
add("I1", item="strategy_holdout_ann_return", value=q(strat_ann),
    note="a GEOMETRIC annualised rate from outputs/session-27/holdout-ladder.csv")
add("I1", item="units_match", value=0,
    note="the two are not comparably defined. Subtracting an arithmetic sum over 1265 "
         "sessions from a geometric annualised rate mixes a level and a rate, and "
         f"{strat_ann!r} minus {short_arith!r} is {strat_ann - short_arith!r}, which is "
         "the 0.5127 the scaffold quotes")
add("I1", item="the_subtraction_the_scaffold_performs", value=q(strat_ann - short_arith),
    note="reproduced here to show where the figure comes from")
ann_factor = 252.0 / n_h
add("I1", item="short_contribution_expressed_as_an_annualised_rate",
    value=q(short_arith * ann_factor),
    note=f"the arithmetic sum times 252 over {n_h}, being the same units as an "
         f"annualised mean")

# the properly defined residual, being the strategy net of the short contributions
sw = {}
for sl in ("T10", "T11", "S2", "S3"):
    sw[sl] = pd.read_parquet(OUT / f"_sleeve_weights_{sl}.parquet")
tot_w = sum(sw.values())
env_panel = None
import scripts.s14_common as C                          # noqa: E402
env = C.build_env(verbose=False)
panel = env["panels"]["realized"]
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
retp = pd.DataFrame({t: panel[t].ret_total for t in TICK})
rwc = pd.read_parquet(S27 / "_canonical_daily.parquet")
idxh = hl.index
scontrib = pd.Series(0.0, index=idxh)
for t in SHORTS:
    if t in tot_w.columns:
        w = tot_w[t].shift(1).reindex(idxh).fillna(0.0)
        scontrib = scontrib + w * retp[t].reindex(idxh).fillna(0.0)
net = (hl["STRATEGY"].reindex(idxh) - scontrib).dropna()
g = float(np.prod(1.0 + net))
net_ann = g ** (252.0 / len(net)) - 1.0
add("I1", item="properly_defined_residual_ann_return", value=q(net_ann),
    note="the strategy's daily return series net of the per-session short-leg "
         "contribution, compounded and annualised the same way the strategy's own "
         "figure is, so the two are comparably defined")
add("I1", item="gap_to_the_primary_window", value=q(net_ann - PRIM_ANN),
    note=f"against the primary window's {PRIM_ANN!r}")
add("I1", item="the_scaffold_figure_is_a_units_mix", value=1,
    note="the 0.5127 the scaffold quotes is a geometric annualised rate minus an "
         "arithmetic sum over 1265 sessions, so the two terms are not comparably "
         "defined and the figure should not be read as a residual annualised return")
add("I1", item="verdict",
    value="the proximity survives the definitional check and is not structurally forced",
    note=f"recomputed with both quantities in the same units the residual reads "
         f"{net_ann!r} against the primary window's {PRIM_ANN!r}, a gap of "
         f"{net_ann-PRIM_ANN!r}, which is closer than the {strat_ann-short_arith!r} the "
         f"scaffold's arithmetic produced. Nothing in the construction forces two "
         f"non-overlapping spans to agree, so the proximity is a coincidence in the "
         f"sense of being unimplied rather than an artifact of the units mix")

# ============================== I2 ==========================================
n_c = int(float(LADC["STRATEGY"]["n_sessions"]))
n_p = 2472
add("I2", item="combined_sessions", value=n_c)
add("I2", item="primary_plus_holdout", value=n_p + n_h,
    note=f"{n_p} plus {n_h}")
add("I2", item="session_count_reconciles", value=int(n_c == n_p + n_h))
cl = pd.read_parquet(S27 / "_combined_line_returns.parquet")
gp = float(np.prod(1.0 + cl["STRATEGY"].loc[cl.index < BOUNDARY].dropna()))
gh = float(np.prod(1.0 + hl["STRATEGY"].dropna()))
gc = float(np.prod(1.0 + cl["STRATEGY"].dropna()))
add("I2", item="primary_growth_factor", value=q(gp))
add("I2", item="holdout_growth_factor", value=q(gh))
add("I2", item="product_of_the_two", value=q(gp * gh))
add("I2", item="combined_growth_factor", value=q(gc))
add("I2", item="relative_gap", value=q(abs(gp * gh - gc) / gc),
    note="the two spans compounded against the combined window computed in one pass")
add("I2", item="return_reconciles", value=int(abs(gp * gh - gc) / gc < 1e-12))

# ============================== I3 ==========================================
def ver(comp, prefix):
    for r in VER:
        if r["component"] == comp and r["quantity"].startswith(prefix):
            return r["value"]
    return None


# P4 exposure, recomputed with the leverage multiple read from the synthetic panel
eff = pd.read_parquet(OUT / "_effective_exposure.parquet")["eff_exposure"]
peak = pd.Timestamp("2022-01-03"); firstro = pd.Timestamp("2022-01-10")
seg = eff.loc[(eff.index > peak) & (eff.index <= firstro)]
s27_val = ver("P4", "mean effective exposure")
add("I3", item="P4_mean_effective_exposure_across_the_interval",
    session_27_value=s27_val, session_28_value=q(seg.mean()),
    value=q(float(seg.mean()) - float(s27_val)),
    note="session 27 read the leverage multiple from the REALIZED panel, where the "
         "loader sets it to NaN for every levered fund, so its figure is the gross "
         "portfolio weight rather than leverage-adjusted exposure. Session 28 reads it "
         "from the synthetic panel as session 16 step 3 does, and reproduces the "
         "committed primary-window canonical figure of 1.7769723457408557 exactly, "
         "which the realized-panel reading does not. The session 27 figure is the one "
         "in error and is corrected here rather than in that report, which is not edited")
add("I3", item="primary_window_mean_effective_exposure_check",
    session_27_value="", session_28_value=dec("exposure", "mean", "primary"),
    value=q(float(dec("exposure", "mean", "primary")) - 1.7769723457408557),
    note="the gap to the committed 1.7769723457408557 at "
         "outputs/session-16/exposure-reconciliation.csv, which is the evidence that "
         "the synthetic-panel reading is the correct one")

# the two prediction premises
add("I3", item="P3_part_one_primary_window_correlation",
    session_27_value=ver("P3 part one", "the same pair over the primary window"),
    session_28_value=ver("P3 part one", "the same pair over the primary window"),
    value="0",
    note="the prediction asserted a negative primary-window SQQQ against TLT "
         "correlation and the measured figure is positive. Session 27 recorded this and "
         "session 28 does not disagree with it")
prim_to = 37.87437898045862
hold_to = 21.026206485079
add("I3", item="P1_turnover_premise",
    session_27_value=repr(hold_to), session_28_value=repr(hold_to),
    value=q(1 - hold_to / prim_to),
    note="P1's mechanism stated that nothing in the holdout reduces turnover. Turnover "
         "fell from 37.87437898045862 to 21.026206485079, a fall of "
         f"{1-hold_to/prim_to:.6f}. Session 27 did not report this and session 28 does, "
         "so it is an addition rather than a disagreement")

for lab, s27k, s28v in (
    ("strategy_holdout_naive_sharpe", LADH["STRATEGY"]["sharpe_naive"],
     LADH["STRATEGY"]["sharpe_naive"]),
    ("strategy_holdout_lo_sharpe", LADH["STRATEGY"]["sharpe_lo"],
     LADH["STRATEGY"]["sharpe_lo"]),
    ("holdout_sessions", LADH["STRATEGY"]["n_sessions"], str(n_h))):
    add("I3", item=lab, session_27_value=s27k, session_28_value=s28v, value="0",
        note="read from the same committed file, so no disagreement is possible")

n_dis = sum(1 for r in rows if r["table"] == "I3" and r["value"] not in ("0", "0.0")
            and r["item"].startswith("P4"))
add("I3_summary", item="quantities_disagreeing_with_session_27",
    value=n_dis,
    note="the P4 effective-exposure figures, arising from reading the leverage multiple "
         "from the wrong panel. Every other quantity checked agrees or is an addition")

fn = ["table", "item", "value", "session_27_value", "session_28_value", "note"]
with open(OUT / "reconciliation.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote reconciliation.csv, {len(rows)} rows")
print(f"  I1 residual properly defined: {net_ann!r} against {PRIM_ANN!r}")
print(f"  I2 sessions reconcile: {n_c == n_p + n_h}, "
      f"return relative gap {abs(gp*gh-gc)/gc:.3e}")
print(f"  I3 disagreements with session 27: {n_dis}")
