# STATE — read this first

Refreshed 2026-08-19 by session 18s. Supersedes the session 16 version, which
was stale from session 16b onward and still stated that the grid had not run
and that D24 was open. Both are now false.

Position is commit `9e7aa47` plus session 18s. `9e7aa47` carries sessions 16b,
17, 18 steps 0 through 3, and 18r. `a90f352` is session 16 and is one commit
behind that.

## What this project is

A daily multi-model tactical allocation study: four sleeves (T10 eleven-name
overbought cascade, T11 two-tier overbought with a trend switcher and 50/50
bear split, S2 TQQQ 200-SMA gate, S3 four-vote SMA regime), 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Where the repository lives

`/Users/GualyCr/Downloads/tactical-allocation`, moved from `~/Desktop` on
2026-08-19 to get it out of iCloud Drive after an eviction incident. Do not
move it back under a synced path. Registered at 10.1.

## Position

**The backtest has run and the grid has run.** The holdout boundary 2021-08-01
(2.10) is untouched and no post-boundary quantity has been computed.

- **Designated headline cell (4.1b)**: open-to-open, realized panel, primary
  window, class-tiered slippage with the 2.0x auction premium at the 10 bp
  anchor, commission Arm S, 5% participation cap, canonical NAV 1,000,000.
  Under the corrected 7.14 boundary of 2011-10-04 it reads **52.18%
  annualised and Lo-corrected Sharpe 1.3817**. Session 18 step 1 reproduced
  both from the completed grid.
- **Close-to-close comparison** at equal prominence per 4.1 and 2.8, realized
  29.62% and 0.9251 on the corrected boundary.
- **Benchmark ladder (8.8)**: the strategy ranks sixth of twelve on
  Lo-corrected Sharpe in its own designated cell.
- **Nulls (8.9)**: 98th to 100th percentile of both the timing-shuffle and
  turnover-matched nulls on every window. Romano-Wolf (8.10) leaves one
  family-wise comparison below 0.05.
- **The grid ran** (session 17) at 121,500 of the 364,500 enumerated
  specifications, in 2.19h across eight shards, emitting 48-block moment
  sums, a 72-column metric set, and the specification index. The 121,500
  follows from dropping 7.4, the tier-two offset, from the searched set on
  the grounds that the register marks it informed rather than closed.
  364,500 divided by that axis's three values is 121,500.
- **Panels carry equal weight (2.8)**; no panel is primary.

## Open

- **Session 18 is resumable at step 3.** Steps 0 through 2 completed and their
  outputs are intact. Steps 4 through 10 have not run.
- **PBO is partial.** `outputs/session-18/pbo-partial.csv` carries S equal to
  8, 12 and 16 on the full grid. S equal to 24, S equal to 48 and the
  smooth-axis restriction never ran. Per-pass status is in
  `pbo-partial-status.csv`.
- **The deflated Sharpe and the specification curve** have not run.
- **D16**, the financing spread, assumed and swept 25 to 200 bp.
- **D26 and D27** were raised in `outputs/session-16b/REPORT.md` and are not
  in the register, which ends its defect numbering at D25.

## Custody, the standing risk

**There is no remote and no off-machine copy.** The object store was packed by
session 18s, which consolidates and checksums but does not duplicate. 862 of
886 objects now sit in a single pack file. One storage failure loses the
repository. A private GitHub remote closes this and nothing else does.

The 1.1 GB of ephemeral daily panels under `outputs/session-17/panel/` are
excluded from the backup set by design and are scheduled for deletion at
session 18 step 8. `.venv` is reconstructible from the freeze recorded at
`outputs/session-18s/environment.csv`.

## Defect register, current

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. D25 recorded as documentation. Open: **D16** financing spread,
**D23** portfolio-level per-instrument attribution confound (corrected in
place session 15.5), and **D26** and **D27** pending entry into the register.

## What is built

`src/` carries config, indicators, the two-path loader, the four sleeve weight
functions, the portfolio label/merge/cap layer, the per-date fund schedule, and
the spread estimators. `scripts/s13_backtest.py` is the engine, `s14_common.py`
carries the canonical cost model, panels, and cap, `s15_lines.py` carries the
ladder builders and the 8.11 metric set, and the session 17 scripts carry the
grid emitter.

## Environment

Python 3.13.13 from the system framework interpreter. `.venv` rebuilt by
session 18s with every resolved version identical to the pre-rebuild state, so
session 17's grid stands under an unchanged environment. numpy 2.5.2, pandas
3.0.5, pyarrow 25.0.1, pytest 9.1.1.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV,
all SHA-256 verified and truncated at 2026-08-14 (1.14). Re-verified 339 of
339 against manifest by session 18r.
