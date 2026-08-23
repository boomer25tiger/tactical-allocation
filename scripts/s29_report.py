"""Session 29 phase H. Write outputs/session-29/REPORT.md from the emitted CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
O = R / "outputs" / "session-29"


def rd(p):
    return list(csv.DictReader(open(O / p)))


PRE = rd("preregistration.csv"); CA = rd("corporate-actions.csv")
G3 = rd("instrument-attribution.csv"); SZ = rd("size.csv")


def g(rows, t, i, f="value", **kw):
    for r in rows:
        if r.get("table") == t and r.get("item") == i and all(
                r.get(k) == v for k, v in kw.items()):
            return r.get(f)
    return None


def p(rows, i, f="value"):
    for r in rows:
        if r.get("item") == i:
            return r.get(f)
    return None


L = []; a = L.append
unexp = [r for r in CA if r["table"] == "unexplained_detail"]
holdout_unexp = [r for r in unexp if r["window"] == "holdout"]

a("# Session 29, robustification")
a("")
a("2026-08-23. Phase A ran, phase B ran and fired its gate, and the measurement phases "
  "did not run. One commit, at phase H.")
a("")
a("## Opening")
a("")
a(f"**Gate B fired.** {g(CA,'above_threshold_summary','sessions_above_50_percent')} "
  f"sessions across both windows carry an absolute return above 0.50 in the loaded "
  f"universe, and "
  f"{g(CA,'above_threshold_summary','unexplained_in_a_held_instrument')} are unexplained "
  f"in a held instrument, of which {g(CA,'gate_B','unexplained_inside_the_holdout')} is "
  f"inside the holdout. **Phases C, D, E, F, G1 and G2 did not run**, since the gate was "
  f"written at 9.79 before the check and requires the session to halt before any other "
  f"phase.")
a("")
a(f"**The holdout defect is SOXS on 2026-05-26**, a return of "
  f"{holdout_unexp[0]['value']} with no corporate action in the frozen record and an "
  f"implied multiple 7.04 times the registered magnitude. **It contributes exactly "
  f"{g(CA,'unexplained_contribution','total')} to holdout return**, since SOXS carries "
  f"zero weight across the whole of 2026-05-18 to 2026-06-05.")
a("")
a("**The holdout null exceedance counts, the multi-factor alpha and the NAV capacity "
  "curve are not reported, since none was computed.** The gate exists so that the "
  "holdout result is not robustified on a series that may carry an unadjusted split, "
  "and it did what it was written to do.")
a("")
a("## Machine and the positive control")
a("")
a(f"Load average {g(PRE,'machine_at_start','load_1min')} one minute, "
  f"{g(PRE,'machine_at_start','load_5min')} five minutes and "
  f"{g(PRE,'machine_at_start','load_15min')} fifteen minutes on "
  f"{g(PRE,'machine_at_start','cores')} cores, compressor "
  f"{g(PRE,'machine_at_start','compressor_gib')} GiB, swap used "
  f"{g(PRE,'machine_at_start','swap_used_mb')} MB and swap free "
  f"{g(PRE,'machine_at_start','swap_free_mb')} MB. **Phase E would have carried the "
  f"resampling load and did not run, so no memory ceiling was consumed.**")
a("")
a(f"**The standing positive control passed** at {g(PRE,'positive_control','ann_return')} "
  f"annualised and {g(PRE,'positive_control','sharpe_lo')} Lo-corrected over "
  f"{g(PRE,'positive_control','n_sessions')} sessions, inside the "
  f"{g(PRE,'positive_control','tolerance')} tolerance stated before comparing.")
a("")
a("## Phase A, the pre-registration")
a("")
a("The session 28 ruling at 9.70 stands. The complete quantity list for phases B "
  "through G was written to `outputs/session-29/preregistration.csv` and to the register "
  "at 9.79 before any measurement ran, and it is closed.")
a("")
a("Every measurement in the session is a disclosed post-hoc sensitivity under 9.10 with "
  "its motivation recorded before the run.")
a("")
a("| phase | motivation |")
a("|---|---|")
for k in ("B_corporate_actions", "C_holdout_nulls", "D_multi_factor",
          "E_block_bootstrap", "F_nav_sensitivity"):
    a(f"| {k.split('_')[0]} | {g(PRE,'motivation_9_10',k,'note')} |")
a("")
a(f"**Gate B, written before the check.** {g(PRE,'gate_B','rule','note')}.")
a("")
a("## Phase B, corporate action integrity")
a("")
a(f"{g(CA,'scope','loaded_universe')} instruments in the loaded universe, of which "
  f"{g(CA,'scope','instruments_ever_held')} are ever held. Every session above the 0.50 "
  f"threshold was screened first against the frozen record's own corporate action "
  f"columns and second against the registered underlying, since a large market move "
  f"explains a jump as much as a split does. The registered multiple and benchmark come "
  f"from `src/schedule.py` and the volatility funds are screened against the frozen "
  f"constant-maturity thirty-day VIX futures settle at "
  f"`data/interim/vx-cm30.parquet`.")
a("")
a("### Every session above 50 percent")
a("")
a("| window | instrument | date | return | screen |")
a("|---|---|---|---|---|")
for r in CA:
    if r["table"] == "above_threshold":
        verdict = r["note"].split(".")[0]
        a(f"| {r['window']} | {r['item']} | {r['date']} | {r['value']} | {verdict}, "
          f"{r['corporate_action']} |")
a("")
a("### The four unexplained sessions")
a("")
a("| window | instrument | date | return | what the screen shows |")
a("|---|---|---|---|---|")
for r in unexp:
    tail = r["note"].split("so the session is ", 1)[-1]
    a(f"| {r['window']} | {r['item']} | {r['date']} | {r['value']} | {tail} |")
a("")
a(f"**SOXS on 2026-05-26 is the one that fires the gate.** Its close runs 1159.5 on "
  f"2026-05-22 and 62.900001525878906 on 2026-05-26 while SMH rose "
  f"0.04480151130636223 across the same gap, and the Stock Splits column reads zero on "
  f"that session. The three primary-window sessions are a proxy limitation rather than "
  f"a data defect.")
a("")
a("### The independent cross-check")
a("")
a("| rank | instrument | date | adjusted-close path | deviation from the engine |")
a("|---|---|---|---|---|")
for r in CA:
    if r["table"] == "cross_check":
        dev = r["note"].split("a deviation of ")[-1].split(".")[0] if "deviation of" in r["note"] else ""
        dev = r["note"].split("a deviation of ")[-1].split(". The")[0] if "deviation of" in r["note"] else ""
        a(f"| {r['rank']} | {r['item']} | {r['date']} | {r['value']} | {dev} |")
a("")
a("**The vendor's own adjusted-close column carries the same jump on SOXS**, so the two "
  "price paths inside the frozen parquet agree with each other. The defect is a missing "
  "corporate action record rather than a disagreement between columns, which is why an "
  "alternative path inside the frozen inputs cannot repair it.")
a("")
a("### Split adjustment status")
a("")
n_unadj = sum(1 for r in CA if r["table"] == "split_adjustment"
              and r["value"] == "UNADJUSTED")
n_adj = sum(1 for r in CA if r["table"] == "split_adjustment" and r["value"] == "adjusted")
n_none = sum(1 for r in CA if r["table"] == "split_adjustment"
             and r["value"] == "no split in the frozen record")
a(f"**{n_unadj} instruments carry a close that looks unadjusted at a recorded split.** "
  f"{n_adj} carry recorded splits and pass the check, and {n_none} carry no split entry "
  f"in the frozen record at all. The check compares the close ratio at each recorded "
  f"event against the reciprocal of the split factor, which is what an unadjusted series "
  f"would show.")
a("")
a(f"**The adjustment method does not differ between the two windows.** "
  f"{g(CA,'adjustment_method','differs_between_windows','note')}.")
a("")
a(f"**The realized arm takes {g(CA,'adjustment_method','realized_arm')}** and the "
  f"synthetic arm takes {g(CA,'adjustment_method','synthetic_arm')}. The designated cell "
  f"is the realized arm.")
a("")
a("### The defect's contribution")
a("")
a(f"**{g(CA,'unexplained_contribution','total')}**, against a holdout arithmetic return "
  f"sum of 3.4218690114239116. SOXS carries zero weight across the whole of 2026-05-18 "
  f"to 2026-06-05. It is held on {g(CA,'gate_B','soxs_holdout_sessions_held')} of the "
  f"holdout's sessions and appears in `src/sleeves.py` at line 266 alone, inside T11's "
  f"bear split, which is a position rather than a signal, so the defect cannot enter "
  f"through the signal path either.")
a("")
a(f"### The gate")
a("")
a(f"**{g(CA,'gate_B','verdict')}.** {g(CA,'gate_B','verdict','note')}.")
a("")
a("## Phases C through G, not run")
a("")
a("| phase | status |")
a("|---|---|")
a("| C, the holdout nulls | not run, gate B fired |")
a("| D, multi-factor decomposition | not run, gate B fired |")
a("| E, interval estimates | not run, gate B fired |")
a("| F, the NAV sensitivity | not run, gate B fired |")
a("| G1, instrument attribution | not run, gate B fired |")
a("| G2, the leave-one-year-out convention restatement | not run, gate B fired |")
a("| G3, the numpy repr inspection | run, see below |")
a("")
a(f"**G3 was completed and its scope is stated rather than assumed.** "
  f"{p(G3,'scope','note')}.")
a("")
a(f"**{p(G3,'numpy_repr_wrappers_found')} numpy repr wrappers reached the session 28 "
  f"prose**, and the scaffold names two.")
a("")
a("| line | as written | corrected |")
a("|---|---|---|")
for r in G3:
    if r["item"].startswith("line_"):
        a(f"| {r['line']} | `{r['value']}` | {r['corrected_to']} |")
a("")
a(f"{p(G3,'cause','note').capitalize()}. {p(G3,'register_entries_affected','note')}. "
  f"`outputs/session-28/REPORT.md` is not edited and the correction stands at 9.81.")
a("")
a("**Session 28's G2 convention mismatch is not corrected**, since restating both "
  "windows' leave-one-year-out ranges on each convention is a measurement and the gate "
  "halted the measurement phases. It remains open.")
a("")
a("## What each finding is")
a("")
a("| finding | what acting on it would be |")
a("|---|---|")
a("| the SOXS 2026-05-26 defect in a frozen input | a correctness repair, and one with "
  "hashing and manifest consequences, so it is reported rather than applied here |")
a("| the defect contributing 0.0 to holdout return | documentation |")
a("| the three primary-window sessions the proxy cannot confirm | documentation, since "
  "each is directionally accounted for by the registered underlying or by a strike-time "
  "mismatch |")
a("| no instrument's close looking unadjusted at a recorded split | documentation |")
a("| the three numpy repr wrappers | a correctness repair, applied at 9.81 in the "
  "register rather than by editing that report |")
a("| phases C through G2 not running | a specification change if the gate is to be "
  "relaxed, and a register decision if the defect is to be repaired first |")
a("")
a("**No recommendation is made on any of them.**")
a("")
a("## What remains before the paper")
a("")
a("**The gate's disposition is the open question and it is not decided here.** Repairing "
  "a frozen input changes a hashed file, its manifest entry and the input-integrity "
  "check every session runs, so it is a decision rather than an edit. Leaving it "
  "unrepaired and disclosing it is the alternative, and the measured contribution of "
  "0.0 to holdout return bears on that choice without settling it.")
a("")
a("**Six measurement phases remain uncomputed**, being the holdout nulls, the "
  "multi-factor decomposition, the interval estimates, the NAV sensitivity, the "
  "instrument attribution and the leave-one-year-out convention restatement. Each was "
  "pre-registered at 9.79 and none was run.")
a("")
a("Outside this session, S equal to 48 of the B1 re-emission remains open at 9.48 and "
  "the corrected degradation null remains unrun at 9.46, neither load-bearing. **No "
  "claim in docs/CLAIMS.md is added or amended, docs/HOLDOUT-PREDICTION.md is not "
  "edited, and no figure is drawn.**")
a("")
a("## Repository size and free space")
a("")
a(f"**No committed file exceeds 100 megabytes.** The largest is "
  f"{g(SZ,'size','largest_tracked_file_mb')} MB, being "
  f"`{g(SZ,'size','largest_tracked_file_bytes','note')}`, and the count above the limit "
  f"is {g(SZ,'size','tracked_files_over_100mb')}.")
a("")
a("| reading | before the commit | expected delta |")
a("|---|---|---|")
a(f"| working tree, KiB | {g(SZ,'size','working_tree_kib_before_commit')} | "
  f"{g(SZ,'expected_delta','working_tree_kib')} |")
a(f"| git directory, KiB | {g(SZ,'size','git_directory_kib_before_commit')} | "
  f"{g(SZ,'expected_delta','git_directory_kib')} |")
a(f"| free space, GiB | {g(SZ,'space','free_gib_before_commit')} | "
  f"{g(SZ,'expected_delta','free_space_gib')} |")
a("")
a(f"The commit touches {g(SZ,'commit_contents','files_in_the_commit')} files totalling "
  f"{g(SZ,'commit_contents','bytes_of_those_files')} bytes on disk, of which "
  f"{g(SZ,'commit_contents','files_new_to_the_repository')} files and "
  f"{g(SZ,'commit_contents','bytes_new_to_the_repository')} bytes are new. **Nothing is "
  f"read after the commit**, under 9.62.")
a("")
a("## Register")
a("")
a("9.79 the pre-registration and the quantity list, written before any measurement. "
  "9.80 corporate action integrity and the gate outcome. 9.81 the three numpy repr "
  "wrappers in the session 28 report.")
a("")
a("## Artifacts")
a("")
for x in ("preregistration.csv", "corporate-actions.csv", "instrument-attribution.csv",
          "size.csv"):
    a(f"- `outputs/session-29/{x}`")
a("")
a("The remaining pre-registered artifacts were not written, since the phases that would "
  "have written them did not run.")
a("")
(O / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"wrote REPORT.md, {len(L)} lines")
