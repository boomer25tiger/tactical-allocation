"""Session 13.8 steps 8-9: BTAL capacity (contemporaneous) and the
concentration set under per-year covariance (5.7 registered canonical)."""
from __future__ import annotations

import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
from src import config

OUT = ROOT / "outputs" / "session-13.8"
st = pickle.load(open(OUT / "_anchor_run.pkl", "rb"))
daily = st["daily"]
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                   for r in st["raw_rows"]], index=daily.index)
nav = daily["nav"]

# ---------------- step 8: capacity, contemporaneous ------------------------
rows8 = []
print("== step 8: capacity vs contemporaneous median dollar volume ==")
for t in ra.TARGET_TICKERS:
    raw = bt._load_raw(t)
    dvol = (raw["Volume"].astype(float) * raw["Close"].astype(float))
    dvol = dvol[raw["Volume"].fillna(0) > 0]
    pos = (rw[t] * nav)
    worst = None
    for y in sorted(set(daily.index.year)):
        p_y = pos[pos.index.year == y]
        v_y = dvol[dvol.index.year == y]
        if not len(p_y) or not len(v_y) or p_y.max() <= 0:
            continue
        ratio = float(p_y.max() / v_y.median())
        rows8.append({"table": "by_year", "ticker": t, "year": y,
                      "max_position": round(float(p_y.max())),
                      "median_dollar_volume_same_year": round(float(v_y.median())),
                      "ratio": round(ratio, 4)})
        if worst is None or ratio > worst[1]:
            worst = (y, ratio)
    if worst:
        rows8.append({"table": "per_instrument_worst", "ticker": t,
                      "worst_year": worst[0], "worst_ratio": round(worst[1], 4)})
w8 = pd.DataFrame([r for r in rows8 if r["table"] == "per_instrument_worst"])
w8 = w8.sort_values("worst_ratio", ascending=False)
print(w8.head(5).to_string(index=False))
# affected sessions for any instrument whose contemporaneous ratio > 1
for t in w8[w8.worst_ratio > 1]["ticker"]:
    raw = bt._load_raw(t)
    dvol = (raw["Volume"].astype(float) * raw["Close"].astype(float))
    dvol = dvol[raw["Volume"].fillna(0) > 0]
    pos = (rw[t] * nav)
    for y in sorted(set(daily.index.year)):
        p_y = pos[(pos.index.year == y) & (pos > 0)]
        v_y = dvol[dvol.index.year == y]
        if not len(p_y) or not len(v_y):
            continue
        med = float(v_y.median())
        bad = p_y[p_y > med]
        for d, v in bad.items():
            rows8.append({"table": "affected_sessions", "ticker": t,
                          "date": str(d.date()), "position": round(float(v)),
                          "same_year_median_dvol": round(med),
                          "ratio": round(float(v) / med, 2)})
n_aff = len([r for r in rows8 if r["table"] == "affected_sessions"])
print(f"  affected sessions (position > same-year median dvol): {n_aff}")
pd.DataFrame(rows8).to_csv(OUT / "capacity.csv", index=False)

