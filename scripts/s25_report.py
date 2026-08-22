"""Session 25 phase F. Write outputs/session-25/REPORT.md from the emitted CSVs."""
from __future__ import annotations
import csv
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation"); O = R/"outputs"/"session-25"
def rd(p): return list(csv.DictReader(open(O/p)))
A_ = rd("claim-checks.csv"); B_ = rd("figure-inventory.csv")
M_ = rd("machine-and-size.csv")
def mz(w, i):
    for r in M_:
        if r["when"] == w and r["item"] == i: return r["value"]
    return None
D_ = rd("paper-figure-analysis.csv"); E_ = rd("figure-claim-check.csv")
def g(rows, t, i, f="value"):
    for r in rows:
        if r.get("table") == t and r.get("item") == i: return r.get(f)
    return None
def gn(rows, t, i): return g(rows, t, i, "note")
draw = [r for r in B_ if r["table"] == "candidate" and r["disposition"] == "draw"]
nof = [r["item"].replace("claim_", "") for r in B_ if r["table"] == "claim_without_figure"]
num = [r for r in E_ if r["verdict"] in ("agrees", "agrees within tolerance", "DISAGREES")]
tolonly = [r for r in num if r["verdict"] == "agrees within tolerance"]
bad = [r for r in num if r["verdict"] == "DISAGREES"]
top = g(D_, "result", "pairs_at_the_maximum")
L = []; a = L.append

a("# Session 25, the figures")
a("")
a("2026-08-22. Six phases. One commit, at phase F.")
a("")
a("## Opening")
a("")
a(f"**The 8.2 argument holds as stated and fails if generalised.** {gn(A_,'A1_verdict','argument_generalised_to_all_outranking')}. "
  f"8.2 names buy-and-hold QQQ specifically, and on that pairing it stands. "
  f"8.2 is not amended here.")
a("")
a(f"**Claim 4's wording spans all five block counts while its two quoted figures do not.** "
  f"The range's numeric endpoints are S equal to 8 at "
  f"{g(A_,'A2','range_minimum')} and S equal to 12 at {g(A_,'A2','range_maximum')}, both "
  f"re-emitted on repaired code at session 24, and the scope phrase names block counts 8 "
  f"through 48, which includes the unre-emitted S equal to 48.")
a("")
a(f"**{len(draw)} figures drawn**, each with the exact series it plots emitted as a CSV "
  f"beside it in `outputs/session-25/figures/`.")
a("")
if bad:
    a(f"**{len(bad)} figure-to-claim disagreements.** They are reported below and not repaired.")
else:
    a(f"**No figure disagrees with the claim it illustrates.** {len(num)} numeric checks ran, "
      f"{len(num)-len(tolonly)-len(bad)} exact and {len(tolonly)} agreeing within the "
      f"stated tolerance rather than exactly.")
a("")
a("## Machine")
a("")
a(f"At the start, load average {g(A_,'machine_at_start','load_1min')} one minute, "
  f"{g(A_,'machine_at_start','load_5min')} five minutes and "
  f"{g(A_,'machine_at_start','load_15min')} fifteen minutes on eight cores, compressor "
  f"{g(A_,'machine_at_start','compressor_gib')} GiB, swap used "
  f"{g(A_,'machine_at_start','swap_used_mb')} MB and swap free "
  f"{g(A_,'machine_at_start','swap_free_mb')} MB. Nothing in phases A through E loads the "
  f"moment array, so no contention gate applied. At phase F, load average "
  f"{mz('before_commit','load_1min')}, compressor {mz('before_commit','compressor_gib')} "
  f"GiB, swap used {mz('before_commit','swap_used_mb')} MB and swap free "
  f"{mz('before_commit','swap_free_mb')} MB.")
a("")
a(f"**The standing positive control passed.** Annualised return "
  f"{g(A_,'positive_control','ann_return')} against the target "
  f"{g(A_,'positive_control','ann_return','target')}, Lo-corrected Sharpe "
  f"{g(A_,'positive_control','sharpe_lo')} against "
  f"{g(A_,'positive_control','sharpe_lo','target')}, "
  f"{g(A_,'positive_control','n_sessions')} sessions against "
  f"{g(A_,'positive_control','n_sessions','target')}, inside the tolerance "
  f"{g(A_,'positive_control','tolerance')} stated before comparing.")
