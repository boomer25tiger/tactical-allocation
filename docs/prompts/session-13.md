Session 13 — canonical backtest, in-sample only
Scaffold

Repository is tactical-allocation. Session 12.5 committed the full construction and wrote docs/DECISIONS-v3.md and docs/STATE.md. Read both before starting. They carry every closed decision with its value, the open items with their blockers, the corrections list, and the construction limitations that bear on any result.

Run alone. The timeout binary is absent on this machine and returns exit 127 without executing. Do not use it. Every search or filter carries a positive control confirming a known-present result before any negative finding is reported.

Do not commit. Leave the working tree dirty. Commits happen between sessions.

The prohibition lifts, and what replaces it

Every prior session carried an absolute prohibition on computing a return or performance statistic. That prohibition lifts here. This session computes the first strategy result in the project.

The risk changes rather than disappearing. Until now the danger was computing a number too early. From here it is computing the wrong number and believing it. Three rules replace the prohibition.

Nothing is tuned. Every parameter comes from src/config.py as already closed. If a result looks wrong, report it and stop. Do not adjust a parameter, a threshold, a cost, or a construction to improve it. A parameter changed after seeing a result is a post-freeze change, and it belongs in DECISIONS.md with a date and a reason, decided by the user rather than inside a session.

The holdout is physically inaccessible. See step 1.

Every number carries its diagnostics. A Sharpe ratio without turnover, exposure, and cost sensitivity beside it is not a result.

Step 1, holdout enforcement

The holdout boundary is 2021-08-01 under 2.10.

Truncate every input series at 2021-07-31 inside the loader, before any strategy code runs, so no downstream function can reach a post-boundary observation even by mistake.

Assert after loading that the maximum date across every loaded series is on or before 2021-07-31, and raise if not. Report the assertion result.

Do not compute, plot, or reference any post-boundary quantity anywhere in this session.

The crash branch reads a trailing 60-session window and the warm-up reads 210 sessions, both backward-looking only, so neither crosses the boundary.

Step 2, canonical configuration

Read every parameter from src/config.py. Do not hardcode any value in the backtest script. Report the full resolved configuration at the top of the report, so the run is reproducible from the report alone.

For reference, the canonical point is RSI 14 across all three function-tied periods, overbought tier one 70, tier two 80, oversold 30, long SMA 200, short SMA 20, crash threshold minus 15 percent on the trailing 60-session QQQ total return, vote threshold 3 of 4, warm-up 210 sessions. Execution is signal at the T close, fill at the T+1 close, close-to-close accumulation, truncation sizing, uniform slippage swept, IBKR Fixed commission at 0.005 per share with a 1.00 minimum and a 1 percent cap, DTB3 accrual at rate over 360 on calendar days. Portfolio is four sleeves at 25 percent each, gross capped at 100 percent with proportional truncation, drift permitted between label transitions with no calendar reset, label rounded to whole percent of sleeve budget with the short circuit after all four sleeve calls and before summation.

Config wins over this list. If any value here disagrees with src/config.py, use config and report the discrepancy.

Sample starts 2007-01-01 under 2.9. The trend series RYMFX begins 2007-02-22, so the pairwise comparison raises for roughly the first sixty sessions under the 2.11 unavailable rule. Report how many sessions that affects and their dates.

Step 3, instrument sourcing

All-synthetic primary under 2.8. Every leveraged and inverse exposure reads from data/interim/synthetics/, regenerating them with scripts/s10_build.py if absent, since they are derived rather than frozen. Unlevered instruments read from their frozen files.

SOXS uses the synthetic despite its recorded exception, being 6.21 percent annualised tracking difference and 1394 percent maximum rolling divergence against the real fund. The alternative, listed SOXS from 2010-03, would remove T11's bull-branch inverse basket across 2008 and the decision was to keep the synthetic. Report the exception beside every result that depends on it.

SVIX and UVIX do not exist before 2022, which is outside this sample entirely, so the T10 short-volatility and S3 volatility legs resolve to SVXY and UVXY throughout. Report that.

Run the realized-instrument arm under 2.8 alongside, using listed funds wherever they existed on each date and the unavailable rule where they did not. Report both arms side by side. The difference is the implementability check.

Step 4, the run

Execute the canonical specification across 2007-01-01 to 2021-07-31.

