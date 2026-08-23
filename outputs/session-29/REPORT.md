# Session 29, robustification

2026-08-23. Phase A ran, phase B ran and fired its gate, and the measurement phases did not run. One commit, at phase H.

## Opening

**Gate B fired.** 8 sessions across both windows carry an absolute return above 0.50 in the loaded universe, and 4 are unexplained in a held instrument, of which 1 is inside the holdout. **Phases C, D, E, F, G1 and G2 did not run**, since the gate was written at 9.79 before the check and requires the session to halt before any other phase.

**The holdout defect is SOXS on 2026-05-26**, a return of -0.9457524782010531 with no corporate action in the frozen record and an implied multiple 7.04 times the registered magnitude. **It contributes exactly 0.0 to holdout return**, since SOXS carries zero weight across the whole of 2026-05-18 to 2026-06-05.

**The holdout null exceedance counts, the multi-factor alpha and the NAV capacity curve are not reported, since none was computed.** The gate exists so that the holdout result is not robustified on a series that may carry an unadjusted split, and it did what it was written to do.

## Machine and the positive control

Load average 8.25 one minute, 11.04 five minutes and 7.92 fifteen minutes on 8 cores, compressor 2.942 GiB, swap used 11222.12 MB and swap free 1065.88 MB. **Phase E would have carried the resampling load and did not run, so no memory ceiling was consumed.**

**The standing positive control passed** at 0.5218447451814521 annualised and 1.3817013060244996 Lo-corrected over 2472 sessions, inside the 5e-07 tolerance stated before comparing.

## Phase A, the pre-registration

The session 28 ruling at 9.70 stands. The complete quantity list for phases B through G was written to `outputs/session-29/preregistration.csv` and to the register at 9.79 before any measurement ran, and it is closed.

Every measurement in the session is a disclosed post-hoc sensitivity under 9.10 with its motivation recorded before the run.

| phase | motivation |
|---|---|
| B | UVXY and SQQQ reverse split repeatedly, several times inside the holdout span, and a single unadjusted split in a levered or inverse ETP produces a spurious return of several hundred percent on one session |
| C | the primary window's significance claims rest on the timing-shuffle and turnover-matched nulls clearing at zero exceedances of 10,000 draws, and neither has been run on the holdout |
| D | the static regression against buy-and-hold QQQ carries an R-squared of 0.12086286064363738, so 88 percent of holdout variance is unexplained by construction and lands in the 0.5637941837318013 alpha, while the strategy holds semiconductor, biotechnology, volatility and Treasury instruments none of which is QQQ |
| E | the paper reports point estimates throughout with no interval anywhere, and holdout excess kurtosis at 5.223157724383093 means the iid standard error understates the true one |
| F | the participation cap bound on 0.9406631762652705 of holdout transitions against 0.4909274193548387 of primary ones, on a book compounding from 816441.3464029437 to 1028029775.2491124, so the two windows may not measure the same object |

**Gate B, written before the check.** if any unexplained session above 50 percent absolute return is found in a held instrument, the session halts and reports before any other phase runs. The holdout result cannot be robustified on a series that may carry an unadjusted split.

## Phase B, corporate action integrity

35 instruments in the loaded universe, of which 17 are ever held. Every session above the 0.50 threshold was screened first against the frozen record's own corporate action columns and second against the registered underlying, since a large market move explains a jump as much as a split does. The registered multiple and benchmark come from `src/schedule.py` and the volatility funds are screened against the frozen constant-maturity thirty-day VIX futures settle at `data/interim/vx-cm30.parquet`.

### Every session above 50 percent

