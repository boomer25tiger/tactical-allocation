# STATE, read this first

Refreshed 2026-08-20 by session 20. Supersedes the session 19.5 version.

Session 20 ran phases A through C, tripped gate C, and did not reach phases D
through G. Partial completion through a completed phase is the state this
project is in.

## What this project is

A daily multi-model tactical allocation study, four sleeves at 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Custody

`/Users/GualyCr/Downloads/tactical-allocation`, outside iCloud Drive. Private
remote at `https://github.com/boomer25tiger/tactical-allocation`.
`http.postBuffer` is 524288000 locally, without which a push of this pack size
fails with HTTP 400.

**The machine is memory-constrained.** 8 GiB physical with roughly 1 GiB free
and swap near exhaustion. Session 19's chunk of 514 peaked at 3.56 GB and is not
available. Any step loading the moment array must state a ceiling from measured
free memory and halt rather than enter swap.

## Position

The backtest, the grid, PBO, the deflated Sharpe, and the specification curve
have all run. The holdout boundary 2021-08-01 (2.10) is untouched.

- **The primary window boundary is repaired.** `s14_common.PRIMARY_START` now
  reads 2011-10-04. Every session 15 output carried 2,473 sessions against the
  corrected 2,472, and the affected outputs are rebuilt into
  `outputs/session-20/rebuilt/` with the originals preserved.
- **Designated headline cell**, 0.521845 annualised and 1.381701 Lo-corrected
  Sharpe, confirmed by positive control before and after the repair.
- **No ladder rank changed** under the repair. The strategy holds sixth of
  twelve on both metrics.
- **PBO 0.1578** at S equal to 16. **Deflated Sharpe** 0.000660 canonical at N
  equal to 364,500.

## Gate C, tripped and unresolved

On the designated cell the timing-shuffle null on annualised return moved from
p 0.000 to **p 0.001**, which does not clear p below 0.001, and the strategy's
percentile on that arm moved from 100.0 to 99.9. On the Lo-corrected Sharpe,
which 8.2 designates as headline, both nulls remain at p 0.000 with the strategy
at the 100th percentile. **What the paper claims from the annualised-return arm
is an open register decision.** Registered at 9.23.

## Open before the holdout can run

- **Gate C is unresolved**, above.
- **The B1 re-emission is outstanding.** The chunk-first-element defect is
  repaired at all four code sites, but the three regression figures in
  `outputs/session-19/pbo.csv` and the regression columns of `pbo-strata.csv`
  still carry it. The pass halted on the memory gate. Known magnitude is
  3.176e-04 on the S equal to 16 slope. PBO and stratified PBO are immune.
- **Phases D through G are unrun**, so the Lo q sweep, the deflated Sharpe
  correction to N equal to 121,500, the axis census, the three unsourced 9.11
  axes, effective N, the January 2013 attribution, and the corrected
  degradation null all remain open.
- **SVIX and UVIX leave a code path untested at the holdout read.** They are
  held in code, load on neither panel, and list 2022-03-30 inside the holdout
  span, so the holdout measures a strategy that differs from the source over
  that span. Registered at 9.20.
- **D16**, the financing spread, remains assumed.
- **8.2** is open, being whether the Lo-corrected Sharpe remains headline given
  the estimator's sampling behaviour. Registered at 9.24.
- **7.14b tension** on early-start return figures, at 9.18, left open.

## Authoritative artifacts

`outputs/session-20/held-universe.csv` is the derived held and signal universe
and **supersedes every hardcoded ticker list in the repository**. 19 held, 13
signal-only, derived from the AST of `src/sleeves.py`. The list in
`scripts/s195_strip.py` carried four misclassifications.

## Defect register

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. **D25 applied** by the 1.777 matched-exposure rebuild. **D26 and
D27 are now written into the register** at session 20. Open: **D16**, **D23**.

## Environment

Python 3.13.13, numpy 2.5.2, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1.
matplotlib is deliberately absent.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV, all
SHA-256 verified and truncated at 2026-08-14 (1.14). 339 of 339 verified against
manifest by session 19.5.
