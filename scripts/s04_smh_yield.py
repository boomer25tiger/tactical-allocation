"""Session 04, step 3. SMH HOLDRS basket dividend yield 2007-2012, informs 3.12.

The HOLDRS prospectus confirms dividends passed through to holders net of a
trustee custody fee of $2.00 per quarter per round lot of 100 HOLDRS ($8.00
per lot per year), waived beyond dividends received. The zero-distribution
record in the price feed describes the data, not the instrument.

The basket below is the 2003 prospectus composition, share amounts per round
lot of 100 HOLDRS. Reconstitutions and mergers changed it before and during
the window (National Semiconductor was acquired by Texas Instruments in
2011); it is treated as an approximation and NOT reconstructed.

Measurement, not a frozen pull: nothing is written under data/. SMH prices
are read from the frozen parquet; dividend histories come from yfinance.
No strategy return, allocation, or performance statistic is computed.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import yfinance as yf

OUT = ROOT / "outputs" / "session-04"
OUT.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2013)
FEE_PER_LOT_PER_YEAR = 8.00  # $2.00/quarter per 100 HOLDRS, floored at divs

# 2003 prospectus basket: shares per round lot of 100 HOLDRS (150 total).
BASKET = {
    "AMD": 4, "ALTR": 6, "AMKR": 2, "ADI": 6, "AMAT": 26, "ATML": 8,
    "BRCM": 2, "INTC": 30, "KLAC": 3, "LLTC": 5, "LSI": 5, "MXIM": 5,
    "MU": 9, "NSM": 3, "NVLS": 2, "SNDK": 1, "TER": 3, "TXN": 22,
    "VTSS": 3, "XLNX": 5,
}
assert sum(BASKET.values()) == 150

# Tickers whose 2003-basket entity is known to have been reused by an
# unrelated listing after delisting. Window dividends under these tickers
# would belong to the wrong entity and are excluded if they appear.
REUSED_TICKERS = {"SNDK": "re-listed 2025 as the WDC SanDisk spin-off",
                  "LSI": "ticker later assigned to Life Storage (REIT)",
                  "NSM": "ticker reused by Nationstar Mortgage (IPO 2012-03)"}


def window_dividends(t: str) -> tuple[pd.Series | None, str, bool]:
    """Per-share dividends inside 2007-2012 for one ticker, with a status.

    yfinance dividends are split-adjusted retroactively, so a split dated
    after a dividend's ex-date scales the reported per-share amount down by
    the split ratio. Each window dividend is un-adjusted back to as-paid by
    the cumulative product of split ratios dated after its ex-date -- the
    same treatment the SMH price gets. KLAC is the live case: a 10-for-1
    split on 2026-06-12 makes its reported window dividends one tenth of
    as-paid. Third return: description of any un-adjustment applied.
    """
    try:
        h = yf.Ticker(t).history(period="max", actions=True)
    except Exception as e:  # network or symbol failure
        return None, f"fetch error: {type(e).__name__}", ""
    if h.empty:
        return None, "no data returned (delisted/renamed)", ""
    idx = pd.to_datetime(h.index).tz_localize(None)
    div = pd.Series(h["Dividends"].to_numpy(), index=idx)
    splits = pd.Series(h["Stock Splits"].to_numpy(), index=idx)
    split_events = splits[splits != 0]
    win = div[(div.index >= "2007-01-01") & (div.index <= "2012-12-31")]
    win = win[win > 0]
    unadj_note = ""
    if len(win):
        factors = pd.Series(
            [float(split_events[split_events.index > d].prod())
             if (split_events.index > d).any() else 1.0
             for d in win.index],
            index=win.index,
        )
        if (factors != 1.0).any():
            unadj_note = (f"un-adjusted by future splits "
                          f"{[(str(d.date()), r) for d, r in split_events[split_events.index > win.index.min()].items()]}")
        win = win * factors
    status = (f"data from {idx.min().date()}; "
              f"{len(win)} dividend events in window, "
              f"as-paid sum/share ${win.sum():.4f}"
              + (f"; {unadj_note}" if unadj_note else ""))
    return win, status, unadj_note


def main() -> None:
    # ---- POSITIVE CONTROL: INTC must show window dividends ---------------
    intc, intc_status, _ = window_dividends("INTC")
    assert intc is not None and len(intc) > 0 and intc.sum() > 0, (
        f"CONTROL FAILED: INTC returned no window dividends ({intc_status}); "
        "no zero for any other ticker can be trusted"
    )
    print(f"CONTROL PASSED: INTC {intc_status}\n")

    per_ticker = {}
    statuses = {}
    excluded = {}
    for t in sorted(BASKET):
        win, status, _ = window_dividends(t)
        statuses[t] = status
        if win is None or len(win) == 0:
            per_ticker[t] = pd.Series(dtype=float)
            continue
        if t in REUSED_TICKERS:
            excluded[t] = f"{REUSED_TICKERS[t]}; window dividends excluded"
            per_ticker[t] = pd.Series(dtype=float)
            continue
        per_ticker[t] = win

    print("=== per-ticker status ===")
    for t in sorted(BASKET):
        note = f"  [EXCLUDED: {excluded[t]}]" if t in excluded else ""
        print(f"  {t:5s} x{BASKET[t]:3d}: {statuses[t]}{note}")

    # SMH price must be the AS-TRADED price of the year's first session.
    # yfinance Close is retroactively split-adjusted, and the frozen file
    # carries a 2-for-1 split on 2023-05-05, so every pre-2023 stored Close
    # is half what a HOLDR actually traded at. Un-adjust by the cumulative
    # product of splits dated after the pricing session, from the file's own
    # Stock Splits column.
    smh = pd.read_parquet(ROOT / "data" / "raw" / "etf" / "SMH.parquet")
    smh.index = pd.to_datetime(smh.index)
    close = smh["Close"].astype(float)
    smh_splits = smh["Stock Splits"].astype(float)
    split_events = smh_splits[smh_splits != 0]
    print(f"\nSMH split events in frozen file: "
          f"{[(str(d.date()), r) for d, r in split_events.items()]}")

    def as_traded(date: pd.Timestamp) -> float:
        factor = float(split_events[split_events.index > date].prod()) \
            if (split_events.index > date).any() else 1.0
        return float(close.loc[date]) * factor

    rows = []
    for y in YEARS:
        gross_per_lot = 0.0
        contributors = {}
        for t, sh in BASKET.items():
            d = per_ticker[t]
            if len(d):
                amt = float(d[d.index.year == y].sum()) * sh
                if amt > 0:
                    contributors[t] = amt
                gross_per_lot += amt
        first_sess = close[close.index.year == y].index.min()
        px = as_traded(first_sess)
        lot_value = px * 100.0
        net_per_lot = max(gross_per_lot - FEE_PER_LOT_PER_YEAR, 0.0)
        rows.append(dict(
            year=y,
            smh_first_session=str(first_sess.date()),
            smh_price=px,
            gross_div_per_lot=round(gross_per_lot, 4),
            gross_yield_pct=100.0 * gross_per_lot / lot_value,
            fee_drag_pp=100.0 * (gross_per_lot - net_per_lot) / lot_value,
            net_div_per_lot=round(net_per_lot, 4),
            net_yield_pct=100.0 * net_per_lot / lot_value,
            n_contributing_tickers=len(contributors),
            contributors="; ".join(f"{t} ${v:.2f}" for t, v in
                                   sorted(contributors.items())),
        ))

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "smh-basket-yield.csv", index=False)

    print("\n=== basket yield per year ===")
    show = df[["year", "smh_first_session", "smh_price", "gross_div_per_lot",
               "gross_yield_pct", "fee_drag_pp", "net_yield_pct",
               "n_contributing_tickers"]]
    print(show.round(3).to_string(index=False))
    print(f"\nmean net yield 2007-2012: {df.net_yield_pct.mean():.3f} pct")
    print(f"mean gross yield:          {df.gross_yield_pct.mean():.3f} pct")
    print("\ncontributors by year:")
    for r in rows:
        print(f"  {r['year']}: {r['contributors']}")
    print("\nWROTE outputs/session-04/smh-basket-yield.csv")


if __name__ == "__main__":
    main()
