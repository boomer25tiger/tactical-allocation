# Session 18s, environment rebuild and repository hygiene

Run 2026-08-19. Maintenance only. No measurement, no grid execution, no
session 18 measurement step, no holdout approached. The 2021-08-01 boundary
under 2.10 is untouched. No file under `data/` was read for content beyond
flag inspection, and no file under `data/` or `outputs/` was deleted or had
its content modified. One rename occurred under `outputs/`, described at step
4, and it preserved content byte for byte.

## Step 1, verify the relocated repository

| check | result |
|---|---|
| working directory | `/Users/GualyCr/Downloads/tactical-allocation`, the Downloads path |
| `git status` | clean |
| `git log --oneline -3` | `9e7aa47`, `a90f352`, `502ca42` |
| `git fsck --no-dangling` | exit 0, no output |
| dataless files outside `.venv` | **0 of 1,740 files** |
| volume | 460 GB size, 400 GB used, 20 GB free, 96 percent capacity |

Neither halt condition fired. The dataless count was taken two ways, by
`st_flags` against `SF_DATALESS` in a full tree walk and by `find -flags
+dataless`, and both returned zero. The relocation off iCloud Drive is
holding.

One correction to the scaffold background. It names `a90f352` as the commit
carrying sessions 16b through 18r. That commit is session 16. `9e7aa47` is the
one carrying 16b, 17, 18 steps 0 through 3, and 18r. Session 18r's report is
consistent with this, since it recorded `HEAD` at `a90f352` while running,
before the commit that superseded it was made.

## Step 2, rebuild the virtual environment

Pre-rebuild versions were recorded before anything was removed. numpy 2.5.2
and pandas 3.0.5 both resolved, under Python 3.13.13. A full 30 package freeze
was captured to `outputs/session-18s/pre-rebuild-freeze.txt`.

The environment was rebuilt with
`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`, the system
framework interpreter, which is the same interpreter and same version recorded
in the old `pyvenv.cfg`. No interpreter inside the removed directory was used.

**No package version diverges.** All 30 post-rebuild versions equal their
pre-rebuild values, and `diff` of the two freezes is empty. All 24 pins
declared in `requirements-session-00a.txt` match what is installed.

| quantity | value |
|---|---|
| packages recorded | 30 |
| declared in `requirements-session-00a.txt` | 24 |
| installed beyond the declared file | 6 |
| versions diverging pre against post | 0 |
| versions differing from a declared pin | 0 |
| interpreter, pre and post | Python 3.13.13 |

Two deviations from the step as written, both reported rather than absorbed.

The scaffold names `requirements.txt`. No such file exists. The project's
requirements file is `requirements-session-00a.txt`, fully pinned at 24
packages.

Installing from that file alone would have dropped 6 packages the environment
carried, being `pytest` with its four transitive dependencies plus `pypdf`.
Dropping `pytest` would leave the test suite unrunnable. The install was
therefore made from the pre-removal freeze, which is a strict superset of the
declared file carrying identical pins for all 24 shared entries. That choice
is what makes the divergence count zero, and it is disclosed here because a
zero produced by construction is weaker evidence than a zero produced by
independent resolution.

The rebuild was staged at `.venv.new` and verified before `.venv` was removed,
so a failed install could not have left the session without an environment.
Once the staged build proved installable from cache, `.venv` was removed and
recreated at its canonical path, and the staging copy was deleted. The end
state is the one the step specifies.

`import numpy, pandas` completes. First run took 14.84 seconds and subsequent
runs 0.29 to 0.40 seconds, which locates the first figure in bytecode
compilation rather than in the indefinite hang seen during session 18.
`src.config` also imports, so `validate()` runs clean under the rebuilt
environment.

Evidence is `outputs/session-18s/environment.csv`, with the two freezes beside
it.

## Step 3, pack the object store

| quantity | before | after |
|---|---|---|
| loose objects | 886 | 24 |
| pack files | 0 | 1 |
| objects in pack | 0 | 862 |
| `.git` size | 202 MB | 197 MB |

`git gc` exited 0. `git fsck --no-dangling` exits 0 after packing with no
output, `HEAD` resolves unchanged at `9e7aa47`, and the working tree is
otherwise as it was. No halt condition fired.

