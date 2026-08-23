"""Session 29 phase A. The pre-registration and the standing positive control.

Written and emitted BEFORE any measurement in phases B through G runs. The list is
closed and nothing outside it is computed. Every measurement here is a disclosed
post-hoc sensitivity under 9.10 with its motivation recorded before the run.

The session 28 ruling at 9.70 stands, being that describing a committed holdout
result is permitted while selecting against it is not.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM                            # noqa: E402
OUT = ROOT / "outputs" / "session-29"
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
             ("cores", cores), ("compressor_gib", s["compressor_gib"]),
             ("swap_used_mb", s["swap_used_mb"]), ("swap_free_mb", s["swap_free_mb"])):
    add("machine_at_start", item=k, value=v)

add("ruling", item="session_28_ruling_stands", value=1,
    note="9.70, describing a committed holdout result is permitted while selecting "
         "against it is not. No canonical value moves whatever any phase returns, no "
         "specification is chosen on holdout performance, and the frozen claim set is "
         "not amended")

PLAN = [
 ("B", "corporate action integrity, run FIRST because a defect here invalidates every "
  "downstream measurement",
  "the largest single-session absolute return per held instrument across each window "
  "with its date, ranked; every session on which a held instrument's absolute return "
  "exceeds 50 percent with the instrument, date and return, each screened against a "
  "known corporate action or reported unexplained; particular attention to UVXY, SQQQ, "
  "PSQ, SVXY and every other inverse or volatility instrument; for each held instrument "
  "whether the frozen parquet is split-adjusted, how that is established and the source "
  "of the adjustment; whether the adjustment method differs between the two windows; "
  "the contribution of any unexplained session to holdout return; an independent "
  "cross-check of the three largest holdout single-session returns against an "
  "alternative frozen price path where one exists"),
 ("C", "the holdout nulls",
  "the timing-shuffle and turnover-matched constructions read from the session 14 "
  "scripts rather than rewritten, run over the holdout at 10,000 replications at the "
  "session 22 seed convention; per null and per metric the exceedance count, the total "
  "draws, the implied p value and the strategy's percentile, with exceedance counts as "
  "the primary form; annualised return, naive Sharpe and Lo-corrected Sharpe; the "
  "primary-window exceedance counts beside the holdout ones; each null distribution's "
  "mean and standard deviation"),
 ("D", "multi-factor decomposition",
  "a positive control regressing each benchmark on itself; the factor set built from "
  "instruments already inside the frozen inputs with each confirmed as a held "
  "instrument, a ladder line or an index file already present, covering an equity "
  "market factor, a semiconductor factor, a biotechnology factor, a long Treasury "
  "factor and a volatility factor; the single-factor baseline against buy-and-hold QQQ; "
  "the multi-factor regression with alpha, each loading, R-squared and the Newey-West t "
  "on alpha at the 8.11 lag of 21; the incremental R-squared as each factor is added; "
  "the same decomposition over the primary window; the multi-factor residual's "
  "annualised return, volatility and both Sharpes; the correlation matrix among the "
  "factors"),
 ("E", "interval estimates",
  "the stationary block bootstrap with the block length selection rule and the reason "
  "for the choice stated before running, the replication count and the seed stated "
  "before drawing, and a memory ceiling stated before the run with peak observed "
  "reported; bootstrap 5th, 50th and 95th percentiles for the holdout naive Sharpe, the "
  "holdout Lo-corrected Sharpe, the holdout annualised return, the single-factor alpha, "
  "the multi-factor alpha, and the naive-Sharpe gap against buy-and-hold QQQ and "
  "against the matched-exposure line; the same intervals over the primary window for "
  "the naive Sharpe and the gap against buy-and-hold QQQ; the iid approximate standard "
  "error beside each interval; whether the holdout gap against buy-and-hold QQQ "
  "excludes zero at the 5th percentile"),
 ("F", "the NAV sensitivity on the D20 axis, which the register records as a curve axis "
  "rather than a grid axis",
  "F1 the capacity curve at five NAV levels stated before running and chosen for "
  "coverage, reporting at each level the annualised return, both Sharpes, annualised "
  "turnover, rebalancing events per session, mean trade value as a share of NAV, the "
  "cap-binding share of events and the ladder rank on the naive Sharpe, with whether "
  "degradation is smooth or breaks at a threshold and the level at which cap binding "
  "first exceeds 0.75 and 0.90; F2 the holdout re-run with NAV reset to the study "
  "anchor at the boundary, reporting every session 28 phase C statistic beside the "
  "inherited-NAV figures; F3 the cap-binding share of events by calendar year across "
  "the combined window with NAV at each year end and the year binding first exceeds "
  "0.75 and 0.90; F4 the session 28 cost sweep re-run with NAV held constant at one "
  "stated level across all six points, with whether the non-monotonicity disappears"),
 ("G", "instrument attribution and two repairs",
  "G1 every held instrument's contribution to holdout return and to holdout variance "
  "ranked with the primary-window figures alongside, each instrument's own annualised "
  "volatility over the holdout and its correlation with buy-and-hold QQQ, and which "
  "instruments carry k equal to zero under 2.15 with their combined share of holdout "
  "return and of holdout variance; G2 both windows' leave-one-year-out ranges on the "
  "naive convention and on the Lo convention separately, restating session 28's G3 "
  "comparison on one convention; G3 the two numpy repr wrappers that reached the "
  "session 28 prose, reported and corrected in the register rather than by editing that "
  "report"),
]
for ph, what, quantities in PLAN:
    add("plan", item=f"phase_{ph}", value=what, note=quantities)
add("plan", item="closed", value=1,
    note="the list is complete at the time of writing. A quantity not on it is not "
         "added later in this session")

MOT = [
 ("B_corporate_actions",
  "UVXY and SQQQ reverse split repeatedly, several times inside the holdout span, and a "
  "single unadjusted split in a levered or inverse ETP produces a spurious return of "
  "several hundred percent on one session"),
 ("C_holdout_nulls",
  "the primary window's significance claims rest on the timing-shuffle and "
  "turnover-matched nulls clearing at zero exceedances of 10,000 draws, and neither has "
  "been run on the holdout"),
 ("D_multi_factor",
  "the static regression against buy-and-hold QQQ carries an R-squared of "
  "0.12086286064363738, so 88 percent of holdout variance is unexplained by "
  "construction and lands in the 0.5637941837318013 alpha, while the strategy holds "
  "semiconductor, biotechnology, volatility and Treasury instruments none of which is "
  "QQQ"),
 ("E_block_bootstrap",
  "the paper reports point estimates throughout with no interval anywhere, and holdout "
  "excess kurtosis at 5.223157724383093 means the iid standard error understates the "
  "true one"),
 ("F_nav_sensitivity",
  "the participation cap bound on 0.9406631762652705 of holdout transitions against "
  "0.4909274193548387 of primary ones, on a book compounding from 816441.3464029437 to "
  "1028029775.2491124, so the two windows may not measure the same object"),
]
for k, why in MOT:
    add("motivation_9_10", item=k, value="disclosed post-hoc sensitivity", note=why)
add("motivation_9_10", item="none_selects", value=1,
    note="every measurement in this session is reported whatever it returns and none "
         "chooses a specification")

add("gate_B", item="rule",
    note="if any unexplained session above 50 percent absolute return is found in a "
         "held instrument, the session halts and reports before any other phase runs. "
         "The holdout result cannot be robustified on a series that may carry an "
         "unadjusted split")
add("gate_B", item="written_before_the_check", value=1)

# ---- the standing positive control ---------------------------------------------------
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
add("positive_control", item="ann_return", value=repr(float(m["ann_return"])),
    target=0.521845)
add("positive_control", item="sharpe_lo", value=repr(float(m["sharpe_lo"])),
    target=1.381701)
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
