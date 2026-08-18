"""Unit tests for src/sleeves.py.

Every state is hand-constructed synthetic input. Each branch of each sleeve
is driven to each terminal state. No data under data/ is touched and no
strategy return, allocation against real prices, or performance statistic is
computed.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.sleeves import (  # noqa: E402
    PAIRWISE_SITES,
    S3_VOTES,
    T10_CASCADE,
    T11_PANEL,
    s2_weights,
    s3_weights,
    t10_weights,
    t11_weights,
)

DATE = "2020-06-01"  # sleeves receive a date; synthetic states ignore it
TREND = config.TREND_SIGNAL_SERIES
T1 = config.OVERBOUGHT_TIER_1
T2 = config.OVERBOUGHT_TIER_2
OS = config.OVERSOLD


@dataclass
class FakeState:
    """Dict-backed IndicatorState. Anything unset is unavailable (None)."""

    exhaustion: dict = field(default_factory=dict)
    dip: dict = field(default_factory=dict)
    rs: dict = field(default_factory=dict)
    prices: dict = field(default_factory=dict)
    smas: dict = field(default_factory=dict)      # (ticker, length) -> value
    trailing: dict = field(default_factory=dict)  # (ticker, horizon) -> pct
    avail: set = field(default_factory=set)

    def rsi_exhaustion(self, t):
        return self.exhaustion.get(t)

    def rsi_dip(self, t):
        return self.dip.get(t)

    def rsi_rs(self, t):
        return self.rs.get(t)

    def price(self, t):
        return self.prices.get(t)

    def sma(self, t, n):
        return self.smas.get((t, n))

    def trailing_return_pct(self, t, horizon):
        return self.trailing.get((t, horizon))

    def available(self, t):
        return t in self.avail


def neutral(d: dict, tickers, value=50.0):
    for t in tickers:
        d.setdefault(t, value)


def t10_state(**kw) -> FakeState:
    """A T10 state that reaches the trend comparison and loses it (bear)."""
    s = FakeState(**kw)
    neutral(s.exhaustion, T10_CASCADE)
    neutral(s.dip, ("TQQQ", "SOXL", "SPXL", "LABU"))
    s.rs.setdefault("XLK", 40.0)
    s.rs.setdefault(TREND, 60.0)
    return s


def t11_bull_state(**kw) -> FakeState:
    s = FakeState(**kw)
    neutral(s.exhaustion, T11_PANEL)
    neutral(s.dip, ("TQQQ", "SPY"))
    s.prices.setdefault("SPY", 110.0)
    s.smas.setdefault(("SPY", config.SMA_LONG), 100.0)
    s.rs.setdefault("XLK", 60.0)
    s.rs.setdefault(TREND, 40.0)
    return s


def t11_bear_state(**kw) -> FakeState:
    """SPY below its long SMA; both sub-models reach clean terminals."""
    s = FakeState(**kw)
    neutral(s.exhaustion, T11_PANEL)
    neutral(s.dip, ("TQQQ", "SPY", "PSQ"))
    s.prices.setdefault("SPY", 90.0)
    s.smas.setdefault(("SPY", config.SMA_LONG), 100.0)
    s.prices.setdefault("TQQQ", 110.0)
    s.smas.setdefault(("TQQQ", config.SMA_SHORT), 100.0)
    s.rs.setdefault("TLT", 40.0)
    s.rs.setdefault("PSQ", 50.0)
    s.rs.setdefault("AGG", 60.0)
    s.rs.setdefault("SH", 40.0)
    s.rs.setdefault("IEF", 40.0)
    s.rs.setdefault("BND", 40.0)
    s.rs.setdefault("QQQ", 60.0)
    return s


def s2_state(**kw) -> FakeState:
    s = FakeState(**kw)
    s.prices.setdefault("TQQQ", 100.0)
    s.smas.setdefault(("TQQQ", config.SMA_LONG), 110.0)   # below gate
    s.smas.setdefault(("TQQQ", config.SMA_SHORT), 90.0)   # above short SMA
    neutral(s.exhaustion, ("TQQQ",))
    neutral(s.dip, ("TQQQ", "SOXL"))
    s.rs.setdefault("SQQQ", 40.0)
    s.rs.setdefault("BSV", 60.0)
    return s


def s3_state(bull_votes=4, **kw) -> FakeState:
    s = FakeState(**kw)
    for i, t in enumerate(S3_VOTES):
        s.prices.setdefault(t, 110.0 if i < bull_votes else 90.0)
        s.smas.setdefault((t, config.SMA_LONG), 100.0)
    neutral(s.exhaustion, S3_VOTES)
    neutral(s.dip, ("QQQ", "SMH"))
    return s


def assert_budget(w: dict):
    assert all(v > 0 for v in w.values())
    if w:
        assert sum(w.values()) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# T10
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", T10_CASCADE)
def test_t10_cascade_fires_each_name_at_tier1(name):
    s = t10_state()
    s.exhaustion[name] = T1 + 0.5
    assert t10_weights(DATE, s) == {"UVXY": 1.0}


def test_t10_cascade_does_not_fire_at_tier1_exactly():
    s = t10_state()
    s.exhaustion["QQQE"] = float(T1)  # strict inequality, as in source
    assert "UVXY" not in t10_weights(DATE, s)


@pytest.mark.parametrize(
    "ticker,target", [("TQQQ", "TECL"), ("SOXL", "SOXL"), ("SPXL", "SPXL"), ("LABU", "LABU")]
)
def test_t10_dips_route_in_cascade_order(ticker, target):
    s = t10_state()
    s.dip[ticker] = OS - 1.0
    assert t10_weights(DATE, s) == {target: 1.0}


def test_t10_dip_order_tqqq_takes_precedence():
    s = t10_state()
    s.dip["TQQQ"] = OS - 1.0
    s.dip["SOXL"] = OS - 1.0
    assert t10_weights(DATE, s) == {"TECL": 1.0}


def test_t10_labu_dip_threshold_is_oversold_not_25():
    """Source used 25 for LABU; spec collapses it to OVERSOLD."""
    s = t10_state()
    s.dip["LABU"] = OS - 0.5  # 29.5: below 30, above source's 25
    assert t10_weights(DATE, s) == {"LABU": 1.0}


def test_t10_xlk_wins_risk_on_with_svix_available():
    s = t10_state()
    s.rs["XLK"], s.rs[TREND] = 60.0, 40.0
    s.avail.add("SVIX")
    w = t10_weights(DATE, s)
    assert w == {"TECL": pytest.approx(1 / 3), "SOXL": pytest.approx(1 / 3),
                 "SVIX": pytest.approx(1 / 3)}
    assert_budget(w)


def test_t10_xlk_wins_falls_back_to_svxy_when_svix_unavailable():
    s = t10_state()
    s.rs["XLK"], s.rs[TREND] = 60.0, 40.0
    w = t10_weights(DATE, s)
    assert "SVXY" in w and "SVIX" not in w


def test_t10_trend_wins_bear_terminal():
    w = t10_weights(DATE, t10_state())  # XLK 40 < TREND 60
    assert w == {"SQQQ": 0.5, "TLT": 0.5}
    assert_budget(w)


def test_t10_unavailable_cascade_reads_false_and_falls_through():
    s = t10_state()
    del s.exhaustion["QQQE"]  # unavailable, must not fire or raise
    assert t10_weights(DATE, s) == {"SQQQ": 0.5, "TLT": 0.5}


def test_t10_pairwise_unavailable_raises_naming_site():
    s = t10_state()
    del s.rs[TREND]
    with pytest.raises(NotImplementedError, match="t10_weights:XLK>TREND"):
        t10_weights(DATE, s)


def test_t10_no_permissive_fallback():
    """Unready trend must raise, never default to risk-on (substitution 3)."""
    s = t10_state()
    s.rs[TREND] = None
    s.avail.add("SVIX")
    with pytest.raises(NotImplementedError):
        t10_weights(DATE, s)


# ---------------------------------------------------------------------------
# T11 main branch
# ---------------------------------------------------------------------------

def test_t11_tier2_full_uvxy():
    s = t11_bull_state()
    s.exhaustion["SPY"] = T2 + 1.0
    assert t11_weights(DATE, s) == {"UVXY": 1.0}


def test_t11_tier1_only_partial_hedge():
    s = t11_bull_state()
    s.exhaustion["IOO"] = (T1 + T2) / 2  # 75: above tier 1, below tier 2
    w = t11_weights(DATE, s)
    assert w == {"UVXY": pytest.approx(1 / 3), "BIL": pytest.approx(1 / 3),
                 "BTAL": pytest.approx(1 / 3)}
    assert_budget(w)


def test_t11_tier2_reachable_from_any_tier1_name():
    """Tier 2 disjunction is evaluated across the panel, not per name."""
    s = t11_bull_state()
    s.exhaustion["SPY"] = T1 + 0.5   # trips tier 1
    s.exhaustion["XLF"] = T2 + 0.5   # a different name trips tier 2
    assert t11_weights(DATE, s) == {"UVXY": 1.0}


def test_t11_tqqq_dip():
    s = t11_bull_state()
    s.dip["TQQQ"] = OS - 1.0
    assert t11_weights(DATE, s) == {"TQQQ": 1.0}


def test_t11_spy_dip_routes_to_spxl():
    s = t11_bull_state()
    s.dip["SPY"] = OS - 1.0
    assert t11_weights(DATE, s) == {"SPXL": 1.0}


def test_t11_bull_xlk_wins_long_basket():
    w = t11_weights(DATE, t11_bull_state())
    assert w == {"TECL": pytest.approx(1 / 3), "SOXL": pytest.approx(1 / 3),
                 "TQQQ": pytest.approx(1 / 3)}


def test_t11_bull_trend_wins_but_below_own_sma_stays_long():
    s = t11_bull_state()
    s.rs["XLK"], s.rs[TREND] = 40.0, 60.0
    s.prices[TREND] = 90.0
    s.smas[(TREND, config.SMA_SHORT)] = 100.0
    w = t11_weights(DATE, s)
    assert "TECL" in w and "TECS" not in w


def test_t11_bull_trend_wins_above_own_sma_short_basket():
    s = t11_bull_state()
    s.rs["XLK"], s.rs[TREND] = 40.0, 60.0
    s.prices[TREND] = 110.0
    s.smas[(TREND, config.SMA_SHORT)] = 100.0
    w = t11_weights(DATE, s)
    assert w == {"TECS": pytest.approx(1 / 3), "SOXS": pytest.approx(1 / 3),
                 "SQQQ": pytest.approx(1 / 3)}


def test_t11_trend_sma_unavailable_reads_false_routes_short():
    """Trend won RSI; its own SMA is unavailable -> threshold reads false ->
    the discount does not apply and the short basket is taken (1.9)."""
    s = t11_bull_state()
    s.rs["XLK"], s.rs[TREND] = 40.0, 60.0
    s.prices[TREND] = 90.0  # SMA missing from state
    w = t11_weights(DATE, s)
    assert "TECS" in w


def test_t11_spy_sma_unavailable_reads_false_routes_bear():
    s = t11_bear_state()
    del s.smas[("SPY", config.SMA_LONG)]
    w = t11_weights(DATE, s)
    assert set(w) <= {"QQQ", "PSQ", "TQQQ", "SQQQ", "QLD", "BTAL"}


def test_t11_pairwise_unavailable_raises_naming_site():
    s = t11_bull_state()
    del s.rs["XLK"]
    with pytest.raises(NotImplementedError, match="t11_weights:XLK>TREND"):
        t11_weights(DATE, s)


# ---------------------------------------------------------------------------
# T11 bear sub-models
# ---------------------------------------------------------------------------

def test_t11_bear_5050_distinct_tickers():
    s = t11_bear_state()
    # bond_baller: TLT 40 < PSQ 50 -> not QQQ; TQQQ above short SMA; PSQ dip
    # 50 not < 30; AGG 60 > SH 40 -> TQQQ.
    # feaver_bear: no crash (thr unavailable) -> same tail -> TQQQ.
    w = t11_weights(DATE, s)
    assert w == {"TQQQ": 1.0}  # both picked TQQQ: sums to 1.0 on one ticker


def test_t11_bear_sums_when_submodels_agree():
    s = t11_bear_state()
    s.rs["TLT"] = 60.0  # bond_baller -> QQQ; feaver unaffected -> TQQQ
    w = t11_weights(DATE, s)
    assert w == {"QQQ": 0.5, "TQQQ": 0.5}
    assert_budget(w)


def test_t11_bond_baller_psq_dip_threshold_is_30_not_35():
    s = t11_bear_state()
    s.rs["TLT"] = 40.0
    s.dip["PSQ"] = OS + 2.0  # 32: source 35 would fire, spec 30 must not
    w = t11_weights(DATE, s)
    assert w == {"TQQQ": 1.0}  # AGG>SH path, not the PSQ dip
    s.dip["PSQ"] = OS - 1.0   # 29: fires under spec
    w = t11_weights(DATE, s)
    assert w.get("PSQ", 0) >= 0.5


def test_t11_bear_tqqq_below_short_sma_ief_psq_leg():
    s = t11_bear_state()
    s.prices["TQQQ"] = 80.0  # below short SMA -> IEF/PSQ leg
    s.rs["IEF"], s.rs["PSQ"] = 60.0, 40.0
    assert t11_weights(DATE, s) == {"PSQ": 1.0}
    s.rs["IEF"] = 30.0
    assert t11_weights(DATE, s) == {"SQQQ": 1.0}


def crash_key():
    return (config.CRASH_REFERENCE_TICKER, config.CRASH_HORIZON_SESSIONS)


def test_t11_crash_branch_bnd_wins_qld():
    s = t11_bear_state()
    s.trailing[crash_key()] = config.CRASH_THRESHOLD_PCT - 5.0  # below: fires
    s.rs["BND"], s.rs["QQQ"] = 60.0, 40.0
    w = t11_weights(DATE, s)
    assert w.get("QLD", 0) == pytest.approx(0.5)  # feaver half


def test_t11_crash_branch_qqq_wins_btal():
    s = t11_bear_state()
    s.trailing[crash_key()] = config.CRASH_THRESHOLD_PCT - 5.0
    w = t11_weights(DATE, s)  # BND 40 < QQQ 60
    assert w.get("BTAL", 0) == pytest.approx(0.5)


def test_t11_crash_above_threshold_does_not_fire():
    s = t11_bear_state()
    s.trailing[crash_key()] = config.CRASH_THRESHOLD_PCT + 5.0  # -5: above
    w = t11_weights(DATE, s)
    assert "QLD" not in w and "BTAL" not in w


def test_t11_crash_exactly_at_threshold_does_not_fire():
    """Strict less-than, matching source's qqq_60d < -12 shape."""
    s = t11_bear_state()
    s.trailing[crash_key()] = config.CRASH_THRESHOLD_PCT  # exactly -10.0
    w = t11_weights(DATE, s)
    assert "QLD" not in w and "BTAL" not in w


