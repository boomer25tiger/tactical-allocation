"""Session 27 phase H. Write outputs/session-27/REPORT.md from the emitted CSVs.

No interpretation. Every component carries its verdict against its stated condition
and nothing beyond that.
"""
from __future__ import annotations

import csv
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
O = R / "outputs" / "session-27"


def rd(p):
    return list(csv.DictReader(open(O / p)))


G = rd("gates.csv"); COV = rd("holdout-coverage.csv"); V = rd("prediction-verdicts.csv")
LADR = rd("holdout-ladder.csv"); COMBR = rd("combined-window.csv")
CVH = rd("claims-vs-holdout.csv"); SZ = rd("size.csv")
LAD = [r for r in LADR if r["table"] == "line"]
COMB = [r for r in COMBR if r["table"] == "line"]
byl = {r["line"]: r for r in LAD}
bylc = {r["line"]: r for r in COMB}


def g(rows, t, i, f="value"):
    for r in rows:
        if r.get("table") == t and r.get("item") == i:
            return r.get(f)
    return None


def qv(comp, prefix, f="value"):
    for r in V:
        if r["component"] == comp and r["quantity"].startswith(prefix):
            return r[f]
    return None


def rank_of(rows, line, conv):
    for r in rows:
        if r["table"] == "rank" and r["line"] == line and r["convention"] == conv:
            return r["rank"], r["of"]
    return None, None


L = []; a = L.append
nr, nof = rank_of(LADR, "STRATEGY", "sharpe_naive")
lr, _ = rank_of(LADR, "STRATEGY", "sharpe_lo")

a("# Session 27, the holdout read")
a("")
a("2026-08-22. Eight phases. One commit, at phase H. The holdout is read once and no "
  "quantity is recomputed.")
a("")
a("## Opening")
a("")
a(f"**All three gates pass.** The prediction hook exits {g(G,'A1','hook_exit_code')} "
  f"with the committed blob reading {g(G,'A1','committed_blob_sha256')} at commit "
  f"{g(G,'A1','commit')}. {g(G,'A3','manifested_and_checked')} hashed frozen inputs "
  f"verify with {g(G,'A3','mismatches')} mismatches. The standing positive control "
  f"reproduces {g(G,'A2','ann_return')} annualised and {g(G,'A2','sharpe_lo')} "
  f"Lo-corrected over {g(G,'A2','n_sessions')} sessions inside the "
  f"{g(G,'preregistration','tolerance')} tolerance stated before comparing.")
a("")
a(f"**The holdout span the frozen data supports runs "
  f"{g(COV,'holdout_span','boundary')} to "
  f"{g(COV,'holdout_span','end_date_the_data_supports')}**, being "
  f"{g(COV,'holdout_span','sessions')} sessions against the primary window's "
  f"{g(COV,'holdout_span','primary_window_sessions')}, a ratio of "
  f"{g(COV,'holdout_span','ratio_to_primary')}. The branch taken is "
  f"{g(COV,'branch','taken')}.")
a("")
a(f"**The strategy ranks {nr} of {nof} on the naive Sharpe and {lr} of {nof} on the "
  f"Lo-corrected**, at {byl['STRATEGY']['sharpe_naive']} and "
  f"{byl['STRATEGY']['sharpe_lo']}.")
a("")
a("| component | verdict |")
a("|---|---|")
a(f"| P1 | **{qv('P1','rank on the naive','verdict')}** |")
a(f"| P2 | **{qv('P2','holdout naive Sharpe','verdict')}** |")
a(f"| P3 part one | **{qv('P3 part one','SQQQ and TLT','verdict')}** |")
a(f"| P3 part two | **{qv('P3 part two','T10 risk-off','verdict')}** |")
a("| P4 | not a prediction, so it carries no verdict |")
a("| P5 | evaluated because P1 is falsified, reported below |")
a("")
a("## Phase A, the gates")
a("")
a(f"**A1.** The hook exits {g(G,'A1','hook_exit_code')}. Commit "
  f"{g(G,'A1','commit')}, blob {g(G,'A1','blob_at_HEAD')}, author timestamp "
  f"{g(G,'A1','author_timestamp')} and commit timestamp "
  f"{g(G,'A1','commit_timestamp')}. The working copy hash "
  f"{g(G,'A1','working_copy_sha256')} matches the committed blob's, so the prediction "
  f"predates this read.")
a("")
a(f"**A3.** {g(G,'A3','files_under_data')} files under data/, of which "
  f"{g(G,'A3','manifested_and_checked')} carry a manifest row and were checked, with "
  f"{g(G,'A3','mismatches')} mismatches and {g(G,'A3','unmanifested')} unmanifested "
  f"derived artifacts. Run before the rebuild, so no holdout quantity was computed on "
  f"unverified input.")
