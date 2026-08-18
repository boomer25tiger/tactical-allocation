"""Session 09, step 2: financing-rate harvest from N-CSR schedules (2.14).

Harvests per-swap floating financing rates for the twelve swap-based funds
from annual-report schedules of investments. Bounded: the most recent
annual N-CSRs per trust plus an older probe; partial coverage is the
expected outcome and is reported as such. Every extracted row carries the
raw text snippet it came from, for audit.
"""

import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import html as htmllib

import pandas as pd
import requests

OUT = ROOT / "outputs" / "session-09"
OUT.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "tactical-allocation research cgualytx@gmail.com"}

TRUSTS = {
    "ProShares Trust": dict(
        cik=1174610,
        funds={
            "TQQQ": ["UltraPro QQQ"],
            "QLD": ["Ultra QQQ"],
            "SQQQ": ["UltraPro Short QQQ"],
            "PSQ": ["Short QQQ"],
            "SH": ["Short S&P500", "Short S&P 500"],
        },
        marker="UltraPro QQQ",
    ),
    "Direxion Shares ETF Trust": dict(
        cik=1424958,
        funds={
            "TECL": ["Technology Bull 3X"],
            "TECS": ["Technology Bear 3X"],
            "SOXL": ["Semiconductor Bull 3X"],
            "SOXS": ["Semiconductor Bear 3X"],
            "SPXL": ["S&P 500  Bull 3X", "S&P 500 Bull 3X", "S&P 500® Bull 3X"],
            "FAS": ["Financial Bull 3X"],
            "LABU": ["S&P Biotech Bull 3X", "Biotech Bull 3X"],
        },
        marker="Semiconductor Bull 3X",
    ),
}

REF_NAMES = ["OBFR", "Overnight Bank Funding", "SOFR", "Federal Funds",
             "FEDEF", "LIBOR", "T-Bill", "Treasury Bill"]
COUNTERPARTIES = ["Goldman", "Morgan Stanley", "J.P. Morgan", "JPMorgan",
                  "Citibank", "Citigroup", "UBS", "BNP", "Societe Generale",
                  "Bank of America", "Merrill", "Barclays", "Credit Suisse",
                  "Natixis", "Nomura", "Royal Bank", "RBC", "Deutsche",
                  "Wells Fargo", "Macquarie", "TD Bank", "Canadian Imperial",
                  "Truist", "HSBC"]


def get(url, **kw):
    r = requests.get(url, headers=H, timeout=180, **kw)
    r.raise_for_status()
    return r


def ncsr_list(cik, max_n=40):
    s = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json").json()
    fr = s["filings"]["recent"]
    out = []
    for form, fdate, acc, rdate in zip(fr["form"], fr["filingDate"],
                                       fr["accessionNumber"], fr["reportDate"]):
        if form == "N-CSR":
            out.append(dict(filed=fdate, accession=acc, period=rdate))
    return out[:max_n]


def doc_text(cik, acc, cap=14_000_000):
    a2 = acc.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{cik}/{a2}/"
    items = get(base + "index.json").json()["directory"]["item"]
    docs = sorted(
        [i for i in items if i["name"].endswith(".htm") and "index" not in i["name"]],
        key=lambda i: -int(i.get("size", 0) or 0),
    )
    if not docs:
        return ""
    raw = get(base + docs[0]["name"]).text[:cap]
    txt = re.sub(r"<[^>]+>", " ", raw)
    return htmllib.unescape(re.sub(r"[ \t\r\f\v]+", " ", txt))


def harvest_fund(text, aliases):
    """Windows near the fund's schedule containing swap financing rates."""
    findings = []
    for alias in aliases:
        for m in re.finditer(re.escape(alias), text):
            seg = text[m.end(): m.end() + 60_000]
            stop = len(seg)
            # stop at the next obvious fund header to limit bleed
            nxt = re.search(r"ProShares [A-Z]|Direxion Daily [A-Z]", seg[200:])
            if nxt:
                stop = min(stop, 200 + nxt.start())
            seg = seg[:stop]
            if "financing rate" not in seg.lower() and "swap" not in seg.lower():
                continue
            for cp in COUNTERPARTIES:
                for cm in re.finditer(re.escape(cp), seg):
                    w = seg[max(0, cm.start() - 260): cm.start() + 420]
                    rates = re.findall(r"(\d{1,2}\.\d{2,4})\s*%", w)
                    if not rates:
                        continue
                    ref = next((r_ for r_ in REF_NAMES if r_.lower() in w.lower()), "")
                    findings.append(dict(counterparty=cp, rates=rates[:4],
                                         reference_named=ref,
                                         snippet=re.sub(r"\s+", " ", w)[:380]))
            if findings:
                return findings
    return findings


def main():
    # POSITIVE CONTROL: harvest logic must find rates in the document session
    # 08 already read manually -- the PT2 10-K schedule convention. Synthetic
    # control here: a hand-built schedule line must parse.
    ctrl = ("ProShares UltraPro QQQ swap agreements Goldman Sachs "
            "International financing rate 5.55% (OBFR + 0.30%) notional")
    got = harvest_fund(ctrl, ["UltraPro QQQ"])
    assert got and got[0]["rates"] == ["5.55", "0.30"] and got[0]["reference_named"] == "OBFR", got
    print("CONTROL PASSED: extraction parses a known-form schedule line\n")

    rows, coverage = [], []
    for trust, spec in TRUSTS.items():
        filings = ncsr_list(spec["cik"])
        print(f"== {trust}: {len(filings)} recent N-CSR filings ==")
        seen_periods = set()
        picked = []
        for f in filings:
            yr = f["period"][:4]
            if (yr, ) in seen_periods:
                continue
            picked.append(f)
            seen_periods.add((yr,))
            if len(picked) >= 7:
                break
        for f in picked:
            try:
                text = doc_text(spec["cik"], f["accession"])
            except Exception as e:
                print(f"  {f['period']} {f['accession']}: fetch failed {e}")
                continue
            if spec["marker"] not in text:
                coverage.append(dict(trust=trust, period=f["period"],
                                     accession=f["accession"],
                                     status="document does not cover these funds"))
                print(f"  {f['period']}: doc lacks {spec['marker']!r} - skipped")
                time.sleep(1)
                continue
            n_found = 0
            for fund, aliases in spec["funds"].items():
                found = harvest_fund(text, aliases)
                for x in found[:8]:
                    rows.append(dict(trust=trust, fund=fund,
                                     fiscal_period_end=f["period"],
                                     accession=f["accession"], **{
                                         "counterparty": x["counterparty"],
                                         "rates_pct": "; ".join(x["rates"]),
                                         "reference_named": x["reference_named"],
                                         "snippet": x["snippet"]}))
                coverage.append(dict(trust=trust, fund=fund, period=f["period"],
                                     accession=f["accession"],
                                     status=(f"{len(found)} rate rows"
                                             if found else "no rates parsed")))
                n_found += len(found)
            print(f"  {f['period']} {f['accession']}: {n_found} rate rows "
                  f"across funds")
            time.sleep(1.5)

    df = pd.DataFrame(rows)
    cov = pd.DataFrame(coverage)
    df.to_csv(OUT / "financing-rates-raw.csv", index=False)
    cov.to_csv(OUT / "financing-coverage.csv", index=False)
    print(f"\nWROTE financing-rates-raw.csv ({len(df)} rows), "
          f"financing-coverage.csv ({len(cov)} rows)")
    if len(df):
        print("\nsample rows:")
        print(df[["fund", "fiscal_period_end", "counterparty", "rates_pct",
                  "reference_named"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
