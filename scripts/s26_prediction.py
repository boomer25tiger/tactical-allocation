"""Session 26 phase C. Write docs/HOLDOUT-PREDICTION.md.

Every figure is read from outputs/session-26/prediction-sources.csv, which carries
the emitted literal and the file it came from. Nothing is taken from the scaffold.
Where the scaffold named a value the source does not carry, the source is used and
the difference is recorded in outputs/session-26/prompt-disagreements.csv and in
the closing section here.
"""
from __future__ import annotations
import csv
from pathlib import Path
R = Path("/Users/GualyCr/Downloads/tactical-allocation")
O = R/"outputs"/"session-26"
S = {r["item"]: r for r in csv.DictReader(open(O/"prediction-sources.csv"))}
D = list(csv.DictReader(open(O/"prompt-disagreements.csv")))
def v(i): return S[i]["literal_value"]
def f(i): return S[i]["source_file"]
L = []; a = L.append

a("# HOLDOUT PREDICTION")
a("")
a("Written 2026-08-22, before any post-boundary quantity is computed. **This document "
  "is frozen on the commit that adds it and is not amended after the holdout is read.**")
a("")
a(f"The sealed span runs from {v('holdout_boundary')} to {v('data_end')}, the latter "
  f"being the frozen truncation date across all 39 inputs at `{f('data_end')}`. The "
  f"primary window carries {v('primary_window_sessions')} sessions, read from "
  f"`{f('primary_window_sessions')}`.")
a("")
a("**The holdout session count is not stated here.** Register 2.10 records that no "
  "post-boundary quantity has been computed anywhere, and counting sessions inside the "
  "sealed span is a post-boundary quantity. The count is established by the read.")
a("")
a("**The holdout is read once.** There is no second read and no read of any part of the "
  "span before the full read.")
a("")
a("## P1, primary")
a("")
a("**In the holdout, on the designated cell, the strategy ranks no better than sixth of "
  "twelve on the naive Sharpe.** Falsified by any rank of fifth or better.")
a("")
a("The Lo-corrected rank is reported alongside, since 8.2 leads on the naive figure "
  "while the pre-registered convention is Lo, and a divergence between the two ranks is "
  "itself reportable.")
a("")
a("### Mechanism")
a("")
a(f"The primary-window shortfall is a cost of carry rather than a timing failure. The "
  f"timing component contributes {v('timing_ann_contribution_60')} of "
  f"{v('total_ann_check_60')} at a 60-session beta window, and it changes sign across "
  f"the estimation window, reading {v('timing_ann_contribution_120')} at 120 sessions, "
  f"{v('timing_ann_contribution_252')} at 252 and {v('timing_ann_contribution_504')} at "
  f"504. Source `{f('timing_ann_contribution_60')}` and "
  f"`{f('timing_ann_contribution_252')}`.")
a("")
a(f"The strategy turns over {v('strategy_ann_turnover')} times annually against "
  f"{v('buy_hold_QQQ_ann_turnover')} for buy-and-hold QQQ, read from "
  f"`{f('strategy_ann_turnover')}`. Nothing in the holdout reduces that turnover or "
  f"raises the value of timing, and a span containing one sharp regime change with two "
  f"trending years gives a high-turnover overlay fewer opportunities than a decade-long "
  f"bull rather than more.")
a("")
a("## P2, secondary")
a("")
a(f"**The strategy's holdout naive Sharpe lands between 0.25 and 0.85**, against "
  f"{v('strategy_sharpe_naive_primary')} over the primary window at "
  f"`{f('strategy_sharpe_naive_primary')}`. Falsified above 0.85 or below 0.25.")
a("")
a("### Mechanism")
a("")
a(f"Leave-one-out places the strategy's worst risk-adjusted years at its crisis years. "
  f"Removing 2011 raises the Lo-corrected Sharpe to {v('loo_drop_2011_sharpe_lo')} and "
  f"removing 2020 raises it to {v('loo_drop_2020_sharpe_lo')}, against a base of "
  f"{v('loo_base_sharpe_lo')}, read from `{f('loo_base_sharpe_lo')}`. **That the holdout "
  f"contains the only sustained bear in either window is an external premise and is "
  f"labelled as one**, since establishing it from the panel would be a post-boundary "
  f"quantity.")
