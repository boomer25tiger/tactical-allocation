"""Session 27 phase G. The fifth and sixth figures under the cap at 9.60.

Both are drawn from outputs/session-27/_combined_line_returns.parquet, which phase
C wrote in the single pass, so neither figure recomputes any quantity. Each emits
the exact series it plots as a CSV beside it.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))

import pandas as pd                                   # noqa: E402
import scripts.s25_svg as V                           # noqa: E402
from scripts.s19_svg import Fig, L, T, PW, PH, FG     # noqa: E402

OUT = ROOT / "outputs" / "session-27"
FIG = OUT / "figures"; FIG.mkdir(parents=True, exist_ok=True)
BOUNDARY = pd.Timestamp("2021-08-01")
LINES = ["STRATEGY", "buy_hold_QQQ", "matched_exposure_levered_QQQ_1.70"]

df = pd.read_parquet(OUT / "_combined_line_returns.parquet")[LINES].dropna()
DATES = [d.strftime("%Y-%m-%d") for d in df.index]
PERIOD = f"{DATES[0]} to {DATES[-1]}, {len(DATES)} sessions"
BI = int((df.index < BOUNDARY).sum())          # first holdout position
SRC = "outputs/session-27/_combined_line_returns.parquet, written in the phase C pass"
YT = []
for i, d in enumerate(DATES):
    if i == 0 or d[:4] != DATES[i - 1][:4]:
        YT.append((i, d[:4]))
YT = [t for k, t in enumerate(YT) if k % 2 == 0]
xs = list(range(len(DATES)))
def q(v): return repr(float(v))


def growth(rs):
    g, out = 1.0, []
    for r in rs:
        g *= (1.0 + r); out.append(g)
    return out


def ddown(gs):
    pk, out = -1e18, []
    for g in gs:
        pk = max(pk, g); out.append(g / pk - 1.0)
    return out


def boundary_mark(f, y_at):
    f.line(f.sx(BI), T, f.sx(BI), T + PH, "#444", 1.4, "6,3")
    V.halo(f, f.sx(BI) - 6, y_at, f"holdout boundary {BOUNDARY.date()}, session {BI}",
           "end", 9, "#444")


def done(name, fig, header, rows):
    V.caption(fig, SRC, PERIOD)
    (FIG / f"{name}.svg").write_text(fig.svg())
    with open(FIG / f"{name}.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows)
    print(f"  {name:26s} {(FIG/f'{name}.svg').stat().st_size:>7} bytes  "
          f"{len(rows):>5} plotted rows")


G = [(ln, growth(df[ln].tolist())) for ln in LINES]
ys = [math.log10(v) for _, g in G for v in g]
f = Fig("Growth of one dollar across the primary window and the holdout",
        "session date", "growth of one dollar, log base 10",
        (0, len(xs) - 1), (min(ys), max(ys)))
V.axes2(f, xticks=YT, yfmt="{:.1f}")
for i, (ln, g) in enumerate(G):
    V.polyline(f, xs, [math.log10(v) for v in g], V.PAL[i], 1.5)
boundary_mark(f, T + 16)
V.legend_box(f, [(f"{ln}, final {g[-1]:.3f} times", V.PAL[i])
                 for i, (ln, g) in enumerate(G)], L + 14, T + 34)
done("combined-equity-curve", f, ["date"] + LINES,
     [[DATES[k]] + [q(g[k]) for _, g in G] for k in xs])

D = [(ln, ddown(g)) for ln, g in G]
lo = min(v for _, dd in D for v in dd)
f = Fig("Drawdown from the running peak across the primary window and the holdout",
        "session date", "drawdown, fraction of the running peak",
        (0, len(xs) - 1), (lo, 0.0))
V.axes2(f, xticks=YT, yfmt="{:.2f}")
for i, (ln, dd) in enumerate(D):
    V.polyline(f, xs, dd, V.PAL[i], 1.3)
boundary_mark(f, T + PH - 8)
V.legend_box(f, [(f"{ln}, worst {min(dd):.6f}", V.PAL[i])
                 for i, (ln, dd) in enumerate(D)], L + 14, T + PH - 74)
done("combined-drawdown", f, ["date"] + LINES,
     [[DATES[k]] + [q(dd[k]) for _, dd in D] for k in xs])

print(f"two figures written, being the fifth and sixth under the cap at 9.60")