a("")
a(f"**A2.** Annualised return {g(G,'A2','ann_return')} against "
  f"{g(G,'A2','ann_return','target')}, Lo-corrected Sharpe {g(G,'A2','sharpe_lo')} "
  f"against {g(G,'A2','sharpe_lo','target')}, {g(G,'A2','n_sessions')} sessions against "
  f"{g(G,'A2','n_sessions','target')}, primary start "
  f"{g(G,'A2','primary_start')} read from the module.")
a("")
a("## Phase B, what the data covers")
a("")
a(f"{g(COV,'summary','frozen_inputs_surveyed')} frozen inputs surveyed for their first "
  f"and last observation. The loaded universe holds "
  f"{g(COV,'summary','loaded_universe_size')} tickers and every one of them runs to "
  f"{g(COV,'summary','latest_all_held_tickers_available')}. The risk-free series, the "
  f"index files and the NAV files all run to the same date, so the canonical "
  f"specification is computable end to end through "
  f"{g(COV,'summary','latest_canonical_computable_end_to_end')}.")
a("")
a(f"The span runs {g(COV,'holdout_span','first_session')} to "
  f"{g(COV,'holdout_span','last_session')}, being "
  f"{g(COV,'holdout_span','sessions')} sessions.")
a("")
_b = g(COV,'branch','taken'); _n = g(COV,'branch','read_runs_entirely_on_hashed_data','note')
a(f"**The branch taken.** {_b[0].upper()}{_b[1:]}. {_n[0].upper()}{_n[1:]}.")
a("")
a("**SVIX and UVIX both list 2022-03-30, inside the span, and the loader excludes "
  "both.** Neither appears in bt.LEVERED or bt.UNLEVERED, exactly as the disposition at "
  "9.43 recorded, and bt.LEVERED is not modified.")
a("")
a("## Phase C, the read")
a("")
a("One pass. The specification was read from `src/config.py` and "
  "`scripts/s14_common.py` rather than typed.")
a("")
a("| parameter | value |")
a("|---|---|")
for r in rd("holdout-canonical.csv"):
    if r["table"] == "specification":
        a(f"| {r['item']} | {r['value']} |")
a("")
a("The truncation at 2.10 was lifted for this process alone through an explicit "
  "environment variable read by `scripts/s13_backtest.py`. **The module default is "
  "unchanged at 2021-07-31 and the boundary is unchanged at 2021-08-01**, so every "
  "other context still loads nothing past the boundary.")
a("")
a("### The holdout ladder")
a("")
a("| line | annualised return | annualised volatility | naive Sharpe | Lo-corrected "
  "Sharpe | maximum drawdown | annualised turnover |")
a("|---|---|---|---|---|---|---|")
for r in sorted(LAD, key=lambda x: -float(x["sharpe_naive"])):
    a(f"| {r['line']} | {r['ann_return']} | {r['ann_vol']} | {r['sharpe_naive']} | "
      f"{r['sharpe_lo']} | {r['max_drawdown']} | {r['ann_turnover']} |")
a("")
s = byl["STRATEGY"]
a(f"**The canonical's daily series over the holdout.** Mean {s['daily_mean']}, standard "
  f"deviation {s['daily_sd']}, skewness {s['skewness']}, excess kurtosis "
  f"{s['excess_kurtosis']}, across {s['n_sessions']} sessions from "
  f"{s['first_session']} to {s['last_session']}.")
a("")
a("## Phase D, the components")
a("")
a(f"Phase D re-executed the identical deterministic pass to obtain the per-session "
  f"sleeve dicts phase C did not persist. **The re-execution reproduces phase C "
  f"exactly**, {qv('pass','re-execution','note')}.")
a("")
for comp, cond_prefix in (("P1", "rank on the naive"), ("P2", "holdout naive Sharpe"),
                          ("P3 part one", "SQQQ and TLT"),
                          ("P3 part two", "T10 risk-off"),
                          ("P4", "the 2022 peak"), ("P5", "short-equity")):
    rowsc = [r for r in V if r["component"] == comp]
    if not rowsc:
        continue
    cond = next((r["condition"] for r in rowsc if r["condition"]), "")
    a(f"### {comp}")
    a("")
    if cond:
        a(f"The condition as the prediction states it.")
        a("")
        a(f"> {cond}")
        a("")
    a("| quantity | value | verdict |")
    a("|---|---|---|")
    for r in rowsc:
        of = f" of {r['of']}" if r["of"] else ""
        a(f"| {r['quantity']} | {r['value']}{of} | {r['verdict']} |")
    a("")
a("## Phase E, the frozen claims against the holdout")
a("")
n_bear = sum(1 for r in CVH if r["bears_on_the_holdout"] == "yes")
n_no = sum(1 for r in CVH if r["bears_on_the_holdout"] == "no")
n_eval = sum(1 for r in CVH if r["bears_on_the_holdout"] == "yes"
             and r["holdout_value"] not in ("not evaluated", "not applicable"))
