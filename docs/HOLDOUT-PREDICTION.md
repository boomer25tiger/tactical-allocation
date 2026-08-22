# HOLDOUT PREDICTION

Written 2026-08-22, before any post-boundary quantity is computed. **This document is frozen on the commit that adds it and is not amended after the holdout is read.**

The sealed span runs from 2021-08-01 to 2026-08-14, the latter being the frozen truncation date across all 39 inputs at `outputs/session-00e/manifest-truncated.csv`. The primary window carries 2472 sessions, read from `outputs/session-25/figures/equity-curve.csv`.

**The holdout session count is not stated here.** Register 2.10 records that no post-boundary quantity has been computed anywhere, and counting sessions inside the sealed span is a post-boundary quantity. The count is established by the read.

**The holdout is read once.** There is no second read and no read of any part of the span before the full read.

## P1, primary

**In the holdout, on the designated cell, the strategy ranks no better than sixth of twelve on the naive Sharpe.** Falsified by any rank of fifth or better.

The Lo-corrected rank is reported alongside, since 8.2 leads on the naive figure while the pre-registered convention is Lo, and a divergence between the two ranks is itself reportable.

### Mechanism

The primary-window shortfall is a cost of carry rather than a timing failure. The timing component contributes 0.011293050910284682 of 0.5725633797029721 at a 60-session beta window, and it changes sign across the estimation window, reading 0.027230151692897046 at 120 sessions, -0.004075416692355631 at 252 and -0.0077512681113622505 at 504. Source `outputs/session-21/beta-decomposition.csv` and `outputs/session-22/beta-window-sensitivity.csv`.

The strategy turns over 37.87437898045862 times annually against 0.017286585046131533 for buy-and-hold QQQ, read from `outputs/session-20/rebuilt/metrics-full.csv`. Nothing in the holdout reduces that turnover or raises the value of timing, and a span containing one sharp regime change with two trending years gives a high-turnover overlay fewer opportunities than a decade-long bull rather than more.

## P2, secondary

**The strategy's holdout naive Sharpe lands between 0.25 and 0.85**, against 1.0910863648060856 over the primary window at `outputs/session-20/rebuilt/metrics-full.csv`. Falsified above 0.85 or below 0.25.

### Mechanism

Leave-one-out places the strategy's worst risk-adjusted years at its crisis years. Removing 2011 raises the Lo-corrected Sharpe to 1.5635962707744817 and removing 2020 raises it to 1.6183359759194622, against a base of 1.3817013060244996, read from `outputs/session-22/rebuilt/leave-one-out.csv`. **That the holdout contains the only sustained bear in either window is an external premise and is labelled as one**, since establishing it from the panel would be a post-boundary quantity.

Separately, the strategy runs a mean effective exposure of 1.7769723457408557 through leveraged ETPs carrying issuer financing, read from `outputs/session-16/exposure-reconciliation.csv`. **The policy-rate premise is external and is labelled as one**, being that the rate was near zero across most of the primary window while it exceeded five percent for a period inside the holdout. No committed CSV carries a policy-rate series, and reading one inside the sealed span would be a post-boundary quantity. The financing channel affects every levered line, so it bears more on P2 than on P1.

## P3, mechanism

Two parts, each falsifiable alone.

**Part one. SQQQ and TLT realise positive daily return correlation over the holdout.** Falsified by a negative realised correlation.

The primary-window baseline in a committed file is the short leg against the rest of its own sleeve on the canonical arm, at -0.5618926986740371 over 513.0 held sessions, read from `outputs/session-15.5/short-leg-decomposition.csv`. **A direct SQQQ against TLT correlation over the primary window is in no committed CSV**, so the read computes both the direct pair and the sleeve-level figure and reports them together.

**Part two. T10's risk-off branch contributes negatively to holdout return.** Falsified by a positive contribution.

**Part two is the weaker half and is recorded as such.** The branch's short leg already contributes -1.074235187878671 arithmetically over the primary window, of which -1.0846763867101825 is the beta component and 0.010441198831511622 the residual, at `outputs/session-15.5/short-leg-decomposition.csv`. Part two therefore predicts that a sign already observed persists, while part one predicts that a sign flips.

**Part one is checkable from price data alone**, without reference to the strategy, so the mechanism is testable independently of the outcome. Part one holding with part two failing is more informative than either alone, since it would show the diversification failing while something else carried the branch.

### Mechanism

T10's risk-off branch holds SQQQ at 0.5 and TLT at 0.5 at `src/sleeves.py:190`, and the realised mean weight when held is 0.49741933465476185 at `outputs/session-15.5/short-leg-decomposition.csv`. The pairing diversifies only when the legs are negatively correlated.

SQQQ is a portfolio-wide position rather than a T10 one. It is returned at 5 sites across 3 sleeves, being S2, T10, T11, so the branch's failure is not confined to T10. The sites are as follows.