def test_t11_crash_horizon_unavailable_reads_false():
    """The boundary where the horizon has not yet accumulated: a threshold
    test with an unavailable input reads false under 1.9."""
    s = t11_bear_state()  # trailing left unset -> unavailable
    w = t11_weights(DATE, s)
    assert "QLD" not in w and "BTAL" not in w


def test_t11_crash_input_is_percent_not_decimal():
    """Unit tripwire: a decimal-form -15 percent (-0.15) sits far above the
    percent-form threshold -10.0 and must NOT fire."""
    s = t11_bear_state()
    s.trailing[crash_key()] = -0.15
    w = t11_weights(DATE, s)
    assert "QLD" not in w and "BTAL" not in w


@pytest.mark.parametrize("kill,site", [
    ("TLT", "t11_bond_baller:TLT>PSQ"),
    ("AGG", "t11_bond_baller:AGG>SH"),
])
def test_t11_bond_baller_pairwise_raises(kill, site):
    s = t11_bear_state()
    del s.rs[kill]
    with pytest.raises(NotImplementedError, match=site):
        t11_weights(DATE, s)


def test_t11_feaver_bnd_pairwise_raises_inside_crash():
    s = t11_bear_state()
    s.trailing[crash_key()] = config.CRASH_THRESHOLD_PCT - 5.0
    del s.rs["BND"]
    with pytest.raises(NotImplementedError, match="t11_feaver_bear:BND>QQQ"):
        t11_weights(DATE, s)


