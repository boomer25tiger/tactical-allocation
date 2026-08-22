"""Session 26 phases A and B. The four decisions and the withdrawal.

Claim 4's wording is repaired in the claim map and both documents are regenerated
from it, so the map stays the single source the documents are built from. The
quoted figures do not move.
"""
from __future__ import annotations
import csv, subprocess, sys
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = R/"outputs"/"session-26"; OUT.mkdir(parents=True, exist_ok=True)
SRC = {r["item"]: r for r in csv.DictReader(open(OUT/"prediction-sources.csv"))}
def v(i): return SRC[i]["literal_value"]
DEC = []
def dec(n, item, reg, kind, before, after, grounds):
    DEC.append({"n": n, "decision": item, "register_item": reg, "kind": kind,
                "before": before, "after": after, "grounds": grounds})

# ---- A1, claim 4's wording ----------------------------------------------------
CP = R/"outputs"/"session-24"/"claim-sources.csv"
cr = list(csv.DictReader(open(CP))); cfn = list(cr[0].keys())
c4 = next(r for r in cr if r["n"] == "4")
before = c4["statement"]
after = ("Probability of backtest overfitting is 0.1578088578088578 at S equal to 16 "
         "over the full 12,870 combination enumeration, spanning 0.11428571428571428 "
         "to 0.170995670995671 across the block counts 8, 12, 16 and 24 re-emitted on "
         "repaired code.")
assert "0.11428571428571428" in after and "0.170995670995671" in after
assert "0.1578088578088578" in after
c4["statement"] = after
c4["register_item"] = "8.12, re-emitted in part at 9.48, wording repaired at 9.59"
csv.DictWriter(open(CP, "w", newline=""), fieldnames=cfn).writerows(
    [dict(zip(cfn, cfn))] + cr)
dec("A1", "claim 4's scope phrase narrowed to the re-emitted block counts", "9.59",
    "correctness repair, being a wording repair", before, after,
    "the two quoted figures are 0.11428571428571428 at S equal to 8 and "
    "0.170995670995671 at S equal to 12, both re-emitted on repaired code at 9.48, and "
    "neither depends on the unre-emitted S equal to 48. No quoted figure moved and the "
    "claim asserts the same thing about the same numbers")

# ---- A2, the figure cap --------------------------------------------------------
dec("A2", "the paper's figure cap raised from two to six", "9.60",
    "specification change",
    "the paper carries two figures with the rest carried by the PBO report",
    "the paper carries at most six figures with the rest carried by the PBO report, "
    "and six is fixed rather than left open",
    "the cap of two was set before the paper's shape was known. Eight figures are drawn "
    "at 9.55 and four of them illustrate no frozen claim, so a cap of two forced a "
    "choice the evidence did not support. Six is fixed now rather than after the "
    "holdout is read, so no figure is added on the basis of what the read shows")

# ---- A3, 9.56's grounds ---------------------------------------------------------
CC = R/"outputs"/"session-25"/"claim-checks.csv"
ck = list(csv.DictReader(open(CC)))
def a1(item, f="value"):
    return next(r[f] for r in ck if r["table"] in ("A1_outranking", "A1_strategy")
                and r["item"] == item)
narrowed = (f"buy-and-hold QQQ's Lo factor at {a1('buy_hold_QQQ')} sits outside its own "
            f"null upper bound of {a1('buy_hold_QQQ','null_p95')} while the strategy's "
            f"at {a1('STRATEGY')} sits inside its own bound of "
            f"{a1('STRATEGY','null_p95')}")
general = (f"long_legs_only at {a1('long_legs_only')} and vol_targeted_QQQ_matched at "
           f"{a1('vol_targeted_QQQ_matched')} both outrank the strategy from inside "
           f"their own nulls, their upper bounds being "
           f"{a1('long_legs_only','null_p95')} and "
           f"{a1('vol_targeted_QQQ_matched','null_p95')}")
dec("A3", "9.56's grounds recorded in the narrowed form", "9.61", "register decision",
    "the strategy's own Lo factor sits inside its own no-autocorrelation null while "
    "buy-and-hold QQQ's sits outside",
    f"the narrowed form, being that {narrowed}. The general form fails, since {general}",
    "the 8.2 decision to lead on the naive Sharpe rests on the narrowed form together "
    "with the q sweep moving nine of twelve ladder rows in rank, the second being "
    "independent of the null finding, so 8.2 does not rest on the form that fails")

# ---- A4, the size convention -----------------------------------------------------
dec("A4", "the size convention", "9.62", "documentation",
    "repository size and free space are read before and after the commit",
    "repository size, working tree size and free space are read before the commit and "
    "reported with the expected delta stated, and no figure is read after the commit",
    "session 25 ended with two dirty files carrying post-commit readings, which a "
    "one-commit session cannot contain. Reading pre-commit and stating the expected "
    "delta leaves no file dirty. Applies from session 26 forward")

# ---- B, the withdrawal -------------------------------------------------------------
WP = R/"outputs"/"session-24"/"withdrawn-sources.csv"
wr = list(csv.DictReader(open(WP))); wfn = list(wr[0].keys())
assert not any(r["n"] == "11" for r in wr), "withdrawal 11 already present"
wr.append({
 "n": "11",
 "withdrawn_claim": "The handoff's section 4 prediction that the holdout's 2022 tests a "
                    "demonstrated weakness rather than a demonstrated strength.",
 "grounds": (
   "The claim rested on an inference chain running from the leave-one-out result to a "
   "statement about hedge behaviour to a statement about 2022. Session 22's leave-one-out "
   "rebuild confirmed the underlying figures without supporting the chain, the base "
   f"estimate reproducing at {v('loo_base_sharpe_lo')}, and session 22's beta window "
   "sensitivity showed the timing component changing sign across windows, reading "
   f"{v('timing_ann_contribution_60')} at 60 sessions and "
   f"{v('timing_ann_contribution_504')} at 504. An inference that a crisis-year weakness "
   "transfers to a specific future period is not supported by either measurement."),
 "measurement_or_argument": "argument, from the inference chain rather than from a result",
 "session": "22 for both underlying measurements, withdrawn at session 26",
 "source_file": "outputs/session-22/rebuilt/leave-one-out.csv and "
                "outputs/session-22/beta-window-sensitivity.csv",
 "literal_value": (f"base {v('loo_base_sharpe_lo')}; timing at 60 "
                   f"{v('timing_ann_contribution_60')}; timing at 252 "
                   f"{v('timing_ann_contribution_252')}; timing at 504 "
                   f"{v('timing_ann_contribution_504')}")})
csv.DictWriter(open(WP, "w", newline=""), fieldnames=wfn).writerows(
    [dict(zip(wfn, wfn))] + wr)
dec("B", "the section 4 holdout prediction withdrawn", "9.63",
    "register decision, recorded as documentation of a withdrawal",
    "the holdout's 2022 tests a demonstrated weakness rather than a demonstrated strength",
    "withdrawn by argument, the inference chain being unsupported by either session 22 "
    "measurement", "as recorded in docs/WITHDRAWN.md item 11")

fn = ["n", "decision", "register_item", "kind", "before", "after", "grounds"]
with open(OUT/"decisions-applied.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader(); w.writerows(DEC)
print(f"wrote decisions-applied.csv, {len(DEC)} decisions")
r = subprocess.run([sys.executable, str(R/"scripts"/"s24_docs.py")],
                   capture_output=True, text=True, cwd=R)
print(r.stdout.strip() or r.stderr.strip())
