"""Session 00C, Steps 4 and 5.

Step 4. RSI relationship, long leveraged fund against underlying (informs 6.9).
Step 5. RSI relationship, inverse fund against underlying (closes 6.20), testing
        the proposition RSI(inverse) = 100 - RSI(underlying).

RSI is Wilder, alpha = 1/n (decision 1.6), computed on the total return series.
No strategy return, allocation, or performance statistic is computed.
"""

import numpy as np
import pandas as pd

from s00c_indicators import (OUT, RSI_PERIODS, RSI_THRESHOLDS, load_panel,
                             tr_series, wilder_rsi)

LONG_PAIRS = [
    ("TQQQ", "QQQ"), ("QLD", "QQQ"), ("TECL", "XLK"), ("SOXL", "SMH"),
    ("SPXL", "SPY"), ("FAS", "XLF"), ("LABU", "XBI"),
]
INVERSE_PAIRS = [
    ("SQQQ", "QQQ"), ("PSQ", "QQQ"), ("SH", "SPY"),
    ("TECS", "XLK"), ("SOXS", "SMH"),
]
# Decision 6.20 names PSQ and SH specifically. These compare inverse funds
# against each other directly, with no 100-minus transform, to show whether one
# inverse carries information the other does not.
CROSS_INVERSE_PAIRS = [("PSQ", "SH"), ("PSQ", "SQQQ"), ("SH", "SQQQ")]

MIN_N = 20  # minimum sessions before a correlation is reported for a window


def pair_stats(a: pd.Series, b: pd.Series, thresholds, inverse: bool) -> dict:
    """a is the fund series, b is the comparison series already put on the
    fund's scale (the underlying for Step 4, 100 - underlying for Step 5)."""
    d = a - b
    ad = np.abs(d)
    row = dict(
        n_sessions=int(len(a)),
        first_date=a.index[0].date().isoformat(),
        last_date=a.index[-1].date().isoformat(),
        mean_abs_diff=float(ad.mean()),
        median_abs_diff=float(ad.median()),
        p95_abs_diff=float(np.percentile(ad, 95)),
        p99_abs_diff=float(np.percentile(ad, 99)),
        max_abs_diff=float(ad.max()),
        mean_signed_diff=float(d.mean()),
        sd_signed_diff=float(d.std(ddof=1)) if len(d) > 1 else np.nan,
        frac_fund_above_comparison=float((d > 0).mean()),
        correlation=(float(np.corrcoef(a.to_numpy(), b.to_numpy())[0, 1])
                     if len(a) >= MIN_N and a.std() > 0 and b.std() > 0 else np.nan),
    )
    for thr in thresholds:
        if not inverse:
            ca, cb = a > thr, b > thr
        elif thr >= 50:
            # overbought side on the inverse: RSI(inv) > thr against
            # RSI(underlying) < 100 - thr, which is b = 100 - RSI(und) > thr
            ca, cb = a > thr, b > thr
        else:
            ca, cb = a < thr, b < thr
        agree = (ca == cb)
        row[f"agree_{thr}"] = float(agree.mean())
        row[f"n_disagree_{thr}"] = int((~agree).sum())
        row[f"n_fire_fund_{thr}"] = int(ca.sum())
        row[f"n_fire_comparison_{thr}"] = int(cb.sum())
    return row


def dispersion(ret: pd.Series) -> float:
    """Annualized standard deviation of daily total returns. A property of the
    instrument's return distribution, carried as context so that the by-year
    divergence can be read against volatility as well as against the rate
    environment. Not a strategy or performance statistic."""
    r = ret.dropna()
    return float(r.std(ddof=1) * np.sqrt(252)) if len(r) > 1 else np.nan