def test_t11_ief_pairwise_raises_naming_first_caller():
    s = t11_bear_state()
    s.prices["TQQQ"] = 80.0
    del s.rs["IEF"]
    with pytest.raises(NotImplementedError, match="t11_bond_baller:IEF>PSQ"):
        t11_weights(DATE, s)


# ---------------------------------------------------------------------------
# S2
# ---------------------------------------------------------------------------

def test_s2_gate_clean_tqqq():
    s = s2_state()
    s.prices["TQQQ"] = 120.0  # above long SMA
    assert s2_weights(DATE, s) == {"TQQQ": 1.0}


def test_s2_gate_overbought_uvxy_at_tier1():
    s = s2_state()
    s.prices["TQQQ"] = 120.0
    s.exhaustion["TQQQ"] = T1 + 1.0  # source used 79; spec tier 1
    assert s2_weights(DATE, s) == {"UVXY": 1.0}


def test_s2_dips():
    s = s2_state()
    s.dip["TQQQ"] = OS - 1.0
    assert s2_weights(DATE, s) == {"TECL": 1.0}
    s = s2_state()
    s.dip["SOXL"] = OS - 1.0
    assert s2_weights(DATE, s) == {"SOXL": 1.0}


def test_s2_defensive_split_both_ways():
    s = s2_state()
    s.prices["TQQQ"] = 80.0  # below short SMA
    s.rs["SQQQ"], s.rs["BSV"] = 60.0, 40.0
    assert s2_weights(DATE, s) == {"SQQQ": 1.0}
    s.rs["SQQQ"] = 30.0
    assert s2_weights(DATE, s) == {"BSV": 1.0}


