# Tactical allocation, a pre-registered negative-result study

A four-sleeve daily tactical allocation strategy, reconstructed from a public QuantConnect source with every numeric parameter re-specified and registered, was tested against a ladder of eleven leverage-matched passive and mechanical benchmarks. Over the primary window from 2011-10-04 it placed sixth of twelve on both Sharpe conventions. A five-year holdout was sealed at 2021-08-01, a prediction of what it would show was committed to git before it was opened, and it was then read once. In the holdout the strategy placed 2 of twelve on the naive Sharpe. **All five pre-registered prediction components were falsified, every one in the same direction.**

## Method

- **Pre-registration.** Every decision is recorded in `docs/DECISIONS-v3.md` with the date it was taken and the grounds. Rules that govern a measurement are written before the measurement runs, and a rule that produces an unexpected result is reported rather than adjusted.
- **A frozen claim set.** `docs/CLAIMS.md` carries 15 claims, each with its source file, the literal emitted value, and the condition that would overturn it. `docs/WITHDRAWN.md` carries 11 claims the project made and then withdrew.
- **A sealed holdout, read once.** The prediction in `docs/HOLDOUT-PREDICTION.md` was committed before the read, and `scripts/verify_prediction_precedes_read.py` checks that precedence against git rather than against anyone's recollection.
- **Every figure traces to a file.** Prose figures are read from emitted CSVs and checked against them before a report is written.

## Headline figures

| quantity | primary window | holdout | source |
|---|---|---|---|
| naive Sharpe | 1.0910863648060856 | 1.637799226672021 | `outputs/session-20/rebuilt/metrics-full.csv`, `outputs/session-27/holdout-ladder.csv` |
| Lo-corrected Sharpe | 1.3817013060244996 | 2.7585227658215015 | `outputs/session-20/rebuilt/metrics-full.csv`, `outputs/session-27/holdout-ladder.csv` |
| annualised return | 0.5218447451814521 | 0.8287111594113898 | `outputs/session-20/rebuilt/metrics-full.csv`, `outputs/session-27/holdout-ladder.csv` |
| rank of twelve, naive | 6 | 2 | `outputs/session-27/holdout-ladder.csv` |
| rank of twelve, Lo-corrected | 6 | 1 | `outputs/session-27/holdout-ladder.csv` |

The naive convention leads throughout, per the decision at 8.2, on the grounds that the Lo-corrected ordering is not stable under a lag parameter the study never registered.

**Probability of backtest overfitting is 0.1578088578088578** at S equal to 16 over the full 12,870-combination enumeration of a 121,500-specification grid, read from `outputs/session-19/pbo.csv`. An estimator control puts the same harness at 0.9919283331048036 when selection is driven purely by idiosyncratic noise, read from `outputs/session-19_6/degradation-null.csv`.

**The holdout naive Sharpe's block-bootstrap interval runs 0.9929195170218649 to 2.2821600447939803** at the 5th and 95th percentiles, read from `outputs/session-30/bootstrap-intervals.csv`.

**A five-factor decomposition leaves an annualised alpha of 0.45868406085120844** against a single-factor figure of 0.5637941837318013, read from `outputs/session-30/multi-factor.csv`.

## Limitations

- **One holdout over one macro regime.** The sealed span is a single five-year observation carrying 1265 sessions, and the outperformance is spread across all six of its calendar years rather than concentrated in one. It remains one regime.
- **The result is capacity-bounded.** Across five starting NAV levels the holdout naive Sharpe falls monotonically to 0.9817333726959366 at a starting NAV of 1028029775.2491124, and the 5 percent participation cap already binds on 0.9406631762652705 of transitions at the study anchor. Source `outputs/session-30/nav-sensitivity.csv`.
- **One corporate action defect stands unrepaired.** SOXS on 2026-05-26 carries a price discontinuity the frozen record does not explain. It contributes exactly 0.0 to holdout return, since the instrument carries zero weight across that span, and the disposition is recorded as open at 9.85 rather than decided. Source `outputs/session-30/corporate-action-sweep.csv`.
- **10 parameters defined in `src/config.py` have no consumer outside it**, and two more carry a read that is never invoked. Source `outputs/session-21/unwired-config.csv`.
- **Two measurements remain unrun**, being S equal to 48 of one re-emission and a corrected degradation null whose statistic is withdrawn on separate grounds. Neither is load-bearing.

## Repository map

| path | holds |
|---|---|
| `docs/` | the claim set, the withdrawn set, the holdout prediction, and the decision register |
| `src/` | the strategy itself, being the sleeves, the portfolio tracker, the indicators, the fund schedule, and the configuration every parameter is read from |
| `scripts/` | the backtest engine and one driver per session |
| `outputs/` | one directory per session, each carrying that session's emitted CSVs and its report |
| `data/` | the frozen inputs, hash-verified against manifests under `outputs/` |

Read in this order.

1. `docs/CLAIMS.md`, the frozen claim set with its limitations.
2. `docs/WITHDRAWN.md`, what the project stopped believing.
3. `docs/HOLDOUT-PREDICTION.md`, what was predicted before the read.
4. `docs/DECISIONS-v3.md`, the decision register.

## Reproduction

```
git clone https://github.com/boomer25tiger/tactical-allocation.git
cd tactical-allocation
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/reproduce.py
```

The expected output is an annualised return of 0.521844 and a Lo-corrected Sharpe of 1.381701 over 2472 sessions, inside a tolerance of 5e-07 on each figure. Bit-identical output is not asserted, since float reduction order varies with thread count and BLAS version. `docs/REPRODUCE.md` carries the full guide including what a cloner cannot reproduce.

## What this is not

This is a study of whether a strategy's measured edge survives its own specification search and a sealed forward window. It is not investment advice and it is not a recommendation to trade anything described here.

