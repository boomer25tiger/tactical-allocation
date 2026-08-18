"""Session 00e, step 1. Apply decision 1.14: truncate frozen panels to 2026-08-14.

The Session 00C pull ran at 13:19 Eastern on a trading Monday, so the final bar of
each series is a partial-session print. Rows are dropped, never adjusted.

A file is rewritten only when rows are actually removed, so that files needing no
truncation keep their original bytes and hash. VX files are not touched.
"""
import hashlib
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "etf"
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00e"
PRE = OUT / "pre-truncation-hashes"

CUTOFF = pd.Timestamp("2026-08-14")

# manifests copied verbatim before anything is modified
MANIFESTS = [
    ROOT / "outputs" / "session-00c" / "etf-manifest.csv",
    ROOT / "outputs" / "session-00c" / "pull-metadata.json",
    ROOT / "outputs" / "session-00a" / "vx-manifest.csv",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def date_of(df):
    """Return (series_of_dates, kind) for whichever date carrier the file uses."""
    if isinstance(df.index, pd.DatetimeIndex):
        return pd.Series(df.index, index=df.index), "index"
    for c in ("date", "Date", "trade_date"):
        if c in df.columns:
            return pd.to_datetime(df[c]), f"column:{c}"
    raise SystemExit("no date carrier found")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PRE.mkdir(parents=True, exist_ok=True)

    # ---- preserve original manifests before touching anything --------------
    copied = []
    for m in MANIFESTS:
        if m.exists():
            dest = PRE / f"{m.parent.name}__{m.name}"
            shutil.copy2(m, dest)
            copied.append((str(m.relative_to(ROOT)), sha256(m)))
            print(f"preserved {m.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")
        else:
            print(f"MISSING manifest: {m.relative_to(ROOT)}")
    pd.DataFrame(copied, columns=["source_file", "sha256_at_copy"]).to_csv(
        PRE / "_copied-manifests.csv", index=False)

    targets = sorted(RAW.glob("*.parquet")) + [
        INTERIM / "etf-panel.parquet",
        INTERIM / "vixy-yfinance-raw-s00b.parquet",
        INTERIM / "vxx-yfinance-raw-s00b.parquet",
        INTERIM / "vixy-nav-proshares-s00b.parquet",
    ]
    print(f"\n{len(targets)} target files "
          f"({len(list(RAW.glob('*.parquet')))} raw etf + 4 interim)")

    rows = []
    for p in targets:
        if not p.exists():
            rows.append({"filename": str(p.relative_to(ROOT)),
                         "status": "MISSING"})
            continue
        old_hash = sha256(p)
        df = pd.read_parquet(p)
        dates, kind = date_of(df)
        old_rows, old_last = len(df), dates.max()

        keep = dates <= CUTOFF
        n_drop = int((~keep).sum())

        if n_drop > 0:
            trunc = df[keep.to_numpy()]
            if kind == "index":
                trunc.to_parquet(p)
            else:
                trunc.to_parquet(p, index=False)
            new_hash = sha256(p)
            df2 = pd.read_parquet(p)
            d2, _ = date_of(df2)
            new_rows, new_last = len(df2), d2.max()
            status = "truncated"
        else:
            new_hash, new_rows, new_last = old_hash, old_rows, old_last
            status = "already_at_or_before_cutoff"

        rows.append({
            "filename": str(p.relative_to(ROOT)),
            "date_carrier": kind,
            "status": status,
            "old_sha256": old_hash,
            "new_sha256": new_hash,
            "old_rows": old_rows,
            "new_rows": new_rows,
            "rows_dropped": old_rows - new_rows,
            "old_last_date": old_last.date().isoformat(),
            "new_last_date": new_last.date().isoformat(),
        })

    man = pd.DataFrame(rows)
    man.to_csv(OUT / "manifest-truncated.csv", index=False)

    trunc = man[man.status == "truncated"]
    already = man[man.status == "already_at_or_before_cutoff"]
    multi = man[man.rows_dropped > 1]
    print(f"\ntruncated: {len(trunc)}   already at/before cutoff: {len(already)}"
          f"   >1 row dropped: {len(multi)}")
    if len(already):
        print("\nANOMALY, already at or before cutoff:")
        print(already[["filename", "old_last_date", "old_rows"]].to_string(index=False))
    if len(multi):
        print("\nANOMALY, more than one row dropped:")
        print(multi[["filename", "rows_dropped", "old_last_date",
                     "new_last_date"]].to_string(index=False))
    print("\nnew_last_date values across all files:",
          sorted(man.new_last_date.dropna().unique()))
    print("rows_dropped distribution:",
          man.rows_dropped.value_counts().to_dict())


if __name__ == "__main__":
    main()