a("")
a(f"Separately, the strategy runs a mean effective exposure of "
  f"{v('canonical_mean_effective_exposure')} through leveraged ETPs carrying issuer "
  f"financing, read from `{f('canonical_mean_effective_exposure')}`. **The policy-rate "
  f"premise is external and is labelled as one**, being that the rate was near zero "
  f"across most of the primary window while it exceeded five percent for a period inside "
  f"the holdout. No committed CSV carries a policy-rate series, and reading one inside "
  f"the sealed span would be a post-boundary quantity. The financing channel affects "
  f"every levered line, so it bears more on P2 than on P1.")
a("")
a("## P3, mechanism")
a("")
a("Two parts, each falsifiable alone.")
a("")
a("**Part one. SQQQ and TLT realise positive daily return correlation over the "
  "holdout.** Falsified by a negative realised correlation.")
a("")
a(f"The primary-window baseline in a committed file is the short leg against the rest "
  f"of its own sleeve on the canonical arm, at "
  f"{v('t10_corr_short_vs_rest_of_sleeve')} over "
  f"{v('t10_short_leg_held_sessions')} held sessions, read from "
  f"`{f('t10_corr_short_vs_rest_of_sleeve')}`. **A direct SQQQ against TLT correlation "
  f"over the primary window is in no committed CSV**, so the read computes both the "
  f"direct pair and the sleeve-level figure and reports them together.")
a("")
a("**Part two. T10's risk-off branch contributes negatively to holdout return.** "
  "Falsified by a positive contribution.")
a("")
a(f"**Part two is the weaker half and is recorded as such.** The branch's short leg "
  f"already contributes {v('t10_short_leg_total_arith_contribution')} arithmetically "
  f"over the primary window, of which {v('t10_short_leg_beta_component')} is the beta "
  f"component and {v('t10_short_leg_residual_component')} the residual, at "
  f"`{f('t10_short_leg_total_arith_contribution')}`. Part two therefore predicts that a "
  f"sign already observed persists, while part one predicts that a sign flips.")
a("")
a("**Part one is checkable from price data alone**, without reference to the strategy, "
  "so the mechanism is testable independently of the outcome. Part one holding with part "
  "two failing is more informative than either alone, since it would show the "
  "diversification failing while something else carried the branch.")
a("")
a("### Mechanism")
a("")
a(f"T10's risk-off branch holds SQQQ at 0.5 and TLT at 0.5 at "
  f"`src/sleeves.py:190`, and the realised mean weight when held is "
  f"{v('t10_short_leg_mean_weight_when_held')} at "
  f"`{f('t10_short_leg_mean_weight_when_held')}`. The pairing diversifies only when the "
  f"legs are negatively correlated.")
a("")
a(f"SQQQ is a portfolio-wide position rather than a T10 one. It is returned at "
  f"{v('sqqq_position_sites')} sites across {v('sqqq_sleeves').count(',')+1} sleeves, "
  f"being {v('sqqq_sleeves').replace(',', ', ')}, so the branch's failure is not "
  f"confined to T10. The "
  f"sites are as follows.")
a("")
a("| file and line | function |")
a("|---|---|")
for k, r in S.items():
    if k.startswith("sqqq_site_"):
        a(f"| `{k.replace('sqqq_site_','')}` | `{r['literal_value']}` |")
a("")
a("## P4, the named unknown")
a("")
a("**State-classification latency in a slow bear is not measurable from the primary "
  "window and is not predicted.**")
a("")
a(f"The state machine votes at a threshold of {v('s3_vote_threshold')}, and register "
  f"6.7 marks it informed rather than closed, so the threshold's value was reasoned "
  f"about rather than settled by measurement.")