| window | instrument | date | return | screen |
|---|---|---|---|---|
| holdout | SOXL | 2025-04-09 | 0.5478788433652935 | EXPLAINED, market move, SMH returned 0.17160325316201197 and the implied multiple is 3.192706625719017 against the registered 3 |
| holdout | SOXS | 2025-04-09 | -0.5597618034878775 | EXPLAINED, market move, SMH returned 0.17160325316201197 and the implied multiple is -3.2619533323147554 against the registered -3 |
| holdout | SOXS | 2026-05-26 | -0.9457524782010531 | UNEXPLAINED, none identifiable |
| holdout | UVXY | 2024-08-05 | 0.583034323123736 | EXPLAINED, market move, the frozen constant-maturity thirty-day VIX futures settle returned 0.42641633471884277 and the implied multiple is 1.3672889044181649 against the registered 1.5 |
| primary | SVXY | 2018-02-06 | -0.8295739372998041 | UNEXPLAINED, none identifiable |
| primary | UVXY | 2018-02-05 | 0.6620639534883721 | UNEXPLAINED, none identifiable |
| primary | UVXY | 2020-03-16 | 0.5747728860936407 | UNEXPLAINED, none identifiable |
| primary | UVXY | 2020-06-11 | 0.5016479894528676 | EXPLAINED, market move, the frozen constant-maturity thirty-day VIX futures settle returned 0.4028978967686947 and the implied multiple is 1.2450995487347152 against the registered 1.5 |

### The four unexplained sessions

| window | instrument | date | return | what the screen shows |
|---|---|---|---|---|
| holdout | SOXS | 2026-05-26 | -0.9457524782010531 | an order of magnitude beyond what any move in the registered underlying produces, which is the signature of an unrecorded corporate action |
| primary | SVXY | 2018-02-06 | -0.8295739372998041 | not attributable by this screen, since a fund whose net asset value strikes at a different time from the proxy's settle can move against it on a single session |
| primary | UVXY | 2018-02-05 | 0.6620639534883721 | within a factor the proxy's own tracking error can account for, so it is consistent with a market move the proxy measures imperfectly |
| primary | UVXY | 2020-03-16 | 0.5747728860936407 | within a factor the proxy's own tracking error can account for, so it is consistent with a market move the proxy measures imperfectly |

**SOXS on 2026-05-26 is the one that fires the gate.** Its close runs 1159.5 on 2026-05-22 and 62.900001525878906 on 2026-05-26 while SMH rose 0.04480151130636223 across the same gap, and the Stock Splits column reads zero on that session. The three primary-window sessions are a proxy limitation rather than a data defect.

### The independent cross-check

| rank | instrument | date | adjusted-close path | deviation from the engine |
|---|---|---|---|---|
| 1 | SOXS | 2026-05-26 | -0.9457524797518353 | 1.550782169346121e-09 |
| 2 | UVXY | 2024-08-05 | 0.583034323123736 | 0.0 |
| 3 | SOXL | 2025-04-09 | 0.54787896700471 | 1.236394164827459e-07 |

**The vendor's own adjusted-close column carries the same jump on SOXS**, so the two price paths inside the frozen parquet agree with each other. The defect is a missing corporate action record rather than a disagreement between columns, which is why an alternative path inside the frozen inputs cannot repair it.

### Split adjustment status

**0 instruments carry a close that looks unadjusted at a recorded split.** 23 carry recorded splits and pass the check, and 12 carry no split entry in the frozen record at all. The check compares the close ratio at each recorded event against the reciprocal of the split factor, which is what an unadjusted series would show.

**The adjustment method does not differ between the two windows.** the same loader and the same total-return construction run across both windows on the realized arm, so the adjustment method does not change at the boundary. What changes is which instruments are available, since the primary window carries sessions on which some loaded tickers had not yet listed.

**The realized arm takes the issuer's own history as the vendor supplies it** and the synthetic arm takes reconstructions validated against live NAV. The designated cell is the realized arm.

### The defect's contribution

**0.0**, against a holdout arithmetic return sum of 3.4218690114239116. SOXS carries zero weight across the whole of 2026-05-18 to 2026-06-05. It is held on 252 of the holdout's sessions and appears in `src/sleeves.py` at line 266 alone, inside T11's bear split, which is a position rather than a signal, so the defect cannot enter through the signal path either.

### The gate

**HALT.** the session halts before any other phase runs.

## Phases C through G, not run