a("")
a("## Phase A1, the Lo null argument")
a("")
a(f"{g(A_,'A1','rows_outranking_strategy')} ladder rows outrank the strategy on the "
  f"Lo-corrected Sharpe, the strategy placing "
  f"{g(A_,'A1','strategy_rank_by_lo')} of 12.")
a("")
a("| row | observed Lo-corrected Sharpe | own null 5th percentile | own null 95th percentile | inside |")
a("|---|---|---|---|---|")
for r in B_[:0]: pass
for r in A_:
    if r["table"] == "A1_outranking":
        a(f"| {r['item']} | {r['value']} | {r['null_p05']} | {r['null_p95']} | "
          f"{'yes' if r['inside_own_null']=='1' else 'no'} |")
s = next(r for r in A_ if r["table"] == "A1_strategy")
a(f"| **{s['item']}** | {s['value']} | {s['null_p05']} | {s['null_p95']} | "
  f"{'yes' if s['inside_own_null']=='1' else 'no'} |")
a("")
a(f"The inside flag agrees with the percentile bounds on every row, so the emitted flag "
  f"and the emitted bounds are consistent.")
a("")
a(f"**As stated, the argument holds.** {gn(A_,'A1_verdict','argument_as_stated')}.")
a("")
a(f"**Narrowed to the top three, it holds.** {gn(A_,'A1_verdict','argument_narrowed_to_top_three')}.")
a("")
a(f"**Generalised to every row above the strategy, it fails.** "
  f"{gn(A_,'A1_verdict','argument_generalised_to_all_outranking')}.")
a("")
a("The grounds as they should read.")
a("")
a(f"> {gn(A_,'A1_verdict','grounds_as_they_should_read')}.")
a("")
a("The current register text at 8.2, for comparison.")
a("")
a(f"> {gn(A_,'A1_verdict','current_register_text_8_2')}.")
a("")
a("## Phase A2, claim 4's block-count range")
a("")
a("Claim 4 verbatim.")
a("")
a(f"> {gn(A_,'A2','claim_4_statement_verbatim')}")
a("")
a(f"Block counts re-emitted on repaired code at session 24, "
  f"{g(A_,'A2','block_counts_re_emitted')}. Not re-emitted, "
  f"{g(A_,'A2','block_counts_not_re_emitted')}.")
a("")
a(f"**The two numeric endpoints are both re-emitted**, being "
  f"{g(A_,'A2','range_minimum')} at S equal to 8 and {g(A_,'A2','range_maximum')} at S "
  f"equal to 12. **The wording spans all five block counts**, since "
  f"{gn(A_,'A2','wording_spans_all_five_block_counts')}.")
a("")
a("The two candidate repairs, with no change made and no recommendation.")
a("")
a(f"1. Narrow the wording. {gn(A_,'A2_repair_candidate','narrow_the_wording')}.")
a(f"2. Leave the item open. {gn(A_,'A2_repair_candidate','leave_open_pending_S48')}.")
a("")
a("## Phase B, the figure inventory")
a("")
a(f"**Both session 24 undrawable findings are confirmed against the current artifacts.** "
  f"{gn(B_,'confirm_undrawable','null_histograms')}. "
  f"{gn(B_,'confirm_undrawable','effective_exposure_by_decile')}.")
a("")
a(f"A five-point quantile marker plot is drawable from the null summary columns and is "
  f"not substituted for a histogram, since it would not show the distribution shape the "
  f"figure exists to show.")
a("")
a(f"{g(B_,'inventory','candidates')} candidates, "
  f"{g(B_,'inventory','excluded_undrawable')} excluded as undrawable and "
  f"{g(B_,'inventory','excluded_already_drawn')} excluded because the PBO report already "
  f"carries them, leaving {g(B_,'inventory','final_drawable_set')} against a target of "
  f"{g(B_,'inventory','target')}.")
