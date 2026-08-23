"""Session 30 phase I. Write outputs/session-30/REPORT.md from the emitted CSVs."""
from __future__ import annotations

import csv
import re
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
O = R / "outputs" / "session-30"


def rd(p):
    return list(csv.DictReader(open(O / p)))


PRE = rd("preregistration.csv"); SW = rd("corporate-action-sweep.csv")
DIS = rd("disposition.csv"); NU = rd("holdout-nulls.csv"); MF = rd("multi-factor.csv")
BS = rd("bootstrap-intervals.csv"); NV = rd("nav-sensitivity.csv")
IA = rd("instrument-attribution.csv"); SZ = rd("size.csv")


def g(rows, t, i, f="value", w=None):
    for r in rows:
        if r.get("table") == t and r.get("item") == i and (w is None or r.get("window") == w):
            return r.get(f)
    return None


L = []; a = L.append
a("# Session 30, the class sweep, the disposition and the resumed phases")
a("")
a("2026-08-23. Nine phases. One commit, at phase I. No specification is selected on any "
  "holdout observation, no frozen input is repaired and no canonical value moves.")
a("")
a("## Opening")
a("")
a(f"**The class sweep screened {g(SW,'B1_summary','sessions_screened')} "
  f"instrument-sessions across {g(SW,'B1_summary','instruments_screened')} held "
  f"instruments and flagged {g(SW,'B1_summary','sessions_flagged')}, a selectivity of "
  f"{re.search(r'0[.0-9]+', g(SW,'B1_summary','sessions_flagged','note') or '0').group()}.** "
  f"{g(SW,'B4_summary','price_discontinuities_with_no_recorded_split')} price "
  f"discontinuities carry no recorded split, of which "
  f"{g(SW,'B4_summary','breaks_after_conjoining_the_two_screens')} survive the residual "
  f"screen as breaks, being "
  f"{g(SW,'B4_summary','breaks_after_conjoining_the_two_screens','note')}.")
a("")
a(f"**Gate B reads {g(SW,'gate_B','verdict')}.** "
  f"{g(SW,'gate_B','verdict','note')}. The first implementation tested materiality "
  f"without conjoining the break condition and would have read "
  f"{g(SW,'gate_B','verdict_materiality_alone')}, and both evaluations are recorded.")
a("")
a("**The holdout nulls.**")
a("")
a("| null | metric | holdout exceedances | primary exceedances |")
a("|---|---|---|---|")
for r in NU:
    if r["table"] == "null":
        a(f"| {r['item']} | {r['metric']} | {r['exceedances']} of {r['n_draws']} | "
          f"{r['primary_exceedances']} |")
a("")
a(f"**The multi-factor alpha survives.** The holdout annualised alpha falls from "
  f"{g(MF,'single_factor','alpha_annualised',w='holdout')} to "
  f"{g(MF,'multi_factor','alpha_annualised',w='holdout')}, absorbing "
  f"{g(MF,'verdict','alpha_absorbed_by_the_extra_factors',w='holdout')} or "
  f"{g(MF,'verdict','share_of_the_single_factor_alpha_absorbed',w='holdout')} of it, "
  f"with the Newey-West t moving from "
  f"{g(MF,'single_factor','alpha_t_newey_west',w='holdout')} to "
  f"{g(MF,'multi_factor','alpha_t_newey_west',w='holdout')}.")
a("")
a(f"**The holdout result is capacity-bounded.** Across five starting NAV levels the "
  f"naive Sharpe runs from {[r['sharpe_naive'] for r in NV if r['table']=='G1'][0]} at "
  f"the study anchor to {[r['sharpe_naive'] for r in NV if r['table']=='G1'][-1]} at the "
  f"terminal NAV, degrading "
  f"{g(NV,'G1_summary','degrades_smoothly_or_breaks')} and monotone in NAV.")
