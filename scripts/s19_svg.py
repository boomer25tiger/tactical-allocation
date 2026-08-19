"""Minimal deterministic SVG plotting, pure Python.

matplotlib is not in the environment session 18s rebuilt and registered at
10.1, and adding it would change the environment record that the manifest
carries. These helpers draw the four figures step 8 requires using the
standard library alone, so the environment stays exactly as registered.

Output is deterministic, being fixed coordinate rounding and no timestamps,
so the regenerability check compares byte for byte.
"""
from __future__ import annotations

import math

W, H = 760, 420
L, R, T, B = 70, 20, 34, 52
PW, PH = W - L - R, H - T - B
FG, GRID, ACC, ACC2, SHADE = "#222", "#d8d8d8", "#2b6cb0", "#b03030", "#f0c9c9"


def _f(x):
    return f"{x:.2f}"


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _nice(lo, hi, n=6):
    if hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    start = math.floor(lo / step) * step
    out = []
    v = start
    while v <= hi + step * 0.5:
        out.append(round(v, 10))
        v += step
    return out


class Fig:
    def __init__(self, title, xlabel, ylabel, xlim, ylim):
        self.p = []
        self.title, self.xlabel, self.ylabel = title, xlabel, ylabel
        self.x0, self.x1 = xlim
        self.y0, self.y1 = ylim
        if self.x1 <= self.x0:
            self.x1 = self.x0 + 1.0
        if self.y1 <= self.y0:
            self.y1 = self.y0 + 1.0

    def sx(self, x):
        return L + (x - self.x0) / (self.x1 - self.x0) * PW

    def sy(self, y):
        return T + PH - (y - self.y0) / (self.y1 - self.y0) * PH

    def rect(self, x, y, w, h, fill, op=1.0, stroke="none"):
        self.p.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" '
                      f'height="{_f(h)}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}"/>')

    def line(self, x1, y1, x2, y2, col=FG, w=1.0, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" '
                      f'stroke="{col}" stroke-width="{w}"{d}/>')

    def text(self, x, y, s, anchor="middle", size=11, col=FG, weight="normal"):
        self.p.append(f'<text x="{_f(x)}" y="{_f(y)}" text-anchor="{anchor}" '
                      f'font-family="Helvetica,Arial,sans-serif" font-size="{size}" '
                      f'font-weight="{weight}" fill="{col}">{_esc(s)}</text>')

    def axes(self, xfmt="{:g}", yfmt="{:g}"):
        for v in _nice(self.y0, self.y1):
            if not (self.y0 - 1e-9 <= v <= self.y1 + 1e-9):
                continue
            y = self.sy(v)
            self.line(L, y, L + PW, y, GRID, 1.0)
            self.text(L - 8, y + 4, yfmt.format(v), "end", 10)
        for v in _nice(self.x0, self.x1):
            if not (self.x0 - 1e-9 <= v <= self.x1 + 1e-9):
                continue
            x = self.sx(v)
            self.line(x, T, x, T + PH, GRID, 1.0)
            self.text(x, T + PH + 16, xfmt.format(v), "middle", 10)
        self.p.append(f'<rect x="{L}" y="{T}" width="{PW}" height="{PH}" '
                      f'fill="none" stroke="{FG}" stroke-width="1"/>')
        self.text(W / 2, 20, self.title, "middle", 13, FG, "bold")
        self.text(W / 2, H - 14, self.xlabel, "middle", 11)
        self.p.append(f'<text x="16" y="{_f(T + PH / 2)}" text-anchor="middle" '
                      f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
                      f'fill="{FG}" transform="rotate(-90 16 {_f(T + PH / 2)})">'
                      f'{_esc(self.ylabel)}</text>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>'
                + "".join(self.p) + "</svg>\n")


def histogram(values, bins, title, xlabel, shade_below=None, note=""):
    lo, hi = float(min(values)), float(max(values))
    if hi <= lo:
        hi = lo + 1.0
    edges = [lo + (hi - lo) * i / bins for i in range(bins + 1)]
    counts = [0] * bins
    for v in values:
        k = int((v - lo) / (hi - lo) * bins)
        counts[min(k, bins - 1)] += 1
    f = Fig(title, xlabel, "count", (lo, hi), (0, max(counts) * 1.08))
    f.axes()
    for i in range(bins):
        x, w = f.sx(edges[i]), f.sx(edges[i + 1]) - f.sx(edges[i])
        y = f.sy(counts[i])
        shaded = shade_below is not None and edges[i + 1] <= shade_below
        f.rect(x, y, max(w - 0.6, 0.4), T + PH - y,
               SHADE if shaded else ACC, 1.0 if shaded else 0.75)
    if shade_below is not None:
        x = f.sx(shade_below)
        f.line(x, T, x, T + PH, ACC2, 1.6, "4,3")
        f.text(x + 6, T + 14, f"logit = {shade_below:g}", "start", 10, ACC2)
    if note:
        f.text(L, T - 8, note, "start", 10)
    return f.svg()


