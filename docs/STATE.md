# STATE, read this first

Refreshed 2026-08-20 by session 21. Supersedes the session 20 version.

Sessions 20 and 21 both ran to completion. Session 20's gate C failed and is now
recorded as unresolved with a defect in the gate specification itself. Session
21's gates A and C both cleared and no phase was skipped.

## What this project is

A daily multi-model tactical allocation study, four sleeves at 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Custody and machine

`/Users/GualyCr/Downloads/tactical-allocation`, outside iCloud Drive, private
remote at `https://github.com/boomer25tiger/tactical-allocation`.
`http.postBuffer` is 524288000 locally.

**The machine has not been rebooted since 2026-08-06.** Roughly 0.05 GiB is
genuinely free, 3.18 GiB sits in the compressor, and free swap is near 1.2 GB.
Two session 20 passes died on this. Any step loading the moment array must state
a ceiling from measured free memory and halt rather than enter swap. A reboot
would return most of it.

## Position

The backtest, the grid, PBO, and the specification curve have all run. The
holdout boundary 2021-08-01 is untouched.

- **Designated headline cell**, 0.521845 annualised and 1.381701 Lo-corrected
  Sharpe, confirmed by positive control in every session since 19.
- **The boundary is repaired** at 2011-10-04 and session 15's outputs are
  rebuilt into `outputs/session-20/rebuilt/`. No ladder rank changed.
- **PBO 0.1578** at S equal to 16. **N is 121,500**, not 364,500.
- **The canonical ranks 6,834 of 121,500** on Lo-corrected Sharpe, and eight of
  its nine axis values were fixed before any comparison on that axis.

## Statistics removed or withdrawn

- **The deflated Sharpe is REMOVED** at 8.7, on a misspecified null rather than
  an unfavourable result. The recentred comparison replaces it. The canonical
  sits 1.0425 cross-sectional standard deviations above the grid mean at the
  89.28th percentile, and exceeds the expected maximum only at the
  participation-ratio effective count of 3.43, not at 6.72, 17, or 121,500.
- **The degradation slope is REMOVED** at 9.35, since no valid null exists and
  session 20's phase G was blocked on memory.
- **The session 19.5 window strip is WITHDRAWN** at 9.36, since it compared a
  nested strategy against seven stateful re-initialised benchmark lines.

## The beta decomposition, session 21

Static beta to buy-and-hold QQQ is 1.108673 at an R-squared of 0.186794. **The
beta-hedged residual carries a naive Sharpe of 0.655836 and a Lo-corrected
Sharpe of 0.864915**, against the strategy's 1.0911 and 1.3817. Timing is the
smallest of the three return components. A passive QQQ line at the canonical's
own realised beta, daily rebalanced and identically charged, reaches a naive
Sharpe of 1.108581 and places sixth of thirteen. Registered at 9.34.

## Open before the holdout can run

- **Session 20 gate C is unresolved**, and the gate itself is defective, since
  clearing p below 0.001 at 1,000 draws requires zero exceedances and turns on a
  single draw. Registered at 9.38.
- **Session 20's B1 re-emission and phase G are outstanding**, both halted on
  memory, and the machine has not been rebooted since.
- **8.2 is open**, being whether the Lo-corrected Sharpe stays headline. The Lo
  q is an unregistered Python default, at 9.37.
- **Ten config parameters have no consumer** and two more are read but never
  invoked, at 9.31. `FINANCING_SPREAD_BP` is never read by the engine, which
  bears on how D16 is described.
- **`crash_threshold` was fixed after measurement on its own axis**, at 9.32.
- **The leave-one-out artifacts carry the superseded boundary**, since session
  20 phase C rebuilt only four scripts.
- **SVIX and UVIX leave a code path that will not execute at the holdout read.**
- **D16 and D23 stand.**

## Authoritative artifacts

`outputs/session-20/held-universe.csv` supersedes every hardcoded ticker list,
at 19 held and 13 signal-only. `outputs/session-21/unwired-config.csv` is the
config-consumer map.

## Defect register

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. D25 applied. D26 and D27 recorded at session 20. Open: **D16**,
**D23**.

## Environment

Python 3.13.13, numpy 2.5.2, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1.
matplotlib deliberately absent.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV, all
SHA-256 verified and truncated at 2026-08-14. 339 of 339 verified by session 19.5.
