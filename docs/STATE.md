# STATE, read this first

Refreshed 2026-08-22 by session 24. Supersedes the session 22 version.

**The claim set is frozen.** `docs/CLAIMS.md` carries 15 claims with the
limitations written beside each, and `docs/WITHDRAWN.md` carries 10 withdrawals.
No claim is added after 2026-08-22 without a dated register entry recording the
addition and its grounds. Registered at 9.51 and 9.52.

**The measurement phase is closed.** One measurement remains outstanding, being
S equal to 48 of the B1 re-emission, and it is not load-bearing.

## What this project is

A daily multi-model tactical allocation study, four sleeves at 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Custody and machine

`/Users/GualyCr/Downloads/tactical-allocation`, private remote at
`https://github.com/boomer25tiger/tactical-allocation`. `http.postBuffer` is
524288000 locally.

**The constraint on this machine is CPU contention, not memory.** Load average
reached 39.57 on eight cores with Chrome taking four of them, and a measured
pass received a mean of 6.25 percent CPU. Session 24 added the first supporting
completion observation, four of five stages completing at a load-to-core ratio
of 1.90 at launch against 4.9463 when session 22's pass failed, at 9.50. Report
compressor size, swap used, swap free and page-outs. **Do not quote free memory
as headroom**, since macOS holds free near zero by design.

## Position

- **Designated headline cell**, 0.521845 annualised and 1.381701 Lo-corrected
  Sharpe over 2,472 sessions, confirmed by positive control every session.
- **The boundary is 2011-10-04** and session 15's outputs are rebuilt.
- **PBO 0.1578** at S equal to 16. **N is 121,500.** The figure re-emits
  exactly on repaired code, as do S equal to 8, 12 and 24, at 9.48.
- **The canonical ranks 6,834 of 121,500** on Lo-corrected Sharpe, with eight of
  nine axis values fixed before any comparison on that axis.

## The 8.2 decision, made

**Both Sharpe conventions are reported throughout, with the naive Sharpe
leading.** The grounds are that the strategy's Lo factor sits inside its own
no-autocorrelation null while buy-and-hold QQQ's sits outside, and that nine of
twelve ladder rows change rank across the unregistered q sweep. Registered at
8.2 as decided.

## Gate C of session 20, resolved

At 10,000 draws on the designated cell all four null and metric combinations
clear p below 0.001, the timing-shuffle annualised-return arm at seven
exceedances being p 0.00070 and the other three at zero. Every 1,000-draw count
is consistent with the new estimate. The earlier trip was a property of the
gate's resolution, since clearing p below 0.001 at 1,000 draws requires exactly
zero exceedances. Registered at 9.40.

## Statistics removed or withdrawn

The deflated Sharpe at 8.7, the degradation slope at 9.35, and the session 19.5
window strip at 9.36. The recentred comparison replaces the first.

## Findings that overturned prior sessions

- **The leave-one-out artifacts were already on the corrected boundary.** Base
  estimate identical to ten decimals. Session 21's F2 finding overturned, at
  9.41.
- **The 1.5636 agreement is structural, not coincidental**, at a gap of
  8.326e-07, since dropping calendar 2011 and starting at the first 2012 session
  remove very nearly the same sessions. Session 21 overturned, at 9.41.
- **The rolling beta extremes are estimation noise.** The standard deviation
  falls monotonically from 1.164612 at a 60-session window to 0.209 at 504. The
  timing component changes sign and the exposure-matched line beats the strategy
  only at the shortest window. Session 21 qualified, at 9.42.
- **The register's blocked-on-memory claims were wrong in mechanism**, corrected
  at 9.35 and 8.12.

## Open before the holdout can run

**One measurement remains outstanding and it is not load-bearing.** Session 24
ran the B1 re-emission on a quiet machine and reached four of five block counts
before its wall limit fired, leaving S equal to 48 alone. **All four re-emitted
PBO values reproduce the reported figures exactly**, so the chunk-first-element
defect did not touch PBO and S equal to 48 sets neither endpoint of the reported
range. The corrected degradation null at 9.46 is not run and its slope is
withdrawn at 9.35 regardless. Registered at 9.48.

**The wall limit was mis-derived**, at 969 seconds taken from a single-chunk
pass against a sweep measuring 2424.37 seconds when first run, so the halt
reflects the limit rather than the machine. A wall limit for a multi-stage pass
is derived from that pass's own stage times. Registered at 9.49.
- **Ten config parameters have no consumer** and two more are read but never
  invoked, at 9.31.
- **`crash_threshold` was fixed after measurement on its own axis**, at 9.32.
- **SVIX and UVIX leave a code path that will not execute at the holdout read**,
  at 9.43. The loader is left unchanged deliberately.
- **D16 and D23 stand.**

## Defect register

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. D25 applied. D26 and D27 recorded. Open: **D16**, **D23**.

## Environment

Python 3.13.13, numpy 2.5.2, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1.
matplotlib deliberately absent.

## Figures

**None is drawn.** Ten are specified at `outputs/session-24/figure-spec.csv`,
two of which are not drawable from committed artifacts, being the null
distribution histograms and effective exposure by decile. Plotting will use the
standard-library SVG path at `scripts/s19_svg.py`, since matplotlib is
deliberately absent. Registered at 9.53.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV, all
SHA-256 verified and truncated at 2026-08-14. 339 of 339 verified by session 19.5.
