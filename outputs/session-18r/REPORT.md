# Session 18r — storage damage assessment

Run 2026-08-19. Diagnostic only. Nothing deleted, nothing moved, nothing
committed, no object store written, no grid re-executed, no holdout approached.
Evidence: `outputs/session-18r/damage-assessment.csv`.

## Headline, step 4 first as instructed

**Every frozen input verifies against its manifest. There are no mismatches,
no read failures, and no absences.**

347 files under `data/` were hashed and compared against the eight acquisition
manifests, with the 1.14 truncation manifest at
`outputs/session-00e/manifest-truncated.csv` superseding the acquisition hash
for the 39 files it touched. 339 files carry a manifest row and all 339 match.
The remaining 8 are derived interim VX artifacts that were never manifested.

| set | files | verdict |
|---|---|---|
| data/raw/etf | 44 | all match |
| data/raw/vx | 268 | all match |
| data/raw/nav | 2 | all match |
| data/raw/index | 1 | all match |
| data/raw/rates | 1 | all match |
| data/interim/synthetics | 19 | all match |

`data/raw` carried **zero** dataless files at any point in this session. The 11
evicted files under `data/` were all derived synthetics under
`data/interim/synthetics`, and 9 of those were still flagged dataless at hash
time, materialised on read, and hashed correctly. The irreplaceable layer was
never at risk.

## Step 1, volume and sync state

The volume reads 494 GB with 429 GB used and 26 GB free at 95 percent capacity,
against 19 GB free and 96 percent when this session opened. No local Time
Machine snapshots exist, so nothing is reclaimable from that source.

`bird`, `cloudd` and `fileproviderd` are all running and the CloudDocs container
reported `caught-up` at 14:30:47, moving to `needs-sync-up|in-sync-down` while
serving the reads below.

**The download queue was active rather than stalled.** 242 files outside `.venv`
carried the dataless flag when the session opened, being 200 under `.git`, 23
under `outputs`, 11 under `data`, 4 under `scripts`, 2 under `.pytest_cache`, 1
under `src` and 1 under `docs`. Every one of them was fetched successfully.
Cold single-file latency was the constraint rather than bandwidth, with the
worst observed fetch taking 92 seconds for a 256 KB file, while 12-way parallel
reads sustained 34.1 files per minute once warmed. A further 3,751 dataless
files sit under `.venv`, which is reconstructible from requirements and is not
data loss, though it is why an earlier `import numpy` blocked indefinitely.

## Step 2, whole-tree read test

Every file outside `.venv` was read in full with `os.read` in 4 MB chunks and
the byte count compared against `stat`, so a short read or an I/O error surfaces
rather than passing silently.

| class | count |
|---|---|
| fully readable | 1,630 |
| readable but shorter than stat size | 0 |
| zero bytes read with non-zero stat size | 0 |
| read error | 0 |
| genuinely zero-byte file | 1 |

The single zero-byte file is `src/__init__.py`, which is zero bytes by
construction and is not damage.

For `.git/objects` specifically, 779 files were tested, 37 of which still
carried the dataless flag when they were read, and all 779 read complete.

## Step 3, the grid output

| artifact | shards | result |
|---|---|---|
| moment shards | 8 | all read full, parse to (15187 or 15188, 96) float64, 121,500 total |
| metric shards | 8 | all read full, parse to (15187 or 15188, 72) float64, 121,500 total |
| specification index | 8 | all read full, ids 0 to 121,499 |
| block-sizes.npy | 1 | read full |

The index carries **0 duplicates and 0 gaps** and covers the identifier space
contiguously. Moment shards are 48 blocks by 2 moments, being the sum and the
sum of squares of excess returns, with the per-block count held once in
`block-sizes.npy`. The first metric row carries a single NaN in
`time_to_recovery_sessions`, which 8.11 specifies for a specification that does
not recover inside the window, so it is expected rather than damage.

