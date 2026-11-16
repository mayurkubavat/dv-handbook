#!/usr/bin/env python3
"""Generate the figures of the statistics chapter (ch21-*.svg).

ch21-burst.svg   per bin of fifo_cg: the per-seed rate a model of
                 independent cycles predicts, against the measured rate
ch21-coupon.svg  P(every reachable bin hit within n seeds): measured
                 (exact law of the 1000 seeds), independent-bins product,
                 union bound, cycle model
ch21-clean.svg   the 95% bound after n clean seeds, exact and 3/n,
                 against the true rate of the 30-cycle generator
ch21-tway.svg    t-way coverage of the DMA transfer space against tests:
                 greedy array and three random generators
ch21-unseen.svg  bins seen and Chao2 (median, 10-90% band) against
                 seeds, two generators

Every figure is drawn from an example's data file or run.out under
examples/ch21-statistics-random-testing/. Each data file is pinned by
its SHA-256, and the values a caption or the prose quotes are checked
against the run.out that prints them, so a changed run fails this
script instead of silently redrawing a figure the text no longer
describes.

    python3 figures/gen_ch21_figures.py [name ...]
"""
import hashlib
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import AMBER, BLUE, DIM, GREEN, HW, INK, MONO, RULE, VIOLET  # noqa

HERE = pathlib.Path(__file__).resolve().parent
EX = HERE.parent / "examples" / "ch21-statistics-random-testing"
PIN = {
    "seed-unit/data.tsv":
        ("310e5c00768212fd3dc849c3c69c7ec5"
         "7804c09eacc3dd7d57ed87a0959aa8c0"),
    "seed-unit/curve.tsv":
        ("8eabc9f5c8784a0275474a25506f4112"
         "89dbd2161903c67260c79458ae0926ae"),
    "t-way/data.tsv":
        ("512d75f0a91c0647ee37fc67d4849184"
         "fd2cc34940adffb37af7b1bea55abf46"),
    "unseen/data.tsv":
        ("52381211f14ae0fea13b347e62fdb437"
         "0205ac8323d62b7a97706f52e0c887a9"),
    "clean-seeds/run.out":
        ("d3d0644dfcc258b07dab8bcd5e5d42db"
         "fa2dfb5af46d0155445090e0eb54d4fc"),
}


def data(rel):
    """Text of a pinned data file; fails if it has changed."""
    raw = (EX / rel).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    assert got == PIN[rel], "%s changed (sha256 %s): re-check the " \
        "chapter's text and captions, then re-pin" % (rel, got)
    return raw.decode()


def out(example):
    return (EX / example / "run.out").read_text()


def tsv(rel):
    lines = [x for x in data(rel).split("\n") if x and not x.startswith("#")]
    head = lines[0].split("\t")
    return head, [x.split("\t") for x in lines[1:]]


# ---- a small chart kit on top of HW -----------------------------------