def test_s2_fallthrough_tqqq():
    assert s2_weights(DATE, s2_state()) == {"TQQQ": 1.0}


def test_s2_gate_unavailable_reads_false():
    s = s2_state()
    del s.smas[("TQQQ", config.SMA_LONG)]
    assert s2_weights(DATE, s) == {"TQQQ": 1.0}  # falls through, not gate


def test_s2_pairwise_raises_naming_site():
    s = s2_state()
    s.prices["TQQQ"] = 80.0
    del s.rs["BSV"]
    with pytest.raises(NotImplementedError, match="s2_weights:SQQQ>BSV"):
        s2_weights(DATE, s)


# ---------------------------------------------------------------------------
# S3
# ---------------------------------------------------------------------------

def test_s3_bull_clean_split():
    w = s3_weights(DATE, s3_state(bull_votes=4))
    assert w == {"TQQQ": 0.5, "SOXL": 0.5}
    assert_budget(w)


def test_s3_three_votes_suffice():
    assert s3_weights(DATE, s3_state(bull_votes=3)) == {"TQQQ": 0.5, "SOXL": 0.5}


def test_s3_two_votes_do_not():
    assert s3_weights(DATE, s3_state(bull_votes=2)) == {}


def test_s3_overbought_uvix_when_available():
    s = s3_state(bull_votes=4)
    s.exhaustion["SMH"] = T1 + 1.0  # source used 72; spec tier 1
    s.avail.add("UVIX")
    assert s3_weights(DATE, s) == {"UVIX": 1.0}