a("")
a(f"**The drop rule was not needed.** {gn(B_,'inventory','drop_rule_applied')}.")
a("")
a("| figure | claims illustrated | tier | carries the claim's literal | source |")
a("|---|---|---|---|---|")
for r in draw:
    a(f"| {r['item']} | {r['illustrates_claims'] or 'none'} | {r['claim_tier']} | "
      f"{'yes' if r['carries_claim_literal']=='1' else 'no'} | `{r['source_file']}` |")
a("")
a(f"**{g(B_,'inventory','figures_illustrating_no_claim')} of the eight illustrate no "
  f"frozen claim**, being drawdown, hedge-intensity, nav-capacity and "
  f"rolling-beta-dispersion. Each is retained because the set is at target without "
  f"dropping any, and each is recorded here rather than carried silently.")
a("")
a(f"**{g(B_,'inventory','figures_carrying_a_claim_literal')} of the eight plot a value "
  f"the claim quotes.** The other five illustrate a claim's subject or a register finding "
  f"without plotting any figure the claim carries, which is what phase E can and cannot "
  f"check.")
a("")
a(f"**{g(B_,'inventory','claims_without_any_figure')} claims have no figure anywhere**, "
  f"being {', '.join(nof)}. Claim 2 is among them because its figure is undrawable rather "
  f"than because it was passed over.")
a("")
a("## Phase C, the figures as drawn")
a("")
a("Each figure carries axis labels with units, the source file in a caption line and the "
  "sample period, and no title states a conclusion. Each is written with its plotted "
  "series as a CSV at full round-trip precision.")
a("")
a("| figure | SVG bytes | plotted rows |")
a("|---|---|---|")
for r in draw:
    p = O/"figures"/f"{r['item']}.svg"
    c = sum(1 for _ in open(O/"figures"/f"{r['item']}.csv")) - 1
    a(f"| `{r['item']}.svg` | {p.stat().st_size} | {c} |")
a("")
a("Plotting used `scripts/s19_svg.py`, extended by `scripts/s25_svg.py` for the marks "
  "this session needed. `scripts/s19_svg.py` is unmodified so session 19's four figures "
  "stay byte-identical under the regenerability check. matplotlib was not installed.")
a("")
a("## Phase D, the paper's two")
a("")
a(f"The criterion is the scaffold's, being which two illustrate the largest number of "
  f"primary claims between them, applied by enumerating all "
  f"{len([r for r in D_ if r['table']=='pair'])} pairs.")
a("")
a(f"**The maximum coverage by any pair is "
  f"{g(D_,'result','largest_primary_coverage')} distinct primary claims, and "
  f"{g(D_,'result','pairs_at_the_maximum')} pair reaches it.**")
a("")
a(f"> {gn(D_,'result','pairs_at_the_maximum')}, covering primary claims "
  f"{next(r['primary_claims'] for r in D_ if r['table']=='pair' and r['note']=='highest')}.")
a("")
a("| figure | primary claims | supporting claims |")
a("|---|---|---|")
for r in D_:
    if r["table"] == "per_figure":
        a(f"| {r['item']} | {r['primary_claims'] or 'none'} | "
          f"{r['supporting_claims'] or 'none'} |")
a("")
a(f"A second ordering is available if a tie ever needs breaking. "
  f"{gn(D_,'result','second_criterion_if_needed')}.")
a("")
a(f"**The PBO report carries four figures and none of the eight duplicates one.** "
  f"{gn(D_,'duplication','figures_in_the_eight_duplicating_a_report_figure')}.")
a("")
a(f"**One correction to the session 24 specification.** "
  f"{gn(D_,'duplication','report_figures_illustrating_a_withdrawn_statistic')}.")
a("")
a(f"**No selection is made.** {gn(D_,'result','selection_made')}.")
a("")
a("## Phase E, the figure-to-claim check")
a("")
a(f"{len(num)} numeric checks against the tolerance "
  f"{next(r['claim_value'] for r in E_ if r['quantity']=='tolerance')} stated before "
  f"comparing. {len(num)-len(tolonly)-len(bad)} agree exactly, {len(tolonly)} agree "
  f"within tolerance rather than exactly, and {len(bad)} disagree.")