Produce a daily series carrying, per session, the joint label, each sleeve's target weights, realized weights after drift, gross exposure, effective market exposure as the sum of weight times signed multiple, portfolio return, cumulative NAV, cash held, and whether a transition occurred.

Write to outputs/session-13/daily-series.csv.

Step 5, headline results

Report at the canonical point, for each of the six cost levels in SLIPPAGE_BASE_GRID_BP, being 0, 5, 10, 20, 35, and 50 basis points round-turn.

Total return, annualised return, annualised volatility, Sharpe ratio using DTB3 as the risk-free per 8.1, maximum drawdown, Calmar ratio, and annualised turnover implied by realized transitions.

Report the Sharpe both naively annualised and Lo-corrected per 8.2, with the corrected figure as the headline.

The cost curve is the primary object, not any single point. Session 07 measured 105 label transitions per year at canonical parameters with a median holding length of one session, so cost is a headline axis rather than a sensitivity. State the round-turn cost at which annualised return crosses zero and the level at which Sharpe crosses zero.

Write outputs/session-13/headline-results.csv.

Step 6, diagnostics that accompany the headline

Realized transitions per year and the holding-length distribution, compared against session 07's signal-level count of 105. A difference means the label short-circuit or the drift rule behaves differently in the full pipeline than in the label computation alone, which is worth knowing.

Concentration under 5.7, being effective number of constituents by one over HHI on tickers and on underlyings, effective number of minimum-torsion bets using minimum-torsion rather than PCA per Meucci et al. 2015, effective market exposure, and maximum single-ticker and single-underlying weight with the top-three sum. Daily series plus distributions conditional on drawdown quintile, target and realized both.

Effective breadth under 5.6, being how often each sleeve sits in each of its terminal states, and how often two or more sleeves hold the same ticker simultaneously.

Reach rate per cascade step in T10 under 6.13, and the firing rate of every branch in all four sleeves. A branch that never fires in-sample is worth knowing before the writeup claims it does anything.

Time in each instrument, as a fraction of sessions held and as a fraction of dollar exposure.

Fraction of sessions where the 5.3 gross cap bound and proportional truncation fired.

Fraction of sessions where a pairwise comparison raised under the 2.11 unavailable rule, with dates.

Write outputs/session-13/diagnostics.csv.

Step 7, sanity checks before the result is believed

Report each explicitly with its result.

NAV reconciles, meaning the cumulative product of daily returns equals ending NAV within floating tolerance.

No lookahead, meaning shifting every signal one additional session forward degrades the result. Report the degraded figures. A strategy that improves under additional lag has a timing defect.

Cash accounts, meaning position values plus cash equals NAV on every session.

Gross never exceeds 100 percent after truncation.

Weights sum to the intended budget within rounding on every session where a sleeve is invested.

Warm-up boundary, meaning the first traded session is 210 sessions after the first loaded session and no indicator is read before it is defined.

Commission never exceeds 1 percent of any trade value, per the IBKR Fixed cap.

Report any failure and stop rather than continuing to interpretation.

Write outputs/session-13/sanity-checks.csv.

Step 8, sub-period stability

Report headline figures by calendar year and by the sub-periods defined under 7.14.

Report 2008 separately. Session 12 established that construction tracking error rises 5.4 times from the calmest to the wildest volatility decile, and 2008 sits in the wildest, so any result concentrated there rests on the least reliable part of the construction and the report says so.

Write outputs/session-13/subperiod.csv.

Step 9, report

outputs/session-13/REPORT.md covering the resolved configuration, the holdout assertion, the headline table across the cost curve, every diagnostic, every sanity check, the sub-period breakdown, and both arms of 2.8.

State plainly whether the strategy survives costs at the 10 basis point anchor and where it stops surviving.

Do not interpret beyond the numbers. No benchmark comparison, since the 8.8 ladder and the nulls are a later session. No alpha, PSR, DSR, or test statistic. Do not characterise the result as good or bad. Report what the strategy did, with its diagnostics and its limitations.

State every limitation bearing on the result, being the SOXS exception, the SVIX and UVIX absence, the regime-conditional construction weakness, the single-fiscal-year financing anchor, the partial expense schedule covering seven Direxion funds in FY2025 only, the proxy status of each underlying, and the unvalidated pre-inception window per fund. docs/STATE.md carries all of these.

Stop condition

Halt after step 9. Do not run the holdout. Do not run the grid. Do not run benchmarks or nulls. Do not commit. Working tree left dirty.