| file and line | function |
|---|---|
| `src/sleeves.py:190` | `t10_weights` |
| `src/sleeves.py:210` | `_t11_bond_baller` |
| `src/sleeves.py:239` | `_t11_feaver_bear` |
| `src/sleeves.py:266` | `t11_weights` |
| `src/sleeves.py:300` | `s2_weights` |

## P4, the named unknown

**State-classification latency in a slow bear is not measurable from the primary window and is not predicted.**

The state machine votes at a threshold of 3 of 4, and register 6.7 marks it informed rather than closed, so the threshold's value was reasoned about rather than settled by measurement.

The primary window carries 13.0 drawdowns beyond 20 percent with the deepest lasting 70.0 sessions, being 99.0 calendar days, at `outputs/session-20/rebuilt/metrics-full.csv`. No episode in the window resembles a grind lasting a year.

**What the record actually carries about lag is narrower than a located mechanism.** Session 15's lag sweep reads an annualised return of 0.2971065884533939 with a Lo-corrected Sharpe of 0.928624610696173 at one session of lag, against 0.4723877298801684 and 0.8601102920915699 at two sessions, so the two metrics disagree on the direction, at `outputs/session-15/lag-anomaly.csv`. The register's corrections list item 12 records this as an execution-lag sensitivity and records that no dedicated lookahead test has run. **No committed file locates a dip-buying mechanism, separates fast crashes from other episodes, or establishes that the long side enters early while the short side enters late.**

### The guard

**P4 does not qualify P1, P2 or P3.** If the holdout falsifies any of the three, P4 is not the explanation unless the state series is examined and shows the latency mechanism operating.

The examination is specified in advance and is the following two readings, taken together and reported whatever they show.

1. The count of sessions from the 2022 peak to the first risk-off state.
2. The strategy's effective exposure across that interval, session by session.

A latency explanation requires the first count to be materially larger than the corresponding count in the primary window's own episodes and the exposure to stay long across the interval. Neither reading on its own establishes it.

## P5, the interesting failure mode

**If P1 fails, the most likely reason is that 2022 gave the short-equity sleeve its only sustained tailwind in either window, carrying the strategy past passive in the one period its hedges exist for.**

**Recorded as less likely than even.** The hedge needs both legs, and the premise that TLT had its worst year in decades in 2022 is external, carried in no committed CSV and labelled as external here. If that premise holds, the diversifying leg was broken across exactly the period the short leg would have paid.

It is written down because a prediction naming only the confirming path is not a prediction. **If P5 holds, the paper's finding inverts**, since a strategy that beats passive in the sealed span is not the negative result the frozen claims describe.

## The post-read constraints

- No parameter, threshold, weight, instrument, or window changes on the basis of holdout observation.
- No second read.
- No figure added after the read.
- No claim added to `docs/CLAIMS.md` except the holdout result itself.
- If the holdout contradicts a frozen claim, the contradiction is reported and the claim is not amended.

## Figures the scaffold named that its source does not carry

Recorded here rather than adopted, since a prediction built on a figure its source does not carry is not testable against the record.

| item | the scaffold's value | the source's value | source | kind |
|---|---|---|---|---|
| buy_hold_QQQ_ann_turnover | 0.02 | 0.017286585046131533 | `outputs/session-20/rebuilt/metrics-full.csv` | rounding |
| crisis_years | fast crashes in 2011, 2018 and 2020 | 2011 1.5635962707744817, 2020 1.6183359759194622, 2018 1.287076427656795 against a base of 1.3817013060244996 | `outputs/session-22/rebuilt/leave-one-out.csv` | figure |
| mean_effective_exposure | near 1.70 | 1.7769723457408557 | `outputs/session-16/exposure-reconciliation.csv` | figure |
| sqqq_sites | four sites across three sleeves | 5 sites across 3 sleeves | `src/sleeves.py` | figure |
| lag_mechanism | session 15 located the mechanism of the dip-buying signal firing roughly one session early in fast crashes so the long side enters early and the short side late | the register's corrections list item 12 records an execution-lag sensitivity in which annualised return improves under one extra session of lag while the Lo-corrected Sharpe degrades, and records that no dedicated lookahead test has run | `docs/DECISIONS-v3.md and outputs/session-15/lag-anomaly.csv` | unsupported claim |
| holdout_session_count | the session count against the primary window's 2,472 | not established | `docs/DECISIONS-v3.md` | not computed |
| tlt_2022 | TLT had its worst year in decades in 2022 | not in any emitted file | `none` | external fact |

The full map with the grounds for each is `outputs/session-26/prompt-disagreements.csv`, and every figure quoted above is in `outputs/session-26/prediction-sources.csv` with its source file beside it.

