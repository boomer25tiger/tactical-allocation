# scripts/hw2/

Re-runs behind the investor-pitch deck for Columbia B9339, Homework 2. They sit
on top of the frozen study and change none of its registered specifications,
frozen inputs or earlier outputs. Every result lands in `outputs/hw2/`.

These are post-read analyses. The 25% volatility target, the January 2012
analysis window and the fee terms were chosen after the holdout was read, and
the deck says so where it uses them.

## Run order

From the repository root, after the frozen inputs verify (`python3 scripts/s195_verify_inputs.py`):

```
python3 scripts/hw2/h01_constnav.py   # about 15 seconds
python3 scripts/hw2/h02_cost_sweep.py # about 10 seconds
python3 scripts/hw2/h03_ladder.py     # about 1 minute (bootstrap)
python3 scripts/hw2/h04_fund.py       # about 2 minutes (bootstrap); needs h01
python3 scripts/hw2/h05_fund_evidence.py  # about 1 minute; needs h01
python3 scripts/hw2/h06_risk_stats.py     # a few seconds; needs h01
```

## What each file does

| file | writes | deck slides |
|---|---|---|
| `common.py` | nothing; windows, metric set, fund overlay, fee model, stationary bootstrap | all |
| `engine.py` | nothing; the constant-NAV account loop shared by h01, h02 and h05 | 9, 14, 15 |
| `h01_constnav.py` | `constnav-sweep.csv`, `constnav-by-instrument.csv`, `constnav-10m-daily.csv`, `dollar-volume-by-year.csv` | 9, 10, 15, 17 |
| `h02_cost_sweep.py` | `cost-sweep.csv` (engine reference in the notes) | 14 |
| `h03_ladder.py` | `ladder-windows.csv`, `ladder-misc.json` (engine reference figures) | 4, 6, 13, 22 |
| `h04_fund.py` | `fund-windows.csv`, `fund-start-dates.csv`, `fund-targets.csv`, `fund-fees.csv`, `fund-checks.json` | 9, 10, 18, 19, 20, 22 |
| `h05_fund_evidence.py` | `fund-ladder.csv`, `fund-holdout-years.csv`, `fund-holdout-path.csv`, `fund-cost-sweep.csv`, `fund-rolling-5y.csv`, `fund-evidence.json` | 1, 3, 6, 8, 12, 13, 14, 16, 17, 19, 22 |
| `h06_risk_stats.py` | `fund-risk-stats.csv` (beta, correlation, R-squared, alpha, tracking error, information ratio, capture, skewness, kurtosis, VaR, CVaR, worst day and month, underwater) | 7 |

## Windows

| name | dates | sessions | use |
|---|---|---|---|
| P11 | 2011-10-04 to 2021-07-30 | 2,472 | registered primary window (decision 7.14a); search, PBO and nulls |
| P12 | 2012-01-03 to 2021-07-30 | 2,410 | the deck's analysis window, the first full calendar year in which every order can fill |
| H | 2021-08-02 to 2026-08-14 | 1,265 | sealed holdout |

## Definitions

- **Fund.** w = min(1, 0.25 / sigma), sigma = sqrt(252) x sd of the last 60 daily engine returns, applied two sessions later. Fund return = w r + (1 - w) rf - 10 bp x |change in w|. The engine is the constant-$10M re-run from h01.
- **Sortino.** mean(r - rf) x 252 / (sqrt(252) x sqrt(mean of min(r - rf, 0)^2)), over all days.
- **Calmar.** CAGR / |max drawdown| over the whole window.
- **Fees.** Management fee accrues daily at m / 252. The incentive fee accrues daily in NAV on gains above max(high-water mark, year-start NAV x (1 + that year's T-bill return)) and is paid at each anniversary.
- **Bootstrap.** Politis-Romano stationary bootstrap, mean block 21 sessions, 10,000 draws, seed 20260823, matching `scripts/s30_phaseF.py`.

## Checks

- `h01_constnav.py` reruns the designated cell at a compounding $1M and prints its primary-window CAGR, which must equal the canonical 0.521845.
- `h02_cost_sweep.py` reproduces the session-20 uniform-cost sweep on P11 (1.21, 1.18, 1.16, 1.10, 0.99, 0.86).
- `h03_ladder.py` reproduces the canonical annualised returns on P11 (0.52184) and H (0.82871).
- `h05_fund_evidence.py` reruns its factor regressions on the engine as a positive control, reproducing the session-30 holdout alphas of 0.56379 and 0.45868.

The deck presents the fund (the 25% volatility target on the constant-$10M engine) on its performance slides. PBO, the timing nulls, Romano-Wolf, the signal-delay test and the holdout prediction test the engine signal and stay on the registered search window, P11.
