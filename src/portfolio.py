"""Merge and label across the four sleeves.

Decision 5.1. All four weight functions execute on every evaluated date
regardless of whether the label matches. The label is the concatenation
across all four sleeves at whole-percent rounding of sleeve budget; the
equality test is on the joint string; and the short circuit occurs after the
calls and before the summation. Structure here makes that ordering explicit:
`step` receives the four already-computed sleeve dicts, builds the label,
and returns before `merge` runs when the label is unchanged.

Decision 5.3. Gross cap at config.GROSS_CAP with proportional truncation if
it binds. Truncation happens after the label is built, so a truncated
composition never feeds back into the label.

Decision 5.2. Drift is permitted and positions reset on label transition
only; there is no calendar reset. The tracker therefore emits targets only
on a transition, and emits nothing — no rebalance back to target — however
many sessions pass without one.

No-trade band implied by 5.1's rounding: a sleeve component changes the
label only when its rounded whole-percent value moves, so the band is half a
percent of sleeve budget on either side, which at a 25 percent budget is
±0.125 percent of portfolio value per component. Because every sleeve
terminal in src/sleeves.py emits weights from the discrete set {1, 1/2,
1/3} (rounded 100, 50, 33), no two distinct terminal states round to the
same label, and the band is inert in practice: transitions are exactly
composition changes. The band would bind only if a sleeve ever emitted
near-continuous weights.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Iterator

from src import config
from src.sleeves import s2_weights, s3_weights, t10_weights, t11_weights

__all__ = [
    "sleeve_label",
    "joint_label",
    "merge",
    "apply_gross_cap",
    "Decision",
    "PortfolioTracker",
    "run_daily",
    "SLEEVE_ORDER",
]

# Sleeve order fixed by source's merge (L301-317) and label (L308).
SLEEVE_ORDER = ("T10", "T11", "S2", "S3")

WeightFn = Callable[[object, object], dict[str, float]]
DEFAULT_SLEEVES: dict[str, WeightFn] = {
    "T10": t10_weights,
    "T11": t11_weights,
    "S2": s2_weights,
    "S3": s3_weights,
}


def sleeve_label(w: dict[str, float]) -> str:
    """One sleeve's label at whole-percent rounding of sleeve budget (5.1).

    Format follows source L306-307: "33%TECL+33%SOXL+33%SVIX", or "CASH" for
    the empty dict. Insertion order of the weight dict is preserved, which is
    deterministic because every sleeve builds its dict in literal order.
    Python's round applies (banker's rounding at exact halves); sleeve
    terminals never sit at a half percent, so the tie rule is never exercised
    by the current sleeves.
    """
    if not w:
        return "CASH"
    return "+".join(f"{round(frac * 100):.0f}%{t}" for t, frac in w.items())


def joint_label(w10, w11, w2, w3) -> str:
    parts = zip(SLEEVE_ORDER, (w10, w11, w2, w3))
    return "|".join(f"{name}={sleeve_label(w)}" for name, w in parts)


def merge(w10, w11, w2, w3) -> dict[str, float]:
    """Scale each sleeve by its budget (5.4) and sum overlapping tickers."""
    out: dict[str, float] = {}
    for w in (w10, w11, w2, w3):
        for ticker, frac in w.items():
            out[ticker] = out.get(ticker, 0.0) + frac * config.SLEEVE_BUDGET
    return out


def apply_gross_cap(weights: dict[str, float]) -> tuple[dict[str, float], float, bool]:
    """Proportional truncation when gross exceeds the cap (5.3).

    Returns (weights, gross_before, truncated). With four sleeves at 25
    percent each emitting at most 1.0, gross cannot exceed 1.0, so the cap
    binds only under synthetic input; it is implemented, not dead-coded,
    because 5.3 specifies it.
    """
    gross = sum(weights.values())
    if gross <= config.GROSS_CAP + 1e-9:
        return dict(weights), gross, False
    scale = config.GROSS_CAP / gross
    return {t: v * scale for t, v in weights.items()}, gross, True


@dataclass(frozen=True)
class Decision:
    """One evaluated session."""

    date: object
    label: str
    changed: bool
    targets: dict[str, float] | None  # None = hold, drift continues (5.2)
    gross_before_cap: float | None
    cap_truncated: bool


class PortfolioTracker:
    """Holds the last label; emits targets on transitions only (5.1, 5.2)."""

    def __init__(self) -> None:
        self.last_label: str | None = None

    def step(self, date, w10, w11, w2, w3) -> Decision:
        label = joint_label(w10, w11, w2, w3)

        # Short circuit: after the four calls (the dicts are already in
        # hand), before summation (merge has not run).
        if label == self.last_label:
            return Decision(date, label, False, None, None, False)

        merged = merge(w10, w11, w2, w3)
        capped, gross, truncated = apply_gross_cap(merged)
        self.last_label = label
        return Decision(date, label, True, capped, gross, truncated)


def run_daily(
    calendar: Iterable,
    state_for: Callable[[object], object],
    sleeves: dict[str, WeightFn] | None = None,
    warmup_sessions: int = config.WARMUP_SESSIONS,
) -> Iterator[Decision]:
    """Drive the tracker across a calendar.

    The first `warmup_sessions` sessions are skipped entirely: no sleeve is
    permitted to emit a weight during warm-up (2.11). After warm-up all four
    weight functions are called on every session (5.1), whether or not the
    label subsequently matches. NotImplementedError from a pairwise site
    propagates — it is the marker of the open half of 2.11, not an error to
    swallow.

    This driver is exercised only against synthetic input in this session.
    """
    fns = sleeves or DEFAULT_SLEEVES
    tracker = PortfolioTracker()
    for i, date in enumerate(calendar):
        if i < warmup_sessions:
            continue
        state = state_for(date)
        yield tracker.step(
            date,
            fns["T10"](date, state),
            fns["T11"](date, state),
            fns["S2"](date, state),
            fns["S3"](date, state),
        )
