"""Session 25 plotting helpers, built on scripts/s19_svg.py.

s19_svg.py is left untouched so session 19's four figures stay byte-identical
under the regenerability check. These helpers add the marks session 25 needs
and nothing else. Standard library only, matplotlib deliberately absent.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path("/Users/GualyCr/Downloads/tactical-allocation")))
from scripts.s19_svg import Fig, W, H, L, R, T, B, PW, PH, FG, GRID, _f, _esc  # noqa: F401

PAL = ["#2b6cb0", "#b03030", "#2f7d4f", "#7a5195", "#bf8b2e", "#3d3d3d"]


def polyline(fig, xs, ys, col, w=1.4, dash=""):
    pts = " ".join(f"{_f(fig.sx(x))},{_f(fig.sy(y))}" for x, y in zip(xs, ys))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    fig.p.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
                 f'stroke-width="{w}"{d}/>')


def band(fig, xs, los, his, col, op=0.18):
    up = " ".join(f"{_f(fig.sx(x))},{_f(fig.sy(y))}" for x, y in zip(xs, his))
    dn = " ".join(f"{_f(fig.sx(x))},{_f(fig.sy(y))}" for x, y in zip(reversed(xs), reversed(los)))
    fig.p.append(f'<polygon points="{up} {dn}" fill="{col}" fill-opacity="{op}" stroke="none"/>')


def marker(fig, x, y, col, r=3.0, shape="o"):
    if shape == "o":
        fig.p.append(f'<circle cx="{_f(fig.sx(x))}" cy="{_f(fig.sy(y))}" r="{r}" '
                     f'fill="{col}" stroke="#fff" stroke-width="0.6"/>')
    else:
        s = r * 1.6
        fig.p.append(f'<rect x="{_f(fig.sx(x)-s/2)}" y="{_f(fig.sy(y)-s/2)}" '
                     f'width="{_f(s)}" height="{_f(s)}" fill="{col}"/>')


def vbar(fig, x, y0, y1, col, width_units, op=1.0):
    x0 = fig.sx(x - width_units / 2); x1 = fig.sx(x + width_units / 2)
    ya, yb = fig.sy(max(y0, y1)), fig.sy(min(y0, y1))
    fig.rect(x0, ya, x1 - x0, yb - ya, col, op)


def hrange(fig, y, lo, hi, col, w=2.0, cap=4.0):
    fig.line(fig.sx(lo), fig.sy(y), fig.sx(hi), fig.sy(y), col, w)
    for v in (lo, hi):
        fig.line(fig.sx(v), fig.sy(y) - cap, fig.sx(v), fig.sy(y) + cap, col, w)


def legend(fig, entries, x=None, y=None):
    x = L + 12 if x is None else x
    y = T + 16 if y is None else y
    for i, (lab, col) in enumerate(entries):
        yy = y + i * 15
        fig.p.append(f'<rect x="{_f(x)}" y="{_f(yy-7)}" width="16" height="3" fill="{col}"/>')
        fig.text(x + 22, yy - 1, lab, "start", 10)


def caption(fig, source, period):
    fig.text(L, H - 4, f"source {source}", "start", 8, "#555")
    fig.text(L + PW, H - 4, f"sample period {period}", "end", 8, "#555")


def write(fig, path):
    Path(path).write_text(fig.svg())
    return Path(path).stat().st_size


def axes2(fig, xticks=None, yticks=None, xfmt="{:g}", yfmt="{:g}"):
    """As Fig.axes, but tick positions and labels may be given explicitly and
    either axis may be suppressed by passing an empty list. Categorical axes
    carry no numeric ticks, since a row index is not a quantity."""
    from scripts.s19_svg import _nice
    ys = ([(v, yfmt.format(v)) for v in _nice(fig.y0, fig.y1)]
          if yticks is None else list(yticks))
    xs = ([(v, xfmt.format(v)) for v in _nice(fig.x0, fig.x1)]
          if xticks is None else list(xticks))
    for v, lab in ys:
        if not (fig.y0 - 1e-9 <= v <= fig.y1 + 1e-9):
            continue
        y = fig.sy(v)
        fig.line(L, y, L + PW, y, GRID, 1.0)
        fig.text(L - 8, y + 4, lab, "end", 10)
    for v, lab in xs:
        if not (fig.x0 - 1e-9 <= v <= fig.x1 + 1e-9):
            continue
        x = fig.sx(v)
        fig.line(x, T, x, T + PH, GRID, 1.0)
        fig.text(x, T + PH + 16, lab, "middle", 10)
    fig.p.append(f'<rect x="{L}" y="{T}" width="{PW}" height="{PH}" '
                 f'fill="none" stroke="{FG}" stroke-width="1"/>')
    fig.text(W / 2, 20, fig.title, "middle", 13, FG, "bold")
    fig.text(W / 2, H - 16, fig.xlabel, "middle", 11)
    fig.p.append(f'<text x="16" y="{_f(T + PH / 2)}" text-anchor="middle" '
                 f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
                 f'fill="{FG}" transform="rotate(-90 16 {_f(T + PH / 2)})">'
                 f'{_esc(fig.ylabel)}</text>')


def halo(fig, x, y, s, anchor="start", size=9, col=FG, weight="normal", pad=2.0):
    w = 0.55 * size * len(str(s)) + 2 * pad
    x0 = {"start": x - pad, "middle": x - w / 2, "end": x - w + pad}[anchor]
    fig.rect(x0, y - size + 1, w, size + 3, "#fff", 0.85)
    fig.text(x, y, s, anchor, size, col, weight)


def legend_box(fig, entries, x, y):
    w = max(0.55 * 10 * len(lab) for lab, _ in entries) + 34
    fig.rect(x - 6, y - 14, w, 15 * len(entries) + 8, "#fff", 0.88, FG)
    for i, (lab, col) in enumerate(entries):
        yy = y + i * 15
        fig.p.append(f'<rect x="{_f(x)}" y="{_f(yy-7)}" width="16" height="3" fill="{col}"/>')
        fig.text(x + 22, yy - 1, lab, "start", 10)
