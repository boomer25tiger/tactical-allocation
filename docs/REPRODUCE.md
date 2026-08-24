# REPRODUCE

What a cloner can run, what they will get, and what they cannot get.

## Environment

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The study ran on Python 3.13.13. `requirements.txt` pins every direct dependency at the version installed when it was generated. **It is generated from the current environment rather than from an authoritative record**, since no authoritative requirements file exists. Session 18s rebuilt the environment from a pre-removal freeze and the register notes at 10.1 that the zero version divergence it reported is partly a construction of that method.

**matplotlib is deliberately absent.** Every figure is drawn through `scripts/s19_svg.py` using the standard library alone, so that adding matplotlib would change the environment the manifest records.

## Data

The frozen inputs are committed. `data/raw/` carries the price, settlement, net-asset-value and rate series the study reads, each hash-verified against a manifest under `outputs/`. No network access is needed to reproduce the canonical figure.

`scripts/s195_verify_inputs.py` checks every frozen input against its manifest and exits non-zero on any mismatch. It is the precondition every measuring session runs.

## The command sequence

```
git clone https://github.com/boomer25tiger/tactical-allocation.git
cd tactical-allocation
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/s195_verify_inputs.py
.venv/bin/python scripts/reproduce.py
```

## Expected output

| quantity | expected | tolerance |
|---|---|---|
| annualised return | 0.521845 | 5e-07 |
| Lo-corrected Sharpe | 1.381701 | 5e-07 |
| sessions | 2472 | exact |

**Bit-identical output is not asserted.** Float reduction order varies with thread count and BLAS version, so the check is a tolerance rather than an equality. `scripts/reproduce.py` exits 0 on reproduction and 1 on any deviation beyond it.

## What a cloner cannot reproduce

- **The ephemeral daily return panel.** Roughly 1.26 gigabytes across sixteen shards were deleted under the four-tier artifact scheme at 9.14, once the tiers above them could carry every downstream figure. The 48-block moment sums under `outputs/session-17/grid/` are the committed evidence the PBO computation actually reads, and the regenerability check verified that the report and its figures regenerate byte-identically after the deletion. Rebuilding the panel is possible from the frozen inputs through `scripts/s17_grid_worker.py` and takes the disk back.
- **Any series a vendor licence does not permit redistributing.** The frozen inputs are committed and the licence question on them is recorded as open. A cloner receives whatever the repository carries and inherits the same open question.
- **Two measurements that were never run.** S equal to 48 of the B1 re-emission at 9.48 and the corrected degradation null at 9.46. Neither is load-bearing, the first setting no endpoint of any quoted range and the second carrying a statistic withdrawn on separate grounds.
- **The synthetic reconstructions under `data/interim/synthetics/`.** They are gitignored and rebuildable through `scripts/s10_build.py`, and the rebuild of SVIX and UVIX reads a network series at run time, so that step is not offline.

## The holdout

`scripts/s13_backtest.py` truncates every loaded series at the session before the 2021-08-01 boundary. The default is unchanged and any context that does not set the single-read environment variable loads nothing past it. The holdout was read once, on 2026-08-22, under the prediction committed at 35466c2131f24e35a5ce7fed13c4ed8c821ca45b, and it is not read again.

