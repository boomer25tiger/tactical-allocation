# scripts/

195 files in one flat directory, which needs explaining. They fall into three
groups and the grouping is derived from the import graph rather than asserted.

## Entry points, being what a reader runs

| file | what it does |
|---|---|
| `reproduce.py` | rebuilds the canonical figure from the frozen inputs and checks it against the expected value inside a stated tolerance. This is the one to run first |
| `s195_verify_inputs.py` | verifies every frozen input against its SHA-256 manifest and exits non-zero on any mismatch. It is the precondition every measuring session runs |
| `verify_prediction_precedes_read.py` | confirms against git that `docs/HOLDOUT-PREDICTION.md` was committed before the holdout was opened. A holdout session runs it as its first step |

## The engine, being what everything else imports

| file | imported by | what it holds |
|---|---|---|
| `s13_backtest.py` | 75 | the account, the fill and cost model, the indicator panel and the holdout truncation |
| `s14_common.py` | 53 | the environment build, the cost arms, the participation cap and the open-to-open panel |
| `s15_lines.py` | 36 | the benchmark ladder and the metric set |
| `s17_common.py` | 25 | the specification grid |
| `s13_runall.py` | 23 | the target ticker set and the run driver |
| `s22_vm.py` | 16 | the machine sampler, reporting compressor size and swap rather than free memory |
| `s17_grid_worker.py` | 11 | the grid shard worker |
| `s19_svg.py` | 4 | deterministic SVG plotting using the standard library alone, since matplotlib is deliberately absent |

## Session drivers, being the remaining 184 files

One or more per session, named `s<session>_<phase>.py`. Each writes its artifacts
to `outputs/session-<n>/` and is not imported by anything. They are kept because
every figure the study reports names the file that produced it, and a reader
checking a figure needs the driver that emitted it to still be there.

The numbering follows the session order in `docs/DECISIONS-v3.md`, so a register
entry dated to a session points at the drivers with that session's prefix.

## Why the layout is flat

Moving these files into subdirectories would break 1,023 path citations across
`docs/` and `outputs/`, and 105 files import them as `scripts.<module>`. Those
citations are the study's evidence trail under the rule at 9.12 that every figure
names its source file, so the paths are load-bearing and the directory stays flat.

## scripts/hw2/, the investor-pitch re-runs

A subdirectory holds the post-read re-runs behind the Columbia B9339 Homework 2
pitch deck: the constant-NAV account, the January 2012 analysis window, the
25% volatility-target fund and its fee model. They import the engine and change
nothing it produced. `scripts/hw2/README.md` gives the run order, and every
result lands in `outputs/hw2/`.