# ---------------- step 9: concentration under per-year covariance ----------
print("== step 9: ENB per-year covariance (canonical) + concentration set ==")
rows9 = []
sig = bt.ArmSignals(bt.load_arm_panel("synthetic"), bt.load_arm_panel("synthetic")["SPY"].index)
# ENB per-year vs fixed
ret_panel = pd.DataFrame({t: pd.read_parquet(
    ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")["syn_ret"]
    if (ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet").exists()
    else bt.build_ticker_frame(t, bt._load_raw(t)).ret_total
    for t in ra.TARGET_TICKERS})
ret_panel.index = pd.to_datetime(ret_panel.index).normalize()
ret_panel = ret_panel.reindex(daily.index)
cov_full = ret_panel.dropna().cov().to_numpy() * 252
t_full = ra.min_torsion(cov_full)
enb_fixed = ra.enb_series(rw[list(ra.TARGET_TICKERS)], cov_full, t_full)
enb_year = pd.Series(np.nan, index=daily.index)
for y in sorted(set(daily.index.year)):
    m_ = daily.index.year == y
    sub = ret_panel[m_].dropna(axis=1, how="any")
    ticks = [t for t in ra.TARGET_TICKERS if t in sub.columns]
    Sig_y = sub[ticks].cov().to_numpy() * 252
    t_y = ra.min_torsion(Sig_y)
    e_y = ra.enb_series(rw.loc[m_, ticks], Sig_y, t_y)
    enb_year.loc[m_] = e_y
    rows9.append({"table": "enb_by_year", "year": int(y), "n_tickers": len(ticks),
                  "enb_per_year_cov_mean": float(e_y.mean()),
                  "enb_fixed_cov_mean": float(enb_fixed[m_].mean()),
                  "gap": float(e_y.mean() - enb_fixed[m_].mean())})
rows9.append({"table": "enb_summary",
              "enb_per_year_mean": float(enb_year.mean()),
              "enb_fixed_mean": float(enb_fixed.mean()),
              "note": "per-year covariance CANONICAL (5.7 registered, post-hoc "
                      "9.10, 2026-08-18); fixed-window retained as comparison"})
print(f"  ENB canonical (per-year) mean {enb_year.mean():.2f} vs fixed "
      f"{enb_fixed.mean():.2f}")

# full concentration set under canonical ENB
mult = {}
for t in ra.TARGET_TICKERS:
    fr = bt.load_arm_panel("synthetic")[t].frame if False else None
mult_cache = {}
p_syn = bt.load_arm_panel("synthetic")
for t in ra.TARGET_TICKERS:
    fr = p_syn[t].frame
    if "multiple" in fr.columns and fr["multiple"].notna().any():
        mult_cache[t] = fr["multiple"].reindex(daily.index).to_numpy()
    else:
        mult_cache[t] = (np.zeros(len(daily)) if t == "BTAL"
                         else np.ones(len(daily)))
eff = pd.Series(sum(rw[t].to_numpy() * mult_cache[t] for t in ra.TARGET_TICKERS),
                index=daily.index)
enc_t = ra.enc(rw)
ug = {}
for t in ra.TARGET_TICKERS:
    ug.setdefault(bt.UNDERLYING[t], []).append(t)
u_df = pd.DataFrame({g: rw[c].sum(axis=1) for g, c in ug.items()})
enc_u = ra.enc(u_df)
mx_t = rw.max(axis=1)
top3 = pd.Series(np.sort(rw.to_numpy(), axis=1)[:, -3:].sum(axis=1), index=rw.index)
for name, s in (("enc_tickers", enc_t), ("enc_underlyings", enc_u),
                ("enb_canonical", enb_year), ("eff_exposure", eff),
                ("max_single_ticker", mx_t), ("top3_sum", top3)):
    rows9.append({"table": "concentration_summary", "metric": name,
                  "mean": float(s.mean()), "median": float(s.median())})
dd = nav / nav.cummax() - 1
q5 = pd.qcut(dd, 5, labels=False, duplicates="drop")
for qi in range(5):
    m_ = q5 == qi
    rows9.append({"table": "dd_quintile", "quintile": int(qi),
                  "note": "0 = deepest drawdown",
                  "dd_range": f"{dd[m_].min():.3f}..{dd[m_].max():.3f}",
                  "enb_canonical": float(enb_year[m_].mean()),
                  "enc_tickers": float(enc_t[m_].mean()),
                  "eff_exposure": float(eff[m_].mean())})
qtrail = pd.Series(sig.crash[config.WARMUP_SESSIONS:], index=daily.index)
qqq_r = pd.Series(p_syn["QQQ"].ret_total.reindex(p_syn["SPY"].index).to_numpy()[config.WARMUP_SESSIONS:],
                  index=daily.index)
qvol = qqq_r.rolling(60).std() * math.sqrt(252)
for nm, ser in (("qqq_trailing60_return_decile", qtrail),
                ("qqq_trailing60_vol_decile", qvol)):
    decs = pd.qcut(ser, 10, labels=False, duplicates="drop")
    for di in sorted(decs.dropna().unique()):
        m_ = decs == di
        rows9.append({"table": nm, "decile": int(di),
                      "enb_canonical": float(enb_year[m_].mean()),
                      "eff_exposure": float(eff[m_].mean())})
pd.DataFrame(rows9).to_csv(OUT / "concentration.csv", index=False)
print(f"[wrote capacity.csv, concentration.csv]")
