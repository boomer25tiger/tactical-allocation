"""Session 30 phase A. The ruling, the positive control and the pre-registration.

Written and emitted BEFORE any measurement in phases B through H runs. The list is
closed, so a quantity not on it is not computed later in this session.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM                            # noqa: E402
OUT = ROOT / "outputs" / "session-30"
OUT.mkdir(parents=True, exist_ok=True)
TOL = 5e-7
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


l = [float(x) for x in subprocess.run(
    ["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True
).stdout.strip().strip("{} ").split()]
s = VM.sample()
cores = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True,
                           text=True).stdout)
for k, v in (("load_1min", l[0]), ("load_5min", l[1]), ("load_15min", l[2]),
             ("compressor_gib", s["compressor_gib"]),
             ("swap_used_mb", s["swap_used_mb"]),
             ("swap_free_mb", s["swap_free_mb"]), ("cores", cores)):
    add("machine_at_phase_A", item=k, value=v)
add("machine_at_phase_A", item="contention_threshold", value=cores * 2,
    note="twice the core count, the precedent at 9.47. Phases F and G each check "
         "against it before launching")

# ---- the ruling ------------------------------------------------------------------
add("ruling", item="stands_from_session_28", value=1,
    note="describing a committed holdout result is permitted while selecting against "
         "it is not, as recorded at 9.70")
add("ruling", item="canonical_unchanged", value=1,
    note="no canonical value moves whatever any phase returns, no specification is "
         "chosen on holdout performance, and the frozen claim set is not amended")
add("ruling", item="no_frozen_input_repaired", value=1,
    note="no hashed file is edited and no manifest entry changes, since the disposition "
         "at phase C is recorded as open")

# ---- the class sweep's own motivation, recorded first -------------------------------
add("motivation", item="phase_B_class_sweep",
    note="session 29 found a discontinuity in SOXS on 2026-05-26 where the close moves "
         "from 1159.5 to 62.900001525878906 against SMH at 0.04480151130636223, implying "
         "a multiple of -21.109834258353413 against a registered -3.0, while the frozen "
         "record's Stock Splits column reads zero. A split column that misses one "
         "corporate action cannot establish the absence of others, and the 50 percent "
         "absolute-return threshold that found it catches ratios of 2 or larger while "
         "levered products split at smaller ratios routinely. The screen that worked is "
         "the implied-multiple comparison, so the class is swept on that rather than on "
         "the return threshold")
CARRIED = {
 "phase_D_holdout_nulls":
   "the primary window's significance claims rest on the timing-shuffle and "
   "turnover-matched nulls clearing at zero exceedances of 10,000 draws, and neither "
   "has been run on the holdout",
 "phase_E_multi_factor":
   "the static regression against buy-and-hold QQQ carries an R-squared of "
   "0.12086286064363738, so 88 percent of holdout variance is unexplained by "
   "construction and lands in the 0.5637941837318013 alpha, while the strategy holds "
   "semiconductor, biotechnology, volatility and Treasury instruments none of which is "
   "QQQ",
 "phase_F_block_bootstrap":
   "the study reports point estimates throughout with no interval anywhere, and holdout "
   "excess kurtosis at 5.223157724383093 means the iid standard error understates the "
   "true one",
 "phase_G_nav_sensitivity":
   "the participation cap bound on 0.9406631762652705 of holdout transitions against "
   "0.4909274193548387 of primary ones, on a book compounding from 816441.3464029437 to "
   "1028029775.2491124, so the two windows may not measure the same object",
 "phase_H_instrument_attribution":
   "the reported mean effective exposure of 0.9681564510351294 against a realised "
   "volatility ratio of 1.7102013039589175 depends on how the instruments carrying k "
   "equal to zero under register 2.15 are treated",
}
for k, v in CARRIED.items():
    add("motivation", item=k, note=v + ". Carried forward from 9.79")
add("motivation", item="all_disclosed_post_hoc", value=1,
    note="every measurement in phases B through H is a disclosed post-hoc sensitivity "
         "under 9.10 with its motivation recorded before the run")

# ---- the enumerated list -----------------------------------------------------------
PLAN = [
 ("B", "the corporate action class sweep, run first because every downstream phase "
       "reads price series it screens",
  "B1 the implied-multiple screen across the full combined window for every held "
  "instrument, with the rule and tolerance stated before running, the underlying read "
  "from src/schedule.py, a stated minimum absolute underlying return below which the "
  "ratio is not computed with those sessions screened on absolute return instead, and "
  "the volatility instruments screened against the frozen constant-maturity thirty-day "
  "VIX futures settle with the proxy limitation recorded; B2 every held instrument "
  "ranked by contribution to each window's return read from "
  "outputs/session-28/holdout-decomposition.csv with the flagged-session count beside "
  "each, the highest contributors named explicitly, and each flagged session's own "
  "contribution with the per-instrument cumulative; B3 for every break, which "
  "indicators read that instrument with each lookback read from src/config.py, the "
  "count of contaminated sessions after the break, the longest contaminated span, "
  "whether any contaminated session coincides with a terminal firing, and whether the "
  "instrument enters as a position, a signal input or both; B4 every recorded split "
  "against a matching price discontinuity in both directions with the counts"),
 ("C", "the disposition and one repair",
  "C1 the three options with their consequences as measured, being repair the frozen "
  "input with the files, hashes and prior integrity checks that change, disclose "
  "unrepaired with the impact bounded by B2, and register the defect with a permanent "
  "implied-multiple check with what implementing it involves, together with the "
  "measured facts bearing on the choice and no recommendation; C2 both windows' "
  "leave-one-year-out ranges on the naive convention and on the Lo convention "
  "separately with each estimate listed and the year whose removal moves each range "
  "most"),
 ("D", "the holdout nulls",
  "the timing-shuffle and turnover-matched constructions read from the session 14 "
  "scripts, run over the holdout at 10,000 replications at the session 22 seed "
  "convention, reporting per null and metric the exceedance count as the primary form, "
  "the total draws, the implied p value and the strategy's percentile, across "
  "annualised return, naive Sharpe and Lo-corrected Sharpe, with each null "
  "distribution's mean and standard deviation and the primary-window exceedance counts "
  "beside the holdout ones"),
 ("E", "the multi-factor decomposition",
  "a positive control regressing each factor on itself; the factor set built from "
  "instruments already inside the frozen inputs covering an equity market, a "
  "semiconductor, a biotechnology, a long Treasury and a volatility factor with the "
  "instrument standing for each named and confirmed present, and any factor with no "
  "suitable instrument reported rather than substituted; the single-factor baseline "
  "reproduced; the multi-factor regression with alpha, each loading, R-squared and the "
  "Newey-West t at the 8.11 lag of 21; the incremental R-squared as each factor enters "
  "in an order stated before running and justified on economic grounds; the factor "
  "correlation matrix and each loading's variance inflation; the same decomposition "
  "over the primary window; and the multi-factor residual's annualised return, "
  "volatility and both Sharpes"),
 ("F", "interval estimates, with a contention check and a wall-clock limit stated "
       "before launching",
  "the stationary block bootstrap with the block length rule, the replication count and "
  "the seed stated before drawing and a memory ceiling stated with peak observed read "
  "from compressor size and swap; intervals at the 5th, 50th and 95th percentiles for "
  "the holdout naive Sharpe, the holdout Lo-corrected Sharpe, the holdout annualised "
  "return, the single-factor alpha, the multi-factor alpha and the naive Sharpe gap "
  "against buy-and-hold QQQ and against the matched-exposure line; the same for the "
  "primary window's naive Sharpe and its gap against buy-and-hold QQQ; the iid "
  "approximate standard error beside each interval; and whether the holdout gap against "
  "buy-and-hold QQQ excludes zero at the 5th percentile"),
 ("G", "the NAV sensitivity on the D20 axis, with a contention check before launching",
  "G1 the holdout at five NAV levels stated before running and chosen for coverage, "
  "reporting at each the annualised return, both Sharpes, annualised turnover, "
  "rebalancing events per session, mean trade value as a share of NAV, the cap-binding "
  "share of events and the ladder rank on the naive Sharpe, with whether performance "
  "degrades smoothly or breaks at a threshold and the level at which the cap-binding "
  "share first exceeds 0.75 and 0.90; G2 the holdout with NAV reset to the study anchor "
  "at the boundary against the inherited figures; G3 the cap-binding share by calendar "
  "year across the combined window with NAV at each year end and the year binding first "
  "exceeds 0.75 and 0.90; G4 session 28's cost sweep re-run at one stated constant NAV "
  "across all six levels with whether the non-monotonicity disappears"),
 ("H", "instrument attribution",
  "every held instrument's contribution to holdout return and to holdout variance "
  "ranked with the primary-window figures alongside, each instrument's own annualised "
  "volatility over the holdout and its correlation with buy-and-hold QQQ; which "
  "instruments carry k equal to zero under register 2.15 and their combined share of "
  "holdout return and variance; and the exposure figure recomputed with a non-zero k "
  "for the volatility instruments at a k stated before computing and recorded as "
  "illustrative rather than adopted"),
]
for ph, what, quantities in PLAN:
    add("plan", item=f"phase_{ph}", value=what, note=quantities)
add("plan", item="closed", value=1,
    note="the list is complete at the time of writing. A quantity not on it is not "
         "added later in this session")

# ---- gate B, written before the check -----------------------------------------------
add("gate_B", item="rule",
    note="if any break is found in an instrument contributing materially to either "
         "window's return, or if any contaminated indicator session coincides with a "
         "terminal firing, halt before phase C and report")
add("gate_B", item="materiality_definition", value=0.05,
    note="an instrument is material when the absolute cumulative contribution of its "
         "flagged sessions exceeds 5 percent of the window's arithmetic return sum. "
         "Stated before the check rather than after seeing the flags")
add("gate_B", item="written_before_the_check", value=1)

# ---- the standing positive control ----------------------------------------------------
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]
ret = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
m = L.standalone_metrics(ret, d["nav"], acc["orders"])
pc = (abs(m["ann_return"] - 0.521845) <= TOL and abs(m["sharpe_lo"] - 1.381701) <= TOL
      and len(ret) == 2472)
add("positive_control", item="tolerance", value=TOL, note="stated before comparing")
add("positive_control", item="ann_return", value=m["ann_return"], target=0.521845)
add("positive_control", item="sharpe_lo", value=m["sharpe_lo"], target=1.381701)
add("positive_control", item="n_sessions", value=len(ret), target=2472)
add("positive_control", item="verdict", value="PASS" if pc else "FAIL")
add("positive_control", item="holdout_truncation_default",
    value=str(bt.HOLDOUT_LAST_DATE.date()),
    note="the control runs with the default truncation in force, so it reads no "
         "post-boundary session")
print(f"positive control {'PASS' if pc else 'FAIL'} ann {m['ann_return']:.6f} "
      f"lo {m['sharpe_lo']:.6f} n {len(ret)}")

with open(OUT / "preregistration.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["table", "item", "value", "target", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote preregistration.csv, {len(rows)} rows")
print(f"load {l[0]} against a contention threshold of {cores*2}")
sys.exit(0 if pc else 1)