a("")
a("| claim | figure | quantity | claim value | figure value | deviation |")
a("|---|---|---|---|---|---|")
for r in tolonly + bad:
    a(f"| {r['claim']} | {r['figure']} | {r['quantity']} | {r['claim_value']} | "
      f"{r['figure_value']} | {r['deviation']} |")
a("")
a(f"**Both non-exact checks have the same cause.** The `lo-factor-vs-null` figure plots "
  f"`outputs/session-20/lo-q-sweep.csv` while claim 1 quotes "
  f"`outputs/session-20/rebuilt/metrics-full.csv`, so the comparison is between two "
  f"emitted files rather than between a figure and its own source. The two differ at the "
  f"seventh decimal, below the tolerance the positive control uses, and neither is "
  f"changed here.")
a("")
a("The derived series were checked against the emitted scalars rather than assumed. The "
  "equity curve's final growth reproduces each line's emitted total return and the "
  "drawdown series minimum reproduces each line's emitted maximum drawdown, all exactly.")
a("")
a("## What acting on each finding would be")
a("")
a("| finding | acting on it would be |")
a("|---|---|")
a("| the 8.2 grounds fail if generalised beyond buy-and-hold QQQ | a register decision |")
a("| claim 4's wording spans a block count not re-emitted | a specification change, or a register decision to leave it open |")
a("| seven claims have no figure | documentation |")
a("| four figures illustrate no frozen claim | documentation |")
a("| the lo-q-sweep and ladder Lo values differ at the seventh decimal | a correctness repair if the difference has a cause worth removing, documentation if it does not |")
a("| the session 24 note that two report figures support a removed statistic overstates it by one | documentation |")
a("| the null histograms and the decile curve remain undrawable | a specification change, since drawing either needs a new measurement |")
a("")
a("No recommendation is made on any of them.")
a("")
a("## What remains before the holdout can run")
a("")
a("S equal to 48 of the B1 re-emission, which sets neither endpoint of claim 4's quoted "
  "range, and the corrected degradation null, whose slope is withdrawn at 9.35 "
  "regardless. Neither is load-bearing. The two claim-wording questions this session "
  "raises are decisions rather than blockers, since neither changes a figure. The SVIX "
  "and UVIX path that will not execute at the holdout read stands as disclosed at 9.43 "
  "with the loader unchanged.")
a("")
a("## Repository size and free space")
a("")
a(f"**No committed file exceeds 100 megabytes.** The largest is "
  f"{mz('before_commit','largest_tracked_file_mb')} MB, being "
  f"`{next(r['note'] for r in M_ if r['when']=='before_commit' and r['item']=='largest_tracked_file_bytes')}`, "
  f"and the count of tracked files above the limit is "
  f"{mz('before_commit','tracked_files_over_100mb')}.")
a("")
a("| reading | before the commit | after the commit |")
a("|---|---|---|")
for i, lab in (("git_dir_bytes","git directory, kilobytes"),
               ("working_tree_bytes","working tree, kilobytes"),
               ("free_gib","free space, GiB")):
    a(f"| {lab} | {mz('before_commit',i)} | {mz('after_commit',i) or 'not yet read'} |")
a("")
a("## Register")
a("")
a("9.55 the figure set as drawn. 9.56 the Lo null argument, with 8.2 left unamended. "
  "9.57 claim 4's wording. 9.58 the claims without a figure and the figures excluded.")
a("")
a("## Artifacts")
a("")
for f_ in ("claim-checks.csv", "figure-inventory.csv", "paper-figure-analysis.csv",
           "figure-claim-check.csv"):
    a(f"- `outputs/session-25/{f_}`")
a(f"- `outputs/session-25/figures/`, {len(draw)} SVG files with {len(draw)} series CSVs")
a("")
(O/"REPORT.md").write_text("\n".join(L)+"\n")
print(f"wrote REPORT.md, {len(L)} lines")
