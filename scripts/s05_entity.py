"""Session 05, step 2: ticker entity verification.

Session 04 found NSM resolving to Nationstar Mortgage rather than National
Semiconductor and SNDK re-listed as a different entity in 2025. Ticker
reuse across entities is a standing hazard; this records, for every frozen
ticker, the entity yfinance currently resolves it to, so later sessions
consult the table instead of rediscovering the problem.

Writes outputs/session-05/ticker-entity-check.csv. Reads data/ only to
report first/last dates held; writes nothing under data/.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import yfinance as yf

OUT = ROOT / "outputs" / "session-05"
OUT.mkdir(parents=True, exist_ok=True)

# Expected entity, as a case-insensitive keyword any one of which must
# appear in the resolved long/short name. Source universe plus RYMFX (2.5).
EXPECTED = {
    "AGG": ["Aggregate Bond"], "BIL": ["1-3 Month", "T-Bill"],
    "BND": ["Total Bond"], "BSV": ["Short-Term Bond"],
    "BTAL": ["Anti-Beta"], "FAS": ["Financial Bull"],
    "IBB": ["Biotech"], "IEF": ["7-10 Year"], "IOO": ["Global 100"],
    "KMLM": ["Mount Lucas", "KFA"], "LABU": ["Biotech Bull"],
    "PSQ": ["Short QQQ"], "QLD": ["Ultra QQQ"], "QQQ": ["QQQ"],
    "QQQE": ["Equal Weight"], "SH": ["Short S&P"],
    "SMH": ["Semiconductor"], "SOXL": ["Semiconductor Bull"],
    "SOXS": ["Semiconductor Bear"], "SPXL": ["S&P 500 Bull", "S&P500 Bull"],
    "SPY": ["S&P 500"], "SQQQ": ["UltraPro Short QQQ", "Short QQQ"],
    "TECL": ["Technology Bull"], "TECS": ["Technology Bear"],
    "TLT": ["20+ Year"], "TQQQ": ["UltraPro QQQ"],
    "VOOG": ["S&P 500 Growth"], "VOOV": ["S&P 500 Value"],
    "VOX": ["Communication"], "VTV": ["Value"],
    "XBI": ["Biotech"], "XLF": ["Financial Select"],
    "XLK": ["Technology Select"], "XLP": ["Consumer Staples"],
    "XLY": ["Consumer Discretionary"],
    "RYMFX": ["Managed Futures"],
}


def resolve_name(t: str) -> tuple[str, str]:
    """(name, status). Never raises."""
    try:
        info = yf.Ticker(t).info or {}
    except Exception as e:
        return "", f"info fetch failed: {type(e).__name__}"
    name = info.get("longName") or info.get("shortName") or ""
    return name, ("ok" if name else "no name in info")


def main() -> None:
    files = sorted(p.stem for p in (ROOT / "data" / "raw" / "etf").glob("*.parquet"))
    assert len(files) == 36, f"expected 36 parquets, found {len(files)}"
    missing_expect = [t for t in files if t not in EXPECTED]
    assert not missing_expect, f"no expected entity recorded for {missing_expect}"

    # ---- POSITIVE CONTROL: SPY must resolve to an S&P 500 name -----------
    spy_name, spy_status = resolve_name("SPY")
    assert spy_status == "ok" and "s&p 500" in spy_name.lower(), (
        f"CONTROL FAILED: SPY resolved to {spy_name!r} ({spy_status}); "
        "no mismatch elsewhere can be trusted"
    )
    print(f"CONTROL PASSED: SPY -> {spy_name!r}\n")

    rows = []
    for t in files:
        f = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{t}.parquet")
        idx = pd.to_datetime(f.index)
        name, status = (spy_name, "ok") if t == "SPY" else resolve_name(t)
        kws = EXPECTED[t]
        if status != "ok":
            verdict = "UNVERIFIABLE"
        elif any(k.lower() in name.lower() for k in kws):
            verdict = "match"
        else:
            verdict = "MISMATCH"
        rows.append(dict(
            ticker=t, resolved_name=name, status=status,
            expected_keywords="; ".join(kws), verdict=verdict,
            first_date_held=str(idx.min().date()),
            last_date_held=str(idx.max().date()),
        ))
        print(f"  {t:6s} {verdict:12s} {name}")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "ticker-entity-check.csv", index=False)
    n_bad = (df.verdict == "MISMATCH").sum()
    n_unv = (df.verdict == "UNVERIFIABLE").sum()
    print(f"\n{len(df)} tickers: {len(df) - n_bad - n_unv} match, "
          f"{n_bad} MISMATCH, {n_unv} unverifiable")
    print("WROTE outputs/session-05/ticker-entity-check.csv")


if __name__ == "__main__":
    main()
