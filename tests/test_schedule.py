"""Tests for src/schedule.py: contiguity, coverage, lookups, qualifiers."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.schedule import FUND_SCHEDULE, Period, fund_terms  # noqa: E402

SEVENTEEN = {"TQQQ", "TECL", "SOXL", "SQQQ", "TECS", "SOXS", "SPXL", "FAS",
             "LABU", "QLD", "PSQ", "SH", "UVXY", "SVIX", "SVXY", "UVIX",
             "BTAL"}


def test_all_seventeen_funds_present():
    assert set(FUND_SCHEDULE) == SEVENTEEN


def test_periods_contiguous_nonoverlapping_covering():
    """Every fund's periods run inception -> present with no gap and no
    overlap: each period starts exactly one calendar day after the prior
    period ends, and only the final period is open-ended."""
    for fund, periods in FUND_SCHEDULE.items():
        assert periods, fund
        for prev, nxt in zip(periods, periods[1:]):
            assert prev.end is not None, f"{fund}: interior period open-ended"
            assert nxt.start == prev.end + timedelta(days=1), (
                f"{fund}: gap or overlap between {prev.end} and {nxt.start}"
            )
        assert periods[-1].end is None, f"{fund}: final period must be open"
        assert all(p.start < (p.end or date.max) for p in periods)


def test_uvxy_svxy_multiple_boundary():
    """Old terms govern through the 2018-02-27 close; new terms from 02-28."""
    assert fund_terms("UVXY", "2018-02-27").multiple == 2.0
    assert fund_terms("UVXY", "2018-02-28").multiple == 1.5
    assert fund_terms("SVXY", "2018-02-27").multiple == -1.0
    assert fund_terms("SVXY", "2018-02-28").multiple == -0.5


def test_soxl_benchmark_boundary_carries_qualifier():
    a = fund_terms("SOXL", "2021-08-24")
    b = fund_terms("SOXL", "2021-08-25")
    assert a.benchmark.startswith("PHLX") and not a.on_or_about
    assert b.benchmark.startswith("ICE") and b.on_or_about, (
        "the filing's 'on or about' must survive into the data"
    )


def test_fas_three_periods():
    assert fund_terms("FAS", "2020-06-01").benchmark.startswith("Russell 1000 Financial Services")
    mid = fund_terms("FAS", "2022-05-02")
    assert "40 Act 15/22.5" in mid.benchmark and mid.on_or_about
    assert fund_terms("FAS", "2023-01-03").benchmark.startswith("Financials Select")
    assert all(p.multiple == 3.0 for p in FUND_SCHEDULE["FAS"])


def test_btal_has_no_multiple():
    p = fund_terms("BTAL", "2020-01-02")
    assert p.multiple is None
    assert "Anti-Beta" in p.benchmark


def test_constant_funds_single_period():
    for f in ("TQQQ", "QLD", "SQQQ", "PSQ", "SH", "SPXL", "TECL", "TECS",
              "LABU", "SVIX", "UVIX", "BTAL"):
        assert len(FUND_SCHEDULE[f]) == 1, f


def test_pre_inception_raises():
    with pytest.raises(ValueError, match="no terms"):
        fund_terms("TQQQ", "2009-12-31")


def test_unknown_fund_raises():
    with pytest.raises(KeyError):
        fund_terms("KMLM", "2022-01-03")


def test_matches_session08_csv():
    """The module must agree with the frozen session 08 schedule on every
    changed fund's boundary dates and multiples."""
    import pandas as pd

    csv = pd.read_csv(ROOT / "outputs" / "session-08" / "fund-schedule.csv")
    for _, row in csv.iterrows():
        fund = row["fund"]
        start = row["period_start"]
        p = fund_terms(fund, start)
        assert str(p.start) == start, (fund, start)
        if row["multiple"] not in ("(none)",):
            assert p.multiple == float(row["multiple"]), (fund, start)
