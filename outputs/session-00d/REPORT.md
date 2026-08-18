# Session 00D report — strategy source not located

**Outcome: the strategy source was not found. Session 00D halted at Step 0.**

Step 0 of the session prompt directs that if the source defining the four
sleeves is not found anywhere on the machine, the session stops immediately,
writes this report listing the directories searched, proceeds to no other step,
and does not reconstruct the strategy from the register. That branch was taken.

Not executed, by instruction:

- Step 1, the AST scanner. `scan_indicators.py` was **not** written and **not**
  run. There is no source to scan.
- Step 2, the semantic audit and `signal-sources.csv`. Not produced.
- Step 3, the comparison against the manual audit table. Not performed.
- Step 4, warm-up availability and `warmup-availability.csv`. Not produced. No
  yfinance query was issued in this session.

`source-location.md` was not written, since that artifact is specified only for
the branch where source is found.

**Decision 2.11 is not closed by this session.** The question Step 3 was to
answer — whether any volatility instrument appears as an indicator source in any
sleeve — is unanswered. It cannot be answered from a prose description without
reconstructing the strategy, which Step 0 forbids.

---

## What was searched

All searches were content searches for the distinctive identifiers named in the
session prompt, not filename guesses. The markers used were `_t11_bond_baller`,
`_t11_feaver_bear`, `bond_baller`, `feaver`, `_last_label`, `FeaverFrontrunner`,
`DailyRegimeRotation`, `HolyGrail`, `holy_grail`, `_rebalance`, and `_weights`.

| # | Scope | Method | Result |
|---|---|---|---|
| 1 | `/Users/GualyCr/Desktop/tactical-allocation` (working directory) | full recursive file listing, then content grep | Only session scripts `s00a_*`, `s00b_*`, `s00c_*`, `s00e_*`. No sleeve definitions. |
| 2 | `/Users/GualyCr/Desktop` (parent) | directory listing plus recursive `*.py` enumeration | 6 unrelated project directories. No sleeve definitions. |
| 3 | `/Users/GualyCr` (home), all file types | recursive content grep, excluding `.venv`, `.git`, `node_modules`, `Library`, `.Trash`, `site-packages`, `__pycache__`, `.cache`, `.npm` | Markers found only in Claude session transcripts and in `docs/DECISIONS-OPEN-v2.md`. No source. |
| 4 | All 31,375 `*.py` and `*.ipynb` files under `/Users/GualyCr` | explicit file-list grep via `find -print0 \| xargs grep` | **Zero hits** on all six unique markers. |
| 5 | `~/Library/Mobile Documents` (iCloud Drive) | `find` for `*.py` and `*.ipynb` | **Zero** Python or notebook files present. |
| 6 | Git histories of all Desktop repositories | `git log --all` filename and pickaxe search | No sleeve-like file ever committed. `95-delta-strategy-tests` (10 commits), `options-dashboard` (92), `vol-target-qqq` (1), `intraday-shape-spy` (0), `short-vol-reversion` (0), `tactical-allocation` (0). |
| 7 | Archives under Desktop, Downloads, Documents | `find` by extension, enumerated | 15 archives, all unrelated by name (coursework, images, media). **Not expanded.** |
| 8 | `/Users/Shared`, `/opt`, `/usr/local`, `/Applications`, `/private/tmp`, `/private/var/tmp` | content grep, partial | No hits before the sweep exceeded practical time limits. |

### Scope not exhaustively swept

Stated plainly rather than glossed:

- `~/Library` internals (`Caches`, `Containers`, `Application Support`) were not
  exhaustively grepped. Both `grep -r` and even a bare `find` over that tree
  exceeded a ten-minute limit. This is macOS application state, not a plausible
  location for user-authored strategy source, and the one user-facing subtree
  within it, iCloud Drive, was cleared directly and holds no Python files.
- Archive interiors were not expanded.
- No remote host, unmounted volume, or unsynced cloud storage was reachable.

The claim this report supports is therefore: **no Python source defining the
four sleeves exists anywhere in user space on this machine.** Scopes 4 and 5
are the load-bearing ones, and both are complete and negative.

---

## Methodological disclosure: an invalidated first pass

The first four search commands in this session were prefixed with `timeout`,
which is a GNU coreutils binary and **is not present on macOS**. Every one of
them exited 127, produced no output, and was initially read as "no matches
found." All four were false negatives.

The error was caught by running a positive control: grepping for `TQQQ`, a
string known to be present in this repository's own `scripts/s00c_rsi.py`. The
control returned nothing, which is impossible if the search were working. Every
search was then re-run without `timeout`, and the corrected runs are the ones
tabulated above. The corrected runs immediately returned hits that the broken
runs had missed, confirming the diagnosis.

This is recorded because the failure mode produces exactly the answer this
session was at risk of reporting — "not found" — through a mechanism unrelated
to whether the file exists. The conclusion above rests only on the corrected
runs.

---

## What exists in place of source

