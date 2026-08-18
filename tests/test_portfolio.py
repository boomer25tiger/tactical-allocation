"""Unit tests for src/portfolio.py. All input is hand-constructed."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.portfolio import (  # noqa: E402
    Decision,
    PortfolioTracker,
    apply_gross_cap,
    joint_label,
    merge,
    run_daily,
    sleeve_label,
)

B = config.SLEEVE_BUDGET


# ---------------------------------------------------------------------------
# Labels (5.1)
# ---------------------------------------------------------------------------

def test_sleeve_label_formats():
    assert sleeve_label({}) == "CASH"
    assert sleeve_label({"TQQQ": 1.0}) == "100%TQQQ"
    assert sleeve_label({"TQQQ": 0.5, "SOXL": 0.5}) == "50%TQQQ+50%SOXL"
    assert sleeve_label({"TECL": 1 / 3, "SOXL": 1 / 3, "SVIX": 1 / 3}) == (
        "33%TECL+33%SOXL+33%SVIX"
    )


def test_sleeve_label_preserves_insertion_order():
    assert sleeve_label({"A": 0.5, "B": 0.5}) != sleeve_label({"B": 0.5, "A": 0.5})


def test_joint_label_order_and_shape():
    lbl = joint_label({"UVXY": 1.0}, {}, {"TQQQ": 1.0}, {})
    assert lbl == "T10=100%UVXY|T11=CASH|S2=100%TQQQ|S3=CASH"


def test_label_distinguishes_all_terminal_weight_levels():
    """Whole-percent rounding must separate 1, 1/2, 1/3 — the discrete set
    the sleeves emit — so the no-trade band is inert for real transitions."""
    labels = {sleeve_label({"X": f}) for f in (1.0, 0.5, 1 / 3)}
    assert len(labels) == 3


# ---------------------------------------------------------------------------
# Merge and cap (5.3, 5.4)
# ---------------------------------------------------------------------------

def test_merge_scales_by_sleeve_budget():
    m = merge({"TQQQ": 1.0}, {}, {}, {})
    assert m == {"TQQQ": pytest.approx(B)}


def test_merge_sums_overlapping_tickers():
    m = merge({"TQQQ": 1.0}, {"TQQQ": 1 / 3}, {"TQQQ": 1.0}, {"SOXL": 1.0})
    assert m["TQQQ"] == pytest.approx(B * (1 + 1 / 3 + 1))
    assert m["SOXL"] == pytest.approx(B)


def test_full_agreement_reaches_but_does_not_exceed_cap():
    m = merge({"TQQQ": 1.0}, {"TQQQ": 1.0}, {"TQQQ": 1.0}, {"TQQQ": 1.0})
    capped, gross, truncated = apply_gross_cap(m)
    assert gross == pytest.approx(config.GROSS_CAP)
    assert not truncated
    assert capped["TQQQ"] == pytest.approx(config.GROSS_CAP)


def test_cap_binds_proportionally_on_synthetic_overweight():
    over = {"A": 0.8, "B": 0.4}  # gross 1.2 > 1.0
    capped, gross, truncated = apply_gross_cap(over)
    assert truncated and gross == pytest.approx(1.2)
    assert capped["A"] == pytest.approx(0.8 / 1.2)
    assert capped["B"] == pytest.approx(0.4 / 1.2)
    assert sum(capped.values()) == pytest.approx(config.GROSS_CAP)
    # proportionality preserved
    assert capped["A"] / capped["B"] == pytest.approx(2.0)


def test_cap_no_op_below_cap():
    w = {"A": 0.5}
    capped, gross, truncated = apply_gross_cap(w)
    assert capped == w and gross == 0.5 and not truncated


# ---------------------------------------------------------------------------
# Tracker (5.1 ordering, 5.2 drift)
# ---------------------------------------------------------------------------

def test_first_step_emits_targets():
    d = PortfolioTracker().step("d1", {"TQQQ": 1.0}, {}, {}, {})
    assert d.changed and d.targets == {"TQQQ": pytest.approx(B)}


def test_unchanged_label_emits_nothing_however_long():
    """Drift with no calendar reset: 100 sessions, one emission."""
    tr = PortfolioTracker()
    decisions = [tr.step(f"d{i}", {"TQQQ": 1.0}, {}, {}, {}) for i in range(100)]
    assert decisions[0].changed
    assert all(not d.changed and d.targets is None for d in decisions[1:])


def test_transition_emits_again():
    tr = PortfolioTracker()
    tr.step("d1", {"TQQQ": 1.0}, {}, {}, {})
    d2 = tr.step("d2", {"UVXY": 1.0}, {}, {}, {})
    assert d2.changed and d2.targets == {"UVXY": pytest.approx(B)}


def test_label_change_in_one_sleeve_suffices():
    tr = PortfolioTracker()
    tr.step("d1", {"TQQQ": 1.0}, {"QQQ": 0.5, "TQQQ": 0.5}, {}, {})
    d = tr.step("d2", {"TQQQ": 1.0}, {"QQQ": 1.0}, {}, {})
    assert d.changed


def test_short_circuit_skips_summation(monkeypatch):
    """The 5.1 ordering: merge must not run on an unchanged label."""
    import src.portfolio as P

    calls = {"n": 0}
    real = P.merge

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)

    monkeypatch.setattr(P, "merge", counting)
    tr = P.PortfolioTracker()
    tr.step("d1", {"TQQQ": 1.0}, {}, {}, {})
    tr.step("d2", {"TQQQ": 1.0}, {}, {}, {})
    tr.step("d3", {"TQQQ": 1.0}, {}, {}, {})
    assert calls["n"] == 1


def test_label_built_from_pre_cap_weights():
    """Truncation must not feed the label (5.3 after 5.1)."""
    tr = PortfolioTracker()
    d = tr.step("d1", {"A": 3.0}, {"B": 3.0}, {}, {})  # synthetic gross 1.5
    assert d.cap_truncated
    assert "300%A" in d.label  # label reflects the sleeve dict, not the cap
    assert sum(d.targets.values()) == pytest.approx(config.GROSS_CAP)


# ---------------------------------------------------------------------------
# Driver (5.1 all-four-every-date, 2.11 warm-up)
# ---------------------------------------------------------------------------

def _counting_sleeves(counter):
    def fn(name):
        def f(date, state):
            counter[name] = counter.get(name, 0) + 1
            return {"TQQQ": 1.0}
        return f
    return {n: fn(n) for n in ("T10", "T11", "S2", "S3")}


def test_driver_calls_all_four_every_post_warmup_date():
    counter = {}
    cal = [f"d{i}" for i in range(10)]
    out = list(run_daily(cal, lambda d: None,
                         sleeves=_counting_sleeves(counter), warmup_sessions=4))
    assert len(out) == 6
    # label never changes after the first, yet every sleeve ran every date
    assert all(counter[n] == 6 for n in ("T10", "T11", "S2", "S3"))
    assert sum(d.changed for d in out) == 1


def test_driver_skips_warmup_entirely():
    counter = {}
    cal = [f"d{i}" for i in range(5)]
    out = list(run_daily(cal, lambda d: None,
                         sleeves=_counting_sleeves(counter), warmup_sessions=5))
    assert out == [] and counter == {}


def test_driver_default_warmup_comes_from_config():
    import inspect

    sig = inspect.signature(run_daily)
    assert sig.parameters["warmup_sessions"].default == config.WARMUP_SESSIONS


def test_driver_propagates_pairwise_raise():
    def raising(date, state):
        raise NotImplementedError("pairwise comparison ... t10_weights:XLK>TREND")

    fns = {"T10": raising, "T11": lambda d, s: {}, "S2": lambda d, s: {},
           "S3": lambda d, s: {}}
    with pytest.raises(NotImplementedError, match="XLK>TREND"):
        list(run_daily(["d0"], lambda d: None, sleeves=fns, warmup_sessions=0))


def test_decision_is_frozen():
    d = Decision("d", "L", False, None, None, False)
    with pytest.raises(Exception):
        d.changed = True
