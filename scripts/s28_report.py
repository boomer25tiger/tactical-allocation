"""Session 28 phase J. Write outputs/session-28/REPORT.md from the emitted CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
O = R / "outputs" / "session-28"


def rd(p):
    return list(csv.DictReader(open(O / p)))


PRE = rd("preregistration.csv"); LADC = rd("ladder-comparison.csv")
LO = rd("lo-holdout-null.csv"); DEC = rd("holdout-decomposition.csv")
YR = rd("holdout-by-year.csv"); CS = rd("holdout-cost-sweep.csv")
RB = rd("robustness.csv"); BE = rd("holdout-beta.csv"); RC = rd("reconciliation.csv")
SZ = rd("size.csv")


def g(rows, t, i, f="value", w=None):
    for r in rows:
        if r.get("table") == t and r.get("item") == i and (w is None or r.get("window") == w):
            return r.get(f)
    return None


L = []; a = L.append
lag = {(r["window"], r["fill_lag"]): r for r in RB if r["table"] == "G1_lag"}
lines = [r for r in LADC if r["table"] == "line"]
byl = {r["item"]: r for r in lines}
s = byl["STRATEGY"]

a("# Session 28, the holdout decomposition")
a("")
a("2026-08-23. Ten phases. One commit, at phase J. No specification is selected on any "
  "holdout observation and no canonical value moves.")
a("")
a("## Opening")
a("")
a(f"**The dedicated lookahead test ran, closing the gap the corrections list item 12 "
  f"records.** Under one additional session of signal-to-execution lag the holdout "
  f"annualised return falls from {lag[('holdout','1')]['ann_return']} to "
  f"{lag[('holdout','2')]['ann_return']} and the naive Sharpe from "
  f"{lag[('holdout','1')]['sharpe_naive']} to {lag[('holdout','2')]['sharpe_naive']}, "
  f"while the ladder rank holds at {lag[('holdout','2')]['rank_naive']} of 12. Over the "
  f"primary window the rank moves from {lag[('primary','1')]['rank_naive']} to "
  f"{lag[('primary','2')]['rank_naive']}. **The rank survives and the level does not.**")
a("")
a(f"**One ladder line beats the strategy on the naive Sharpe over the holdout**, being "
  f"{g(LADC,'summary','lines_beating_the_strategy_on_the_naive_sharpe','note')}. The "
  f"strategy's advantage over buy-and-hold QQQ is "
  f"{g(LADC,'advantage','source_as_measured')}, carrying "
  f"{float(g(LADC,'advantage','holdout_return_ratio_strategy_over_QQQ')):.4f} times its "
  f"annualised return at "
  f"{float(g(LADC,'advantage','holdout_vol_ratio_strategy_over_QQQ')):.4f} times its "
  f"annualised volatility.")
a("")
a(f"**The holdout Lo factor sits inside its own null.** The observed factor of "
  f"{g(LO,'strategy','observed_factor')} lies between the null's 5th and 95th "
  f"percentiles, whose upper bound is {g(LO,'strategy','null_p95_at_holdout_length')} "
  f"against the session 20 figure at n equal to 2472 of 1.4783. **The Lo-corrected rank "
  f"of 1 of 12 occurs at q equal to 252 alone**, the strategy ranking 2 of 12 at every "
  f"other swept q.")
a("")
a(f"**The outperformance is spread rather than concentrated.** All "
  f"{g(YR,'year_summary','years_with_a_positive_gap','n_sessions')} calendar years in "
  f"the span carry a positive arithmetic gap against buy-and-hold QQQ, totalling "
  f"{g(YR,'year_summary','total_gap')}, with 2022 the largest single year at "
  f"{g(YR,'year_summary','largest_single_year_gap')}.")
a("")
a("## Machine and the positive control")
a("")
a(f"Load average {g(PRE,'machine_at_start','load_1min')} one minute, "
  f"{g(PRE,'machine_at_start','load_5min')} five minutes and "
  f"{g(PRE,'machine_at_start','load_15min')} fifteen minutes on eight cores, compressor "
  f"{g(PRE,'machine_at_start','compressor_gib')} GiB, swap used "
  f"{g(PRE,'machine_at_start','swap_used_mb')} MB and swap free "
  f"{g(PRE,'machine_at_start','swap_free_mb')} MB.")
a("")
a(f"**The standing positive control passed** at {g(PRE,'positive_control','ann_return')} "
  f"annualised and {g(PRE,'positive_control','sharpe_lo')} Lo-corrected over "
  f"{g(PRE,'positive_control','n_sessions')} sessions, inside the "
  f"{g(PRE,'positive_control','tolerance')} tolerance stated before comparing. It runs "
  f"with the truncation default in force at "
  f"{g(PRE,'positive_control','holdout_truncation_default')}, so it reads no "
  f"post-boundary session.")
a("")
a("## Phase A, the ruling and the pre-registration")
a("")
a(f"**Permitted.** {g(PRE,'ruling','permitted','note')}.")
a("")
a(f"**Not permitted.** {g(PRE,'ruling','not_permitted','note')}.")
a("")
a("The complete quantity list was written to `outputs/session-28/preregistration.csv` "
  "and to the register at 9.70 before any measurement ran, and it is closed, so no "
  "quantity outside it was added later.")
a("")
a("Two measurements vary a specification and both are recorded under 9.10 as disclosed "
  "post-hoc sensitivities, being the phase F cost sweep and the phase G1 lag shift. "
  "**Neither can change the canonical whatever it returns.**")
a("")
a("## Phase B, the ladder")
a("")
a("Read from `outputs/session-27/holdout-ladder.csv` and "
  "`outputs/session-20/rebuilt/metrics-full.csv`. No pass ran.")
a("")
a("| line | holdout naive | primary naive | holdout Lo | primary Lo | holdout rank | "
  "primary rank | move |")
a("|---|---|---|---|---|---|---|---|")
for r in sorted(lines, key=lambda x: int(x["holdout_rank_naive"])):
    a(f"| {r['item']} | {r['holdout_sharpe_naive']} | {r['primary_sharpe_naive']} | "
      f"{r['holdout_sharpe_lo']} | {r['primary_sharpe_lo']} | "
      f"{r['holdout_rank_naive']} | {r['primary_rank_naive']} | "
      f"{r['rank_move_naive']} |")
a("")
a(f"**Buy-and-hold QQQ.** Naive Sharpe {g(LADC,'buy_hold_QQQ','holdout_sharpe_naive')} "
  f"over the holdout against {byl['buy_hold_QQQ']['primary_sharpe_naive']} over the "
  f"primary window, and Lo-corrected {g(LADC,'buy_hold_QQQ','holdout_sharpe_lo')} "
  f"against {byl['buy_hold_QQQ']['primary_sharpe_lo']}. It falls from rank "
  f"{byl['buy_hold_QQQ']['primary_rank_naive']} to "
  f"{g(LADC,'buy_hold_QQQ','holdout_rank_naive')}. "
  f"{g(LADC,'buy_hold_QQQ','scaffold_figure_check','note')}.")
a("")
a(f"**The matched-exposure line** places "
  f"{g(LADC,'matched_exposure','holdout_rank_naive')} of 12 on the naive Sharpe over "
  f"the holdout against {byl['matched_exposure_levered_QQQ_1.70']['primary_rank_naive']} "
  f"over the primary window.")
a("")
a(f"**The advantage is a return effect.** "
  f"{g(LADC,'advantage','source_as_measured','note')}.")
a("")
a("## Phase C, the Lo estimator at holdout length")
a("")
a(f"The session 20 D1 permutation null re-run at n equal to "
  f"{g(LO,'meta','n_sessions')} with q equal to {g(LO,'meta','q')} at "
  f"{g(LO,'meta','draws')} draws on seed {g(LO,'meta','seed')}, the same seed session 20 "
  f"used. q over n rose to {g(LO,'meta','q_over_n')}.")
a("")
a("| quantity | holdout | session 20 at n equal to 2472 |")
a("|---|---|---|")
a(f"| observed factor | {g(LO,'strategy','observed_factor')} | 1.2664 |")
a(f"| null mean | {g(LO,'strategy','null_mean_at_holdout_length')} | 1.1129 |")
a(f"| null 95th percentile | {g(LO,'strategy','null_p95_at_holdout_length')} | 1.4783 |")
a(f"| inside its own null | {g(LO,'strategy','inside_own_null')} | 1 |")
a("")
a(f"The observed factor sits "
  f"{g(LO,'strategy','standard_deviations_above_the_null_mean')} standard deviations "
  f"above the null mean. **{g(LO,'summary','rows_inside_own_null')} of 12 ladder rows "
  f"sit inside their own nulls at holdout length**, against 9 of 12 at primary length.")
a("")
a(f"**The strategy's rank across q runs {g(LO,'summary','strategy_rank_range_across_q')}.** "
  f"{g(LO,'summary','strategy_rank_range_across_q','note')}. "
  f"{g(LO,'summary','rows_changing_rank_across_q')} of 12 rows change rank across the "
  f"sweep.")
a("")
a(f"The Lo variance turns non-positive at a weighted autocorrelation sum of "
  f"{g(LO,'meta','negative_variance_threshold')}. "
  f"{g(LO,'meta','negative_variance_threshold','note')}.")
a("")
a("## Phase D, the decomposition")
a("")
a("### Sleeve attribution")
a("")
a("| sleeve | holdout | primary window |")
a("|---|---|---|")
for sl in ("T10", "T11", "S2", "S3"):
    a(f"| {sl} | {g(DEC,'sleeve',sl,w='holdout')} | {g(DEC,'sleeve',sl,w='primary')} |")
a("")
a(f"**The short sleeve flips sign**, contributing "
  f"{g(DEC,'instrument_summary','short_sleeve_total',w='holdout')} across the holdout "
  f"against {g(DEC,'instrument_summary','short_sleeve_total',w='primary')} across the "
  f"primary window. TQQQ is the largest positive contributor in both windows, at "
  f"{g(DEC,'instrument_summary','largest_positive',w='holdout')} and "
  f"{g(DEC,'instrument_summary','largest_positive',w='primary')}. The largest negative "
  f"contributor is {g(DEC,'instrument_summary','largest_negative','note',w='holdout')} "
  f"at {g(DEC,'instrument_summary','largest_negative',w='holdout')} over the holdout and "
  f"{g(DEC,'instrument_summary','largest_negative','note',w='primary')} at "
  f"{g(DEC,'instrument_summary','largest_negative',w='primary')} over the primary "
  f"window.")
a("")
a("### Terminals")
a("")
a(f"**{g(DEC,'terminal_summary','fired_first_in_the_holdout')} terminals executed for "
  f"the first time inside the holdout**, being "
  f"{g(DEC,'terminal_summary','fired_first_in_the_holdout','note')}. "
  f"{g(DEC,'terminal_summary','fired_only_in_the_primary_window')} fired in the primary "
  f"window and never in the holdout, being "
  f"{g(DEC,'terminal_summary','fired_only_in_the_primary_window','note')}.")
a("")
a("### Exposure")
a("")
a("| quantity | holdout | primary window |")
a("|---|---|---|")
for k in ("mean", "sd", "min", "max", "share_above_1.0", "share_above_1.7"):
    a(f"| {k} | {g(DEC,'exposure',k,w='holdout')} | {g(DEC,'exposure',k,w='primary')} |")
a("")
a("The primary-window mean reproduces the committed 1.7769723457408557 at "
  "`outputs/session-16/exposure-reconciliation.csv` exactly.")
a("")
a("### Turnover, with the mechanism")
a("")
a("| quantity | holdout | primary window |")
a("|---|---|---|")
for k in ("ann_turnover_committed", "rebalancing_events",
          "rebalancing_events_per_session", "mean_trade_value_share_of_nav",
          "transitions_with_the_participation_cap_binding",
          "cap_binding_share_of_events", "nav_at_window_start", "nav_at_window_end"):
    a(f"| {k} | {g(DEC,'turnover',k,w='holdout')} | {g(DEC,'turnover',k,w='primary')} |")
a("")
a(f"Turnover fell by {g(DEC,'turnover','turnover_fall_share',w='both')}. **Rebalancing "
  f"events per session rose**, so the strategy transitioned more often rather than "
  f"less, while the mean trade value as a share of NAV fell and the participation cap "
  f"bound on nearly every holdout event. **The figures support the capacity reading**, "
  f"since a larger book binds the cap on more transitions and trades a smaller share of "
  f"NAV per event by construction.")
a("")
a("### Drawdown")
a("")
a("| line | maximum drawdown | peak, trough and duration |")
a("|---|---|---|")
for ln in ("STRATEGY", "buy_hold_QQQ", "matched_exposure_levered_QQQ_1.70"):
    a(f"| {ln} | {g(DEC,'drawdown',ln,w='holdout')} | "
      f"{g(DEC,'drawdown',ln,'note',w='holdout')} |")
a("")
a(f"The strategy's drawdown is "
  f"{g(DEC,'drawdown_summary','strategy_against_buy_hold_QQQ',w='holdout')} than "
  f"buy-and-hold QQQ's and "
  f"{g(DEC,'drawdown_summary','strategy_against_matched_exposure',w='holdout')} than the "
  f"matched-exposure line's.")
a("")
a("### Panel source and the return distribution")
a("")
a(f"Every loaded ticker is simultaneously available on "
  f"{g(DEC,'availability','share_of_sessions_every_loaded_ticker_available',w='holdout')} "
  f"of holdout sessions against "
  f"{g(DEC,'availability','share_of_sessions_every_loaded_ticker_available',w='primary')} "
  f"of primary-window sessions, which reproduces the 0.629 the scaffold names. "
  f"Restricted to the tickers actually held, both windows read "
  f"{g(DEC,'availability','share_of_sessions_every_held_ticker_available',w='holdout')}.")
a("")
a("| quantity | holdout | primary window |")
a("|---|---|---|")
for k in ("n_sessions", "daily_mean", "daily_sd", "skewness", "excess_kurtosis"):
    a(f"| {k} | {g(DEC,'distribution',k,w='holdout')} | "
      f"{g(DEC,'distribution',k,w='primary')} |")
a("")
a("## Phase E, the year split")
a("")
a("| year | sessions | annualised return | naive Sharpe | Lo-corrected Sharpe | "
  "maximum drawdown | naive rank |")
a("|---|---|---|---|---|---|---|")
for r in YR:
    if r["table"] == "year_line" and r["item"] == "STRATEGY":
        rk = next((x["value"] for x in YR if x["table"] == "year_rank"
                   and x["year"] == r["year"]), "")
        a(f"| {r['year']} | {r['n_sessions']} | {r['ann_return']} | "
          f"{r['sharpe_naive']} | {r['sharpe_lo']} | {r['max_drawdown']} | {rk} of 12 |")
a("")
a("| year | arithmetic gap against buy-and-hold QQQ |")
a("|---|---|")
for r in YR:
    if r["table"] == "year_gap":
        a(f"| {r['year']} | {r['value']} |")
a("")
a(f"**The outperformance is {g(YR,'year_summary','concentration')}.** "
  f"{g(YR,'year_summary','years_with_a_positive_gap')} of "
  f"{g(YR,'year_summary','years_with_a_positive_gap','n_sessions')} years carry a "
  f"positive gap, totalling {g(YR,'year_summary','total_gap')}, and the largest single "
  f"year is {g(YR,'year_summary','largest_single_year_gap','year')} at "
  f"{g(YR,'year_summary','largest_single_year_gap')}, "
  f"{g(YR,'year_summary','largest_single_year_gap','note')}. **One observation over one "
  f"macro regime remains the principal limitation, and the year split is how it is "
  f"stated.**")
a("")
a(f"**2022 separately.** The strategy returns "
  f"{g(YR,'year_2022','strategy_arithmetic_return')} arithmetically against "
  f"buy-and-hold QQQ's {g(YR,'year_2022','buy_hold_QQQ_arithmetic_return')}, with the "
  f"short sleeve contributing {g(YR,'year_2022','short_sleeve_contribution')} across "
  f"{g(YR,'year_2022','sessions')} sessions.")
a("")
a("## Phase F, the cost sweep")
a("")
a(f"A disclosed post-hoc sensitivity under 9.10. The range is read from "
  f"`{g(CS,'preregistration','range_source')}`, "
  f"{g(CS,'preregistration','range_source','note')}. "
  f"{g(CS,'preregistration','stacking_rule','note')}.")
a("")
a("| round-turn cost, bp | naive Sharpe | Lo-corrected Sharpe | rank on the naive |")
a("|---|---|---|---|")
for r in CS:
    if r["table"] == "sweep" and r["item"] == "STRATEGY":
        rk = next((x["value"] for x in CS if x["table"] == "rank"
                   and x["slippage_bp"] == r["slippage_bp"]
                   and x["convention"] == "sharpe_naive"), "")
        a(f"| {r['slippage_bp']} | {r['sharpe_naive']} | {r['sharpe_lo']} | {rk} of 12 |")
a("")
a("| crossing | convention | basis points | inside the range |")
a("|---|---|---|---|")
for r in CS:
    if r["table"] == "rank_crossing":
        a(f"| {r['item']} | {r['convention']} | {r['value']} | {r['note']} |")
a("")
a(f"Over the primary window "
  f"{g(CS,'primary_summary','crossings_inside_the_swept_range')} crossings fall inside "
  f"the same range, {g(CS,'primary_summary','crossings_inside_the_swept_range','note')}.")
a("")
a("## Phase G, robustness")
a("")
a("### G1, the lookahead test")
a("")
a("| window | fill lag | annualised return | naive Sharpe | Lo-corrected Sharpe | rank |")
a("|---|---|---|---|---|---|")
for w in ("primary", "holdout"):
    for fl in ("1", "2"):
        r = lag[(w, fl)]
        a(f"| {w} | {fl} | {r['ann_return']} | {r['sharpe_naive']} | {r['sharpe_lo']} | "
          f"{r['rank_naive']} of 12 |")
a("")
a(f"**The holdout advantage survives one additional session of lag on rank and not on "
  f"level.** {g(RB,'G1_verdict','holdout_advantage_survives_one_extra_session_of_lag','note')}. "
  f"The holdout annualised return changes by "
  f"{g(RB,'G1_shift','ann_return_change',w='holdout')} and the primary window's by "
  f"{g(RB,'G1_shift','ann_return_change',w='primary')}.")
a("")
a(f"**A negative shift is not computable without forward information.** "
  f"{g(RB,'G1','negative_shift_computable','note')}.")
a("")
a(f"**Corrections item 12 does not reproduce on the designated cell.** "
  f"{g(RB,'G1_corrections_item_12','reproduces_on_the_designated_cell','note')}. "
  f"{g(RB,'G1_corrections_item_12','the_close_to_close_figures_item_12_rests_on','note')}.")
a("")
a("### G2, concentration")
a("")
a("| quantity | holdout | primary window |")
a("|---|---|---|")
for k in ("share_from_the_best_1_sessions", "share_from_the_best_5_sessions",
          "share_from_the_best_10_sessions", "share_from_the_best_25_sessions",
          "share_from_the_worst_5_sessions", "share_from_the_worst_25_sessions",
          "naive_sharpe_unmodified", "naive_sharpe_with_the_best_5_removed",
          "naive_sharpe_with_the_best_10_removed",
          "sessions_accounting_for_half_the_return"):
    a(f"| {k} | {g(RB,'G2',k,w='holdout')} | {g(RB,'G2',k,w='primary')} |")
a("")
a("### G3, leave one year out over the holdout")
a("")
a(f"{g(RB,'G3_summary','estimates')} estimates. The naive Sharpe range is "
  f"{g(RB,'G3_summary','naive_sharpe_range')}, "
  f"{g(RB,'G3_summary','naive_sharpe_range','note')}. The year whose removal moves it "
  f"most is {g(RB,'G3_summary','year_whose_removal_moves_it_most')}, "
  f"{g(RB,'G3_summary','year_whose_removal_moves_it_most','note')}.")
a("")
a("### G4, rolling stability")
a("")
a(f"{g(RB,'G4','windows')} rolling {g(RB,'G4','window_sessions')}-session windows across "
  f"the combined span. The minimum is {g(RB,'G4','minimum')} "
  f"{g(RB,'G4','minimum','note')} and the maximum is {g(RB,'G4','maximum')} "
  f"{g(RB,'G4','maximum','note')}, with {g(RB,'G4','share_above_1.0')} of windows above "
  f"1.0. Split at the boundary, the primary window carries "
  f"{g(RB,'G4','share_above_1.0',w='primary')} above 1.0 and the holdout "
  f"{g(RB,'G4','share_above_1.0',w='holdout')}. The series is emitted at "
  f"`outputs/session-28/rolling-sharpe-series.csv` with the boundary marked.")
a("")
a("## Phase H, the beta decomposition")
a("")
a(f"**The positive control passed**, buy-and-hold QQQ regressed on itself returning a "
  f"beta of {g(BE,'positive_control','beta')} and a daily alpha of "
  f"{g(BE,'positive_control','alpha_daily')} inside the "
  f"{g(BE,'positive_control','tolerance')} tolerance.")
a("")
a("| quantity | holdout | primary window |")
a("|---|---|---|")
for k in ("beta", "alpha_annualised", "r_squared", "alpha_t_newey_west",
          "residual_ann_return", "residual_ann_vol", "residual_sharpe_naive",
          "residual_sharpe_lo"):
    a(f"| {k} | {g(BE,'static',k)} | {g(BE,'static',k,'primary_window') or ''} |")
a("")
a("| window | beta mean | beta sd | primary sd | timing contribution | primary timing |")
a("|---|---|---|---|---|---|")
for W in ("60", "120", "252", "504"):
    a(f"| {W} | {g(BE,'rolling','beta_mean',w=W)} | {g(BE,'rolling','beta_sd',w=W)} | "
      f"{g(BE,'rolling','beta_sd','primary_window',w=W)} | "
      f"{g(BE,'timing','timing_ann_contribution',w=W)} | "
      f"{g(BE,'timing','timing_ann_contribution','primary_window',w=W)} |")
a("")
a(f"**The timing component is material over the holdout and does not change sign**, "
  f"reading {g(BE,'timing_summary','timing_contribution_range')} across the four "
  f"windows, {g(BE,'timing_summary','timing_contribution_range','note')}. The "
  f"sign-change flag reads "
  f"{g(BE,'timing_summary','changes_sign_across_the_window')} and the materiality flag "
  f"{g(BE,'timing_summary','material_over_the_holdout')}, "
  f"{g(BE,'timing_summary','material_over_the_holdout','note')}.")
a("")
a("| window | exposure-matched naive Sharpe | beats the strategy |")
a("|---|---|---|")
for W in ("60", "120", "252", "504"):
    a(f"| {W} | {g(BE,'exposure_matched','sharpe_naive',w=W)} | "
      f"{g(BE,'exposure_matched','beats_the_strategy_on_the_naive_sharpe',w=W)} |")
a("")
a(f"{g(BE,'exposure_matched','construction','note')}.")
a("")
a("## Phase I, reconciliation")
a("")
a(f"**I1.** {g(RC,'I1','the_scaffold_figure_is_a_units_mix','note')}. "
  f"{g(RC,'I1','verdict','note')}.")
a("")
a(f"**I2.** The combined window carries {g(RC,'I2','combined_sessions')} sessions "
  f"against {g(RC,'I2','primary_plus_holdout')}, "
  f"{g(RC,'I2','primary_plus_holdout','note')}, and the session count reconciles. The "
  f"two spans compounded give {g(RC,'I2','product_of_the_two')} against the combined "
  f"window's {g(RC,'I2','combined_growth_factor')}, a relative gap of "
  f"{g(RC,'I2','relative_gap')}.")
a("")
a(f"**I3.** {g(RC,'I3_summary','quantities_disagreeing_with_session_27')} quantity "
  f"disagrees with session 27, being the P4 effective-exposure figures. "
  f"{g(RC,'I3','P4_mean_effective_exposure_across_the_interval','note')}. Session 27 "
  f"reported {g(RC,'I3','P4_mean_effective_exposure_across_the_interval','session_27_value')} "
  f"and the corrected figure is "
  f"{g(RC,'I3','P4_mean_effective_exposure_across_the_interval','session_28_value')}.")
a("")
a("## What each finding is")
a("")
a("| finding | what acting on it would be |")
a("|---|---|")
a("| the lookahead test result | documentation, since the canonical fill lag is "
  "unchanged and the result is reported whatever it shows |")
a("| corrections item 12 not reproducing on the designated cell | a register decision, "
  "applied at 9.71 |")
a("| the holdout Lo factor sitting inside its own null | documentation |")
a("| the Lo rank of 1 of 12 occurring at q equal to 252 alone | documentation |")
a("| the turnover fall being a capacity effect | a register decision, applied at 9.73 |")
a("| two terminals firing first inside the holdout | documentation |")
a("| the two prediction premises the measurement contradicts | documentation, since "
  "the prediction is frozen at 9.64 and is not edited |")
a("| session 27's P4 effective-exposure figures | a correctness repair, applied at 9.78 "
  "in the register rather than by editing that report |")
a("| the holdout timing component being material and single-signed | documentation |")
a("| the cost sweep showing no crossing inside the swept range | documentation |")
a("")
a("**No recommendation is made on any of them.**")
a("")
a("## What remains before the paper")
a("")
a("**No measurement remains outstanding for the holdout account.** Every quantity on "
  "the phase A list is computed and emitted. S equal to 48 of the B1 re-emission "
  "remains open at 9.48 and sets neither endpoint of any quoted range, and the "
  "corrected degradation null remains unrun at 9.46 with its slope withdrawn at 9.35, "
  "so neither is load-bearing.")
a("")
a("Seven claims bear on the holdout and were not evaluated at 9.68, being 2, 3, 11, 12, "
  "13, 14 and 15. Claims 11 and 12 now have holdout counterparts from phase H and "
  "claim 13 has one from G3, and whether those counterparts are turned into evaluations "
  "against the frozen claims is a decision that has not been taken. **No claim in "
  "docs/CLAIMS.md is added or amended and docs/HOLDOUT-PREDICTION.md is not edited.**")
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
a("9.70 the ruling and the pre-registration, written before any measurement. 9.71 the "
  "lookahead test. 9.72 the Lo estimator at holdout length. 9.73 the turnover mechanism. "
  "9.74 the sleeve attribution, the year split and the concentration figures, with the "
  "beta decomposition recorded under it. 9.75 the terminals firing first inside the "
  "holdout. 9.76 the two prediction premises. 9.77 the two disclosed sensitivities. "
  "9.78 the correction to session 27's P4 effective-exposure figures.")
a("")
a("## Artifacts")
a("")
for x in ("preregistration.csv", "ladder-comparison.csv", "lo-holdout-null.csv",
          "holdout-decomposition.csv", "holdout-by-year.csv", "holdout-cost-sweep.csv",
          "robustness.csv", "rolling-sharpe-series.csv", "holdout-beta.csv",
          "reconciliation.csv", "size.csv"):
    a(f"- `outputs/session-28/{x}`")
a("- the persisted sleeve dictionaries, being `_sleeve_weights_T10.parquet`, "
  "`_sleeve_weights_T11.parquet`, `_sleeve_weights_S2.parquet`, "
  "`_sleeve_weights_S3.parquet`, `_signal_rows.parquet`, `_terminals.parquet` and "
  "`_effective_exposure.parquet`")
a("")
a("**No figure is drawn, since the cap at 9.60 is reached.**")
a("")
(O / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"wrote REPORT.md, {len(L)} lines")
