# STATE — read this first

Refreshed 2026-08-19 by session 19. Supersedes the session 18s version.

Position is the session 19 commit, whose parent is `40ff46b` (session 18s).
`9e7aa47` carries sessions 16b, 17, 18 steps 0 through 3, and 18r.

## What this project is

A daily multi-model tactical allocation study: four sleeves (T10 eleven-name
overbought cascade, T11 two-tier overbought with a trend switcher and 50/50
bear split, S2 TQQQ 200-SMA gate, S3 four-vote SMA regime), 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Custody

`/Users/GualyCr/Downloads/tactical-allocation`, outside iCloud Drive since
2026-08-19. **A private GitHub remote now exists** at
`https://github.com/boomer25tiger/tactical-allocation`, with remote main
matching local HEAD and upstream tracking set. The single-copy exposure that
STATE.md and session 18s both flagged is closed. Registered at 10.2.

Note `http.postBuffer` is set to 524288000 locally, without which a push of
this pack size fails with HTTP 400.

## Position

**The backtest, the grid, PBO, the deflated Sharpe, and the specification
curve have all run.** The holdout boundary 2021-08-01 (2.10) is untouched and
no post-boundary quantity has been computed.

- **Designated headline cell (4.1b)**, open-to-open, realized panel, primary
  window, class-tiered slippage with the 2.0x auction premium at the 10 bp
  anchor, commission Arm S, 5% participation cap, canonical NAV 1,000,000.
  **52.18% annualised and Lo-corrected Sharpe 1.3817** on the corrected 7.14
  boundary of 2011-10-04. Reproduced from the completed grid at six decimals
  by session 19 step 2.
- **Close-to-close comparison** at equal prominence per 4.1 and 2.8, 29.62%
  and 0.9251.
- **The grid** ran at 121,500 of the 364,500 enumerated specifications, with
  7.4's tier-two offset held at canonical rather than searched.
- **PBO is 0.1578** at S equal to 16 over the full 12,870 combination
  enumeration, spanning 0.1143 to 0.1710 across block counts 8 through 48.
  The degradation slope is -1.0663. Registered at 8.12.
- **Stratified PBO** replaces the 27-specification smooth-axis restriction.
  The full-grid PBO exceeds none of the six within-stratum ranges, lying
  inside five and below one. Registered at 8.13.
- **Deflated Sharpe** at N equal to 364,500 is 0.000660 for the canonical and
  0.023736 for the grid's in-sample-best, against an expected maximum Sharpe
  under the no-skill null of 2.1082 annualised. 8.7 amended.
- **The canonical ranks 6,834 of 121,500** on Lo-corrected Sharpe and 8,237
  on annualised return.
- **Benchmark ladder (8.8)**, sixth of twelve on Lo-corrected Sharpe in its
  own designated cell. **Nulls (8.9)**, 98th to 100th percentile on every
  window, with Romano-Wolf leaving one family-wise comparison below 0.05.
- **Panels carry equal weight (2.8)**; no panel is primary.

## Artifacts

The four-tier scheme is executed and registered at 9.14. The ephemeral daily
panels are **deleted**, reclaiming 1,256.8 MB and taking the working tree from
1,764.7 MB to 508.0 MB. What remains is the frozen raw inputs, the 24 grid
shards, the 2,000-specification subsample, the augmented specification index,
the manifest, and the reports.

`outputs/session-19/MANIFEST.json` carries the canonicalised panel hash, the
39 input hashes, the config hash, the seeds, the block boundary dates, the
environment record, and the exact command that regenerates the panel.
`scripts/verify_panel.py` reports maximum absolute deviation against a 1e-6
tolerance rather than asserting bit-identical equality.

## Open before the holdout can run

- **D16**, the financing spread, remains assumed and swept 25 to 200 bp. No
  emitted CSV carries a per-level designated-cell return.
- **Three specification-curve axes are not sourced**, being the SMH accrual
  arm, the sizing mode, and the unavailable-fill completion rule. Each is
  named as a 9.11 curve axis and no emitted CSV in this repository carries a
  two-arm designated-cell comparison for it.
- **D23**, the portfolio-level per-instrument attribution confound, corrected
  in place session 15.5.
- **D26 and D27** were raised in `outputs/session-16b/REPORT.md` and are still
  not written into the register, which ends its defect numbering at D25.

## Defect register, current

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. D25 recorded as documentation. Open: **D16**, **D23**, and
**D26** and **D27** pending entry into the register.

## What is built

`src/` carries config, indicators, the two-path loader, the four sleeve weight
functions, the portfolio label/merge/cap layer, the per-date fund schedule, and
the spread estimators. `scripts/s13_backtest.py` is the engine, `s14_common.py`
carries the canonical cost model, panels, and cap, `s15_lines.py` carries the
ladder builders and the 8.11 metric set, the session 17 scripts carry the grid
emitter, and the session 19 scripts carry CSCV, the stratification, the
deflated Sharpe, the specification curve, and the report generator.

## Environment

Python 3.13.13 from the system framework interpreter, numpy 2.5.2, pandas
3.0.5, pyarrow 25.0.1, pytest 9.1.1. Rebuilt session 18s from a pre-removal
freeze rather than from an authoritative requirements.txt, which does not
exist, so the zero version divergence that rebuild reported is partly a
construction of that method rather than independent confirmation. The manifest
records this. matplotlib is deliberately absent and the report figures are
generated as SVG by `scripts/s19_svg.py` using the standard library alone.

The machine carries 8 GB. CSCV peak resident memory reached 3.355 GB against a
stated 2.0 GB ceiling, which is recorded at 8.12 and does not affect any
figure.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV,
all SHA-256 verified and truncated at 2026-08-14 (1.14). Re-verified 339 of
339 against manifest by session 18r.
