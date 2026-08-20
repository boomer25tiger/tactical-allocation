# STATE — read this first

Refreshed 2026-08-19 by session 19.5. Supersedes the session 19 version.

Position is the session 19.5 commit, whose parent is `525c0a7` (session 19).

## What this project is

A daily multi-model tactical allocation study: four sleeves (T10 eleven-name
overbought cascade, T11 two-tier overbought with a trend switcher and 50/50
bear split, S2 TQQQ 200-SMA gate, S3 four-vote SMA regime), 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Custody

`/Users/GualyCr/Downloads/tactical-allocation`, outside iCloud Drive. Private
remote at `https://github.com/boomer25tiger/tactical-allocation` with remote
main matching local HEAD. `http.postBuffer` is set to 524288000 locally,
without which a push of this pack size fails with HTTP 400.

## Position

The backtest, the grid, PBO, the deflated Sharpe, and the specification curve
have all run. The holdout boundary 2021-08-01 (2.10) is untouched.

- **Designated headline cell (4.1b)**, 52.18% annualised and Lo-corrected
  Sharpe 1.3817 on the corrected 7.14 boundary of 2011-10-04. Rebuilt from the
  frozen inputs by session 19.5 to six decimals, so it survives the panel
  deletion.
- **PBO 0.1578** at S equal to 16, spanning 0.1143 to 0.1710 across block
  counts. Stratified PBO exceeds none of the six within-stratum ranges (8.12,
  8.13).
- **Deflated Sharpe** 0.000660 canonical and 0.023736 in-sample-best at N
  equal to 364,500 (8.7).
- **The canonical ranks 6,834 of 121,500** on Lo-corrected Sharpe.

## The ladder, audited session 19.5

- **No construction defect.** Every levered and inverse ladder row holds the
  live fund ticker from the frozen parquet, not a costless scaling. The
  ladder's TQQQ row tracks live TQQQ volatility nine times closer than a
  costless 3x. Registered at 9.17.
- **Every ladder row carries the superseded 2011-10-03 boundary.** Its
  STRATEGY row reads 1.3846 over 2473 sessions against the 7.14a corrected
  1.3817 over 2472. `s14_common.PRIMARY_START` still defaults to 2011-10-03.
  **Session 20 step 5 owns this repair. 8.8 is deliberately unamended.**
- **The Lo correction is not separable from sampling noise at this sample
  length.** Under a permutation null that destroys serial dependence, the Lo
  factor still averages 1.1129 and reaches 1.4783 at the 95th percentile
  against QQQ's observed 1.5598. Eight of twelve rows change rank between the
  naive and Lo-corrected metrics. Whether 8.2 keeps the Lo-corrected Sharpe as
  headline is an open register decision.
- **Romano-Wolf direction is now established.** The one comparison below 0.05
  is the equal-weight universe at 0.033 with the **strategy above**.

## The window strip, post-hoc under 9.10

Registered at 9.16. **The primary window remains 2011-10-04.** The strategy's
rank among twelve is not stable across six start dates, spanning 3 to 6 under
the naive Sharpe and 5 to 7 under the Lo-corrected, with the canonical start
returning the lowest rank under both. The earliest full-composition start on
the synthetic panel is **2013-01-23**, bound by QQQE, which is later than
canonical, so no genuinely early arm exists.

## Open before the holdout can run

- **The ladder is on the superseded boundary.** Session 20 step 5.
- **8.2's headline metric** is an open register decision given the Lo
  correction's sampling behaviour.
- **7.14b tension** on early-start return figures, recorded at 9.18, left open.
- **D16**, the financing spread, assumed and swept 25 to 200 bp.
- **Three specification-curve axes unsourced**, being the SMH accrual arm, the
  sizing mode, and the unavailable-fill completion rule.
- **D23**, corrected in place session 15.5. **D26 and D27** still absent from
  the register, which ends its defect numbering at D25.
- **The 8.8 matched-exposure benchmark still names 1.70** where D25 superseded
  it with 1.777.
- **External QQQ verification pending.** No independent offline series exists.

## Defect register, current

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. D25 recorded as documentation. Open: **D16**, **D23**, and
**D26** and **D27** pending entry. Session 19.5 added no new defect number,
since the ladder boundary is a known correction not yet propagated and the Lo
finding is a register decision rather than a defect.

## What is built

`src/` carries config, indicators, the two-path loader, the four sleeve weight
functions, the portfolio label/merge/cap layer, the per-date fund schedule, and
the spread estimators. `scripts/s13_backtest.py` is the engine, `s14_common.py`
carries the canonical cost model, panels, and cap, `s15_lines.py` carries the
ladder builders and the 8.11 metric set, the session 17 scripts carry the grid
emitter, the session 19 scripts carry CSCV and the report generator, and the
session 19.5 scripts carry the ladder audit and the window strip.

## Environment

Python 3.13.13, numpy 2.5.2, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1.
matplotlib is deliberately absent. The machine carries 8 GB; session 19.5
peaked at 0.211 GB against a 4.0 GB stated ceiling.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV,
all SHA-256 verified and truncated at 2026-08-14 (1.14). **Re-verified 339 of
339 against manifest by session 19.5**, which is what every measurement in that
session ran from after the panel deletion.
