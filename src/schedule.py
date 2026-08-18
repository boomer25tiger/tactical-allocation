"""Per-date fund terms: multiple and benchmark schedule (decision 3.11).

Machine-readable encoding of outputs/session-08/fund-schedule.csv, which
carries the filing-grade sources. The synthetic build under 2.1/2.2 consumes
this instead of re-reading the report, and 2.7's validation windows must
respect these boundaries or the bands will register failures whose cause is
the schedule rather than the construction.

Conventions:
  * Period boundaries are the filing-stated effective dates. Where a change
    was effective "as of the close of business" on date D (the UVXY/SVXY
    multiple changes), the old terms govern THROUGH D and the new terms
    begin D+1; the rows below carry that boundary explicitly.
  * The two Direxion index switches (SOXL/SOXS 2021-08-25) and both FAS
    switches (2022-02-28, 2022-08-01) carry the filings' own "on or about"
    qualifier: on_or_about=True means the date is the filing's stated
    intent, not confirmed to the trading session. A later reader must not
    treat those boundaries as session-exact.
  * end=None means the period runs to the present.
  * BTAL has no multiple (anti-beta long/short strategy); its row carries
    multiple=None and the benchmark it tracks.

Sources are the accessions recorded in outputs/session-08/fund-schedule.csv
and REPORT.md (8-K 0001193125-18-059052 for UVXY/SVXY; 497s
0001193125-21-195149, 0001193125-21-370635, 0001193125-22-166266 for the
Direxion switches; current 485BPOS filings for the constant funds).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

__all__ = ["Period", "FUND_SCHEDULE", "fund_terms"]


@dataclass(frozen=True)
class Period:
    start: date          # first date the terms govern
    end: date | None     # last date the terms govern; None = present
    multiple: float | None
    benchmark: str
    on_or_about: bool = False  # start date carries the filing's qualifier


def _d(s: str) -> date:
    return date.fromisoformat(s)


FUND_SCHEDULE: dict[str, list[Period]] = {
    # -- never changed -----------------------------------------------------
    "TQQQ": [Period(_d("2010-02-09"), None, 3.0, "Nasdaq-100 Index")],
    "QLD": [Period(_d("2006-06-19"), None, 2.0, "Nasdaq-100 Index")],
    "SQQQ": [Period(_d("2010-02-09"), None, -3.0, "Nasdaq-100 Index")],
    "PSQ": [Period(_d("2006-06-19"), None, -1.0, "Nasdaq-100 Index")],
    "SH": [Period(_d("2006-06-19"), None, -1.0, "S&P 500 Index")],
    "SPXL": [Period(_d("2008-11-05"), None, 3.0, "S&P 500 Index")],
    "TECL": [Period(_d("2008-12-17"), None, 3.0, "Technology Select Sector Index")],
    "TECS": [Period(_d("2008-12-17"), None, -3.0, "Technology Select Sector Index")],
    "LABU": [Period(_d("2015-05-28"), None, 3.0,
                    "S&P Biotechnology Select Industry Index")],
    "SVIX": [Period(_d("2022-03-28"), None, -1.0, "Short VIX Futures Index")],
    "UVIX": [Period(_d("2022-03-28"), None, 2.0, "Long VIX Futures Index")],
    "BTAL": [Period(_d("2011-09-13"), None, None,
                    "Dow Jones U.S. Thematic Market Neutral Anti-Beta Index")],
    # -- multiple changes (exact close-of-business boundaries) -------------
    "UVXY": [
        Period(_d("2011-10-03"), _d("2018-02-27"), 2.0,
               "S&P 500 VIX Short-Term Futures Index"),
        Period(_d("2018-02-28"), None, 1.5,
               "S&P 500 VIX Short-Term Futures Index"),
    ],
    "SVXY": [
        Period(_d("2011-10-03"), _d("2018-02-27"), -1.0,
               "S&P 500 VIX Short-Term Futures Index"),
        Period(_d("2018-02-28"), None, -0.5,
               "S&P 500 VIX Short-Term Futures Index"),
    ],
    # -- benchmark changes ("on or about" per the filings) -----------------
    "SOXL": [
        Period(_d("2010-03-11"), _d("2021-08-24"), 3.0,
               "PHLX Semiconductor Sector Index"),
        Period(_d("2021-08-25"), None, 3.0, "ICE Semiconductor Index",
               on_or_about=True),
    ],
    "SOXS": [
        Period(_d("2010-03-11"), _d("2021-08-24"), -3.0,
               "PHLX Semiconductor Sector Index"),
        Period(_d("2021-08-25"), None, -3.0, "ICE Semiconductor Index",
               on_or_about=True),
    ],
    "FAS": [
        Period(_d("2008-11-06"), _d("2022-02-27"), 3.0,
               "Russell 1000 Financial Services Index"),
        Period(_d("2022-02-28"), _d("2022-07-31"), 3.0,
               "Russell 1000 Financials 40 Act 15/22.5 Daily Capped Index",
               on_or_about=True),
        Period(_d("2022-08-01"), None, 3.0, "Financials Select Sector Index",
               on_or_about=True),
    ],
}


def fund_terms(fund: str, on: date | str | pd.Timestamp) -> Period:
    """The Period governing `fund` on date `on`.

    Raises KeyError for an unknown fund and ValueError for a date before the
    fund's inception (terms for a fund that did not exist are not a thing
    this module will invent).
    """
    if fund not in FUND_SCHEDULE:
        raise KeyError(f"no schedule for fund {fund!r}")
    d = pd.Timestamp(on).date()
    for p in FUND_SCHEDULE[fund]:
        if d >= p.start and (p.end is None or d <= p.end):
            return p
    raise ValueError(
        f"{fund} has no terms on {d} (inception "
        f"{FUND_SCHEDULE[fund][0].start})"
    )