The sleeve identifiers do appear on this machine, in three places. None is
Python source, and none defines a sleeve.

| Location | Nature | Bearing on Step 0 |
|---|---|---|
| `docs/HANDOFF.md`, lines 23-26 | **Prose description.** Names S1, T11 (FeaverFrontrunner) with `_t11_bond_baller` and `_t11_feaver_bear`, S2 (HolyGrail), S3 (DailyRegimeRotation), and characterizes each sleeve in English. | A description of the sleeves, not an implementation. Nothing to parse, no line numbers, no lookbacks, no data flow. |
| `docs/DECISIONS-OPEN-v2.md`, line 138 | Decision 6.19's label, which contains the string `bond_baller`. | A decision title referencing an internal function name. |
| `~/.claude/projects/.../*.jsonl` | Two Claude session transcripts. One is this session's own log, which contains the 00D prompt text and therefore every marker in it. | Conversation records. Not read. |

`docs/HANDOFF.md` appeared in the working tree during this session and describes
the sleeves as "**Sleeves as supplied**." That phrasing, together with the
session prompt's own statement that the Step 3 audit table "was produced by
manual audit from a prose description of the strategy and has not been verified
against source," is consistent with the strategy having been supplied to this
project as a description rather than as code.

`HANDOFF.md` was inspected by targeted grep for source-location pointers only.
It was not read through, and its prose was not used to enumerate indicators,
because Step 0 forbids reconstructing the strategy from the register.

---

## Flagged against expectations in the register and handoff

Flagged, not reconciled.

### The register is written as though source exists and has been read

Multiple open decisions in `docs/DECISIONS-OPEN-v2.md` reference concrete
implementation detail that only source inspection would yield:

- **6.13** Cascade ordering, "As supplied, report reach rate per step"
- **6.14** Dip ladder ordering, "As supplied"
- **6.16** S2 trend filter series, "TQQQ as supplied"
- **6.17** T11 graded band reading, maximum RSI across panel or the name that crossed first
- **6.18** T11 bear sub-model duplication, "Keep both at 50/50, or collapse"
- **6.19** "Mismatched RSI lookbacks in bond_baller", naming an internal function and two specific lookback periods

"As supplied" and a named internal function imply a supplied artifact that was
read. No such artifact exists on this machine. Either the source is held
somewhere not reachable from here, or these decisions were derived from the
prose description rather than from code. This report does not choose between
those.

### The expected outcome for 2.11 is stated in advance and cannot be verified here

`docs/HANDOFF.md` line 137 records:

> **2.11** Warm-up per indicator. Expected moot pending 00D, since no sleeve
> computes an indicator on a volatility instrument.

The premise — that no sleeve computes an indicator on a volatility instrument —
is the proposition Session 00D was convened to test. It is recorded as an
expectation before the test. This session cannot confirm or refute it. **2.11
remains open, and the "expected moot" status is unverified.**

### The session's stated purpose is not achievable in its current form

The prompt states that Session 00D "Closes decision 2.11 and validates a
signal-source table produced by manual audit." Neither is achievable without the
source. Both remain outstanding.

---

## Incidental finding: the frozen Session 00C pull was modified during this session

Reported because it bears on decision 1.1, the pull-freeze protocol, not because
it is within this session's scope.

A concurrent Session 00E wrote to this repository while Session 00D was running.
New at `14:49:04`: `scripts/s00e_report.py`, `s00e_smh.py`, `s00e_truncate.py`,
`s00e_vote.py`, `docs/HANDOFF.md`, and `outputs/session-00e/`.

Every raw parquet under `data/raw/etf/` and `data/interim/etf-panel.parquet` now
carries an mtime of `14:49:04`, later than the Session 00C pull that created
them. Their contents changed:

| file | 00C as pulled | now |
|---|---|---|
| `data/raw/etf/SPY.parquet` | 7,958 rows, last bar 2026-08-17 | 7,957 rows, last bar 2026-08-14 |
| `data/raw/etf/TQQQ.parquet` | 4,153 rows, last bar 2026-08-17 | 4,152 rows, last bar 2026-08-14 |

This is consistent with a deliberate remediation rather than corruption: the
removed bar is exactly the live intraday print that Session 00C flagged, the
script is named `s00e_truncate.py`, and Session 00E wrote
`outputs/session-00e/pre-truncation-hashes/` and `manifest-truncated.csv`,
indicating the prior hashes were preserved before the change.

The consequence worth stating: the SHA-256 values recorded in Session 00C's
manifest no longer describe the files on disk. Anyone reconciling against that
manifest needs Session 00E's pre-truncation record. Session 00D did not modify
any data file and did not read Session 00C's manifest.

---

## Files written by this session

| file | contents |
|---|---|
| `outputs/session-00d/REPORT.md` | this report |

Nothing else. No scanner, no CSV, no data pull, no modification to any strategy
source, and no commit. The working tree is left dirty.

## Stop

Halted at the Step 0 stop condition.