class Axes:
    """A plotting frame at (x, y, w, h) with linear or log10 scales."""

    def __init__(self, d, x, y, w, h, xr, yr, xlog=False, ylog=False):
        self.d, self.x, self.y, self.w, self.h = d, x, y, w, h
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    def _t(self, v, r, log):
        if log:
            v, r = math.log10(v), (math.log10(r[0]), math.log10(r[1]))
        return (v - r[0]) / (r[1] - r[0])

    def px(self, v):
        return self.x + self._t(v, self.xr, self.xlog) * self.w

    def py(self, v):
        return self.y + self.h - self._t(v, self.yr, self.ylog) * self.h

    def frame(self, xticks, yticks, xlab, ylab, xfmt=str, yfmt=str):
        d = self.d
        for t in yticks:
            d.line(self.x, self.py(t), self.x + self.w, self.py(t), RULE, 0.8)
            d.text(self.x - 8, self.py(t) + 4, yfmt(t), 12, DIM, "400", "end")
        for t in xticks:
            d.line(self.px(t), self.y + self.h, self.px(t), self.y + self.h + 5,
                   INK, 1)
            d.text(self.px(t), self.y + self.h + 20, xfmt(t), 12, DIM, "400",
                   "middle")
        d.line(self.x, self.y + self.h, self.x + self.w, self.y + self.h,
               INK, 1.2)
        d.line(self.x, self.y, self.x, self.y + self.h, INK, 1.2)
        d.text(self.x + self.w / 2, self.y + self.h + 42, xlab, 13.5, INK,
               "600", "middle")
        cx, cy = self.x - 52, self.y + self.h / 2
        d.raw(f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="\'Source Sans 3\','
              f' Arial, sans-serif" font-size="13.5" font-weight="600" '
              f'fill="{INK}" text-anchor="middle" '
              f'transform="rotate(-90 {cx:.1f} {cy:.1f})">{ylab}</text>')

    def line(self, pts, col, sw=2.4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        path = " ".join("%s%.1f,%.1f" % ("M" if i == 0 else "L",
                                          self.px(a), self.py(b))
                        for i, (a, b) in enumerate(pts))
        self.d.raw(f'<path d="{path}" fill="none" stroke="{col}" '
                   f'stroke-width="{sw}" stroke-linejoin="round"{d}/>')

    def band(self, lo, hi, col):
        pts = [(self.px(a), self.py(b)) for a, b in lo] + \
              [(self.px(a), self.py(b)) for a, b in reversed(hi)]
        path = " ".join("%s%.1f,%.1f" % ("M" if i == 0 else "L", a, b)
                        for i, (a, b) in enumerate(pts)) + " Z"
        self.d.raw(f'<path d="{path}" fill="{col}" fill-opacity="0.22" '
                   'stroke="none"/>')

    def dot(self, a, b, col, r=4.5, hollow=False):
        fill = "white" if hollow else col
        self.d.raw(f'<circle cx="{self.px(a):.1f}" cy="{self.py(b):.1f}" '
                   f'r="{r}" fill="{fill}" stroke="{col}" stroke-width="2"/>')


def key(d, x, y, items):
    """A legend: (label, color, dash) for lines, one item per row."""
    for i, (lab, col, dash) in enumerate(items):
        yy = y + i * 22
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        d.raw(f'<line x1="{x}" y1="{yy}" x2="{x + 34}" y2="{yy}" '
              f'stroke="{col}" stroke-width="3"{dd}/>')
        d.text(x + 42, yy + 4.5, lab, 13, INK)


# ---- the figures ------------------------------------------------------

def fig_burst():
    head, rows = tsv("seed-unit/data.tsv")
    assert head == ["bin", "p_cycle", "iid_seed", "measured_seed"], head
    rows = [(r[0], float(r[2]), float(r[3])) for r in rows]
    assert len(rows) == 28, len(rows)
    so = out("seed-unit")
    for name, iid, meas in rows:
        if meas < 1.0:
            m = re.search(r"^%s\s+\S+\s+(\S+)\s+(\S+)" % re.escape(name), so,
                          re.M)
            assert m and abs(float(m.group(1)) - iid) < 0.0006 \
                and abs(float(m.group(2)) - meas) < 0.0006, name
    assert "11 of the 11 not hit by every seed" in so
    assert "17 further bins hit by every seed" in so
    rows.sort(key=lambda r: (r[2], r[0]))
    W, top, rh = 940, 96, 21
    H = top + rh * len(rows) + 122
    d = HW(W, H, "A model of independent cycles against the seeds",
           "fifo_cg, even odds, 200 cycles, 1000 seeds: predicted and "
           "measured per-seed hit rate")
    ax = Axes(d, 300, top, 600, rh * len(rows), (0, 1), (0, len(rows)))
    for t in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        d.line(ax.px(t), top, ax.px(t), top + ax.h, RULE, 0.8)
        d.text(ax.px(t), top + ax.h + 20, "%.1f" % t, 12, DIM, "400",
               "middle")
    d.line(ax.x, top + ax.h, ax.x + ax.w, top + ax.h, INK, 1.2)
    d.text(ax.x + ax.w / 2, top + ax.h + 42, "per-seed hit rate", 13.5, INK,
           "600", "middle")
    for i, (name, iid, meas) in enumerate(rows):
        y = top + (i + 0.5) * rh
        d.text(ax.x - 12, y + 4, name, 11.5, INK, "400", "end", MONO)
        if abs(iid - meas) > 0.004:
            d.line(ax.px(meas), y, ax.px(iid), y, DIM, 1.4)
        d.raw(f'<circle cx="{ax.px(iid):.1f}" cy="{y:.1f}" r="5" '
              f'fill="white" stroke="{AMBER}" stroke-width="2.2"/>')
        d.raw(f'<circle cx="{ax.px(meas):.1f}" cy="{y:.1f}" r="4" '
              f'fill="{BLUE}"/>')
    ly = H - 16
    d.raw(f'<circle cx="310" cy="{ly - 4}" r="5" fill="white" '
          f'stroke="{AMBER}" stroke-width="2.2"/>')
    d.text(322, ly, "predicted from the per-cycle rate, cycles taken as "
           "independent", 13, INK)
    d.raw(f'<circle cx="310" cy="{ly - 26}" r="4" fill="{BLUE}"/>')
    d.text(322, ly - 22, "measured: fraction of the 1000 seeds that hit "
           "the bin", 13, INK)
    d.save("ch21-burst.svg")


def fig_coupon():
    head, rows = tsv("seed-unit/curve.tsv")
    assert head == ["seeds", "measured", "product", "union", "cycle_iid"]
    cols = {h: [(int(r[0]), float(r[i])) for r in rows]
            for i, h in enumerate(head) if i}
    so = out("seed-unit")
    assert re.search(r"median 5, q99 25$", so, re.M)
    assert re.search(r"<= 0\.01:\s+27 seeds", so)
    assert "product: 2126 cycles = 10.6 seeds" in so

    def first(col, level):
        return next(n for n, v in cols[col] if v >= level)
    # the curves cross 0.99 where the run.out says they do
    assert first("measured", 0.99) == 25, first("measured", 0.99)
    assert first("union", 0.99) == 27, first("union", 0.99)
    assert first("cycle_iid", 0.99) == 11, first("cycle_iid", 0.99)
    d = HW(940, 560, "Seeds until every reachable bin of fifo_cg is hit",
           "four answers to the same question; dotted line at 0.99")
    ax = Axes(d, 100, 100, 800, 360, (1, 60), (0, 1))
    ax.frame((1, 10, 20, 30, 40, 50, 60), (0, 0.2, 0.4, 0.6, 0.8, 1.0),
             "seeds", "P(every reachable bin hit)", yfmt=lambda t: "%.1f" % t)
    d.line(ax.px(1), ax.py(0.99), ax.px(60), ax.py(0.99), INK, 1, "2 4")
    ax.line(cols["cycle_iid"], AMBER, 2.4, "8 5")
    ax.line(cols["union"], VIOLET, 2.4)
    ax.line(cols["product"], GREEN, 2.4, "3 3")
    ax.line(cols["measured"], BLUE, 3.0)
    for col, lab, c in (("cycle_iid", "11", AMBER), ("measured", "25", BLUE),
                        ("union", "27", VIOLET)):
        n = first(col, 0.99)
        d.line(ax.px(n), ax.py(0.99), ax.px(n), ax.py(0) , c, 1, "2 3")
        d.text(ax.px(n) + (-4 if col == "measured" else 4), ax.py(0) - 8,
               lab, 12.5, c, "700", "end" if col == "measured" else "start")
    key(d, 560, 330, [("measured: exact law of the 1000 seeds", BLUE, None),
                      ("independent bins (product)", GREEN, "3 3"),
                      ("union-bound guarantee", VIOLET, None),
                      ("independent cycles", AMBER, "8 5")])
    d.save("ch21-coupon.svg")


def fig_clean():
    text = data("clean-seeds/run.out")
    tab = re.findall(r"^\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+[\d.]+\s+[\d.]+$",
                     text.split("== 2.")[0], re.M)
    pts = [(int(n), float(e)) for n, _, e in tab]
    assert len(pts) == 9 and pts[3] == (250, 0.01191), pts
    for n, e in pts:
        assert abs(e - (1 - 0.05 ** (1 / n))) < 6e-6, (n, e)
    m = re.search(r"exact chain for this generator: p = ([\d.e+-]+)", text)
    true_p = float(m.group(1))
    m = re.search(r"bound on the per-seed trigger probability: ([\d.]+)",
                  text)
    b250 = float(m.group(1))
    assert (true_p, b250) == (8.45e-05, 0.0119), (true_p, b250)
    assert "the bound is 141 times the truth" in text
    assert "seeds for a 95% chance of one trigger: 35462" in text
    d = HW(940, 580, "What 250 clean seeds bound, and what they miss",
           "95% upper bound on the per-seed failure probability after n "
           "clean seeds")
    ax = Axes(d, 110, 100, 780, 380, (10, 1e5), (1e-5, 1), True, True)
    sup = {1e-5: "0.00001", 1e-4: "0.0001", 1e-3: "0.001", 1e-2: "0.01",
           1e-1: "0.1", 1: "1"}
    ax.frame((10, 100, 1000, 10000, 100000), sorted(sup),
             "clean seeds n (log scale)", "upper bound on p (log scale)",
             xfmt=lambda t: "{:,}".format(t), yfmt=lambda t: sup[t])
    ax.line([(10, 0.3), (1e5, 3e-5)], DIM, 2.2, "7 4")
    d.text(ax.px(14), ax.py(0.3) - 8, "3/n", 13, DIM, "700")
    for n, e in pts:
        ax.dot(n, e, BLUE)
    d.line(ax.px(10), ax.py(true_p), ax.px(1e5), ax.py(true_p), AMBER, 2.4)
    d.text(ax.px(12), ax.py(true_p) - 9, "true p of the 30-cycle generator, "
           "%.3g (exact chain)" % true_p, 13, AMBER, "600")
    ax.dot(250, b250, AMBER, 7, True)
    d.text(ax.px(250) - 12, ax.py(b250) + 24, "250 clean seeds: bound %.4f,"
           % b250, 13, INK, "600", "end")
    d.text(ax.px(250) - 12, ax.py(b250) + 42, "141 times the true p", 13,
           INK, "400", "end")
    n_meet = 35462
    d.line(ax.px(n_meet), ax.py(true_p), ax.px(n_meet), ax.py(1e-5), AMBER,
           1, "2 3")
    d.text(ax.px(n_meet), ax.py(1e-5) - 8, "35,462", 12.5, AMBER, "700",
           "middle")
    key(d, 600, 150, [("exact bound, 1 - 0.05^(1/n)", BLUE, "1 0"),
                      ("rule of three, 3/n", DIM, "7 4")])
    d.save("ch21-clean.svg")


def fig_tway():
    head, rows = tsv("t-way/data.tsv")
    want = ["n", "greedy2", "uniform2", "ordered2", "ch11gen2", "greedy3",
            "uniform3", "ordered3", "ch11gen3"]
    assert head == want, head
    cols = {h: [(int(r[0]), float(r[i])) for r in rows]
            for i, h in enumerate(head) if i}
    to = out("t-way")
    g2 = next(n for n, v in cols["greedy2"] if v >= 1.0)
    g3 = next(n for n, v in cols["greedy3"] if v >= 1.0)
    assert (g2, g3) == (23, 68), (g2, g3)
    assert "construction found 23 rows" in to and "found 68 rows" in to
    assert re.search(r"generator: 0\.887 of pairs, 0\.828", to)
    d = HW(960, 520, "Covering the DMA transfer space: designed against "
           "drawn", "fraction of legal tuples covered after n tests")
    for k, (t, x0, plateau) in enumerate(((2, 90, 0.887), (3, 560, 0.828))):
        ax = Axes(d, x0, 110, 360, 290, (1, 200), (0, 1))
        ax.frame((1, 50, 100, 150, 200), (0, 0.2, 0.4, 0.6, 0.8, 1.0),
                 "tests", "fraction covered" if k == 0 else "",
                 yfmt=lambda v: "%.1f" % v)
        d.text(x0 + 180, 100, "pairs (t = 2)" if t == 2 else
               "triples (t = 3)", 14.5, INK, "700", "middle")
        d.line(ax.px(1), ax.py(plateau), ax.px(200), ax.py(plateau), AMBER,
               1, "2 4")
        ax.line(cols["ch11gen%d" % t], AMBER, 2.4, "8 5")
        ax.line(cols["uniform%d" % t], VIOLET, 2.4)
        ax.line(cols["ordered%d" % t], GREEN, 2.4, "3 3")
        ax.line(cols["greedy%d" % t], BLUE, 3.0)
        gn = g2 if t == 2 else g3
        ax.dot(gn, 1.0, BLUE, 5, True)
        d.text(ax.px(200) - 4, ax.py(0.42), "greedy: every tuple at n = %d"
               % gn, 12.5, BLUE, "700", "end")
        d.text(ax.px(200) - 4, ax.py(0.34), "dotted line: plateau %.3f,"
               % plateau, 12, AMBER, "600", "end")
        d.text(ax.px(200) - 4, ax.py(0.34) + 15, "len max never drawn", 12,
               AMBER, "600", "end")
    key(d, 120, 470, [("greedy array", BLUE, None),
                      ("random, factor by factor", GREEN, "3 3")])
    key(d, 520, 470, [("random, uniform over legal rows", VIOLET, None),
                      ("random, the DMA's own test", AMBER, "8 5")])
    d.save("ch21-tway.svg")


def fig_unseen():
    head, rows = tsv("unseen/data.tsv")
    assert head == ["generator", "seeds", "seen", "chao2_med", "chao2_p10",
                    "chao2_p90"], head
    uo = out("unseen")
    assert "22 bins seen, Q1 0, Q2 0, Chao2 22.0" in uo
    assert re.search(r"^\s+4\s+25\.7\s+28\.1 \[22\.0,39\.2\]", uo, re.M)
    d = HW(960, 520, "How many bins will this generator reach?",
           "fifo_cg: bins seen and the Chao2 estimate (median, 10 to 90% "
           "band) against seeds")
    for k, (gen, x0, title) in enumerate((("even200", 90, "even odds, 200 "
                                           "cycles"),
                                          ("even30", 560, "even odds, 30 "
                                           "cycles"))):
        rr = [(int(r[1]), *map(float, r[2:])) for r in rows if r[0] == gen]
        ax = Axes(d, x0, 110, 360, 290, (1, 128), (15, 42), xlog=True)
        ax.frame((1, 2, 4, 8, 16, 32, 64, 128), (15, 20, 25, 28, 30, 35, 40),
                 "seeds (log scale)", "bins" if k == 0 else "")
        d.text(x0 + 180, 100, title, 14.5, INK, "700", "middle")
        d.line(ax.px(1), ax.py(28), ax.px(128), ax.py(28), INK, 1.2, "2 4")
        d.text(ax.px(128) - 4, ax.py(28) - 7, "reachable: 28", 12, INK,
               "600", "end")
        ax.band([(s, lo) for s, _, _, lo, _ in rr],
                [(s, hi) for s, _, _, _, hi in rr], VIOLET)
        ax.line([(s, med) for s, _, med, _, _ in rr], VIOLET, 2.4, "6 4")
        ax.line([(s, seen) for s, seen, _, _, _ in rr], BLUE, 3.0)
        if gen == "even30":
            last = rr[-1][1]
            assert last == 22.0, last
            d.line(ax.px(90), ax.py(22.3), ax.px(90), ax.py(27.7), AMBER, 1.6)
            d.text(ax.px(80), ax.py(25) + 4, "6 bins never seen", 12.5,
                   AMBER, "700", "end")
    key(d, 120, 470, [("bins seen (mean over resamples)", BLUE, None)])
    key(d, 520, 470, [("Chao2 median; band 10 to 90%", VIOLET, "6 4")])
    d.save("ch21-unseen.svg")


FIGS = [fig_burst, fig_coupon, fig_clean, fig_tway, fig_unseen]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