The size reduction is small because the tracked content is mostly already
compressed parquet and npy blobs, which do not delta well.

One correction to the step's premise. The scaffold reasons that zero pack
files means no object has a second copy. Packing does not change that.
Consolidating loose objects into a pack adds per-object CRCs and makes
integrity checking cheaper, and it produces exactly one copy of each object
rather than two. The repository is still single-copy. Only a remote or an
off-machine copy changes that.

## Step 4, mark the partial PBO output

The file was renamed rather than given a status column, since renaming leaves
every existing row unaltered. SHA-256 was taken before and after and is
identical at `4f374b33...f60e2`, so content did not change.

`outputs/session-18/pbo.csv` is now `outputs/session-18/pbo-partial.csv`, moved
with `git mv` so history follows it.

Per-pass status was written to a new sibling file,
`outputs/session-18/pbo-partial-status.csv`, which records what completed and
what did not without touching the artifact it describes.

| S | restriction | status | combinations | PBO |
|---|---|---|---|---|
| 8 | full grid | completed | 70 | 0.1143 |
| 12 | full grid | completed | 924 | 0.1710 |
| 16 | full grid | completed, preregistered primary | 12,870 | 0.1578 |
| 24 | full grid | not run | | |
| 48 | full grid | not run | | |
| 16 | smooth axes only | not run | | |

All three completed passes are full enumerations rather than samples, so the
20,000 combination cap never bound. No PBO figure was recomputed and no
missing pass was run. The three completed values were read out of the existing
file, not recalculated.

## Step 5, register and commit

Register entry **10.1** was appended to `docs/DECISIONS-v3.md` under a new
section, "Custody and environment", carrying the relocation and its reason,
the eviction incident with the 339 of 339 manifest verification, the
environment rebuild with its zero divergence, the packing, and the partial
status of the PBO output. Section 10 was free. No existing register entry was
modified.

`docs/STATE.md` was refreshed. The prior version was written by session 16 and
had been stale since session 16b, still asserting that the grid had not run
and that D24 was open.

One commit was made, covering this session only.

## Step 6, can session 18 resume at step 3

**Yes.** Steps 0 through 2 completed and every artifact they produced reads and
parses. Session 18r verified the 24 grid shards across 121,500 specifications
with no gap and no duplicate in the identifier space, and confirmed the 2,000
specification subsample survives independently of the ephemeral panel because
it was written to `outputs/session-18/` rather than left under
`outputs/session-17/panel/`. **The session 17 grid must not be re-run.**

A resuming session needs four things.

**The corrected positive-control basis for step 1's terminal counter.** The
positive control reproduces session 13.5 exactly on session 13.5's own basis,
which is the synthetic panel measured over the full window from warm-up, as
`scripts/s13_5_diagnostics.py` line 374 measured it. The session 18 prompt
named the primary window instead, on which the figures legitimately differ. A
resuming session that compares against the primary window will see a mismatch
that is an artefact of the basis rather than a defect. The verdict row sits in
`outputs/session-18/reachability.csv` under `table=positive_control`.

**The smooth-axis restriction is small.** Six of the nine searched axes
classify structural and three classify smooth, those three being
`rsi_exhaustion`, `sma_short`, and `vote`. Each carries three values, so the
restriction spans 3 by 3 by 3, which is **27 specifications**. That is small
enough that the restricted PBO will be noisy, and small enough that it costs
almost nothing to run.

**PBO is three passes short.** S equal to 24, S equal to 48, and the
smooth-axis restriction have not run, and the file now says so in its name and
in its status sidecar.

**Reachability switches partway along the oversold axis.** Session 16b
recorded that two T11 PSQ-dip terminals fire zero times at oversold 25 and 30
and then fire at 35, so one third of that axis runs a structurally different
strategy. This is already registered and is repeated here because it bears on
how any grid-wide statistic is read.

## Custody, the item that outranks everything above

The repository has no remote and no off-machine copy. Packing did not change
that and nothing in this session did. The tree survived one near-loss today by
the accident that iCloud eviction is reversible. A disk failure would not be.
A private GitHub repository closes this in roughly five minutes and is the
next thing that should happen.

## Stop condition

Halted after step 6. No grid re-executed, no measurement performed, no holdout
approached, one commit made.
