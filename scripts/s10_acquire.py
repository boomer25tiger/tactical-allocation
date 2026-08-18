"""Session 10, step 1: acquire and freeze SVXY, UVXY, SVIX, UVIX and the
sibling funds step 4 needs (QID, SSO, SDS).

Sibling judgment, recorded: QID (-2x Nasdaq-100, 2006), SSO (2x S&P 500,
2006) and SDS (-2x S&P 500, 2006) are pulled -- they give pre-2010 windows
including 2008 on the two index families the study's leveraged funds track.
ROM, USD and UYG (ProShares Ultra Technology / Semiconductors / Financials,
2007) are judged non-probative and NOT pulled: they track Dow Jones U.S.
sector indices, not the Select Sector / PHLX / S&P Biotech families the
study's funds track, and no underlying proxy for those indices is frozen --
exactly the sector residual the session brief pre-declares as a disclosed
limitation.

Each pull: verify gates, truncate per 1.14, refuse overwrite per 1.1,
freeze, hash, manifest row, then run the session 07 split-boundary
consistency check and the interior-null audit before the file is used.
"""

import datetime as dt
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import yfinance as yf

OUT = ROOT / "outputs" / "session-10"
OUT.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw" / "etf"
TRUNC = pd.Timestamp("2026-08-14")

PULLS = ["SVXY", "UVXY", "SVIX", "UVIX", "QID", "SSO", "SDS"]

spy = pd.read_parquet(RAW / "SPY.parquet")
CAL = pd.to_datetime(spy.index)


def audit(close: pd.Series) -> dict:
    s = close.reindex(CAL)
    valid = s.notna().to_numpy()
    if not valid.any():
        return dict(pre=len(s), interior=0, run=0)
    i0 = int(np.argmax(valid))
    i1 = int(len(valid) - 1 - np.argmax(valid[::-1]))
    interior = ~valid[i0:i1 + 1]
    run = best = 0
    for x in interior:
        run = run + 1 if x else 0
        best = max(best, run)
    return dict(pre=i0, interior=int(interior.sum()), run=best)


def boundary_check(df: pd.DataFrame, tol=0.25) -> tuple[int, int]:
    sp = df["Stock Splits"].astype(float)
    ev = sp[sp != 0]
    close = df["Close"].astype(float)
    n = fails = 0
    for d, ratio in ev.items():
        i = df.index.get_indexer([d])[0]
        if i == 0:
            continue
        pre_d = df.index[i - 1]
        f_pre = float(ev[ev.index > pre_d].prod())
        f_post = float(ev[ev.index > d].prod()) if (ev.index > d).any() else 1.0
        br = (close.loc[pre_d] * f_pre) / (close.loc[d] * f_post)
        n += 1
        if abs(br / ratio - 1.0) >= tol:
            fails += 1
    return n, fails


# synthetic positive control for the audit logic
_syn = pd.Series([np.nan, 1.0, np.nan, 2.0], index=CAL[:4])
_r = audit(_syn)
assert (_r["pre"], _r["interior"], _r["run"]) == (1, 1, 1), _r
print("CONTROL PASSED: audit logic\n")

rows = []
for t in PULLS:
    path = RAW / f"{t}.parquet"
    if path.exists():
        print(f"{t}: EXISTS - refusing re-pull per 1.1")
        continue
    pull_ts = dt.datetime.now(dt.timezone.utc).isoformat()
    h = yf.Ticker(t).history(period="max", auto_adjust=False, actions=True)
    if h.empty:
        print(f"{t}: EMPTY PULL - recorded, not written")
        continue
    h.index = pd.to_datetime(h.index).tz_localize(None).normalize()
    h.index.name = "Date"
    h = h[h.index <= TRUNC]
    close = h["Close"].astype(float)
    a = audit(close)
    n_b, f_b = boundary_check(h)
    assert h.index.is_monotonic_increasing and not h.index.has_duplicates
    assert close.notna().all()
    h.to_parquet(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    rows.append(dict(ticker=t, sha256=sha, bytes=path.stat().st_size,
                     rows=len(h), first_date=str(h.index.min().date()),
                     last_date=str(h.index.max().date()),
                     pull_timestamp_utc=pull_ts,
                     yfinance_version=yf.__version__,
                     file=str(path.relative_to(ROOT)),
                     interior_nulls=a["interior"],
                     split_boundaries_checked=n_b,
                     split_boundary_failures=f_b))
    print(f"{t}: {len(h):,} rows {h.index.min().date()} -> "
          f"{h.index.max().date()}  interior nulls {a['interior']}  "
          f"boundaries {n_b} checked / {f_b} failed  sha {sha[:12]}...")

pd.DataFrame(rows).to_csv(OUT / "etf-manifest-additions.csv", index=False)
print(f"\nWROTE etf-manifest-additions.csv ({len(rows)} rows)")
print("judged unnecessary (recorded): ROM, USD, UYG - Dow Jones US sector "
      "benchmarks, not the study families; no underlying proxy frozen")