| phase | status |
|---|---|
| C, the holdout nulls | not run, gate B fired |
| D, multi-factor decomposition | not run, gate B fired |
| E, interval estimates | not run, gate B fired |
| F, the NAV sensitivity | not run, gate B fired |
| G1, instrument attribution | not run, gate B fired |
| G2, the leave-one-year-out convention restatement | not run, gate B fired |
| G3, the numpy repr inspection | run, see below |

**G3 was completed and its scope is stated rather than assumed.** G3 reads outputs/session-28/REPORT.md alone. It touches no price series and computes no quantity, so gate B's halt of the measurement phases does not reach it. G1 and G2 are measurements on the holdout series and did not run.

**3 numpy repr wrappers reached the session 28 prose**, and the scaffold names two.

| line | as written | corrected |
|---|---|---|
| 203 | `np.float64(1.3817013060244996)` | 1.3817013060244996 |
| 203 | `np.float64(0.7381523120792618)` | 0.7381523120792618 |
| 250 | `np.float64(0.6445126075841863)` | 0.6445126075841863 |

Scripts/s15_lines.py standalone_metrics returns numpy scalars, and session 28 formatted several of them with the repr conversion inside an f-string note, which the emitted csv then carried into the report unchanged. the session 28 register entries carry no wrapper, since those figures were read from the CSV columns rather than from the note text. `outputs/session-28/REPORT.md` is not edited and the correction stands at 9.81.

**Session 28's G2 convention mismatch is not corrected**, since restating both windows' leave-one-year-out ranges on each convention is a measurement and the gate halted the measurement phases. It remains open.

## What each finding is

| finding | what acting on it would be |
|---|---|
| the SOXS 2026-05-26 defect in a frozen input | a correctness repair, and one with hashing and manifest consequences, so it is reported rather than applied here |
| the defect contributing 0.0 to holdout return | documentation |
| the three primary-window sessions the proxy cannot confirm | documentation, since each is directionally accounted for by the registered underlying or by a strike-time mismatch |
| no instrument's close looking unadjusted at a recorded split | documentation |
| the three numpy repr wrappers | a correctness repair, applied at 9.81 in the register rather than by editing that report |
| phases C through G2 not running | a specification change if the gate is to be relaxed, and a register decision if the defect is to be repaired first |

**No recommendation is made on any of them.**

## What remains before the paper

**The gate's disposition is the open question and it is not decided here.** Repairing a frozen input changes a hashed file, its manifest entry and the input-integrity check every session runs, so it is a decision rather than an edit. Leaving it unrepaired and disclosing it is the alternative, and the measured contribution of 0.0 to holdout return bears on that choice without settling it.

**Six measurement phases remain uncomputed**, being the holdout nulls, the multi-factor decomposition, the interval estimates, the NAV sensitivity, the instrument attribution and the leave-one-year-out convention restatement. Each was pre-registered at 9.79 and none was run.

Outside this session, S equal to 48 of the B1 re-emission remains open at 9.48 and the corrected degradation null remains unrun at 9.46, neither load-bearing. **No claim in docs/CLAIMS.md is added or amended, docs/HOLDOUT-PREDICTION.md is not edited, and no figure is drawn.**

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count above the limit is 0.

| reading | before the commit | expected delta |
|---|---|---|
| working tree, KiB | 832292 | +0 |
| git directory, KiB | 208428 | +121 or less |
| free space, GiB | 20.10 | 0.00 to -0.01 |

The commit touches 14 files totalling 321181 bytes on disk, of which 12 files and 124370 bytes are new. **Nothing is read after the commit**, under 9.62.

## Register

9.79 the pre-registration and the quantity list, written before any measurement. 9.80 corporate action integrity and the gate outcome. 9.81 the three numpy repr wrappers in the session 28 report.

## Artifacts

- `outputs/session-29/preregistration.csv`
- `outputs/session-29/corporate-actions.csv`
- `outputs/session-29/instrument-attribution.csv`
- `outputs/session-29/size.csv`

The remaining pre-registered artifacts were not written, since the phases that would have written them did not run.

