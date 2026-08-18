"""Session 00a, step 2. Download monthly VX contracts expiring 2004-2026.

Source policy, fixed after the step 1 discovery:
  expiry year 2004-2013 -> archive pattern   CFE_<MC><YY>_VX.csv
  expiry year 2014-2026 -> current pattern   VX_<YYYY-MM-DD>.csv (paths from the CFE API)

Rationale recorded in outputs/session-00a/source-notes.md. Weekly contracts are
excluded by the duration_type field returned by the API and by the archive
pattern being monthly-only by construction.
"""
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "vx"
OUT = ROOT / "outputs" / "session-00a"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
H = {"User-Agent": UA}

MONTH_CODES = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
CODE_TO_MONTH = {c: i + 1 for i, c in enumerate(MONTH_CODES)}

ARCHIVE_TMPL = "https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_{mc}{yy}_VX.csv"
API_LIST = "https://www-api.cboe.com/us/futures/market_statistics/historical_data/product/list/VX/"
CDN_BASE = "https://cdn.cboe.com/"

ARCHIVE_YEARS = range(2004, 2014)   # 2004-2013 inclusive
API_YEARS = range(2014, 2027)       # 2014-2026 inclusive

SLEEP = 0.35
MAX_ATTEMPTS = 3


def fetch(url, attempts=MAX_ATTEMPTS):
    """Return (status, content, error). Retries only transport errors and 5xx."""
    last_err = ""
    for k in range(attempts):
        try:
            r = requests.get(url, headers=H, timeout=60)
            if r.status_code >= 500:
                last_err = f"HTTP {r.status_code}"
                time.sleep(1.5 * (k + 1))
                continue
            return r.status_code, r.content, ""
        except Exception as e:                      # transport failure
            last_err = f"{type(e).__name__}: {e}"[:200]
            time.sleep(1.5 * (k + 1))
    return None, b"", last_err


def looks_like_csv(content):
    """Header may be preceded by a one-line CFE disclaimer in some archive files."""
    head = content[:2000].decode("utf-8", "replace").splitlines()
    return any(ln.startswith("Trade Date,Futures,") for ln in head[:4])


def main():
    # ---- enumerate the API side, and count weeklies while we are there -------
    st, body, err = fetch(API_LIST)
    if st != 200:
        raise SystemExit(f"product list fetch failed: {st} {err}")
    listing = json.loads(body)
    (OUT / "vx-product-list-raw.json").write_text(json.dumps(listing, indent=1))

    weekly_rows, api_monthly = [], []
    for year_key, items in listing.items():
        for it in items:
            exp = it["expire_date"]
            yr = int(exp[:4])
            rec = dict(it, expiry_year=yr)
            if it["duration_type"] == "M":
                api_monthly.append(rec)
            else:
                weekly_rows.append(rec)

    with (OUT / "vx-weeklies-excluded.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["expiry_year", "expire_date", "product_display",
                    "duration_type", "path"])
        for r in sorted(weekly_rows, key=lambda x: x["expire_date"]):
            w.writerow([r["expiry_year"], r["expire_date"], r["product_display"],
                        r["duration_type"], r["path"]])

    # ---- build the download plan -------------------------------------------
    plan = []
    for yr in ARCHIVE_YEARS:
        yy = f"{yr % 100:02d}"
        for mc in MONTH_CODES:
            plan.append({
                "source": "archive",
                "expiry_year": yr,
                "month_code": mc,
                "expected_month": CODE_TO_MONTH[mc],
                "url": ARCHIVE_TMPL.format(mc=mc, yy=yy),
                "filename": f"CFE_{mc}{yy}_VX.csv",
                "api_expire_date": "",
                "product_display": "",
            })
    for r in sorted(api_monthly, key=lambda x: x["expire_date"]):
        if r["expiry_year"] not in API_YEARS:
            continue
        plan.append({
            "source": "api",
            "expiry_year": r["expiry_year"],
            "month_code": r["product_display"].split("/")[-1][0],
            "expected_month": int(r["expire_date"][5:7]),
            "url": CDN_BASE + r["path"],
            "filename": Path(r["path"]).name,
            "api_expire_date": r["expire_date"],
            "product_display": r["product_display"],
        })

    print(f"plan: {len(plan)} candidate contracts "
          f"({sum(p['source']=='archive' for p in plan)} archive, "
          f"{sum(p['source']=='api' for p in plan)} api); "
          f"{len(weekly_rows)} weeklies excluded")

    manifest, absent, failures = [], [], []
    for i, p in enumerate(plan, 1):
        st, content, err = fetch(p["url"])
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if st == 200 and looks_like_csv(content):
            dest = RAW / p["filename"]
            dest.write_bytes(content)                       # unmodified
            text = content.decode("utf-8", "replace")
            nrows = sum(1 for ln in text.splitlines()[1:] if ln.strip())
            manifest.append({
                "filename": p["filename"],
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "row_count": nrows,
                "download_utc": ts,
                "source": p["source"],
                "expiry_year": p["expiry_year"],
                "month_code": p["month_code"],
                "url": p["url"],
            })
        elif st in (403, 404):
            absent.append({**p, "http_status": st, "checked_utc": ts})
        else:
            failures.append({**p, "http_status": st, "error": err,
                             "attempted_utc": ts})
        if i % 40 == 0:
            print(f"  {i}/{len(plan)} ok={len(manifest)} absent={len(absent)} fail={len(failures)}")
        time.sleep(SLEEP)

    with (OUT / "vx-manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["filename", "sha256", "bytes",
                                           "row_count", "download_utc",
                                           "source", "expiry_year",
                                           "month_code", "url"])
        w.writeheader()
        w.writerows(manifest)

    with (OUT / "vx-absent-urls.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["expiry_year", "month_code", "source",
                                           "http_status", "url", "checked_utc"])
        w.writeheader()
        for a in absent:
            w.writerow({k: a[k] for k in w.fieldnames})

    with (OUT / "vx-download-failures.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["expiry_year", "month_code", "source",
                                           "http_status", "error", "url",
                                           "attempted_utc"])
        w.writeheader()
        for f in failures:
            w.writerow({k: f[k] for k in w.fieldnames})

    print(f"DONE downloaded={len(manifest)} absent={len(absent)} failures={len(failures)}")


if __name__ == "__main__":
    main()