def build(pairs, inverse: bool, path: str, label_a: str, label_b: str,
          cross_pairs=None):
    panel = load_panel()
    tr = tr_series(panel)
    rets = {t: g.set_index("date")["ret_total"].astype(float)
            for t, g in panel.groupby("ticker", sort=True)}
    rows = []

    specs = [(f, u, inverse, "fund_vs_underlying") for f, u in pairs]
    specs += [(f, u, False, "inverse_vs_inverse") for f, u in (cross_pairs or [])]

    for fund, und, inv, ptype in specs:
        for n in RSI_PERIODS:
            rf = wilder_rsi(tr[fund], n).dropna()
            ru = wilder_rsi(tr[und], n).dropna()
            j = pd.concat({"f": rf, "u": ru}, axis=1, join="inner").dropna()
            if len(j) == 0:
                continue
            a = j["f"]
            b = (100.0 - j["u"]) if inv else j["u"]

            base = dict(pair=f"{fund}/{und}", pair_type=ptype,
                        **{label_a: fund, label_b: und},
                        comparison=("100 - RSI(underlying)" if inv
                                    else "RSI(underlying)"),
                        rsi_period=n)

            def ctx(idx=None):
                rr_f = rets[fund].reindex(j.index if idx is None else idx)
                rr_u = rets[und].reindex(j.index if idx is None else idx)
                return dict(fund_ann_ret_sd=dispersion(rr_f),
                            underlying_ann_ret_sd=dispersion(rr_u))

            rows.append(dict(**base, window="pooled",
                             **pair_stats(a, b, RSI_THRESHOLDS, inv), **ctx()))
            for yr, idx in j.groupby(j.index.year).groups.items():
                rows.append(dict(**base, window=str(yr),
                                 **pair_stats(a.loc[idx], b.loc[idx],
                                              RSI_THRESHOLDS, inv), **ctx(idx)))
    df = pd.DataFrame(rows)
    df = df.sort_values(["pair_type", "pair", "rsi_period", "window"]).reset_index(drop=True)
    df.to_csv(OUT / path, index=False)
    return df


def main():
    d4 = build(LONG_PAIRS, False, "rsi-leveraged-divergence.csv",
               "leveraged", "underlying")
    d5 = build(INVERSE_PAIRS, True, "rsi-inverse-relationship.csv",
               "inverse", "underlying", cross_pairs=CROSS_INVERSE_PAIRS)

    pd.set_option("display.width", 220)
    cols = ["pair", "rsi_period", "n_sessions", "mean_abs_diff", "p95_abs_diff",
            "p99_abs_diff", "max_abs_diff", "mean_signed_diff", "correlation",
            "agree_70", "n_disagree_70", "agree_80", "n_disagree_80",
            "agree_30", "n_disagree_30", "agree_20", "n_disagree_20"]

    print("=== Step 4, long leveraged against underlying, pooled ===")
    print(d4[d4.window == "pooled"][cols].to_string(index=False,
          float_format=lambda x: f"{x:,.4f}"))
    print()
    print("=== Step 5, inverse against 100 minus underlying, pooled ===")
    m = (d5.window == "pooled") & (d5.pair_type == "fund_vs_underlying")
    print(d5[m][cols].to_string(index=False, float_format=lambda x: f"{x:,.4f}"))
    print()
    print("=== Step 5 supplement, inverse against inverse directly, pooled ===")
    m = (d5.window == "pooled") & (d5.pair_type == "inverse_vs_inverse")
    print(d5[m][cols].to_string(index=False, float_format=lambda x: f"{x:,.4f}"))
    print()
    print("=== Step 4, signed diff and underlying dispersion by year, period 14 ===")
    y = d4[(d4.rsi_period == 14) & (d4.window != "pooled")]
    print(pd.concat([
        y.pivot(index="window", columns="pair", values="mean_signed_diff")
         .add_suffix("  signed"),
        y[y.pair == "QLD/QQQ"].set_index("window")[["underlying_ann_ret_sd"]]
         .rename(columns={"underlying_ann_ret_sd": "QQQ sd"}),
    ], axis=1).to_string(float_format=lambda x: f"{x:.3f}"))
    print()
    print("=== Step 4, mean abs diff by year, period 14 ===")
    p = d4[(d4.rsi_period == 14) & (d4.window != "pooled")].pivot(
        index="window", columns="pair", values="mean_abs_diff")
    print(p.to_string(float_format=lambda x: f"{x:.3f}"))
    print()
    print("=== Step 4, agreement at 70 by year, period 14 ===")
    p = d4[(d4.rsi_period == 14) & (d4.window != "pooled")].pivot(
        index="window", columns="pair", values="agree_70")
    print(p.to_string(float_format=lambda x: f"{x:.4f}"))


if __name__ == "__main__":
    main()
