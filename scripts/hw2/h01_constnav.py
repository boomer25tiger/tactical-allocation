"""h01. Constant-NAV re-run of the designated cell (slides 9, 10, 15, 17).

The canonical engine compounds NAV from a $1M start, so its capacity sweep
mixes account size, compounding and the trading volume of each era. This
script re-runs the designated cell (realized panel, open-to-open, class-tiered
slippage with the 2.0x auction premium, commission arm S, 5% participation
cap) with capital topped up or withdrawn after every session so NAV is held
constant. Signals, costs and the cap are the engine's own.

Writes to outputs/hw2/
    constnav-sweep.csv           return, vol, naive Sharpe, max DD by NAV and era
    constnav-by-instrument.csv   capped transitions and dollars sent to cash
    constnav-10m-daily.csv       daily constant-$10M engine return ('strat'),
                                 QQQ open-to-open return ('qqq') and T-bill
                                 return ('rf') from the first session; every
                                 fund figure in scripts/hw2/h04_fund.py reads it
    dollar-volume-by-year.csv    median daily dollar volume of SOXL and TQQQ
Run time is about a minute.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import *  # noqa: F401,F403,E402  (panel, signals, run, stats, RF, OUT)
from engine import OUT, bt, C, o2o, cal, run, stats, RF, pd  # noqa: E402

# Validation: no reset at $1M must reproduce the canonical primary figures.
d0, *_ = run(1_000_000.0, reset=False)
r0 = d0["ret"].loc[(d0.index >= C.PRIMARY_START) & (d0.index < bt.HOLDOUT_BOUNDARY)].dropna()
cagr0 = (1 + r0).prod() ** (252.0 / len(r0)) - 1
print(f"validation, compounding $1M, primary CAGR {cagr0:.6f} over {len(r0)} sessions "
      "(canonical 0.521845 over 2472)")

WIN = {
    "2011-10 to 2016-07": ("2011-10-04", "2016-07-31"),
    "2012-01 to 2016-07": ("2012-01-03", "2016-07-31"),
    "2016-08 to 2021-07": ("2016-08-01", "2021-07-31"),
    "holdout 2021-08 to 2026-08": ("2021-08-01", "2026-08-14"),
    "last two years 2024-08 to 2026-08": ("2024-08-15", "2026-08-14"),
}
LEVELS = [1e6, 5e6, 10e6, 25e6, 50e6, 100e6, 250e6, 500e6]

ret_arr, _, _ = bt._account_arrays(o2o, cal)
qqq = pd.Series(ret_arr["QQQ"], index=cal)

rows, inst = [], []
for lv in LEVELS:
    d, cp, tl, od = run(lv, reset=True)
    for w, (a, b) in WIN.items():
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        m = (d.index >= a) & (d.index <= b)
        tlw = tl[(tl["date"] >= a) & (tl["date"] <= b)] if len(tl) else tl
        odw = od[(od["date"] >= a) & (od["date"] <= b)] if len(od) else od
        st = stats(d["ret"][m], lv, tlw, cp, odw)
        st.update({"nav": lv, "window": w, "mean_invested": d["invested"][m].mean()})
        rows.append(st)
        if len(cp):
            cw = cp[(cp["date"] >= a) & (cp["date"] <= b)]
            for t, gg in cw.groupby("ticker"):
                inst.append({"nav": lv, "window": w, "ticker": t,
                             "capped_transitions": len(gg),
                             "mean_frac_capped": gg["frac_capped"].mean(),
                             "dollars_to_cash": (gg["target"] - gg["cap"]).sum()})
    print(f"done {lv:,.0f}")

for w, (a, b) in WIN.items():
    m = (qqq.index >= pd.Timestamp(a)) & (qqq.index <= pd.Timestamp(b))
    st = stats(qqq[m])
    st.update({"nav": "QQQ", "window": w})
    rows.append(st)

res = pd.DataFrame(rows)
res.to_csv(OUT / "constnav-sweep.csv", index=False)
pd.DataFrame(inst).to_csv(OUT / "constnav-by-instrument.csv", index=False)
pd.set_option("display.width", 220)
for w in WIN:
    print("\n==", w)
    print(res[res.window == w][["nav", "cagr", "vol", "sharpe_naive", "max_dd",
                                "to_cash_share", "capped_transitions",
                                "mean_invested", "turnover"]].round(3).to_string(index=False))


# The constant-$10M daily series that every fund figure reads.
d10, *_ = run(10e6, reset=True)
r10 = d10["ret"].dropna()
q10 = qqq.reindex(r10.index).fillna(0.0)
rf10 = RF.reindex(r10.index).fillna(0.0)
pd.DataFrame({"strat": r10, "qqq": q10, "rf": rf10}).to_csv(OUT / "constnav-10m-daily.csv")
print(f"constant-$10M daily series {r10.index[0].date()} to {r10.index[-1].date()}, {len(r10)} sessions")

# Median daily dollar volume by calendar year, for the capacity slide.
dvrows = []
for t in ("SOXL", "TQQQ"):
    raw = bt._load_raw(t)
    dv = (raw["Volume"].astype(float) * raw["Close"].astype(float)).where(raw["Volume"].astype(float) > 0)
    for y, v in dv.groupby(dv.index.year).median().items():
        dvrows.append({"ticker": t, "year": int(y), "median_dollar_volume": float(v)})
pd.DataFrame(dvrows).to_csv(OUT / "dollar-volume-by-year.csv", index=False)
