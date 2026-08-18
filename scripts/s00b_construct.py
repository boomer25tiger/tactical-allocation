"""Session 00b, step 2. Build three constant-maturity VX constructions.

A. Interpolation      -- Session 00A series, reused unchanged.
B. S&P roll           -- as documented in outputs/session-00b/methodology-notes.md.
C. Fixed 2-contract   -- business-day linear roll, simple baseline.

Session 00A artifacts are read only. Nothing in outputs/session-00a/ or
data/interim/vx-cm30.parquet or vx-panel.parquet is written to.

No strategy return, Sharpe ratio, allocation, signal or performance statistic is
computed. These are price-series constructions and data properties.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00b"
OUT.mkdir(parents=True, exist_ok=True)


def load_panel():
    p = pd.read_parquet(INTERIM / "vx-panel.parquet")
    p = p[(p["settle_idx"] > 0)].copy()
    p["expiry_effective"] = pd.to_datetime(p["expiry_effective"])
    p["trade_date"] = pd.to_datetime(p["trade_date"])
    return p


def price_lookup(panel):
    """(trade_date, contract) -> settle_idx, plus expiry per contract."""
    px = panel.set_index(["trade_date", "contract"])["settle_idx"]
    px = px[~px.index.duplicated()]
    exp = panel.groupby("contract")["expiry_effective"].first()
    return px, exp


def listed_by_date(panel):
    """trade_date -> list of (expiry, contract, price) sorted by expiry."""
    out = {}
    for t, g in panel.groupby("trade_date"):
        g = g.sort_values("expiry_effective")
        out[t] = list(zip(g["expiry_effective"].to_numpy(),
                          g["contract"].to_numpy(),
                          g["settle_idx"].to_numpy()))
    return out


def bdays_between(sess, d0, d1):
    """Business days between two dates on the observed session calendar."""
    return int(((sess > d0) & (sess <= d1)).sum())


def interp_unlisted(sess, listed_t, target_exp):
    """S&P documented handling for a contract that was not listed on date t.

    DCRP^2_i = DCRP^2_{i-1} + BDays(T_i - T_{i-1})/BDays(T_{i+1} - T_{i-1})
                              * (DCRP^2_{i+1} - DCRP^2_{i-1})
    Returns (price, mode) or (None, None).
    """
    lo = [x for x in listed_t if x[0] < target_exp]
    hi = [x for x in listed_t if x[0] > target_exp]
    if lo and hi:
        e0, _, p0 = lo[-1]
        e1, _, p1 = hi[0]
        span = bdays_between(sess, e0, e1)
        if span <= 0:
            return None, None
        frac = bdays_between(sess, e0, target_exp) / span
        v = p0 ** 2 + frac * (p1 ** 2 - p0 ** 2)
        return (float(np.sqrt(v)) if v > 0 else None), "interpolated"
    if len(lo) >= 2:                                   # extrapolate from below
        e0, _, p0 = lo[-2]
        e1, _, p1 = lo[-1]
        span = bdays_between(sess, e0, e1)
        if span <= 0:
            return None, None
        frac = bdays_between(sess, e0, target_exp) / span
        v = p0 ** 2 + frac * (p1 ** 2 - p0 ** 2)
        return (float(np.sqrt(v)) if v > 0 else None), "extrapolated"
    return None, None


def held_returns(weights_by_date, sessions, px):
    """CDR_t = sum_i w_{i,t-1} P_{i,t} / sum_i w_{i,t-1} P_{i,t-1} - 1.

    Weights attach to contract identity, so a label change between t-1 and t does
    not break the carry. Returns (cdr Series, n_missing_price).
    """
    cdr, missing = {}, 0
    for prev, cur in zip(sessions[:-1], sessions[1:]):
        w = weights_by_date.get(prev)
        if not w:
            continue
        num = den = 0.0
        ok = True
        for c, wt in w.items():
            if wt == 0:
                continue
            p0 = px.get((prev, c))
            p1 = px.get((cur, c))
            if p0 is None or p1 is None or not np.isfinite(p0) or not np.isfinite(p1):
                ok = False
                break
            num += wt * p1
            den += wt * p0
        if not ok or den <= 0:
            missing += 1
            continue
        cdr[cur] = num / den - 1.0
    return pd.Series(cdr).sort_index(), missing


# --------------------------------------------------------------------------- B
def build_sp_roll(panel, sessions, settle_dates, px, exp, listed, px_aug):
    """S&P 500 VIX Short-Term Futures Index roll.

    Roll period k spans [W_k, W_{k+1}).  Within it the 1st month contract (m) is
    the one expiring at W_{k+1} and the 2nd (n) the one expiring at W_{k+2}.
        dt = business days in [period_start, period_end)
        dr = business days strictly between t and period_end
        CRW_m = dr/dt,  CRW_n = (dt-dr)/dt
    """
    sess = np.array(sessions)
    W = np.array(settle_dates)
    by_expiry = {v: k for k, v in exp.items()}

    rows, weights_by_date = [], {}
    for t in sessions:
        idx = int(np.searchsorted(W, t, side="right"))
        if idx + 1 >= len(W):
            continue                                   # no 2nd month available
        m_exp, n_exp = W[idx], W[idx + 1]
        period_end = m_exp
        if idx == 0:
            period_start = sess[0]                     # partial opening period
            partial = True
        else:
            period_start = W[idx - 1]
            partial = False

        dt = int(((sess >= period_start) & (sess < period_end)).sum())
        dr = int(((sess > t) & (sess < period_end)).sum())
        if dt <= 0:
            continue
        w_m = dr / dt
        w_n = 1.0 - w_m

        cm, cn = by_expiry.get(m_exp), by_expiry.get(n_exp)
        if cm is None or cn is None:
            continue

        # S&P documented handling when a required contract was not listed
        fill = ""
        for c, e in ((cm, m_exp), (cn, n_exp)):
            if px.get((t, c)) is None:
                p, mode = interp_unlisted(sess, listed[t], e)
                if p is None:
                    fill = "unavailable"
                    break
                px_aug[(t, c)] = p
                fill = mode
        if fill == "unavailable":
            continue

        weights_by_date[t] = {cm: w_m, cn: w_n}
        rows.append({
            "trade_date": t, "front_contract": cm, "second_contract": cn,
            "d1": (m_exp - t).days, "d2": (n_exp - t).days,
            "w1": w_m, "w2": w_n, "dt": dt, "dr": dr,
            "period_start": period_start, "period_end": period_end,
            "partial_period": partial, "price_fill": fill,
        })
    return pd.DataFrame(rows), weights_by_date


# --------------------------------------------------------------------------- C
def build_fixed_roll(panel, sessions, px, exp):
    """Front and second weighted linearly by business days remaining until the
    front expires, reaching zero front weight on the expiry session.

    Front is the nearest contract with expiry >= t, so on the expiry session the
    expiring contract is the front and carries weight zero.
    """
    sess = np.array(sessions)
    d = panel[["trade_date", "contract", "expiry_effective"]].copy()
    d = d[d["expiry_effective"] >= d["trade_date"]]
    d["dte"] = (d["expiry_effective"] - d["trade_date"]).dt.days
    d = d.sort_values(["trade_date", "dte", "contract"])
    d["rank"] = d.groupby("trade_date").cumcount()
    front = d[d["rank"] == 0].set_index("trade_date")
    second = d[d["rank"] == 1].set_index("trade_date")

    expiries = np.array(sorted(exp.unique()))
    rows, weights_by_date = [], {}
    for t in sessions:
        if t not in front.index or t not in second.index:
            continue
        c1, e1 = front.at[t, "contract"], front.at[t, "expiry_effective"]
        c2, e2 = second.at[t, "contract"], second.at[t, "expiry_effective"]

        # previous expiry, the start of the current cycle
        prior = expiries[expiries < e1]
        e0 = prior[-1] if len(prior) else sess[0] - pd.Timedelta(days=1)

        cycle = int(((sess > e0) & (sess <= e1)).sum())
        remain = int(((sess > t) & (sess <= e1)).sum())
        if cycle <= 0:
            continue
        w1 = remain / cycle
        w2 = 1.0 - w1
        if px.get((t, c1)) is None or px.get((t, c2)) is None:
            continue

        weights_by_date[t] = {c1: w1, c2: w2}
        rows.append({
            "trade_date": t, "front_contract": c1, "second_contract": c2,
            "d1": (e1 - t).days, "d2": (e2 - t).days,
            "w1": w1, "w2": w2,
            "cycle_business_days": cycle, "business_days_remaining": remain,
            "cycle_start": e0, "front_expiry": e1,
        })
    return pd.DataFrame(rows), weights_by_date


def finish(df, cdr, tag, base=100.0):
    df = df.merge(cdr.rename("cdr").reset_index()
                    .rename(columns={"index": "trade_date"}),
                  on="trade_date", how="left")
    df = df.sort_values("trade_date").reset_index(drop=True)
    r = df["cdr"].fillna(0.0)
    df["index_level"] = base * (1.0 + r).cumprod()
    df.loc[0, "cdr"] = np.nan
    df["realized_dte"] = df["w1"] * df["d1"] + df["w2"] * df["d2"]
    df["construction"] = tag
    return df


def main():
    panel = load_panel()
    px, exp = price_lookup(panel)
    sessions = sorted(panel["trade_date"].unique())
    settle_dates = sorted(exp.unique())
    print(f"panel sessions={len(sessions)} contracts={len(exp)} "
          f"settlement dates={len(settle_dates)}")

    # ---- A : Session 00A series, reused unchanged --------------------------
    a = pd.read_parquet(INTERIM / "vx-cm30.parquet").copy()
    a["w2"] = 1.0 - a["w1"]
    a["realized_dte"] = a["w1"] * a["d1"] + a["w2"] * a["d2"]
    a["index_level"] = a["cm30_settle"]
    a["cdr"] = a["cm30_settle"].pct_change()
    a["construction"] = "A_interpolation"
    a = a[["trade_date", "front_contract", "second_contract", "d1", "d2",
           "w1", "w2", "clipped", "realized_dte", "cm30_settle",
           "index_level", "cdr", "construction"]]
    a.to_parquet(INTERIM / "vx-cm30-a.parquet", index=False)
    print(f"A rows={len(a)} clipped={a['clipped'].mean():.4f}")

    # ---- B : S&P roll -------------------------------------------------------
    listed = listed_by_date(panel)
    px_aug = dict(px)                       # copy; synthetic fills added below
    bdf, bw = build_sp_roll(panel, sessions, settle_dates, px, exp,
                            listed, px_aug)
    bcdr, bmiss = held_returns(bw, sorted(bw.keys()), px_aug)
    nfill = int((bdf["price_fill"] != "").sum())
    print(f"B price fills (S&P unlisted-contract rule): {nfill} sessions "
          f"{bdf.loc[bdf['price_fill'] != '', 'price_fill'].value_counts().to_dict()}")
    b = finish(bdf, bcdr, "B_sp_roll")
    b.to_parquet(INTERIM / "vx-cm30-b.parquet", index=False)
    print(f"B rows={len(b)} missing-price sessions={bmiss} "
          f"w1 range {b['w1'].min():.3f}..{b['w1'].max():.3f}")

    # ---- C : fixed business-day roll ---------------------------------------
    cdf, cw = build_fixed_roll(panel, sessions, px, exp)
    ccdr, cmiss = held_returns(cw, sorted(cw.keys()), px)
    c = finish(cdf, ccdr, "C_fixed_roll")
    c.to_parquet(INTERIM / "vx-cm30-c.parquet", index=False)
    print(f"C rows={len(c)} missing-price sessions={cmiss} "
          f"w1 range {c['w1'].min():.3f}..{c['w1'].max():.3f}")

    for tag, df in [("A", a), ("B", b), ("C", c)]:
        print(f"{tag}: {df['trade_date'].min().date()} .. "
              f"{df['trade_date'].max().date()}  "
              f"realized_dte mean={df['realized_dte'].mean():.2f} "
              f"sd={df['realized_dte'].std():.2f}")


if __name__ == "__main__":
    main()