def scatter_fit(xs, ys, slope, intercept, title, xlabel, ylabel, max_points=4000,
                note=""):
    n = len(xs)
    step = max(1, n // max_points)
    xs_s, ys_s = xs[::step], ys[::step]
    x0, x1 = float(min(xs)), float(max(xs))
    y0, y1 = float(min(ys)), float(max(ys))
    px, py = (x1 - x0) * 0.04, (y1 - y0) * 0.06
    f = Fig(title, xlabel, ylabel, (x0 - px, x1 + px), (y0 - py, y1 + py))
    f.axes()
    for a, b in zip(xs_s, ys_s):
        f.p.append(f'<circle cx="{_f(f.sx(a))}" cy="{_f(f.sy(b))}" r="1.5" '
                   f'fill="{ACC}" fill-opacity="0.30"/>')
    f.line(f.sx(x0), f.sy(slope * x0 + intercept),
           f.sx(x1), f.sy(slope * x1 + intercept), ACC2, 2.0)
    f.line(L, f.sy(0.0), L + PW, f.sy(0.0), FG, 0.8, "3,3")
    f.text(L + 8, T + 14,
           f"fit  y = {slope:.4f} x + {intercept:.4f}", "start", 10, ACC2)
    f.text(L + 8, T + 28, f"{n:,} combinations, {len(xs_s):,} plotted", "start", 10)
    if note:
        f.text(L + 8, T + 42, note, "start", 10)
    return f.svg()


def two_cdfs(a, b, la, lb, title, xlabel, note=""):
    sa, sb = sorted(a), sorted(b)
    lo = min(sa[0], sb[0]); hi = max(sa[-1], sb[-1])
    f = Fig(title, xlabel, "cumulative probability", (lo, hi), (0, 1))
    f.axes(yfmt="{:.1f}")

    def path(s, col):
        n = len(s)
        step = max(1, n // 1200)
        pts = [(f.sx(s[i]), f.sy((i + 1) / n)) for i in range(0, n, step)]
        pts.append((f.sx(s[-1]), f.sy(1.0)))
        d = "M" + " L".join(f"{_f(x)},{_f(y)}" for x, y in pts)
        f.p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.8"/>')

    path(sa, ACC); path(sb, ACC2)
    f.rect(L + PW - 210, T + 10, 10, 10, ACC)
    f.text(L + PW - 194, T + 19, la, "start", 10)
    f.rect(L + PW - 210, T + 26, 10, 10, ACC2)
    f.text(L + PW - 194, T + 35, lb, "start", 10)
    if note:
        f.text(L + 8, T + 14, note, "start", 10)
    return f.svg()


def strata_panel(groups, title, ylabel, note=""):
    """groups: list of (axis, classification, [(value, mean, p05, p95)])."""
    n = sum(len(g[2]) for g in groups)
    ys = [v for g in groups for t in g[2] for v in (t[2], t[3])]
    y0, y1 = min(ys), max(ys)
    pad = (y1 - y0) * 0.08
    f = Fig(title, "axis and value", ylabel, (0, n + 1), (y0 - pad, y1 + pad))
    f.axes(xfmt="{:.0f}")
    for i in range(len(f.p) - 1, -1, -1):
        if f.p[i].startswith("<text") and 'text-anchor="middle"' in f.p[i] \
                and f'y="{_f(T + PH + 16)}"' in f.p[i]:
            f.p.pop(i)
    k = 1
    for axis, cls, tuples in groups:
        xs_start = k
        for (val, mean, p05, p95) in tuples:
            x = f.sx(k)
            col = ACC if cls == "structural" else ACC2
            f.line(x, f.sy(p05), x, f.sy(p95), col, 1.4)
            f.p.append(f'<circle cx="{_f(x)}" cy="{_f(f.sy(mean))}" r="3" fill="{col}"/>')
            f.text(x, T + PH + 14, val, "middle", 8)
            k += 1
        mid = f.sx((xs_start + k - 1) / 2.0)
        f.text(mid, T + PH + 30, f"{axis} ({cls[:4]})", "middle", 9)
        if k <= n:
            f.line(f.sx(k - 0.5), T, f.sx(k - 0.5), T + PH, GRID, 1.0)
    f.rect(L + PW - 260, T + 10, 10, 10, ACC)
    f.text(L + PW - 244, T + 19, "structural, separated strata", "start", 10)
    f.rect(L + PW - 260, T + 26, 10, 10, ACC2)
    f.text(L + PW - 244, T + 35, "smooth, sweep", "start", 10)
    if note:
        f.text(L + 8, T + 14, note, "start", 10)
    return f.svg()