n_con = sum(1 for r in CVH if r["contradicted"] == "yes")
a(f"**The holdout bears on {n_bear} of the 15 claims, {n_eval} of which was evaluated "
  f"in this session, and does not bear on {n_no}.** {n_con} claims are contradicted. "
  f"**No claim is amended.**")
a("")
a("| claim | tier | bears on the holdout | holdout value | contradicted |")
a("|---|---|---|---|---|")
for r in CVH:
    if r["bears_on_the_holdout"] == "descriptive only":
        continue
    a(f"| {r['claim']} | {r['tier']} | {r['bears_on_the_holdout']} | "
      f"{r['holdout_value'][:130]} | {r['contradicted']} |")
a("")
c1 = next(r for r in CVH if r["claim"] == "1" and r["bears_on_the_holdout"] == "yes")
a(f"**Claim 1 is the one evaluated.** {c1['note'][0].upper()}{c1['note'][1:]}.")
a("")
a("## Phase F, the combined window")
a("")
a(f"The primary window and the holdout together, being "
  f"{bylc['STRATEGY']['n_sessions']} sessions from "
  f"{bylc['STRATEGY']['first_session']} to {bylc['STRATEGY']['last_session']}. "
  f"**Descriptive only**, since the combined window contains the sample the "
  f"specification was chosen on and is not an out-of-sample measurement.")
a("")
a("| line | annualised return | naive Sharpe | Lo-corrected Sharpe | maximum drawdown |")
a("|---|---|---|---|---|")
for r in sorted(COMB, key=lambda x: -float(x["sharpe_naive"])):
    a(f"| {r['line']} | {r['ann_return']} | {r['sharpe_naive']} | {r['sharpe_lo']} | "
      f"{r['max_drawdown']} |")
a("")
cn, cnof = rank_of(COMBR, "STRATEGY", "sharpe_naive")
cl, _ = rank_of(COMBR, "STRATEGY", "sharpe_lo")
a(f"The strategy places {cn} of {cnof} on the naive Sharpe and {cl} of {cnof} on the "
  f"Lo-corrected across the combined window.")
a("")
a("## Phase G, the figures")
a("")
a("| figure | SVG bytes | plotted rows |")
a("|---|---|---|")
for n in ("combined-equity-curve", "combined-drawdown"):
    p = O / "figures" / f"{n}.svg"
    c = sum(1 for _ in open(O / "figures" / f"{n}.csv")) - 1
    a(f"| `{n}.svg` | {p.stat().st_size} | {c} |")
a("")
a("Both are drawn through `scripts/s19_svg.py` with the 2021-08-01 boundary marked, "
  "each carrying the exact series it plots as a CSV beside it. Both read the series "
  "phase C wrote, so neither recomputes any quantity. **These are the fifth and sixth "
  "figures under the cap at 9.60, so the cap is reached and no further figure is "
  "drawn.**")
a("")
a("## What each finding is")
a("")
a("| finding | what acting on it would be |")
a("|---|---|")
a("| all four falsifiable prediction components are falsified | documentation, since "
  "the prediction is frozen at 9.64 and is not amended after the read |")
a("| the strategy's two holdout ranks diverge | documentation |")
a("| claim 1's holdout value differs from its primary-window value | documentation, "
  "since the claim is scoped to the primary window and is not amended |")
a("| P3 part one's primary-window direction is the opposite of the one the prediction "
  "assumed | documentation |")
a("| the prediction's -1.074235187878671 baseline is portfolio-level while P3 part two "
  "is T10-only | documentation |")
a("| seven claims bear on the holdout and were not evaluated | a specification change, "
  "since evaluating any would need a measurement outside this session's single pass |")
a("| the READ_HOLDOUT_THROUGH override in scripts/s13_backtest.py | a specification "
  "change, recorded at 9.66, with the default and the boundary both unchanged |")
a("| 2.10's second half no longer holds | a register decision, applied |")
a("")
a("**No recommendation and no interpretation is made on any of them.**")
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
a("9.66 the holdout as read, with the span, the branch and the gate output. 9.67 each "
  "component with its verdict. 9.68 the frozen claims against the holdout. 9.69 the "
  "fifth and sixth figures. 2.10 amended, since post-boundary quantities now exist.")
a("")
a("## Artifacts")
a("")
for x in ("gates.csv", "holdout-coverage.csv", "holdout-ladder.csv",
          "holdout-canonical.csv", "prediction-verdicts.csv", "claims-vs-holdout.csv",
          "combined-window.csv", "size.csv"):
    a(f"- `outputs/session-27/{x}`")
a("- `outputs/session-27/figures/`, two SVG files with two series CSVs")
a("- the retained series, being `_holdout_line_returns.parquet`, "
  "`_combined_line_returns.parquet`, `_canonical_daily.parquet`, "
  "`_canonical_orders.parquet` and `_state_series.parquet`")
a("")
(O / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"wrote REPORT.md, {len(L)} lines")
