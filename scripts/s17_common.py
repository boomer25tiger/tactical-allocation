"""Session 17 grid support: indicator sharing and the risk-free prefix.

Two performance changes, neither of which alters a registered quantity.
Both are validated against the canonical designated cell before use.

1. `fat_signals` builds one ArmSignals carrying every RSI period and every
   SMA length the grid axes reach, rather than only the three periods and
   two lengths the current config names. `State` resolves the period and
   length through `config` at call time, so a specification change needs
   no indicator rebuild. The arrays are the same arrays the per-spec
   build would produce.

2. `rf_factor_array` precomputes the per-session cash growth factor that
   `run_account` otherwise recovers with a pandas label slice on every
   session. The factor depends only on the calendar and the rate series,
   never on the specification. Bit-exactness against the label slice is
   asserted, not assumed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.s13_backtest as bt
from src import config
from src.indicators import sma, wilder_rsi


def grid_periods_and_lengths():
    periods = sorted(set(config.RSI_PERIOD_GRID))
    lengths = sorted(set(config.SMA_LONG_GRID) | set(config.SMA_SHORT_GRID))
    return periods, lengths


def fat_signals(panel, calendar):
    """ArmSignals carrying every indicator variant the grid axes reach."""
    sig = bt.ArmSignals(panel, calendar)
    periods, lengths = grid_periods_and_lengths()
    for t, tf in panel.frames.items():
        tr = tf.tr_index.reindex(calendar)
        for n in periods:
            if t not in sig.rsi.setdefault(n, {}):
                sig.rsi[n][t] = wilder_rsi(tr, n).to_numpy()
        for n in lengths:
            if t not in sig.smas.setdefault(n, {}):
                sig.smas[n][t] = sma(tr, n).to_numpy()
    return sig


def rf_factor_array(calendar) -> np.ndarray:
    """Per-session cash growth factor, indexed by calendar position.

    Position i carries the product of the daily factors over
    (calendar[i-1], calendar[i]], matching run_account's label slice.
    Position 0 and every position before the first traded session carry
    1.0 and are never read.
    """
    rf = bt.risk_free_daily_factors(bt.load_risk_free_series())
    rf = rf.loc[:bt.HOLDOUT_LAST_DATE]
    vals = rf.to_numpy()
    idx = rf.index.to_numpy()
    cal = calendar.to_numpy()
    out = np.ones(len(cal), dtype=float)
    hi = np.searchsorted(idx, cal, side="right")
    lo = np.searchsorted(idx, cal + np.timedelta64(1, "D"), side="left")
    for i in range(1, len(cal)):
        a, b = lo[i - 1], hi[i]
        if b > a:
            out[i] = float(np.prod(vals[a:b]))
    return out


def assert_rf_exact(calendar) -> float:
    """Reproduce the label slice on every session and require equality."""
    rf = bt.risk_free_daily_factors(bt.load_risk_free_series())
    rf = rf.loc[:bt.HOLDOUT_LAST_DATE]
    arr = rf_factor_array(calendar)
    worst = 0.0
    prev = None
    for i in range(config.WARMUP_SESSIONS, len(calendar)):
        d = calendar[i]
        if prev is not None:
            ref = float(rf.loc[prev + pd.Timedelta(days=1): d].prod())
            worst = max(worst, abs(ref - arr[i]))
        prev = d
    assert worst == 0.0, f"rf factor array not bit-exact, worst {worst:.3e}"
    return worst


# ---------------------------------------------------------------------------
# Grid enumeration (session 17 step 0 axes, registered order)
# ---------------------------------------------------------------------------

# Axis order is fixed here and never changed: the specification index is a
# mixed-radix encoding of this tuple, so any reordering renumbers every
# specification and invalidates the subsample draw.
#
# Session 17 amendment: NINE searched axes. 7.4, the tier-two offset, is
# recorded in the register as informed rather than closed, so it is not a
# decision the study made and is not searched. It is held at its canonical
# value on every specification by CANONICAL_TIER_TWO_OFFSET below, captured
# at import before apply_spec can mutate OVERBOUGHT_TIER_2.
CANONICAL_TIER_TWO_OFFSET = config.OVERBOUGHT_TIER_2 - config.OVERBOUGHT_TIER_1

AXES = (
    ("sma_long",        "SMA_LONG_GRID",          "SMA_LONG"),
    ("crash_threshold", "CRASH_THRESHOLD_GRID",   "CRASH_THRESHOLD_PCT"),
    ("rsi_exhaustion",  "RSI_PERIOD_GRID",        "RSI_PERIOD_EXHAUSTION"),
    ("rsi_dip",         "RSI_PERIOD_GRID",        "RSI_PERIOD_DIP"),
    ("rsi_rs",          "RSI_PERIOD_GRID",        "RSI_PERIOD_RELATIVE_STRENGTH"),
    ("overbought_t1",   "OVERBOUGHT_TIER_1_GRID", "OVERBOUGHT_TIER_1"),
    ("oversold",        "OVERSOLD_GRID",          "OVERSOLD"),
    ("sma_short",       "SMA_SHORT_GRID",         "SMA_SHORT"),
    ("vote",            "S3_VOTE_THRESHOLD_GRID", "S3_VOTE_THRESHOLD"),
)

# Enumerated but NOT searched: recorded so the report can state both totals.
UNSEARCHED_AXES = (
    ("tier_two_offset", "TIER_TWO_OFFSET_GRID", "7.4", "informed"),
)

AXIS_NAMES = tuple(a[0] for a in AXES)
AXIS_VALUES = tuple(tuple(getattr(config, a[1])) for a in AXES)
AXIS_CARD = tuple(len(v) for v in AXIS_VALUES)


def grid_size() -> int:
    n = 1
    for c in AXIS_CARD:
        n *= c
    return n


def enumerated_size() -> int:
    n = grid_size()
    for _name, grid, _id, _status in UNSEARCHED_AXES:
        n *= len(getattr(config, grid))
    return n


def spec_at(index: int) -> tuple:
    """Mixed-radix decode: specification index to one value per searched axis."""
    out = []
    for card in reversed(AXIS_CARD):
        out.append(index % card)
        index //= card
    pos = tuple(reversed(out))
    return tuple(AXIS_VALUES[k][p] for k, p in enumerate(pos))


def index_of(values: tuple) -> int:
    idx = 0
    for k, v in enumerate(values):
        idx = idx * AXIS_CARD[k] + AXIS_VALUES[k].index(v)
    return idx


def canonical_values() -> tuple:
    return (config.SMA_LONG, config.CRASH_THRESHOLD_PCT,
            config.RSI_PERIOD_EXHAUSTION, config.RSI_PERIOD_DIP,
            config.RSI_PERIOD_RELATIVE_STRENGTH, config.OVERBOUGHT_TIER_1,
            config.OVERSOLD, config.SMA_SHORT, config.S3_VOTE_THRESHOLD)


def apply_spec(values: tuple) -> None:
    """Bind one specification onto config. Every searched axis takes its grid
    value; the unsearched 7.4 offset is re-derived at its canonical level."""
    for k, (_name, _grid, attr) in enumerate(AXES):
        setattr(config, attr, values[k])
    config.OVERBOUGHT_TIER_2 = (values[AXIS_NAMES.index("overbought_t1")]
                                + CANONICAL_TIER_TWO_OFFSET)


# ---------------------------------------------------------------------------
# Risk-free-per-session cache
# ---------------------------------------------------------------------------

def install_rf_cache():
    """Memoise bt.rf_per_session on the index it is called with.

    The series depends only on the index, never on the specification, and
    the grid calls it once per metric evaluation on a fixed window. The
    cached value is checked against a fresh computation on installation.
    """
    original = bt.rf_per_session
    if getattr(original, "_s17_cached", False):
        return original
    cache = {}

    def cached(index):
        key = (index[0], index[-1], len(index))
        hit = cache.get(key)
        if hit is None:
            hit = original(index)
            cache[key] = hit
        return hit

    cached._s17_cached = True
    cached._original = original
    bt.rf_per_session = cached
    return original
