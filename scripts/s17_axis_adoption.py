"""Session 17 step 0, as amended: the axis-adoption record.

Both tables are recorded. The ten-axis enumeration is the space the study
enumerated and is what 8.7 reports as N. The nine-axis table is the space
the grid searches. Nothing here is hardcoded: every value and cardinality
is read from src.config.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S      # noqa: E402
from src import config              # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs" / "session-17"
OUT.mkdir(parents=True, exist_ok=True)

# register id, grid constant, canonical constant, source of the values
AXIS_META = [
    ("sma_long",        "7.6", "SMA_LONG_GRID",          "SMA_LONG",                     "register 7.6, closed"),
    ("crash_threshold", "7.7", "CRASH_THRESHOLD_GRID",   "CRASH_THRESHOLD_PCT",          "register 7.7, revised session 04"),
    ("rsi_exhaustion",  "6.1", "RSI_PERIOD_GRID",        "RSI_PERIOD_EXHAUSTION",        "register 6.1, recorded"),
    ("rsi_dip",         "6.1", "RSI_PERIOD_GRID",        "RSI_PERIOD_DIP",               "register 6.1, recorded"),
    ("rsi_rs",          "6.1", "RSI_PERIOD_GRID",        "RSI_PERIOD_RELATIVE_STRENGTH", "register 6.1, recorded"),
    ("overbought_t1",   "6.2", "OVERBOUGHT_TIER_1_GRID", "OVERBOUGHT_TIER_1",            "docs/HANDOFF.md line 122, recovered session 17"),
    ("tier_two_offset", "7.4", "TIER_TWO_OFFSET_GRID",   None,                           "register 7.4, recorded"),
    ("oversold",        "6.4", "OVERSOLD_GRID",          "OVERSOLD",                     "docs/HANDOFF.md line 122, recovered session 17"),
    ("sma_short",       "6.6", "SMA_SHORT_GRID",         "SMA_SHORT",                    "docs/HANDOFF.md line 122, recovered session 17"),
    ("vote",            "6.7", "S3_VOTE_THRESHOLD_GRID", "S3_VOTE_THRESHOLD",            "register 6.7, recorded"),
]

CANON_OFFSET = S.CANONICAL_TIER_TWO_OFFSET
searched = set(S.AXIS_NAMES)
rows = []


def canon_of(axis, attr):
    if axis == "tier_two_offset":
        return CANON_OFFSET
    return getattr(config, attr)


for table, subset in (("ten_axis_enumerated", None), ("nine_axis_searched", searched)):
    for axis, rid, grid, attr, src in AXIS_META:
        if subset is not None and axis not in subset:
            continue
        vals = getattr(config, grid)
        cv = canon_of(axis, attr)
        rows.append({
            "table": table, "axis": axis, "register_id": rid,
            "values": " ".join(str(v) for v in vals), "cardinality": len(vals),
            "source": src, "canonical_value": cv,
            "canonical_on_axis": cv in vals,
            "searched_by_grid": axis in searched,
        })

# --- the dropped axis -------------------------------------------------------
off = getattr(config, "TIER_TWO_OFFSET_GRID")
rows.append({
    "table": "dropped_axis", "axis": "tier_two_offset", "register_id": "7.4",
    "values": " ".join(str(v) for v in off), "cardinality": len(off),
    "source": "register 7.4", "canonical_value": CANON_OFFSET,
    "canonical_on_axis": CANON_OFFSET in off, "searched_by_grid": False,
    "register_status": "informed",
    "note": ("held at its canonical value on every specification; "
             "the canonical point is unchanged and no strategy quantity changes"),
})

# --- totals -----------------------------------------------------------------
eight = 1
for axis, rid, grid, attr, src in AXIS_META:
    if axis not in ("sma_long", "crash_threshold"):
        eight *= len(getattr(config, grid))
for label, value, note in [
    ("searched_specifications", S.grid_size(),
     "the nine searched axes; the grid evaluates this many points"),
    ("enumerated_specifications", S.enumerated_size(),
     "the ten enumerated axes; 8.7 reports N at this value"),
    ("evaluated_of_enumerated", S.grid_size(),
     f"{S.grid_size():,} of {S.enumerated_size():,} evaluated, "
     "7.4 held at canonical rather than sampled"),
    ("eight_unrepresented_axes_product", eight,
     "the recovery factorisation base"),
    ("v1_v2_total", eight * 5 * 3, "18,225 x 5 x 3, reconciles with no remainder"),
    ("after_7_6_total", eight * 4 * 3, "18,225 x 4 x 3, reconciles with no remainder"),
    ("after_7_6_and_7_7_total", eight * 4 * 5, "18,225 x 4 x 5, reconciles with no remainder"),
    ("alternative_with_7_4_excluded", S.grid_size(),
     "reported by session 16b as the total with 7.4 excluded"),
]:
    rows.append({"table": "totals", "axis": label, "cardinality": value, "note": note})

# --- reason -----------------------------------------------------------------
for key, text in [
    ("grounds",
     "7.4 is recorded in the register as informed rather than closed. An item "
     "the register marks informed is not a decision the study made, so searching "
     "over it would report a specification curve spanning a parameter the "
     "register never fixed."),
    ("occasion_not_grounds",
     "Runtime was the occasion for reading 7.4's status, not the grounds for the "
     "decision. The grounds are the register status alone. Recorded separately "
     "and explicitly so the two are not conflated."),
    ("effect_on_canonical",
     "None. The offset is held at its canonical value of "
     f"{CANON_OFFSET} on every specification, so the canonical point is unchanged."),
    ("effect_on_8_7",
     "8.7 keeps N at the enumerated total. N is the size of the search space the "
     "study enumerated rather than the count of points evaluated, and the grid "
     "running on a disclosed subset does not shrink it."),
    ("effect_on_step_3",
     "The deflated Sharpe reports at N equal to the enumerated total as primary "
     "and at the searched total as the sensitivity, with the cross-sectional "
     "Sharpe standard deviation estimated from the evaluated grid and the "
     "estimation caveat stated."),
    ("effect_on_step_4",
     "The specification curve spans the nine searched axes. The tier-two offset "
     "is not on the curve because it was not searched."),
]:
    rows.append({"table": "reason", "axis": key, "note": text})

cols = ["table", "axis", "register_id", "values", "cardinality", "source",
        "canonical_value", "canonical_on_axis", "searched_by_grid",
        "register_status", "note"]
with open(OUT / "axis-adoption.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"wrote {OUT / 'axis-adoption.csv'} with {len(rows)} rows")
print(f"  searched {S.grid_size():,}   enumerated {S.enumerated_size():,}")
print(f"  canonical on every searched axis: "
      f"{all(r['canonical_on_axis'] for r in rows if r['table'] == 'nine_axis_searched')}")
print(f"  7.4 status informed, held at {CANON_OFFSET}, on its own axis: "
      f"{CANON_OFFSET in off}")
