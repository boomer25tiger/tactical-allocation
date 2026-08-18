# STATE — read this first

As of session 12.5 (2026-08-18). Commit `ad6be24` holds sessions 00A–12.
This file and DECISIONS-v3.md were written after that commit and are
uncommitted by instruction.

## What this project is

A daily multi-model tactical allocation study: four sleeves (T10
eleven-name overbought cascade, T11 two-tier overbought with a trend
switcher and 50/50 bear split, S2 TQQQ 200-SMA gate, S3 four-vote SMA
regime), 25% budget each, reconstructed from a QuantConnect source
(`docs/source-quantconnect.py`) with every numeric parameter deliberately
re-specified and registered. The register is `docs/DECISIONS-v3.md`;
canonical values live in `src/config.py` (validate() runs on import).

**The backtest has never been run. No strategy return, Sharpe, weight, or
performance statistic exists anywhere in this repository. The holdout
boundary 2021-08-01 (2.10) is untouched.**

## What is built (all tested; 199 tests passing)

- `src/config.py` — every parameter, decision IDs, validate() guards
  (incl. the 7.10 grid-product pin).
- `src/indicators.py` — Wilder RSI + SMA, skip gap treatment (1.9).
- `src/data.py` — two-path loader (1.4), trend lag once (2.5a), DTB3
  calendar-day accrual factors (5.5a), skip tr_index.
- `src/sleeves.py` — four weight functions, structure from source, nine
  named pairwise-raise sites, availability switches for SVIX/UVIX legs.
- `src/portfolio.py` — label/short-circuit/merge/cap/drift (5.1–5.4).
- `src/execution.py` — T+1 fills, both 4.1 modes in one path, truncation
  sizing (4.7), DTB3 residual accrual, degeneracy detection.
- `src/schedule.py` — per-date multiple/benchmark for 17 funds,
  filing-grade, "on or about" carried, contiguity tested.
- `src/spread.py` — Corwin-Schultz + Abdi-Ranaldo (now data
  characterisation only; the tier apparatus was abandoned, 4.3).
- `scripts/s10_build.py` — builds the nineteen synthetics into
  `data/interim/synthetics/` (gitignored, rebuildable; SVIX/UVIX rebuilds
  read ^SHORTVOL at run time).

## What is frozen (all SHA-256-verified, 320 files, zero mismatches)

- 44 ETF/fund parquets under `data/raw/etf/` (incl. RYMFX, SOXX, QID, SSO,
  SDS, UVXY, SVXY, SVIX, UVIX) — hashes: 00E `manifest-truncated.csv`
  (authoritative for the original panel) + per-session manifests
  (sessions 01, 10, 12).
- 268 CFE VX CSVs (00A manifest) + derived VX panels under `data/interim/`
  (construction B = `vx-cm30-b.parquet`).
- `data/raw/rates/DTB3.parquet` (session 02), `data/raw/index/NETR.parquet`
  (session 08; the study's only interior gaps, 3 sessions, explicit
  nulls), `data/raw/nav/{UVXY,SVXY}_nav.parquet` (session 12, ProShares
  issuer NAV).
- Everything truncated at 2026-08-14 (1.14).

## Validation standard reached (session 12, `outputs/session-12/`)

Nineteen synthetics validated against real funds/NAV: index-family funds
corr 0.993–0.999, |TD| ≤ 1.3%/yr; sector funds on exact benchmarks
(XLK/SOXX/XBI) 0.978–0.998; UVXY vs issuer NAV 0.9998 (both multiple
eras); mechanism validated through 2008 by five siblings at |M| ∈ {1,2};
tracking error grows ~linearly in |M|; expense arithmetic verified
expected == measured to the bp.

## Limitations that bear on any future result

1. **SOXS exception**: +6.21%/yr TD, 1394% max rolling divergence —
   real-fund frictions compounding at −3×, recorded, not repaired.
2. **SVXY 2018-02-06**: the fund's actual book (+187%) departed from its
   index (+26%) for one session; every other pre-2018 day matches NAV to
   decimals.
3. **SVIX/UVIX**: no issuer NAV; validated against exchange closes only
   (+7.5–8.9%/yr residual of the close-timing class); absent before 2022,
   so T10's short-vol and S3's vol legs resolve to SVXY/UVXY throughout
   the sample.
4. **Regime gradient**: equity tracking error rises 5.4× from calmest to
   wildest underlying-vol decile (D1 1.71% → D10 9.13%); unchanged by the
   SOXX adoption. The construction is weakest where the bear branches
   operate; 2007–2010 extrapolation is the weak case.
5. **Financing anchor** (75 bp long / 70 bp short) is a single-fiscal-year
   snapshot (Direxion FY2025 / ProShares FY2026 harvests).
6. **Expense schedule** stated only for the seven Direxion funds in
   FY2025; everything else carried constants (session 11 schedule).
7. **FAS 2008–2022**: benchmark unobtainable, XLF is an approximation
   (basket mismatch undisclosed by any free source).
8. **Pre-inception windows**: sector funds have no sibling validation
   before their listings; NDX/SPX families do (PSQ/QID/SH/SSO/SDS through
   2008).
9. **4.2**: closes are consolidated-tape, assumed equal to official
   auction prints.

## Operating conventions every session has followed

- Run alone; no concurrent session against this tree.
- Positive control before any negative finding is reported.
- The `timeout` binary does not exist on this machine (exit 127).
- Parameters read from `src/config.py`, never hardcoded.
- No commit inside a session (the single 12.5 commit is the exception).
- Every intermediate artifact under `outputs/<session>/`; reports as
  REPORT.md per session.
- Failures recorded with diagnostics and runs continue; halt only when
  later steps become meaningless.

## Immediate next step

**Session 13: the canonical in-sample backtest** (its full prompt exists;
it was deferred in favour of this handoff session). Key constraints it
carries: holdout truncation at 2021-07-31 in the loader with an assertion;
everything from config; cost curve as the primary object; sanity checks
that must pass before interpretation; both 2.8 arms; no benchmarks, no
nulls, no grid — those are later sessions. After it: the 2.7 band
confirmation, 7.14 sub-periods, the 8.8 ladder and nulls, then the grid.