a("")
a(f"The primary window carries {v('strategy_n_drawdowns_gt_20pct')} drawdowns beyond 20 "
  f"percent with the deepest lasting {v('strategy_max_dd_duration_sessions')} sessions, "
  f"being {v('strategy_max_dd_duration_calendar_days')} calendar days, at "
  f"`{f('strategy_max_dd_duration_sessions')}`. No episode in the window resembles a "
  f"grind lasting a year.")
a("")
a(f"**What the record actually carries about lag is narrower than a located mechanism.** "
  f"Session 15's lag sweep reads an annualised return of {v('lag_1.0_ann_return')} with "
  f"a Lo-corrected Sharpe of {v('lag_1.0_sharpe_lo')} at one session of lag, against "
  f"{v('lag_2.0_ann_return')} and {v('lag_2.0_sharpe_lo')} at two sessions, so the two "
  f"metrics disagree on the direction, at `{f('lag_1.0_ann_return')}`. The register's "
  f"corrections list item 12 records this as an execution-lag sensitivity and records "
  f"that no dedicated lookahead test has run. **No committed file locates a dip-buying "
  f"mechanism, separates fast crashes from other episodes, or establishes that the long "
  f"side enters early while the short side enters late.**")
a("")
a("### The guard")
a("")
a("**P4 does not qualify P1, P2 or P3.** If the holdout falsifies any of the three, P4 "
  "is not the explanation unless the state series is examined and shows the latency "
  "mechanism operating.")
a("")
a("The examination is specified in advance and is the following two readings, taken "
  "together and reported whatever they show.")
a("")
a("1. The count of sessions from the 2022 peak to the first risk-off state.")
a("2. The strategy's effective exposure across that interval, session by session.")
a("")
a("A latency explanation requires the first count to be materially larger than the "
  "corresponding count in the primary window's own episodes and the exposure to stay "
  "long across the interval. Neither reading on its own establishes it.")
a("")
a("## P5, the interesting failure mode")
a("")
a("**If P1 fails, the most likely reason is that 2022 gave the short-equity sleeve its "
  "only sustained tailwind in either window, carrying the strategy past passive in the "
  "one period its hedges exist for.**")
a("")
a("**Recorded as less likely than even.** The hedge needs both legs, and the premise "
  "that TLT had its worst year in decades in 2022 is external, carried in no committed "
  "CSV and labelled as external here. If that premise holds, the diversifying leg was "
  "broken across exactly the period the short leg would have paid.")
a("")
a("It is written down because a prediction naming only the confirming path is not a "
  "prediction. **If P5 holds, the paper's finding inverts**, since a strategy that beats "
  "passive in the sealed span is not the negative result the frozen claims describe.")
a("")
a("## The post-read constraints")
a("")
a("- No parameter, threshold, weight, instrument, or window changes on the basis of "
  "holdout observation.")
a("- No second read.")
a("- No figure added after the read.")
a("- No claim added to `docs/CLAIMS.md` except the holdout result itself.")
a("- If the holdout contradicts a frozen claim, the contradiction is reported and the "
  "claim is not amended.")
a("")
a("## Figures the scaffold named that its source does not carry")
a("")
a("Recorded here rather than adopted, since a prediction built on a figure its source "
  "does not carry is not testable against the record.")
a("")
a("| item | the scaffold's value | the source's value | source | kind |")
a("|---|---|---|---|---|")
for d in D:
    a(f"| {d['item']} | {d['prompt_value']} | {d['source_value']} | "
      f"`{d['source_file'] or 'none'}` | {d['kind']} |")
a("")
a("The full map with the grounds for each is "
  "`outputs/session-26/prompt-disagreements.csv`, and every figure quoted above is in "
  "`outputs/session-26/prediction-sources.csv` with its source file beside it.")
a("")
(R/"docs"/"HOLDOUT-PREDICTION.md").write_text("\n".join(L)+"\n")
print(f"wrote docs/HOLDOUT-PREDICTION.md, {len(L)} lines")
