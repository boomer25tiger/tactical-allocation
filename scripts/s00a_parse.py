"""Session 00a, step 3. Parse raw VX contract files into a long panel.

Handles three format variants found in step 1:
  - optional one-line CFE disclaimer above the header
  - trade dates as M/D/YYYY, MM/DD/YYYY or YYYY-MM-DD
  - the Futures label as "K (May 04)" or "M (Jun 2016)"
No values are altered here. Scale/quotation questions are measured, not corrected.
"""
import csv
import io
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "vx"
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00a"
INTERIM.mkdir(parents=True, exist_ok=True)

MONTH_CODES = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
CODE_TO_MONTH = {c: i + 1 for i, c in enumerate(MONTH_CODES)}
MONTH_TO_CODE = {v: k for k, v in CODE_TO_MONTH.items()}

NUMCOLS = ["Open", "High", "Low", "Close", "Settle", "Change",
           "Total Volume", "EFP", "Open Interest"]


def parse_date(s):
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return date.fromisoformat(s)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", s)
    if m:
        mo, da, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yr < 100:
            yr += 2000
        return date(yr, mo, da)
    raise ValueError(f"unparsed date {s!r}")


def third_friday(y, m):
    d = date(y, m, 1)
    fridays = [d + timedelta(days=i) for i in range(31)
               if (d + timedelta(days=i)).month == m
               and (d + timedelta(days=i)).weekday() == 4]
    return fridays[2]


def rule_expiry(exp_year, month_code):
    """Pre-registered cross-check: 30 days before the third Friday of the
    FOLLOWING month. Applied mechanically, holidays not adjusted for."""
    m = CODE_TO_MONTH[month_code]
    ny, nm = (exp_year + 1, 1) if m == 12 else (exp_year, m + 1)
    return third_friday(ny, nm) - timedelta(days=30)


def read_rows(path):
    text = path.read_bytes().decode("utf-8", "replace")
    lines = text.splitlines()
    hdr = next(i for i, ln in enumerate(lines[:5])
               if ln.startswith("Trade Date,Futures,"))
    body = "\n".join(lines[hdr:])
    return list(csv.DictReader(io.StringIO(body)))