a("")
a("## Machine and the positive control")
a("")
a(f"At phase A, load average {g(PRE,'machine_at_phase_A','load_1min')} one minute, "
  f"{g(PRE,'machine_at_phase_A','load_5min')} five minutes and "
  f"{g(PRE,'machine_at_phase_A','load_15min')} fifteen minutes on "
  f"{g(PRE,'machine_at_phase_A','cores')} cores, compressor "
  f"{g(PRE,'machine_at_phase_A','compressor_gib')} GiB, swap used "
  f"{g(PRE,'machine_at_phase_A','swap_used_mb')} MB and swap free "
  f"{g(PRE,'machine_at_phase_A','swap_free_mb')} MB. At phase B the one-minute figure "
  f"read {g(SW,'machine_at_phase_B','load_1min')}, at phase D "
  f"{g(NU,'machine_at_phase_D','load_1min')}, at phase E "
  f"{g(MF,'machine_at_phase_E','load_1min')}, at phase F "
  f"{g(BS,'machine_at_phase_F','load_1min')}, at phase G "
  f"{g(NV,'machine_at_phase_G','load_1min')} and at phase H "
  f"{g(IA,'machine_at_phase_H','load_1min')}.")
a("")
a(f"**The standing positive control passed** at "
  f"{g(PRE,'positive_control','ann_return')} annualised and "
  f"{g(PRE,'positive_control','sharpe_lo')} Lo-corrected over "
  f"{g(PRE,'positive_control','n_sessions')} sessions, inside the "
  f"{g(PRE,'positive_control','tolerance')} tolerance stated before comparing.")
a("")
a("## Phase A, the ruling and the pre-registration")
a("")
a("The session 28 ruling stands. The complete quantity list for phases B through H went "
  "into the register at 9.82 before any measurement ran, and it is closed. Every "
  "measurement is a disclosed post-hoc sensitivity under 9.10 with its motivation "
  "recorded first, and the class sweep's own motivation is recorded before the rest.")
a("")
a(f"**Gate B was written before the check** and materiality was defined before the "
  f"flags were seen, at {g(PRE,'gate_B','materiality_definition')} of the window's "
  f"arithmetic return sum.")
a("")
a("## Phase B, the corporate action class sweep")
a("")
a("### The rule, stated before running")
a("")
a(f"{g(SW,'rule','residual_tolerance','note')}. RESIDUAL_TOL is "
  f"{g(SW,'rule','residual_tolerance')}.")
a("")
a(f"{g(SW,'rule','min_abs_underlying_return','note')}, the floor being "
  f"{g(SW,'rule','min_abs_underlying_return')}, and "
  f"{g(SW,'rule','absolute_return_tolerance','note')} at "
  f"{g(SW,'rule','absolute_return_tolerance')}.")
a("")
a("### B1, the screen")
a("")
a("| instrument | flagged | screened | below the floor | proxy | registered multiple |")
a("|---|---|---|---|---|---|")
for r in SW:
    if r["table"] == "instrument_screen":
        a(f"| {r['item']} | {r['value']} | {r['n_screened']} | {r['n_low_underlying']} | "
          f"{r['proxy']} | {r['registered_multiple']} |")
a("")
a(f"{g(SW,'B1_summary','sessions_below_the_underlying_floor')} instrument-sessions fell "
  f"below the underlying floor and were screened on absolute return instead. "
  f"{g(SW,'B1_summary','benchmarks_with_no_frozen_proxy')} registered benchmarks lack a "
  f"frozen proxy.")
a("")
a("**The three session 29 volatility flags under this sweep's rule.**")
a("")
for r in SW:
    if r["table"] == "proxy_limitation":
        a(f"- {r['item']}, {r['note']}.")
a("")
a("### B2, ordering by contribution")
a("")
a("| instrument | window | rank | contribution | flagged sessions | flagged contribution |")
a("|---|---|---|---|---|---|")
for r in SW:
    if r["table"] == "contribution_rank" and int(r["rank"]) <= 6:
        a(f"| {r['item']} | {r['window']} | {r['rank']} | {r['value']} | "
          f"{r['n_flagged']} | {r['flagged_contribution']} |")
