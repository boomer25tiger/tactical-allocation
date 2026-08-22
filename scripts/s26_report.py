"""Session 26 phase E. Write outputs/session-26/REPORT.md from the emitted CSVs."""
from __future__ import annotations
import csv
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation"); O = R/"outputs"/"session-26"
def rd(p): return list(csv.DictReader(open(O/p)))
DEC = rd("decisions-applied.csv"); DIS = rd("prompt-disagreements.csv")
SRC = {r["item"]: r for r in rd("prediction-sources.csv")}
MZ = rd("size-and-verification.csv")
def v(i): return SRC[i]["literal_value"]
def f(i): return SRC[i]["source_file"]
def m(t, i):
    for r in MZ:
        if r["table"] == t and r["item"] == i: return r["value"]
    return None
def mn(t, i):
    for r in MZ:
        if r["table"] == t and r["item"] == i: return r["note"]
    return ""
L = []; a = L.append

a("# Session 26, the prediction commit")
a("")
a("2026-08-22. Five phases. One commit, at phase E. No measurement ran, so no positive "
  "control was required.")
a("")
a("## Opening")
a("")
a(f"**{len(DEC)-1} decisions applied and one withdrawal added.**")
a("")
a("| decision | register | kind |")
a("|---|---|---|")
for d in DEC:
    a(f"| {d['decision']} | {d['register_item']} | {d['kind']} |")
a("")
a("**The prediction is written and carries five components.** P1 is the primary rank "
  "prediction, P2 the Sharpe band, P3 the two-part mechanism, P4 the named unknown with "
  "its guard, and P5 the interesting failure mode.")
a("")
a(f"**Pre-commit readings.** Working tree "
  f"{m('size','working_tree_kib_before_commit')} KiB, git directory "
  f"{m('size','git_directory_kib_before_commit')} KiB, free space "
  f"{m('space','free_gib_before_commit')} GiB. The expected delta is "
  f"{m('expected_delta','working_tree_kib')} KiB on the working tree, since "
  f"{mn('expected_delta','working_tree_kib')}, and "
  f"{m('expected_delta','git_directory_kib')} KiB on the git directory. Free space is "
  f"expected to read {m('expected_delta','free_space_gib')} GiB different. **The "
  f"readings were taken immediately before this report was written**, so they exclude "
  f"this file's own bytes and the git objects the staging of it writes.")
a("")
a("## Phase A, the four decisions")
a("")
for d in DEC:
    if d["n"] == "B": continue
    a(f"### {d['n']}, {d['decision']}")
    a("")
    a(f"Register {d['register_item']}. **{d['kind'].capitalize()}.**")
    a("")
    a(f"Before. *{d['before']}*")
    a("")
    a(f"After. *{d['after']}*")
    a("")
    a(f"Grounds. {d['grounds'][0].upper()}{d['grounds'][1:]}.")
    a("")
a("## Phase B, the withdrawal")
b = next(d for d in DEC if d["n"] == "B")
a("")
a(f"Register {b['register_item']}. **Withdrawn by argument rather than by measurement**, "
  f"the two underlying measurements being session 22's leave-one-out rebuild and session "
  f"22's beta window sensitivity, each of which confirmed its own figures without "
  f"supporting the inference chain. The base estimate reproduces at "
  f"{v('loo_base_sharpe_lo')} and the timing component reads "
  f"{v('timing_ann_contribution_60')} at 60 sessions against "
  f"{v('timing_ann_contribution_504')} at 504. Recorded as withdrawal 11 in "
  f"`docs/WITHDRAWN.md`, which now carries 11 against 10 before.")
a("")
a("## Phase C, the prediction")
a("")
a(f"`docs/HOLDOUT-PREDICTION.md`, {m('prediction','bytes')} bytes, SHA-256 "
  f"{m('prediction','sha256')}.")
a("")
a(f"The sealed span runs from {v('holdout_boundary')} to {v('data_end')}, the latter "
  f"read from `{f('data_end')}` across all 39 frozen inputs. The primary window carries "
  f"{v('primary_window_sessions')} sessions.")
a("")
a("**The holdout session count is not stated.** Register 2.10 records that no "
  "post-boundary quantity has been computed anywhere, and counting sessions inside the "
  "sealed span is a post-boundary quantity. The scaffold asked for it, and it is left "
  "for the read with the reason recorded rather than computed.")
a("")
a("| component | prediction | falsified by |")
a("|---|---|---|")
a("| P1 | the strategy ranks no better than sixth of twelve on the naive Sharpe | any "
  "rank of fifth or better |")
a(f"| P2 | the holdout naive Sharpe lands between 0.25 and 0.85, against "
  f"{v('strategy_sharpe_naive_primary')} over the primary window | above 0.85 or below "
  f"0.25 |")
a("| P3 part one | SQQQ and TLT realise positive daily return correlation over the "
  "holdout | a negative realised correlation |")
a("| P3 part two | T10's risk-off branch contributes negatively to holdout return | a "
  "positive contribution |")
a("| P4 | state-classification latency in a slow bear is not predicted | nothing, since "
  "it makes no prediction |")
a("| P5 | if P1 fails, 2022 gave the short sleeve its only sustained tailwind | recorded "
  "as less likely than even |")
