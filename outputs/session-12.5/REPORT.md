# Session 12.5 report — commit, register reissue, handoff preparation

No research, no computation. Thirteen sessions of uncommitted work
committed once, the stale register replaced, and the project state
documented for a fresh session. No strategy return, no performance
statistic, no backtest.

## Step 1 — inventory

Working tree before this session: 10 untracked top-level entries covering
everything ever written (nothing had ever been committed; `git log` was
empty). Sizes: repository 356MB total, of which `.venv/` 306MB and `data/`
36MB (`data/raw/` **13MB**, `data/interim/` 22MB of which synthetics
4.5MB). Code and record: `src/` 188KB (18 files), `tests/` 408KB (14),
`scripts/` 480KB (39), `outputs/` 14MB (116), `docs/` 76KB. The
pre-existing `.gitignore` contained only `.venv/` and `data/raw/`.

## Step 2 — version-control rule applied

Code, tests, docs, scripts, manifests, outputs: committed. **`data/raw/`
is 13MB — far under the 100MB rule — so it is committed and the repository
is fully self-contained**; the prior `.gitignore` exclusion of `data/raw/`
was reversed. `data/interim/` is committed EXCEPT `synthetics/`, which is
derived and rebuilt by `scripts/s10_build.py` (excluded; note: SVIX/UVIX
rebuilds read ^SHORTVOL at run time, so rebuilds are network-dependent).
Excluded: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.DS_Store`. Final
`.gitignore` contents are in the repository root.

Two staging corrections made before committing (both mechanical): the
shell's noclobber blocked the first `.gitignore` overwrite so an early
`git add -A` staged under the old rules; synthetics and `.DS_Store` were
then removed from the index. `outputs/session-10/synthetics-manifest.csv`
(a manifest, not a synthetic) remains committed deliberately.

## Step 3 — verification before committing

| Check | Result |
|---|---|
| Full test suite | **199 passed** (matches session 12) |
| `src/config.py` import + validate() | **passes** |
| `src/schedule.py` import + contiguity tests | **17 funds, 10 tests pass** |
| SHA-256, 00E authoritative manifest (original panel + VX parquet era) | **verified, 0 mismatches** (positive control: SPY verified first) |
| SHA-256, per-session manifests (01 RYMFX, 02 DTB3, 08 NETR, 10 additions, 12 SOXX/NAV) | **52 files verified, 0 mismatches, 0 missing** |
| SHA-256, 00A VX manifest (268 CFE CSVs) | **268/268 verified** after a path-prefix correction in the checker (manifest stores bare filenames); 0 mismatches |
| Files on disk with no manifest row | **none** |
| Manifest rows with no file | **none** |

**All 320 frozen files verify. The repository state matches its own
records.**

## Step 4 — the commit

Single commit **`ad6be24ef13df4967ac3de538afc62eedeab7a81`**, 522 files,
277,457 insertions. Message records: construction complete and validated
across sessions 00A–12; the backtest has not been run; the holdout at
2021-08-01 is untouched; and that the v3 register and STATE.md follow the
commit uncommitted, per this session's stop condition. No branch, no tag,
no push. (The message was amended once, before any other work, to remove
an inaccurate claim that the register was inside the commit.)

## Step 5 — register reissued

- `docs/DECISIONS-OPEN-v2.md` → renamed
  `docs/ARCHIVE-DECISIONS-OPEN-v2-STALE.md` with a header stating it
  predates session 00A and carries wrong values.
- **`docs/DECISIONS-v3.md` written**: every decision with ID, status,
  value, and closing session; full reversal histories for the six
  decisions reversed at least once (2.5 trend series, 2.7 validation —
  reversed twice with the band still awaiting confirmation, 4.3 slippage —
  reversed twice, 4.7 sizing, 6.10 crash threshold — reversed twice, 1.8
  split check); an eleven-item corrections list of claims made and later
  overturned; open decisions with blockers; and [A] flags on every closure
  resting on a stated assumption rather than a measurement (2.7 band
  proposal, 2.14 constancy, 3.12 central value, 4.2 feed assumption, 6.10
  stipulation), per 9.10.

## Step 6 — current-state summary

**`docs/STATE.md` written**: what the project is, what is built (with the
199-test standard), what is frozen (320 files, hash provenance), the
validation standard reached, the nine limitations that bear on any future
result (SOXS exception, SVXY's single unmatched session, SVIX/UVIX
close-only validation and pre-2022 absence, the 5.4× regime gradient, the
single-year financing anchor, the partial expense schedule, FAS's Russell
era, per-fund pre-inception windows, the 4.2 feed assumption), the seven
operating conventions every session has followed, and the immediate next
step (the deferred session 13 canonical backtest, then band confirmation,
7.14, the 8.8 ladder, the grid).

## Self-containment statement

**The repository is fully self-contained at commit `ad6be24`**: code,
tests, frozen data (13MB, hash-verified), manifests, and every session
report are inside it. The only regeneration step a fresh clone needs is
`scripts/s10_build.py` for the synthetics (network needed only for the
SVIX/UVIX legs), plus a Python environment per
`requirements-session-00a.txt` and pytest. The v3 register, STATE.md, the
archived v2, and this report sit in the working tree uncommitted, as
instructed.

## Stop condition

Halted after this report. The step 4 commit was the single exception to
the standing no-commit instruction; nothing after it has been committed.
No backtest, no performance statistic. Working tree carries exactly the
four documentation files listed above plus this report.