def test_s3_overbought_uvxy_when_uvix_unavailable():
    s = s3_state(bull_votes=4)
    s.exhaustion["SMH"] = T1 + 1.0
    assert s3_weights(DATE, s) == {"UVXY": 1.0}


def test_s3_bear_dip_triggers_soxl():
    s = s3_state(bull_votes=1)
    s.dip["QQQ"] = OS - 1.0
    assert s3_weights(DATE, s) == {"SOXL": 1.0}
    s = s3_state(bull_votes=1)
    s.dip["SMH"] = OS - 1.0
    assert s3_weights(DATE, s) == {"SOXL": 1.0}


def test_s3_bear_cash():
    assert s3_weights(DATE, s3_state(bull_votes=0)) == {}


def test_s3_unavailable_vote_reads_bearish():
    """The 1.9 mechanic the continuation flagged: a missing SMA is a false
    vote, so 3 genuine bulls + 1 unavailable still passes, 2 + 2 does not."""
    s = s3_state(bull_votes=4)
    del s.smas[("SOXL", config.SMA_LONG)]
    assert s3_weights(DATE, s) == {"TQQQ": 0.5, "SOXL": 0.5}
    s = s3_state(bull_votes=4)
    del s.smas[("SOXL", config.SMA_LONG)]
    del s.smas[("SMH", config.SMA_LONG)]
    assert s3_weights(DATE, s) == {}


def test_s3_overbought_alone_does_not_short_in_bear():
    s = s3_state(bull_votes=0)
    s.exhaustion["SPY"] = T2 + 5.0
    assert s3_weights(DATE, s) == {}


# ---------------------------------------------------------------------------
# Cross-cutting
# ---------------------------------------------------------------------------

def test_all_pairwise_sites_are_reachable_and_named():
    """Every site in PAIRWISE_SITES must be exercised by some raise above."""
    assert len(PAIRWISE_SITES) == 9
    assert len(set(PAIRWISE_SITES)) == 9


def test_no_sleeve_emits_trend_series_as_a_holding():
    """The trend series is a signal input only; it may appear in no weight
    dict. Exercise every terminal reached in this file and assert."""
    terminals = []
    terminals.append(t10_weights(DATE, t10_state()))
    s = t10_state(); s.rs["XLK"] = 90.0; s.avail.add("SVIX")
    terminals.append(t10_weights(DATE, s))
    terminals.append(t11_weights(DATE, t11_bull_state()))
    terminals.append(t11_weights(DATE, t11_bear_state()))
    terminals.append(s2_weights(DATE, s2_state()))
    terminals.append(s3_weights(DATE, s3_state()))
    for w in terminals:
        assert TREND not in w
        assert "KMLM" not in w


def test_every_terminal_sums_to_sleeve_budget_or_cash():
    cases = [
        t10_weights(DATE, t10_state()),
        t11_weights(DATE, t11_bull_state()),
        t11_weights(DATE, t11_bear_state()),
        s2_weights(DATE, s2_state()),
        s3_weights(DATE, s3_state(bull_votes=4)),
        s3_weights(DATE, s3_state(bull_votes=0)),
    ]
    for w in cases:
        assert_budget(w)
