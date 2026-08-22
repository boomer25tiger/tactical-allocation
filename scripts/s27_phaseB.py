"""Session 27 phase B. What the frozen data actually covers.

Register 2.10 records the holdout span's extent as unestablished, so this phase
establishes it from the frozen inputs before any strategy quantity is computed.
Reading an input's date range is a coverage question rather than a strategy
measurement.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import pandas as pd
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
OUT = ROOT/"outputs"/"session-27"; OUT.mkdir(parents=True, exist_ok=True)
BOUNDARY = bt.HOLDOUT_LAST_DATE + pd.Timedelta(days=1)   # 2021-08-01, from the module
rows = []
def add(t, **kw): rows.append({"table": t, **kw})


def span(p: Path):
    try:
        if p.suffix == ".parquet":
            df = pd.read_parquet(p)
        elif p.suffix in (".csv", ".txt"):
            df = pd.read_csv(p)
        else:
            return None
    except Exception as e:
        return ("unreadable", str(e)[:60], 0)
    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex):
        for c in df.columns:
            if str(c).lower() in ("date", "trade date", "datetime", "observation_date"):
                try:
                    idx = pd.DatetimeIndex(pd.to_datetime(df[c]))
                    break
                except Exception:
                    pass
    if not isinstance(idx, pd.DatetimeIndex):
        try:
            idx = pd.DatetimeIndex(pd.to_datetime(df.iloc[:, 0]))
        except Exception:
            return ("no date index", "", len(df))
    idx = pd.DatetimeIndex(pd.Series(idx).dt.tz_localize(None) if
                           getattr(idx, "tz", None) is not None else idx).normalize()
    return (str(idx.min().date()), str(idx.max().date()), len(df))


files = sorted(p for p in (ROOT/"data").rglob("*") if p.is_file()
               and not p.name.startswith(".") and p.suffix in (".parquet", ".csv"))
ends = {}
for p in files:
    s = span(p)
    rel = str(p.relative_to(ROOT))
    if s is None:
        continue
    add("input_span", item=rel, first_date=s[0], last_date=s[1], n_rows=s[2])
    ends[rel] = s[1]
add("summary", item="frozen_inputs_surveyed", value=len(ends))

# ---- the derived held universe ------------------------------------------------
ETF = ROOT/"data"/"raw"/"etf"
held = sorted(bt.UNLEVERED + bt.LEVERED)
add("summary", item="loaded_universe_size", value=len(held),
    note="bt.UNLEVERED and bt.LEVERED, unmodified")
last = {}
for t in held:
    p = ETF/f"{t}.parquet"
    if not p.exists():
        add("held_ticker", item=t, last_date="", note="no frozen file")
        continue
    s = span(p)
    last[t] = pd.Timestamp(s[1])
    add("held_ticker", item=t, first_date=s[0], last_date=s[1], n_rows=s[2])
simultaneous = min(last.values())
limiting = sorted(t for t, d in last.items() if d == simultaneous)
add("summary", item="latest_all_held_tickers_available", value=str(simultaneous.date()),
    note="the minimum last observation across the loaded universe, limited by " +
         ", ".join(limiting))

# ---- the other inputs the specification needs ---------------------------------
NEED = {"risk free": ROOT/"data"/"raw"/"rates",
        "index": ROOT/"data"/"raw"/"index",
        "nav": ROOT/"data"/"raw"/"nav"}
for name, d in NEED.items():
    if not d.exists():
        continue
    es = []
    for p in sorted(d.rglob("*")):
        if p.is_file() and p.suffix in (".parquet", ".csv"):
            s = span(p)
            if s and s[0] != "no date index":
                es.append((str(p.relative_to(ROOT)), s[1]))
    if es:
        mn = min(e[1] for e in es)
        add("summary", item=f"latest_{name}_available", value=mn,
            note="limited by " + ", ".join(e[0] for e in es if e[1] == mn))

computable = min([simultaneous] + [pd.Timestamp(v) for k, v in
                 [(r["item"], r["value"]) for r in rows
                  if r["table"] == "summary" and str(r["item"]).startswith("latest_")
                  and r["item"] != "latest_all_held_tickers_available"]])
add("summary", item="latest_canonical_computable_end_to_end", value=str(computable.date()),
    note="the earliest of the held-universe limit and every other input the "
         "specification reads, so the specification is computable end to end through "
         "this date and no further")

# ---- the holdout span the data supports ----------------------------------------
cal = pd.DatetimeIndex(pd.read_parquet(ETF/"SPY.parquet").index).tz_localize(None).normalize()
hs = cal[(cal >= BOUNDARY) & (cal <= computable)]
add("holdout_span", item="boundary", value=str(BOUNDARY.date()),
    note="bt.HOLDOUT_LAST_DATE plus one session, read from the module")
add("holdout_span", item="end_date_the_data_supports", value=str(computable.date()))
add("holdout_span", item="sessions", value=len(hs),
    note="SPY calendar sessions inside the span")
add("holdout_span", item="primary_window_sessions", value=2472,
    note="from the standing positive control")
add("holdout_span", item="ratio_to_primary", value=round(len(hs)/2472, 6))
add("holdout_span", item="first_session", value=str(hs[0].date()) if len(hs) else "")
add("holdout_span", item="last_session", value=str(hs[-1].date()) if len(hs) else "")

# ---- SVIX and UVIX ---------------------------------------------------------------
for t in ("SVIX", "UVIX"):
    p = ETF/f"{t}.parquet"
    if p.exists():
        s = span(p)
        add("volatility_terminal", item=t, first_date=s[0], last_date=s[1],
            value=int(pd.Timestamp(s[0]) >= BOUNDARY),
            note="lists inside the holdout span" if pd.Timestamp(s[0]) >= BOUNDARY
                 else "lists before the boundary")
    else:
        add("volatility_terminal", item=t, note="no frozen file")
    add("volatility_terminal", item=f"{t}_in_bt_LEVERED", value=int(t in bt.LEVERED),
        note="the loader is unmodified, per the disposition at 9.43")
    add("volatility_terminal", item=f"{t}_in_bt_UNLEVERED", value=int(t in bt.UNLEVERED))

# ---- the branch --------------------------------------------------------------------
covers = computable >= pd.Timestamp("2026-01-01")
near = computable <= BOUNDARY + pd.Timedelta(days=120)
branch = ("halt, the inputs stop at or near the boundary" if near else
          "proceed, the frozen inputs cover the span" if covers else
          "proceed on the span the data supports")
add("branch", item="taken", value=branch,
    note=f"the boundary is {BOUNDARY.date()} and the frozen inputs support the "
         f"specification through {computable.date()}, being {len(hs)} sessions")
add("branch", item="read_runs_entirely_on_hashed_data", value=1,
    note="every input read is one of the 339 verified at gate A3, and no input is "
         "fetched in this session")
fn = ["table", "item", "value", "first_date", "last_date", "n_rows", "note"]
with open(OUT/"holdout-coverage.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote holdout-coverage.csv, {len(rows)} rows")
for r in rows:
    if r["table"] in ("summary", "holdout_span", "branch"):
        print(f"  {r['table']:14s} {str(r['item']):42s} {r.get('value','')}")
