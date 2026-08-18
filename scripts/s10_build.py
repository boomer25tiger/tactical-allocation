"""Session 10, step 2: build the synthetic daily total-return series.

Construction, per decisions in force:

    r_syn(t) = M(t) * r_u(t) + (1 - M(t)) * ref(t) - k(t) * s(t) - ER/252

where r_u is the proxy underlying's total return (2.12 / session 09), M(t)
is the multiple from src/schedule.py (never hardcoded for the sixteen study
funds), ref(t) is the frozen DTB3 rate accrued at rate/360 per calendar day
between sessions (5.5a convention), and the financing adjustment k*s is:

    long swap equity  (M > 1):  k = M - 1,  s = FINANCING_SPREAD_BP  (2.14)
    short swap equity (M < 0):  k = |M|,    s = FINANCING_SHORT_HAIRCUT_BP
    volatility funds:  k = 0 -- futures-based, no swap financing (2.15);
                       collateral earns ref on the full NAV, so the ref term
                       is + 1.0 * ref regardless of M.

Daily reset: the levered daily return compounds, so path dependence and
volatility decay arise naturally.

Expense ratios: decision 2.13's schedule is NOT among the register
materials available to this session. Constant per-fund net expense ratios
from current prospectuses are used instead and FLAGGED in the session
report; a mis-set ER is indistinguishable from a financing mis-set of the
same annual magnitude, and step 7 bounds that class of error.

Pre-inception extension: before a fund's first schedule period the build
extends the inception-period terms backward -- that is the point of the
synthetic -- and the report labels those windows unvalidated.

Synthetics are derived, not acquired: 1.1 does not apply and rebuilds are
expected.
"""

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src import config
from src.data import build_ticker_frame
from src.schedule import FUND_SCHEDULE

OUT = ROOT / "data" / "interim" / "synthetics"
OUT.mkdir(parents=True, exist_ok=True)
MOUT = ROOT / "outputs" / "session-10"
MOUT.mkdir(parents=True, exist_ok=True)

# proxy underlying per fund family (2.12, session 09 measurements)
UNDERLYING = {
    "TQQQ": "QQQ", "QLD": "QQQ", "SQQQ": "QQQ", "PSQ": "QQQ",
    "SH": "SPY", "SPXL": "SPY",
    "TECL": "XLK", "TECS": "XLK",
    # session 12: SOXX adopted -- exact benchmark both schedule periods
    # (PHLX through 2020, ICE from its 497 of 2021-04-22); replaces SMH.
    "SOXL": "SOXX", "SOXS": "SOXX",
    "FAS": "XLF", "LABU": "XBI",
    "UVXY": "VXCM30", "SVXY": "VXCM30",
    # session 12: SVIX/UVIX build from the Cboe index family. ^SHORTVOL is
    # read at RUN TIME (not frozen; rebuilds are network-dependent, noted).
    # SVIX tracks the Short VIX Futures Index directly (+1x of SHORTVOL --
    # the "-1x" in the fund NAME describes shortness vs long futures, a
    # naming subtlety the report records). UVIX is 2x the Long VIX Futures
    # Index; LONGVOL serves no daily history, so -SHORTVOL stands proxy,
    # flagged.
    "SVIX": "SHORTVOL", "UVIX": "NEG_SHORTVOL",
    # siblings (validation instruments, constant terms since inception)
    "QID": "QQQ", "SSO": "SPY", "SDS": "SPY",
}
SIBLING_TERMS = {"QID": -2.0, "SSO": 2.0, "SDS": -2.0,
                 # vol multiples handled explicitly (see UNDERLYING note):
                 "SVIX": 1.0, "UVIX": 2.0}
VOL_FUNDS = {"UVXY", "SVXY", "SVIX", "UVIX"}

# expense ratios, percent per year. Direxion seven: STATED FY2025
# costs-paid ratios from the tailored shareholder reports (session 11).
# Everything else: CARRIED constants, marked in the session 11 schedule.
ER_PCT = {
    "TQQQ": 0.86, "QLD": 0.95, "SQQQ": 0.95, "PSQ": 0.95, "SH": 0.88,
    "SPXL": 0.81, "TECL": 0.83, "TECS": 0.92, "SOXL": 0.71, "SOXS": 0.87,
    "FAS": 0.86, "LABU": 0.92,
    "UVXY": 0.95, "SVXY": 0.95, "SVIX": 1.49, "UVIX": 1.77,
    "QID": 0.95, "SSO": 0.91, "SDS": 0.90,
}


def multiple_series(fund: str, idx: pd.DatetimeIndex) -> pd.Series:
    if fund in SIBLING_TERMS:
        return pd.Series(SIBLING_TERMS[fund], index=idx)
    periods = FUND_SCHEDULE[fund]
    out = pd.Series(periods[0].multiple, index=idx, dtype=float)
    for p in periods:
        start = pd.Timestamp(p.start)
        end = pd.Timestamp(p.end) if p.end else idx.max()
        out.loc[(idx >= start) & (idx <= end)] = p.multiple
    return out