a("")
for w in ("holdout", "primary"):
    a(f"**{w.capitalize()}.** Cumulative flagged contribution "
      f"{g(SW,'B2_summary','cumulative_flagged_contribution',w=w)}, "
      f"{g(SW,'B2_summary','cumulative_flagged_contribution','note',w=w)}. Instruments "
      f"material under the gate, "
      f"{g(SW,'B2_summary','instruments_material_under_the_gate','note',w=w)}.")
    a("")
a(f"**TQQQ named explicitly.** It contributes "
  f"{g(SW,'B2_named','TQQQ',w='holdout')} across the holdout and "
  f"{g(SW,'B2_named','TQQQ',w='primary')} across the primary window, with "
  f"{[r['n_flagged'] for r in SW if r['table']=='B2_named'][0]} flagged sessions.")
a("")
a("### B3, indicator contamination")
a("")
a(f"{g(SW,'B3_summary','breaks_examined')} flagged sessions examined. "
  f"{g(SW,'B3_summary','longest_contaminated_span')} is the longest contaminated span, "
  f"since no indicator reads any flagged instrument. "
  f"{g(SW,'B3_summary','longest_contaminated_span','note')}.")
a("")
a(f"**{g(SW,'B3_summary','contaminated_sessions_coinciding_with_a_terminal_firing')} "
  f"contaminated indicator sessions coincide with a terminal firing**, which is the "
  f"condition gate B tests. The relative-strength reads carrying a literal ticker are "
  + ", ".join(sorted({r["item"] for r in SW if r["table"] == "indicator_read"}))
  + ", and no flagged instrument is among them.")
a("")
a("### B4, the split column's reliability")
a("")
a(f"{g(SW,'B4_summary','recorded_splits_with_no_price_discontinuity')} recorded splits "
  f"carry no matching price discontinuity, "
  f"{g(SW,'B4_summary','recorded_splits_with_no_price_discontinuity','note')}. "
  f"{g(SW,'B4_summary','price_discontinuities_with_no_recorded_split')} price "
  f"discontinuities carry no recorded split.")
a("")
a("| instrument | date | is a break | reason |")
a("|---|---|---|---|")
for r in SW:
    if r["table"] == "break_classification":
        a(f"| {r['item']} | {r['date']} | {'yes' if r['value']=='1' else 'no'} | "
          f"{r['note']} |")
a("")
a("### Gate B")
a("")
a("| test | result |")
a("|---|---|")
for i in ("instruments_with_a_break", "instruments_material_by_flagged_contribution",
          "instruments_with_both", "contaminated_session_coinciding_with_a_firing",
          "verdict_materiality_alone", "verdict"):
    a(f"| {i} | {g(SW,'gate_B',i)} {('being ' + (g(SW,'gate_B',i,'note') or '')) if g(SW,'gate_B',i,'note') else ''} |")
a("")
a(f"{g(SW,'gate_B','materiality_definition_unchanged','note')}.")
a("")
a("## Phase C, the disposition and one restatement")
a("")
a("### C1, the three options, adopted by none")
a("")
for opt, lab in (("option_1_repair", "Option one, repair the frozen input"),
                 ("option_2_disclose", "Option two, disclose unrepaired"),
                 ("option_3_permanent_check",
                  "Option three, register the defect and add a permanent check")):
    a(f"**{lab}.**")
    a("")
    for r in DIS:
        if r["table"] == opt:
            a(f"- {r['item']}, {r['value']}. {r['note']}")
    a("")
a("**The measured facts bearing on the choice.**")
a("")
for r in DIS:
    if r["table"] == "measured_facts":
        a(f"- {r['item']} {r.get('window','')} {r['value']}. {r['note'][:220]}")
a("")
a(f"**{g(DIS,'disposition','adopted','note')}.**")
a("")
a("### C2, session 28's G3 restated on one convention at a time")
a("")
a("| window | convention | range | mover |")
a("|---|---|---|---|")
for w in ("holdout", "primary"):
    for c in ("naive", "lo"):
        a(f"| {w} | {c} | {g(DIS,'C2_range',c,w=w)} | {g(DIS,'C2_mover',c,w=w)} |")
