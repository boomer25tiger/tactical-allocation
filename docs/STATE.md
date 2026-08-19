# STATE — read this first

Refreshed 2026-08-19 by session 16 (D22 closed). Supersedes the session 12.5
version, which was stale from session 13 onward and still stated that the
backtest had never been run. Commit `502ca42` holds sessions 00A through 12.6;
sessions 13 through 15.5 are uncommitted until session 16's single commit.

## What this project is

A daily multi-model tactical allocation study: four sleeves (T10 eleven-name
overbought cascade, T11 two-tier overbought with a trend switcher and 50/50
bear split, S2 TQQQ 200-SMA gate, S3 four-vote SMA regime), 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Position as of session 16

**The backtest has run.** The holdout boundary 2021-08-01 (2.10) is untouched
and no post-boundary quantity has been computed.

- **Designated headline cell (4.1b)**: open-to-open, realized panel, primary
  window, class-tiered slippage with the 2.0x auction premium at the 10 bp
  anchor, commission Arm S, 5% participation cap, canonical NAV 1,000,000.
  Under the corrected 7.14 boundary of 2011-10-04 (session 16 step 1) it reads
  **52.18% annualised and Lo-corrected Sharpe 1.3817**, against 52.26% and
  1.3846 on the superseded 2011-10-03 start.
- **Close-to-close comparison** at equal prominence per 4.1 and 2.8, realized
  29.62% and 0.9251 on the corrected boundary.
- **Benchmark ladder (8.8)**: the strategy ranks sixth of twelve on
  Lo-corrected Sharpe in its own designated cell. The information ratio is
  negative against the five lines it trails and positive against the six it
  leads (session 15).
- **Nulls (8.9)**: the strategy sits at the 98th to 100th percentile of both
  the timing-shuffle and turnover-matched nulls on every window. Romano-Wolf
  (8.10) leaves one family-wise comparison below 0.05.
- **Participation cap (4.6)**: 5% of a trailing 21-session median dollar
  volume, lagged one session, point-in-time. BTAL binds on 189 transitions.
- **Metric set (8.11)**: 41 standalone metrics the grid emitter carries per
  specification, 12 benchmark-relative metrics for the ladder lines only.
- **Panels carry equal weight (2.8)**; no panel is primary.

## Open before the holdout can run

- **The specification grid has NOT run.** Session 16 established it is not
  runnable as registered: only 20 of the 218,700 specifications are enumerable
  from config, since `GRID_UNREPRESENTED_AXES_CARDINALITY` (10,935) stands in
  for axes that no register decision enumerates. See `outputs/session-16/`.
- **PBO, the deflated Sharpe, and the specification curve** all depend on the
  grid and are therefore unrun.
- **D16**, the financing spread, assumed and swept 25 to 200 bp.

## Defect register, current

D1 through D12, D14, D15, D17, D18, D19, D21, D22 closed, repaired, or swept.
D13 never assigned. Open: **D16** financing spread, **D23** portfolio-level
per-instrument attribution confound (corrected in place session 15.5),
**D24** the grid axes are not enumerated (session 16). D20 closed session 16
step 2, with NAV joining the specification curve and not the grid axes.

## Immediate next step

Session 17. The blocker is the grid axis enumeration under 7.2 through 7.9,
which must be closed in the register before the grid, PBO, the deflated
Sharpe, or the specification curve can run. The holdout stays untouched until
those complete.

## What is built

`src/` carries config, indicators, the two-path loader, the four sleeve weight
functions, the portfolio label/merge/cap layer, the per-date fund schedule, and
the spread estimators. `scripts/s13_backtest.py` is the engine, `s14_common.py`
carries the canonical cost model, panels, and cap, and `s15_lines.py` carries
the ladder builders and the 8.11 metric set.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV,
all SHA-256 verified and truncated at 2026-08-14 (1.14).