def load_underlying(key: str) -> pd.Series:
    if key == "VXCM30":
        # 2.3 / 2.22: VX construction B -- the INVESTABLE rolled-futures
        # index level from session 00B (vx-cm30-b.parquet, index_level).
        # The constant-maturity settle level in vx-cm30.parquet is a price
        # interpolation whose change omits the roll yield and is NOT what a
        # futures position earns; the first build of this session used it
        # by mistake and the vol synthetics overshot by the roll drag
        # (recorded in the session report).
        df = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30-b.parquet")
        s = df.set_index(pd.to_datetime(df["trade_date"]))["index_level"]
        return s.sort_index().pct_change()
    if key in ("SHORTVOL", "NEG_SHORTVOL"):
        import yfinance as yf
        sv = yf.Ticker("^SHORTVOL").history(period="max")["Close"]
        sv.index = pd.to_datetime(sv.index).tz_localize(None).normalize()
        r = sv.sort_index().pct_change()
        return -r if key == "NEG_SHORTVOL" else r
    tf = build_ticker_frame(key, pd.read_parquet(
        ROOT / "data" / "raw" / "etf" / f"{key}.parquet"))
    return tf.ret_total


# DTB3 per-session reference return under the 5.5a day count
dtb3 = pd.read_parquet(ROOT / "data" / "raw" / "rates" / "DTB3.parquet")["DTB3"]
dtb3.index = pd.to_datetime(dtb3.index)
dtb3 = dtb3.ffill()  # carry for accrual purposes only (session 02 departure)


def ref_returns(idx: pd.DatetimeIndex) -> pd.Series:
    days = idx.to_series().diff().dt.days
    rate = dtb3.reindex(idx, method="ffill") / 100.0
    return (rate.shift(1) * days / 360.0).fillna(0.0)


def build(fund: str, spread_long_bp=None, haircut_bp=None) -> pd.DataFrame:
    spread_long = (config.FINANCING_SPREAD_BP if spread_long_bp is None
                   else spread_long_bp) / 1e4
    haircut = (config.FINANCING_SHORT_HAIRCUT_BP if haircut_bp is None
               else haircut_bp) / 1e4
    r_u = load_underlying(UNDERLYING[fund]).dropna()
    idx = r_u.index
    M = multiple_series(fund, idx)
    ref = ref_returns(idx)
    er_d = ER_PCT[fund] / 100.0 / 252.0

    if fund in VOL_FUNDS:
        fin = 0.0
        if UNDERLYING[fund] in ("SHORTVOL", "NEG_SHORTVOL"):
            # The Cboe indices are total-return-like: session 12 measured
            # that adding collateral yield on top lifts the tracking
            # difference by almost exactly the bill yield (+7.6 -> +13.2
            # %/yr), i.e. double-counting. No ref term for these.
            ref_term = 0.0
        else:
            ref_term = ref  # excess-return construction B: collateral on full NAV
    else:
        k = np.where(M > 1, M - 1, np.where(M < 0, M.abs(), 0.0))
        # spread scaled to per-session on the same day count as ref
        days = idx.to_series().diff().dt.days.fillna(0)
        s = np.where(M > 1, spread_long, np.where(M < 0, haircut, 0.0))
        fin = k * s * days.to_numpy() / 360.0
        ref_term = (1.0 - M) * ref
    r_syn = M * r_u + ref_term - fin - er_d
    level = (1.0 + r_syn).cumprod()
    return pd.DataFrame({"syn_ret": r_syn, "syn_index": level,
                         "multiple": M, "underlying_ret": r_u})


def main() -> None:
    rows = []
    for fund in UNDERLYING:
        df = build(fund)
        p = OUT / f"SYN_{fund}.parquet"
        df.to_parquet(p)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        rows.append(dict(fund=fund, underlying=UNDERLYING[fund],
                         rows=len(df), first=str(df.index.min().date()),
                         last=str(df.index.max().date()),
                         er_pct=ER_PCT[fund], sha256=sha,
                         file=str(p.relative_to(ROOT))))
        print(f"SYN_{fund:5s} {len(df):5,} rows {df.index.min().date()} -> "
              f"{df.index.max().date()}  M range "
              f"[{df.multiple.min():+.1f}, {df.multiple.max():+.1f}]")
    pd.DataFrame(rows).to_csv(MOUT / "synthetics-manifest.csv", index=False)

    # schedule boundaries crossed: confirm the switch landed on the session
    print("\nboundary confirmations:")
    for fund, bdate, before, after in [
        ("UVXY", "2018-02-28", 2.0, 1.5),
        ("SVXY", "2018-02-28", -1.0, -0.5),
    ]:
        df = pd.read_parquet(OUT / f"SYN_{fund}.parquet")
        b = pd.Timestamp(bdate)
        prev = df.multiple[df.index < b].iloc[-1]
        cur = df.multiple[df.index >= b].iloc[0]
        first_new = df.index[df.index >= b][0]
        ok = prev == before and cur == after
        print(f"  {fund}: {prev:+.1f} -> {cur:+.1f} at {first_new.date()} "
              f"({'OK' if ok else 'WRONG'})")
    for fund, bdate in [("SOXL", "2021-08-25"), ("SOXS", "2021-08-25"),
                        ("FAS", "2022-02-28"), ("FAS", "2022-08-01")]:
        print(f"  {fund}: benchmark boundary {bdate} crossed; build input "
              f"(proxy {UNDERLYING[fund]}) unchanged across it by design -- "
              f"the switch changes interpretation, not the input series")
    print("\nDONE - 19 synthetics under data/interim/synthetics/")


if __name__ == "__main__":
    main()
