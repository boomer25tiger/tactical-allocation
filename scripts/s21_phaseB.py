"""Session 21 phase B. Canonical axis provenance, traced from the register."""
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s17_common as S      # noqa: E402
OUT = ROOT / "outputs" / "session-21"
CV = dict(zip(S.AXIS_NAMES, S.canonical_values()))

# state, one of
#   before   fixed before any comparison on that axis
#   after    fixed after a comparison on that axis, meaning tuned on that axis
#   repair   fixed by a correctness repair, which is not tuning
#   unknown  provenance not establishable from the register
AX = [
 ("sma_long", "6.5 / 6.6", "no session recorded",
  "before",
  "The register reads 6.5 / 6.6 closed, SMA long 200, short 20, with no measurement "
  "cited and no session attributed. The value is the source value carried across, and "
  "no comparison across long-SMA values is recorded anywhere before the closure. The "
  "ordering rests on the register's phrasing rather than on a dated record, which is "
  "recorded rather than smoothed over."),
 ("crash_threshold", "6.10, with 7.7 fixing the swept levels", "session 09",
  "after",
  "The only axis whose canonical value moved after measurement. Source carried -12 "
  "hardcoded. Session 03 measured all three estimator forms failing and -12 sitting at "
  "the 9.1st percentile, and session 04 closed an absolute threshold at -10. Session 09 "
  "RE-CLOSED at -15, citing session 06's measurement that -12 fired on 37.9 percent of "
  "bear-reached sessions against four times its unconditional rate. The register marks "
  "it [A], a stipulation interpolating the correction convention at 10 and the "
  "bear-market convention at 20. Measurements on this axis preceded the fixing, so the "
  "axis is tuned in the ordering sense, and what those measurements compared was "
  "estimator form and firing rate rather than performance across levels."),
 ("rsi_exhaustion", "6.1", "no session recorded", "before",
  "6.1 closed, three function-tied RSI periods all 14 canonical. The session 01 "
  "call-site mapping resolved which accessor each source call used, which is a "
  "structural resolution rather than a comparison across periods. No comparison across "
  "RSI periods is recorded before the closure."),
 ("rsi_dip", "6.1", "no session recorded", "before", "As rsi_exhaustion, same entry."),
 ("rsi_rs", "6.1", "no session recorded", "before", "As rsi_exhaustion, same entry."),
 ("overbought_t1", "6.2 / 6.3 / 6.4", "no session recorded", "before",
  "6.2 closed at overbought tier one 70, phrased as every source per-name exception "
  "collapsed, so the value is source-derived. The AXIS enumeration moved later, being "
  "marked discretionary by session 16b and then taking the HANDOFF range 60 to 80 at "
  "session 17, but the canonical value was 70 throughout and no comparison across tier "
  "one values preceded its fixing. This is the axis occupying the canonical's worst "
  "stratum at a PBO of 0.235509 and controlling the terminal returning UVXY at full "
  "sleeve weight, and its provenance is nonetheless clean in the ordering sense."),
 ("oversold", "6.4", "no session recorded", "before",
  "Closed in the same entry as 6.2 at oversold 30, source-derived, no comparison "
  "recorded before the closure."),
 ("sma_short", "6.5 / 6.6", "no session recorded", "before",
  "Closed in the same entry as sma_long at short 20, source-derived."),
 ("vote", "6.7", "session 00E", "before",
  "6.7 is recorded as INFORMED rather than closed, with the value canonical at 3 of 4. "
  "A leave-one-out clarification ran in session 00E and its artifact, "
  "outputs/session-00e/vote-leave-one-out.csv, carries flip counts, flip fractions and "
  "bull-state fractions under two threshold treatments. It measures how removing a "
  "voter changes the state series, not performance across vote thresholds, so no "
  "performance comparison across this axis preceded the fixing. The status remains "
  "informed rather than closed, which is a separate weakness from tuning."),
]
rows = []
for axis, reg, sess, state, note in AX:
    rows.append({"table": "axis", "axis": axis, "canonical_value": CV[axis],
                 "register_item": reg, "fixing_session": sess, "state": state,
                 "note": note})
counts = {}
for _, _, _, st, _ in AX:
    counts[st] = counts.get(st, 0) + 1
for st in ("before", "after", "repair", "unknown"):
    rows.append({"table": "state_count", "axis": st, "canonical_value": counts.get(st, 0)})
tuned = [a for a, _, _, st, _ in AX if st == "after"]
rows.append({"table": "verdict", "axis": "axes_fixed_before_comparison",
             "canonical_value": counts.get("before", 0)})
rows.append({"table": "verdict", "axis": "axes_tuned", "canonical_value": len(tuned),
             "note": " ".join(tuned)})
rows.append({"table": "verdict", "axis": "percentile_claim_support",
             "note": "Eight of the nine axes carry a canonical value fixed before any "
                     "comparison on that axis, so the rank of 6,834 of 121,500 on the "
                     "Lo-corrected Sharpe and 8,237 on annualised return is supported on "
                     "those eight. It is weakened on crash_threshold alone, where the "
                     "value moved twice after measurement and settled at a stipulation. "
                     "The weakening is reported per axis rather than as a single verdict, "
                     "and no canonical value is changed."})
rows.append({"table": "caveat", "axis": "dating",
             "note": "Seven of the nine closures carry no session attribution in the "
                     "register, so their ordering relative to any measurement rests on "
                     "the entries' source-derived phrasing rather than on a dated record. "
                     "That is a documentation gap rather than evidence of tuning."})
with open(OUT / "canonical-provenance.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "axis", "canonical_value",
                                       "register_item", "fixing_session", "state", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
for a, _, _, st, _ in AX:
    print(f"  {a:<18} {str(CV[a]):>7}  {st}")
print(f"\nbefore {counts.get('before',0)}, after {counts.get('after',0)}, "
      f"repair {counts.get('repair',0)}, unknown {counts.get('unknown',0)}")
print(f"wrote {OUT/'canonical-provenance.csv'} with {len(rows)} rows")