a("")
a(f"{g(DIS,'C2_correction','session_28_G3_mixed_conventions','note')}.")
a("")
a(f"{g(DIS,'C2_construction','series_drop_rather_than_rebuild','note')}.")
a("")
a("## Phase D, the holdout nulls")
a("")
a(f"{g(NU,'construction','source','note')}. {g(NU,'construction','seed','note')}, at "
  f"{g(NU,'construction','n_draws')} replications.")
a("")
a("| null | metric | exceedances | p value | percentile | null mean | null sd |")
a("|---|---|---|---|---|---|---|")
for r in NU:
    if r["table"] == "null":
        a(f"| {r['item']} | {r['metric']} | {r['exceedances']} of {r['n_draws']} | "
          f"{r['p_value']} | {r['percentile']} | {r['null_mean']} | {r['null_sd']} |")
a("")
a(f"**Both nulls are centred near zero on annualised return**, so the strategy sits "
  f"above a null centred at zero rather than above a high one.")
a("")
a(f"{g(NU,'observed','statistic_drops_the_first_session','note')}.")
a("")
a("## Phase E, the multi-factor decomposition")
a("")
a("| factor | instrument | present | source |")
a("|---|---|---|---|")
for r in MF:
    if r["table"] == "factor":
        a(f"| {r['item']} | {r['instrument']} | {r['value']} | {r['source']} |")
a("")
a(f"{g(MF,'factor_set','convention','note')}.")
a("")
a("| entering factor | window | R-squared | incremental | alpha | t |")
a("|---|---|---|---|---|---|")
for r in MF:
    if r["table"] == "incremental":
        a(f"| {r['item']} | {r['window']} | {r['r_squared']} | "
          f"{r['incremental_r_squared']} | {r['alpha_annualised']} | "
          f"{r['alpha_t_newey_west']} |")
a("")
a("| loading | holdout | primary | holdout variance inflation |")
a("|---|---|---|---|")
for r in MF:
    if r["table"] == "loading" and r["window"] == "holdout":
        a(f"| {r['item']} | {r['value']} | {g(MF,'loading',r['item'],w='primary')} | "
          f"{g(MF,'variance_inflation',r['item'],w='holdout')} |")
a("")
a(f"**Semiconductor absorbs almost all of what is absorbed**, its incremental "
  f"R-squared over the holdout being "
  f"{g(MF,'incremental','semiconductor','incremental_r_squared',w='holdout')} against "
  f"the three that follow it. **The alpha survives**, "
  f"{g(MF,'verdict','alpha_absorbed_by_the_extra_factors','note',w='holdout')}.")
a("")
a(f"The multi-factor residual carries a naive Sharpe of "
  f"{g(MF,'multi_factor_residual','residual_sharpe_naive',w='holdout')} against the "
  f"single-factor residual's 1.527991674661622.")
a("")
a("## Phase F, interval estimates")
a("")
a(f"The contention check passed at a one-minute load of "
  f"{g(BS,'contention_check','load_1min')} against a threshold of "
  f"{g(BS,'contention_check','threshold')}. "
  f"{g(BS,'preregistration','mean_block_length','note')}, at "
  f"{g(BS,'preregistration','replications')} replications on seed "
  f"{g(BS,'preregistration','seed')}. The pass ran in "
  f"{g(BS,'machine_at_phase_F_end','seconds')} seconds against a "
  f"{g(BS,'preregistration','wall_limit_seconds')} second limit at a peak resident "
  f"{g(BS,'machine_at_phase_F_end','peak_rss_gb')} GB against a "
  f"{g(BS,'preregistration','memory_ceiling_gb')} GB ceiling.")
a("")
a("| quantity | window | point | 5th | 50th | 95th | bootstrap sd | iid standard error |")
a("|---|---|---|---|---|---|---|---|")
for r in BS:
    if r["table"] == "interval":
        a(f"| {r['item']} | {r['window']} | {r['value']} | {r['p05']} | {r['p50']} | "
          f"{r['p95']} | {r['bootstrap_sd']} | {r['iid_standard_error'] or 'none'} |")
