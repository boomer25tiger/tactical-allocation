- **9.79 the session 29 pre-registration (session 29, 2026-08-23), written BEFORE any
  measurement in that session ran.** The ruling at 9.70 stands, being that describing a
  committed holdout result is permitted while selecting against it is not.

  **The enumerated list**, complete at the time of writing and closed. Phase B checks
  corporate action integrity and runs first, since a defect there invalidates every
  downstream measurement. Phase C runs the two pre-registered nulls over the holdout at
  10,000 replications. Phase D decomposes the holdout against a multi-factor set built
  from instruments already inside the frozen inputs. Phase E puts intervals on the point
  estimates through a stationary block bootstrap. Phase F varies NAV on the D20 curve
  axis. Phase G attributes by instrument and records two corrections to session 28. The
  full enumeration is outputs/session-29/preregistration.csv.

  **Every measurement in the session is a disclosed post-hoc sensitivity under 9.10 with
  its motivation recorded before the run.** The corporate action check exists because
  UVXY and SQQQ reverse split repeatedly inside the holdout span and one unadjusted
  split in a levered or inverse ETP produces a spurious return of several hundred
  percent on a single session. The holdout nulls exist because the primary window's
  significance claims rest on two nulls neither of which has been run on the holdout.
  The multi-factor decomposition exists because the single-factor R-squared of
  0.12086286064363738 leaves 88 percent of holdout variance in the
  0.5637941837318013 alpha by construction. The block bootstrap exists because the
  paper reports point estimates with no interval anywhere and holdout excess kurtosis
  reads 5.223157724383093. The NAV sensitivity exists because the participation cap
  bound on 0.9406631762652705 of holdout transitions against 0.4909274193548387 of
  primary ones on a book compounding from 816441.3464029437 to 1028029775.2491124.

  **Gate B, written before the check.** If any unexplained session above 50 percent
  absolute return is found in a held instrument, the session halts and reports before
  any other phase runs.

  **No canonical value moves whatever any phase returns**, no specification is chosen on
  holdout performance, and the frozen claim set is not amended.

- **9.80 corporate action integrity, GATE B FIRED (session 29, 2026-08-23).** The gate
  was written at 9.79 before the check and requires the session to halt if any
  unexplained session above 50 percent absolute return is found in a held instrument.
  **It fired. Phases C through G1 and G2 did not run.**

  **8 sessions across both windows carry an absolute return above 0.50 in the loaded
  universe.** Each was screened first against the frozen record's own corporate action
  columns and second against the registered underlying, since a large market move is an
  explanation as much as a split is. The registered multiple and benchmark are read from
  src/schedule.py and the volatility funds are screened against the frozen
  constant-maturity thirty-day VIX futures settle at data/interim/vx-cm30.parquet.

  **4 sessions are unexplained in a held instrument, and only one of them is inside the
  holdout.**

  | window | instrument | date | return | proxy return | implied multiple | registered |
  |---|---|---|---|---|---|---|
  | holdout | SOXS | 2026-05-26 | -0.9457524782010531 | SMH 0.04480151130636223 | -21.109834258353413 | -3.0 |
  | primary | SVXY | 2018-02-06 | -0.8295739372998041 | VIX settle -0.2657166607291297 | 3.1220245468366317 | -1.0 |
  | primary | UVXY | 2018-02-05 | 0.6620639534883721 | VIX settle 0.9668799925258098 | 0.6847426346664206 | 2.0 |
  | primary | UVXY | 2020-03-16 | 0.5747728860936407 | VIX settle 0.3167696925125718 | 1.814481939653458 | 1.5 |

  **SOXS on 2026-05-26 is the one that fires the gate.** Its implied multiple is 7.04
  times the registered magnitude with the same sign, which no move in the registered
  underlying produces. The close runs 1159.5 on 2026-05-22 and 62.900001525878906 on 2026-05-26
  while SMH rose 0.04480151130636223 across the same gap, and the Stock Splits column
  reads zero on that session. **The vendor's own adjusted-close column carries the same
  jump**, so the two price paths inside the frozen parquet agree with each other and the
  defect is a missing corporate action record rather than a disagreement between
  columns. The three primary-window sessions are a proxy limitation rather than a data
  defect, the UVXY pair sitting within a factor the proxy's tracking error accounts for
  and the SVXY session carrying the opposite sign, which a fund striking its net asset
  value at a different time from the settle produces.

  **The defect contributes exactly 0.0 to holdout return.** SOXS carries zero weight
  across the whole of 2026-05-18 to 2026-06-05, so the session itself carries no
  position, against a holdout arithmetic return sum of 3.4218690114239116. SOXS is held
  on 252 of the holdout's sessions and appears in src/sleeves.py at line 266 alone,
  inside T11's bear split, which is a position rather than a signal, so the defect
  cannot enter through the signal path either.

  **No instrument's frozen close looks unadjusted at a recorded split.** Across every
  ticker carrying a non-zero Stock Splits entry, the close ratio at each event is
  compared against the reciprocal of the split factor, which is what an unadjusted
  series would show, and no event matches that pattern. The adjustment method does not
  differ between the two windows, since the same loader and the same total-return
  construction run across both on the realized arm. **The designated cell is the
  realized arm**, so the holdout figures carry the issuer's own history rather than a
  reconstruction.

  **The gate's disposition is not decided here.** The defect is reported, the session
  halted, and no series is repaired, since repairing a frozen input is a decision with
  its own hashing and manifest consequences.

- **9.81 three numpy repr wrappers in the session 28 report (session 29, 2026-08-23).**
  The scaffold names two and the document carries three, at
  outputs/session-28/REPORT.md line 203 twice inside the corrections item 12 sentence,
  reading np.float64(1.3817013060244996) and np.float64(0.7381523120792618), and at line
  250 once inside the timing materiality sentence, reading
  np.float64(0.6445126075841863). **The digits are correct and only the wrapper is
  spurious**, so the corrected readings are 1.3817013060244996, 0.7381523120792618 and
  0.6445126075841863.

  The cause is that scripts/s15_lines.py standalone_metrics returns numpy scalars and
  session 28 formatted several of them with the repr conversion inside an f-string note,
  which the emitted CSV carried into the report unchanged. **The session 28 register
  entries carry no wrapper**, since those figures were read from the CSV columns rather
  than from the note text. **outputs/session-28/REPORT.md is NOT edited** and the
  correction stands here. The session 29 prose check screens for the wrapper before
  writing.

  **Session 28's G2 convention mismatch is NOT corrected here**, since restating both
  windows' leave-one-year-out ranges on each convention is a measurement and gate B
  halted the measurement phases. It remains open.