def main():
    man = pd.read_csv(OUT / "vx-manifest.csv")
    recs, meta = [], []

    for _, mrow in man.iterrows():
        path = RAW / mrow["filename"]
        rows = read_rows(path)
        mc, ey = mrow["month_code"], int(mrow["expiry_year"])
        contract = f"VX{mc}{ey}"

        parsed = []
        for r in rows:
            if not (r.get("Trade Date") or "").strip():
                continue
            vals = {}
            for c in NUMCOLS:
                raw = (r.get(c) or "").strip().replace(",", "")
                vals[c] = float(raw) if raw not in ("", "-") else float("nan")
            parsed.append({
                "trade_date": parse_date(r["Trade Date"]),
                "contract": contract,
                "futures_label": (r.get("Futures") or "").strip(),
                "open": vals["Open"], "high": vals["High"], "low": vals["Low"],
                "close": vals["Close"], "settle": vals["Settle"],
                "change": vals["Change"], "volume": vals["Total Volume"],
                "efp": vals["EFP"], "open_interest": vals["Open Interest"],
                "source_file": mrow["filename"], "source": mrow["source"],
                "month_code": mc, "expiry_year": ey,
            })

        parsed.sort(key=lambda x: x["trade_date"])
        derived_expiry = parsed[-1]["trade_date"]          # last row of the file
        for p in parsed:
            p["expiry_date"] = derived_expiry
        recs.extend(parsed)

        rex = rule_expiry(ey, mc)
        meta.append({
            "contract": contract, "expiry_year": ey, "month_code": mc,
            "source": mrow["source"], "n_rows": len(parsed),
            "first_trade_date": parsed[0]["trade_date"],
            "derived_expiry": derived_expiry,
            "rule_expiry": rex,
            "expiry_match": derived_expiry == rex,
            "diff_days": (derived_expiry - rex).days,
            "median_settle": pd.Series([p["settle"] for p in parsed]).median(),
        })

    df = pd.DataFrame(recs)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"])

    # final settlement row: the contract's own expiry session
    df["final_settlement_row"] = df["trade_date"] == df["expiry_date"]
    zero_ohlc = (df[["open", "high", "low", "close"]].fillna(0) == 0).all(axis=1)
    df["final_zero_ohlc_signature"] = (df["final_settlement_row"] & zero_ohlc
                                       & (df["volume"].fillna(0) == 0)
                                       & (df["settle"] > 0))

    # ---- quotation rescale, measured not assumed -----------------------------
    # Cross-contract median settle falls by ~1/10 on exactly one date. Detect it
    # rather than hard-coding, then normalise pre-break quotes to index points.
    med = df[df["settle"] > 0].groupby("trade_date")["settle"].median()
    ratio = med / med.shift(1)
    breaks = ratio[(ratio < 0.2) | (ratio > 5.0)]
    if len(breaks) != 1:
        raise SystemExit(f"expected exactly one quotation break, found {list(breaks.index)}")
    SCALE_DATE = breaks.index[0]
    print(f"quotation rescale detected at {SCALE_DATE.date()} ratio={breaks.iloc[0]:.6f}")

    df["scale_normalised"] = df["trade_date"] < SCALE_DATE
    for c in ["open", "high", "low", "close", "settle"]:
        df[c + "_idx"] = df[c].where(~df["scale_normalised"], df[c] / 10.0)

    # ---- effective expiry ----------------------------------------------------
    # expiry_date is derived from the last row as specified. For contracts that
    # have not yet expired the last row is simply the last session in the pull,
    # so a rule-based expiry is carried separately for use in step 5.
    last_session = df["trade_date"].max()
    meta = pd.DataFrame(meta).sort_values(["expiry_year", "month_code"])
    meta["rule_expiry"] = pd.to_datetime(meta["rule_expiry"])
    meta["derived_expiry"] = pd.to_datetime(meta["derived_expiry"])
    meta["expired"] = meta["rule_expiry"] <= last_session
    meta["expiry_effective"] = meta["derived_expiry"].where(meta["expired"],
                                                            meta["rule_expiry"])
    meta.to_csv(OUT / "vx-contract-meta.csv", index=False)
    df = df.merge(meta[["contract", "expiry_effective", "expired"]],
                  on="contract", how="left")

    # ---------------- data quality ------------------------------------------
    dup = (df.groupby(["trade_date", "contract"]).size()
             .reset_index(name="n").query("n > 1"))
    nonpos = df[~(df["settle"] > 0)]
    hilo = df[df["high"] < df["low"]]

    qc = {
        "contracts_parsed": len(meta),
        "panel_rows": len(df),
        "duplicate_pairs": len(dup),
        "nonpositive_settle_rows": len(nonpos),
        "high_below_low_rows": len(hilo),
        "final_settlement_rows": int(df["final_settlement_row"].sum()),
        "final_rows_zero_ohlc_signature": int(df["final_zero_ohlc_signature"].sum()),
        "expiry_mismatches": int((~meta["expiry_match"]).sum()),
    }
    for k, v in qc.items():
        print(f"{k:35s} {v}")

    dup.to_csv(OUT / "qc-duplicates.csv", index=False)
    nonpos.to_csv(OUT / "qc-nonpositive-settle.csv", index=False)
    hilo.to_csv(OUT / "qc-high-below-low.csv", index=False)
    meta[~meta["expiry_match"]].to_csv(OUT / "qc-expiry-mismatch.csv", index=False)

    print("\nmedian settle by expiry year (quotation scale check):")
    print(meta.groupby("expiry_year")["median_settle"].median().to_string())

    print("\nhigh<low rows by year:")
    if len(hilo):
        print(hilo.groupby(hilo["trade_date"].dt.year).size().to_string())

    cols = ["trade_date", "contract", "expiry_date", "open", "high", "low",
            "close", "settle", "volume", "open_interest",
            "final_settlement_row", "final_zero_ohlc_signature",
            "settle_idx", "open_idx", "high_idx", "low_idx", "close_idx",
            "scale_normalised", "expiry_effective", "expired",
            "change", "efp", "month_code", "expiry_year", "source",
            "source_file", "futures_label"]
    df = df[cols].sort_values(["trade_date", "expiry_date"]).reset_index(drop=True)
    df.to_parquet(INTERIM / "vx-panel.parquet", index=False)
    print(f"\nwrote {INTERIM/'vx-panel.parquet'} rows={len(df)}")


if __name__ == "__main__":
    main()