a("")
a(f"**The holdout gap against buy-and-hold QQQ excludes zero at the 5th percentile**, "
  f"{g(BS,'verdict','holdout_gap_vs_buy_hold_QQQ_excludes_zero_at_the_5th_percentile','note')}. "
  f"The primary-window gap does not.")
a("")
a(f"{g(BS,'setup','returns_are_excess_of_the_risk_free_rate','note')}.")
a("")
a("## Phase G, the NAV sensitivity")
a("")
a(f"The contention check passed at a one-minute load of "
  f"{g(NV,'contention_check','load_1min')} against "
  f"{g(NV,'contention_check','threshold')}. {g(NV,'preregistration','axis','note')}.")
a("")
a("### G1, the capacity curve")
a("")
a("| starting NAV | annualised return | naive Sharpe | Lo-corrected | turnover | "
  "events per session | mean trade share of NAV | cap-binding share | rank |")
a("|---|---|---|---|---|---|---|---|---|")
for r in NV:
    if r["table"] == "G1":
        a(f"| {r['value']} | {r['ann_return']} | {r['sharpe_naive']} | "
          f"{r['sharpe_lo']} | {r['ann_turnover']} | {r['events_per_session']} | "
          f"{r['mean_trade_share_of_nav']} | {r['cap_binding_share']} | "
          f"{r['rank_naive']} of 12 |")
a("")
a(f"**Performance degrades {g(NV,'G1_summary','degrades_smoothly_or_breaks')}**, the "
  f"largest adjacent step being "
  f"{g(NV,'G1_summary','largest_single_step_change')} and the curve monotone in NAV. "
  f"The cap-binding share first exceeds 0.75 at a starting NAV of "
  f"{g(NV,'G1_summary','nav_at_which_cap_binding_first_exceeds_0.75')} and 0.90 at "
  f"{g(NV,'G1_summary','nav_at_which_cap_binding_first_exceeds_0.9')}, so throttling is "
  f"not something the holdout introduced.")
a("")
a("### G2, NAV reset at the boundary")
a("")
a("| quantity | reset to the study anchor | inherited |")
a("|---|---|---|")
for r in NV:
    if r["table"] == "G2" and r["item"] != "construction":
        a(f"| {r['item']} | {r['value']} | {r['inherited']} |")
a("")
a(f"{g(NV,'G2','construction','note')}.")
a("")
a("### G3, cap binding by calendar year")
a("")
a("| year | cap-binding share | events | NAV at year end | window |")
a("|---|---|---|---|---|")
for r in NV:
    if r["table"] == "G3":
        a(f"| {r['item']} | {r['value']} | {r['events']} | {r['nav_at_year_end']} | "
          f"{r['note']} |")
a("")
a(f"Binding first exceeds 0.75 in "
  f"{g(NV,'G3_summary','first_year_binding_exceeds_0.75')} and 0.90 in "
  f"{g(NV,'G3_summary','first_year_binding_exceeds_0.90')}.")
a("")
a("### G4, the cost sweep at fixed NAV")
a("")
a("| round-turn cost, bp | naive Sharpe at fixed NAV | session 28 coupled |")
a("|---|---|---|")
for r in NV:
    if r["table"] == "G4":
        a(f"| {r['value']} | {r['sharpe_naive']} | {r['session_28_coupled']} |")
a("")
a(f"{g(NV,'G4_summary','session_28_naive_sharpe_was_already_monotone','note')}.")
a("")
a("## Phase H, instrument attribution")
a("")
a("| instrument | contribution | variance share | own annualised volatility | "
  "correlation with buy-and-hold QQQ | k equal to zero |")
a("|---|---|---|---|---|---|")
for r in IA:
    if r["table"] == "instrument" and r["window"] == "holdout" and int(r["rank"]) <= 10:
        a(f"| {r['item']} | {r['value']} | {r['variance_share']} | "
          f"{r['own_ann_vol']} | {r['corr_with_buy_hold_QQQ'] or 'not computed'} | "
          f"{r['k_zero']} |")