Every session 18 artifact reads full, being `subsample-ids.npy`,
`subsample-returns.npy` at 19.8 MB, `spec-index-augmented.csv` at 30.5 MB,
`inventory.csv`, `reachability.csv`, `additivity-check.csv` and
`axis-classification.json`. `reachability.csv` and `additivity-check.csv` were
both among the evicted set earlier and both recovered intact.

All eight panel shards are also now materialised at 1.1 GB total, having been
five-of-eight dataless when the session opened.

**The grid does not need re-running.** The condition stated in the session
scaffold is met in full, since every moment shard, the specification index and
every metric shard read fully and parse. The 2,000-specification subsample
survives independently of the panel, since it was written to
`outputs/session-18/` rather than left inside `outputs/session-17/panel/`.

## Step 5, git object store

`git fsck --no-dangling` exits 0 with no output, run after the step 2
materialisation reads completed. The earlier `fatal: mmap failed: Operation
canceled` was a cancelled iCloud fetch during a mapped read, and it does not
recur once the objects are resident.

All 754 objects reachable from `refs/heads/main` read successfully with zero
failures. The store holds 779 loose objects and **zero pack files**, so no
object has a second copy anywhere. `HEAD` and `refs/heads/main` both resolve to
`a90f352f6dbf7621ecf6ac0e973524e28c5cecb4`, the session 16 commit. The working
tree shows 21 entries, being 6 modified and 15 untracked, the latter having
grown from 13 because this session's `outputs/session-18/` and the session 18
scripts are new.

## Step 6, recoverability verdict

**Intact.** All 316 frozen raw inputs and all 19 synthetics, verified by hash.
All 24 grid shards covering 121,500 specifications. The session 18 artifacts
including the subsample. The git object store and every reachable object. The
working tree. All eight panel shards, which is more than was required.

**Damaged.** Nothing.

**Unrecoverable.** Nothing.

The eviction was fully reversible. Every file that read as empty during session
18 was dataless rather than destroyed, and reading it materialised it from
iCloud with content that hashes correctly where a manifest exists. The session
18 halt was the right call on the evidence available at the time, since a read
returning zero bytes is indistinguishable from destruction without the dataless
flag, but the conclusion drawn then was wrong and this session supersedes it.

**The session 17 grid must not be re-run.** The evidence is step 3, being that
all eight moment shards, all eight metric shards and all eight index shards read
fully and parse at the expected dtype and width, and that the identifier space
is covered contiguously with no duplicate and no gap.

**A backup should exclude two paths.** `outputs/session-17/panel/` at 1.1 GB is
ephemeral by design and is scheduled for deletion at session 18 step 8, and
`.venv` at 200 MB is reconstructible from requirements. Excluding both leaves
roughly 400 MB, which is the set worth copying, against 1.7 GB for the whole
tree.

## Recommended order of recovery operations, none performed here

1. Move the repository off `~/Desktop` to a path outside iCloud Drive, since
   that is what exposed it, and confirm Optimize Mac Storage stays off.
2. Take a copy of the roughly 400 MB set excluding the panel and `.venv`, since
   there is no git remote and no pack redundancy, so the local copy is the only
   copy of 779 loose objects.
3. Establish a git remote, or at minimum a second physical copy, before any
   further session runs.
4. Recreate `.venv` from requirements rather than relying on the 3,751 evicted
   files under it, since a partially materialised environment produces the
   indefinite import hangs seen in this session.
5. Only then resume session 18 at its step 3, since steps 0 through 2 completed
   and their outputs are intact.

Two repairs look obvious and are reported without being performed, being the
`.venv` rebuild and the relocation off iCloud Drive.

## Stop condition

Halted after step 6. Nothing deleted, nothing moved, nothing committed, no
object store written, no grid re-executed, no holdout approached. Two files
written, being `outputs/session-18r/damage-assessment.csv` and this report.
