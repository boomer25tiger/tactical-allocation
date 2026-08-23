"""Session 28 phase A. The ruling, the positive control and the pre-registration.

Written and emitted BEFORE any measurement in phases B through H runs. A quantity
not on the list below is not computed later in this session.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM                            # noqa: E402
OUT = ROOT / "outputs" / "session-28"
OUT.mkdir(parents=True, exist_ok=True)
TOL = 5e-7
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


l = [float(x) for x in subprocess.run(
    ["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True
).stdout.strip().strip("{} ").split()]
s = VM.sample()
for k, v in (("load_1min", l[0]), ("load_5min", l[1]), ("load_15min", l[2]),
             ("compressor_gib", s["compressor_gib"]),
             ("swap_used_mb", s["swap_used_mb"]),
             ("swap_free_mb", s["swap_free_mb"])):
    add("machine_at_start", item=k, value=v)

# ---- the ruling ----------------------------------------------------------------
add("ruling", item="permitted", value="descriptive decomposition of the committed "
    "holdout result",
    note="docs/HOLDOUT-PREDICTION.md states that the holdout is read once. The "
         "distinction drawn is between re-running specifications against the holdout, "
         "which would destroy the read, and describing a result already committed, "
         "which changes nothing. Describing is permitted")
add("ruling", item="not_permitted", value="selection against the holdout",
    note="no canonical value moves on any holdout observation, no specification is "
         "chosen on holdout performance, and the frozen claim set is not amended")
add("ruling", item="canonical_unchanged", value=1,
    note="the primary window remains 2011-10-04, the holdout boundary remains "
         "2021-08-01, and the canonical value on every axis is unchanged whatever any "
         "phase of this session returns")
add("ruling", item="written_before_measurement", value=1)

# ---- the enumerated list ---------------------------------------------------------
PLAN = [
 ("B", "the ladder read from outputs/session-27/holdout-ladder.csv, no pass",
  "twelve rows with annualised return, annualised volatility, both Sharpes, maximum "
  "drawdown and annualised turnover; which line beats the strategy on the naive Sharpe "
  "and by how much; buy-and-hold QQQ holdout against primary; the matched-exposure "
  "line's placement; each line's primary rank beside its holdout rank; whether the "
  "strategy's advantage is return, volatility or both"),
 ("C", "the Lo estimator at holdout sample length, no holdout data required",
  "the permutation null at n equal to 1265 with q equal to 252 at 300 draws at a seed "
  "fixed before drawing; null mean, standard deviation, 5th and 95th percentiles; where "
  "the holdout factor sits in that null; the same null for every ladder line and which "
  "observed factors fall inside; the weighted autocorrelation sum at which the Lo "
  "variance turns non-positive at n equal to 1265 and each line's distance from it; the "
  "holdout ladder ranking at q across 1, 5, 21, 63, 126 and 252 with the strategy's "
  "rank at each"),
 ("D", "one deterministic decomposition pass over the holdout, persisting the "
  "per-session sleeve dictionaries",
  "sleeve attribution with per-instrument contribution inside each, primary and "
  "holdout; instrument attribution ranked, primary and holdout; sessions in each state "
  "per sleeve and every terminal's firing count and per-session rate, primary and "
  "holdout; terminals firing in one window and never the other; mean effective exposure "
  "with standard deviation, minimum, maximum and the share of sessions above 1.0 and "
  "above 1.7; the turnover decomposition being rebalancing event count, mean trade size "
  "as a share of NAV and the count of transitions on which the participation cap bound, "
  "at per-session rates; NAV at the start and end of the holdout; maximum drawdown for "
  "the strategy, buy-and-hold QQQ and the matched-exposure line with peak and trough "
  "dates and duration; the share of sessions with every held ticker available on the "
  "realized panel; the daily return distribution's mean, standard deviation, skewness "
  "and excess kurtosis"),
 ("E", "the year split, from the same pass",
  "the strategy and all twelve ladder lines by calendar year across the holdout with "
  "annualised return, both Sharpes and maximum drawdown per year; the strategy's rank "
  "among twelve per year; which years carry the outperformance and whether it is "
  "concentrated; 2022 reported separately with the strategy's return, the short "
  "sleeve's contribution and buy-and-hold QQQ's return"),
 ("F", "the cost sweep over the holdout, a DISCLOSED POST-HOC SENSITIVITY under 9.10",
  "the strategy's naive and Lo-corrected Sharpe at each level of the pre-registered "
  "range read from src/config.py; the round-turn cost at which the strategy's rank "
  "falls to sixth, to eighth and below buy-and-hold QQQ, each marked inside the swept "
  "range or an extrapolation; the same crossings for the primary window from the "
  "committed file"),
 ("G", "robustness",
  "G1 the lookahead test, being the canonical re-run at one additional session of "
  "signal-to-execution lag over both windows with annualised return, both Sharpes and "
  "the ladder rank at each, whether the negative shift is computable without forward "
  "information, and whether the primary-window lag sensitivity at corrections item 12 "
  "reproduces; G2 concentration, being the share of holdout cumulative return in the "
  "best and worst 1, 5, 10 and 25 sessions, the holdout and primary naive Sharpe with "
  "the best 5 and best 10 removed, and the session count accounting for half the "
  "holdout return; G3 leave-one-year-out across the holdout with the range and the year "
  "whose removal moves it most; G4 rolling 252-session naive Sharpe across the combined "
  "window with the boundary marked, the minimum, the maximum and the share above 1.0"),
 ("H", "the beta decomposition over the holdout, mirroring session 21 phase D",
  "a positive control regressing buy-and-hold QQQ on itself; the static regression of "
  "the canonical's daily excess return on buy-and-hold QQQ's with beta, annualised "
  "alpha, R-squared, the Newey-West t at the 8.11 lag of 21 and the beta-hedged "
  "residual's annualised return, volatility and both Sharpes; the rolling decomposition "
  "at 60, 120, 252 and 504 sessions with beta mean, standard deviation, minimum, "
  "maximum and the timing component at each; the exposure-matched line at each window "
  "with its Sharpe against the strategy's"),
 ("I", "reconciliation",
  "I1 whether the residual annualised return's proximity to the primary window's is "
  "arithmetic coincidence, checked for comparable definition before comparing; I2 that "
  "the combined window reconciles with the two spans separately; I3 every quantity in "
  "this session disagreeing with a figure in outputs/session-27/REPORT.md"),
]
for ph, what, quantities in PLAN:
    add("plan", item=f"phase_{ph}", value=what, note=quantities)
add("plan", item="closed", value=1,
    note="the list is complete at the time of writing. A quantity not on it is not "
         "added later in this session")

# ---- the two disclosed sensitivities ----------------------------------------------
add("sensitivity_9_10", item="phase_F_cost_sweep", value="disclosed post-hoc",
    note="motivation, the primary-window finding attributed the shortfall to cost of "
         "carry at an annualised turnover of 37.87437898045862, and holdout turnover "
         "fell to 21.026206485079 while the rank rose. The sweep tests whether the cost "
         "attribution survives at the holdout's lower turnover. It CANNOT change the "
         "canonical whatever it returns, since the cost model is fixed and the sweep "
         "varies a disclosed sensitivity axis rather than selecting one")
add("sensitivity_9_10", item="phase_G1_lag_shift", value="disclosed post-hoc",
    note="motivation, the register's corrections list item 12 records that no dedicated "
         "lookahead test has run anywhere in the project, and the holdout result raises "
         "the question for every holdout figure. The shift tests whether the advantage "
         "survives one additional session of signal-to-execution lag. It CANNOT change "
         "the canonical whatever it returns, since the canonical lag stays at one "
         "session and the shift is reported as a sensitivity")
add("sensitivity_9_10", item="neither_selects", value=1,
    note="neither measurement chooses a specification. Both are reported whatever they "
         "return and neither moves any canonical value")

# ---- the standing positive control --------------------------------------------------
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
sys.exit(0 if pc else 1)