a("")
a(f"**The k equal to zero instruments are {g(IA,'k_zero','instruments','note')}** They "
  f"contribute {g(IA,'summary','k_zero_share_of_return',w='holdout')} of holdout return "
  f"and {g(IA,'summary','k_zero_share_of_variance',w='holdout')} of holdout variance, "
  f"against {g(IA,'summary','k_zero_share_of_return',w='primary')} and "
  f"{g(IA,'summary','k_zero_share_of_variance',w='primary')} over the primary window.")
a("")
a("| exposure | holdout | primary |")
a("|---|---|---|")
for i in ("mean_at_register_k", "mean_at_illustrative_k_1", "difference"):
    a(f"| {i} | {g(IA,'exposure',i,w='holdout')} | {g(IA,'exposure',i,w='primary')} |")
a("")
a(f"{g(IA,'preregistration','illustrative_k','note')}. "
  f"{g(IA,'exposure','realised_volatility_ratio_against_buy_hold_QQQ','note',w='holdout')}.")
a("")
a("## What each finding is")
a("")
a("| finding | what acting on it would be |")
a("|---|---|")
a("| the SOXS 2026-05-26 break | a correctness repair if option one is taken, "
  "documentation if option two, a specification change if option three |")
a("| the split column carrying three discontinuities it does not record | documentation "
  "of the column's false-negative rate across this study's own instruments |")
a("| the gate's first implementation testing materiality alone | a correctness repair, "
  "applied at 9.84 |")
a("| the holdout null exceedance counts | documentation |")
a("| the multi-factor alpha surviving | documentation |")
a("| the factor set needing the open-to-open convention | a correctness repair, applied "
  "inside phase E before any figure was reported |")
a("| the interval estimates | documentation, and a specification change if the paper "
  "adopts intervals in place of point estimates |")
a("| the holdout result being capacity-bounded | documentation |")
a("| session 28's G3 convention mismatch | a correctness repair, applied at 9.91 in the "
  "register rather than by editing that report |")
a("| the k convention's small effect on the exposure figure | documentation |")
a("")
a("**No recommendation is made on any of them.**")
a("")
a("## What remains before the paper")
a("")
a("**The disposition at 9.85 is the one open decision and it is a research decision "
  "rather than a measurement.** Every quantity on the phase A list is computed and "
  "emitted, and no phase was skipped.")
a("")
a("S equal to 48 of the B1 re-emission remains open at 9.48 and sets neither endpoint "
  "of any quoted range, and the corrected degradation null remains unrun at 9.46 with "
  "its slope withdrawn at 9.35, so neither is load-bearing. Seven claims bear on the "
  "holdout and were not evaluated at 9.68, and whether the holdout counterparts this "
  "session and session 28 produced are turned into evaluations against the frozen "
  "claims is a decision that has not been taken.")
a("")
a("What remains is writing.")
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
a("9.82 the pre-registration and the closed quantity list. 9.83 the class sweep. 9.84 "
  "gate B with the first implementation corrected. 9.85 the disposition, open. 9.86 the "
  "holdout nulls. 9.87 the multi-factor decomposition. 9.88 the interval estimates. "
  "9.89 the NAV sensitivity. 9.90 the instrument attribution. 9.91 the correction to "
  "session 28's G3.")
a("")
a("## Artifacts")
a("")
for x in ("preregistration.csv", "corporate-action-sweep.csv", "disposition.csv",
          "holdout-nulls.csv", "multi-factor.csv", "bootstrap-intervals.csv",
          "nav-sensitivity.csv", "instrument-attribution.csv", "size.csv"):
    a(f"- `outputs/session-30/{x}`")
a("")
a("**No figure is drawn, since the cap at 9.60 is reached.**")
a("")
(O / "REPORT.md").write_text("\n".join(L) + "\n")
txt = (O / "REPORT.md").read_text()
bad = re.findall(r"np\.(float64|int64|bool_)\(", txt)
print(f"wrote REPORT.md, {len(L)} lines")
print(f"numpy repr wrappers in the prose: {len(bad)}")