a("")
a(f"**P3 part two is the weaker half and the document says so.** The branch's short leg "
  f"already contributes {v('t10_short_leg_total_arith_contribution')} arithmetically "
  f"over the primary window at `{f('t10_short_leg_total_arith_contribution')}`, so part "
  f"two predicts that an observed sign persists while part one predicts that a sign "
  f"flips against a committed baseline of {v('t10_corr_short_vs_rest_of_sleeve')}.")
a("")
a(f"**Six items the scaffold named are not carried as it stated them.** Each is recorded "
  f"rather than adopted, in `outputs/session-26/prompt-disagreements.csv` and in the "
  f"document's closing section.")
a("")
a("| item | the scaffold | the source | kind |")
a("|---|---|---|---|")
for d in DIS:
    src = d["source_value"]
    a(f"| {d['item']} | {d['prompt_value'][:110]} | {src[:130]} | {d['kind']} |")
a("")
a(f"**Three external premises are labelled as external** rather than sourced, being that "
  f"the policy rate exceeded five percent inside the holdout, that the holdout contains "
  f"the only sustained bear in either window, and that TLT had its worst year in decades "
  f"in 2022. No committed CSV carries any of them and establishing any from the panel "
  f"would be a post-boundary quantity. P5 rests on the third, which is why it is "
  f"recorded as less likely than even.")
a("")
a("## Phase D, the verification hook")
a("")
a("`scripts/verify_prediction_precedes_read.py`, run as the first step of any holdout "
  "session. It confirms the prediction exists in committed history, reports the commit "
  "SHA with its author and commit timestamps, confirms the working copy is unmodified "
  "against that commit, and reports the file's hash.")
a("")
a(f"**Run in this session before the commit, it exits "
  f"{m('verification_hook','exit_code_pre_commit')}**, reporting that the file appears "
  f"in no commit. That is the correct answer at that moment, since the commit happens "
  f"at phase E. **The first context in which it exits zero is a session running after "
  f"this commit.**")
a("")
a("## What each item is")
a("")
a("| item | what acting on it is |")
a("|---|---|")
a("| claim 4's scope phrase narrowed | correctness repair, being a wording repair |")
a("| the figure cap raised from two to six | specification change |")
a("| 9.56's grounds recorded in the narrowed form | register decision |")
a("| the size convention | documentation |")
a("| the section 4 prediction withdrawn | register decision |")
a("| the prediction document frozen | specification change, since it constrains every "
  "later session |")
a("| the verification hook | specification change, since it gates the holdout session |")
a("| the six scaffold figures not carried as stated | correctness repair on four of them "
  "and documentation on two |")
a("| the holdout session count left uncomputed | documentation |")
a("")
a("## Repository size and free space")
a("")
a(f"**No committed file exceeds 100 megabytes.** The largest is "
  f"{m('size','largest_tracked_file_mb')} MB, being "
  f"`{mn('size','largest_tracked_file_bytes')}`, and the count above the limit is "
  f"{m('size','tracked_files_over_100mb')}.")
a("")
a("| reading | before the commit | expected delta |")
a("|---|---|---|")
a(f"| working tree, KiB | {m('size','working_tree_kib_before_commit')} | "
  f"{m('expected_delta','working_tree_kib')} |")
a(f"| git directory, KiB | {m('size','git_directory_kib_before_commit')} | "
  f"{m('expected_delta','git_directory_kib')} |")
a(f"| free space, GiB | {m('space','free_gib_before_commit')} | "
  f"{m('expected_delta','free_space_gib')} |")
a("")
a(f"The commit touches {m('commit_contents','files_in_the_commit')} files totalling "
  f"{m('commit_contents','bytes_of_those_files')} bytes on disk, of which "
  f"{m('commit_contents','files_new_to_the_repository')} files and "
  f"{m('commit_contents','bytes_new_to_the_repository')} bytes are new to the "
  f"repository. **Nothing is read after the commit**, under the convention adopted at "
  f"9.62, so this session leaves no dirty file.")
a("")
a("## What remains before the holdout can run")
a("")
a("**Nothing.** The claim set is frozen with claim 4's wording repaired, the prediction "
  "is committed and frozen, the verification hook is in place, the figure cap is fixed "
  "at six, and the withdrawn set records what the project stopped believing. S equal to "
  "48 of the B1 re-emission remains outstanding at 9.48 and sets neither endpoint of any "
  "quoted range, and the corrected degradation null remains unrun at 9.46 with its slope "
  "withdrawn at 9.35, so neither is load-bearing and neither blocks the read.")
a("")
a("The holdout session's first step is `scripts/verify_prediction_precedes_read.py`, "
  "and it proceeds only if that exits zero.")
a("")
a("## Register")
a("")
a("9.59 claim 4's narrowed wording. 9.60 the figure cap at six. 9.61 the 8.2 grounds in "
  "the narrowed form. 9.62 the size convention. 9.63 the section 4 prediction withdrawn. "
  "9.64 the prediction frozen. 9.65 the verification hook.")
a("")
a("## Artifacts")
a("")
for x in ("decisions-applied.csv", "prediction-sources.csv", "prompt-disagreements.csv",
          "size-and-verification.csv"):
    a(f"- `outputs/session-26/{x}`")
a("- `docs/HOLDOUT-PREDICTION.md`")
a("- `scripts/verify_prediction_precedes_read.py`")
a("")
(O/"REPORT.md").write_text("\n".join(L)+"\n")
print(f"wrote REPORT.md, {len(L)} lines")
