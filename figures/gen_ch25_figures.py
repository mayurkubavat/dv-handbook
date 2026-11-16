#!/usr/bin/env python3
"""Generate the figures of the mutation-testing chapter (ch25-*.svg).

ch25-axes.svg      kill rate against toggle coverage, four testbenches:
                   the 44 source mutants, and a uniform sample of 1000
                   netlist mutations with 95% intervals
ch25-rip.svg       one mutant (m16) through reach, infect, propagate and
                   reveal, and where each of the four testbenches' chains
                   stops
ch25-matrix.svg    the kill matrix of the 44 source mutants: lint, four
                   testbenches, the property set, and the miter's class
ch25-sampling.svg  95% intervals at n = 30, 100, 300, 1000 from one
                   nested sample, against the population rate

Every figure is drawn from the run.out files of the examples under
examples/ch25-mutation-testing/. Each file read is pinned by its
SHA-256, and the values the captions and the prose quote are checked
against it, so a changed run fails this script instead of silently
redrawing a figure the text no longer describes.

    python3 figures/gen_ch25_figures.py [name ...]
"""
import hashlib
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import (AMBER, BLUE, DEEP, DIM, GREEN, GROUND, HW, INK, MONO,  # noqa
                RULE, TRACE, VIOLET)

HERE = pathlib.Path(__file__).resolve().parent
EX = HERE.parent / "examples" / "ch25-mutation-testing"
PIN = {
    "opening/run.out":
        ("e250ed6b3fe0c990cc01c278a4f1d90f"
         "9d35fa2fcd7a36cf569ed9b9b49256ff"),
    "source-mutants/run.out":
        ("5aa8aaa1aebceb5edb6dc860236d5c53"
         "367f123eb92c23d512aeb64be2a3fb40"),
    "source-sim/run.out":
        ("5dc71d4e224523ee9cf004aba9b7cc2d"
         "86de217049612ac332ef7cb171b99156"),
    "property-set/run.out":
        ("78652a22859395ba71d2ca787747e2ea"
         "93693117efdc14fafdd7e72203aeb267"),
    "miter-differ/run.out":
        ("c1ad82eb709b20670367d3c612ef71cd"
         "b617824afee783d8fe690bb2c3b18a3e"),
    "equiv-outright/run.out":
        ("dc99b75a1890b8c2c31b8647fb21e36a"
         "7381fd6d6b4c0783e61154f1d2323fc0"),
    "equiv-invariant/run.out":
        ("8ec7a500bbb03799f7461989fdedda59"
         "233a84b747b81e8de4a186ff8016dc38"),
    "equiv-reset/run.out":
        ("6ca3150b6a39a8881fa135df2286623e"
         "d42a788eb23fc2e6d5a5e82160f51e98"),
    "white-box/run.out":
        ("a08cf63c10539df228d6fe8079b9dbb8"
         "7c7e7b3a2ac0dfe25ed9ac580a5f5beb"),
    "netlist-sample/run.out":
        ("6798cee4575743d5a8385a9831275a9a"
         "ded2f6ef744fe1c16077b36e785a5fdd"),
    "netlist-population/run.out":
        ("f01f8e1d01fd527881317019fda15b8e"
         "2df21c563bba8592d5cc4b0a6213f4b5"),
}
TB = ["ch01-directed", "ch01-random", "ch08-coverage", "ch09-sva"]
NICE = {"ch01-directed": "directed test", "ch01-random": "random test",
        "ch08-coverage": "coverage testbench",
        "ch09-sva": "checking testbench"}


def check(ok, what):
    """Stop with a message unless OK. Not `assert`, which python -O
    strips, after which a changed run.out would silently redraw."""
    if not ok:
        raise SystemExit("gen_ch25_figures: check failed: %s" % (what,))


def data(rel):
    """Text of a pinned run.out; fails if it has changed."""
    raw = (EX / rel).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    check(got == PIN[rel], "%s changed (sha256 %s): re-check the " \
        "chapter's text and captions, then re-pin" % (rel, got))
    return raw.decode()


# ---- a small chart kit on top of HW -----------------------------------

class Axes:
    """A plotting frame at (x, y, w, h) with linear or log10 scales."""

    def __init__(self, d, x, y, w, h, xr, yr, xlog=False):
        self.d, self.x, self.y, self.w, self.h = d, x, y, w, h
        self.xr, self.yr, self.xlog = xr, yr, xlog

    def px(self, v):
        lo, hi = self.xr
        if self.xlog:
            v, lo, hi = math.log10(v), math.log10(lo), math.log10(hi)
        return self.x + (v - lo) / (hi - lo) * self.w

    def py(self, v):
        lo, hi = self.yr
        return self.y + self.h - (v - lo) / (hi - lo) * self.h

    def frame(self, xticks, yticks, xlab, ylab, xfmt=str, yfmt=str):
        d = self.d
        for t in yticks:
            d.line(self.x, self.py(t), self.x + self.w, self.py(t), RULE, 0.8)
            d.text(self.x - 8, self.py(t) + 4, yfmt(t), 12, DIM, "400", "end")
        for t in xticks:
            d.line(self.px(t), self.y + self.h, self.px(t),
                   self.y + self.h + 5, INK, 1)
            d.text(self.px(t), self.y + self.h + 20, xfmt(t), 12, DIM, "400",
                   "middle")
        d.line(self.x, self.y + self.h, self.x + self.w, self.y + self.h,
               INK, 1.2)
        d.line(self.x, self.y, self.x, self.y + self.h, INK, 1.2)
        d.text(self.x + self.w / 2, self.y + self.h + 42, xlab, 13.5, INK,
               "600", "middle")
        if ylab:
            cx, cy = self.x - 48, self.y + self.h / 2
            d.raw(f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="\'Source '
                  f'Sans 3\', Arial, sans-serif" font-size="13.5" '
                  f'font-weight="600" fill="{INK}" text-anchor="middle" '
                  f'transform="rotate(-90 {cx:.1f} {cy:.1f})">{ylab}</text>')

    def dot(self, a, b, col, r=5.5):
        self.d.raw(f'<circle cx="{self.px(a):.1f}" cy="{self.py(b):.1f}" '
                   f'r="{r}" fill="{col}" stroke="white" stroke-width="1.5"/>')

    def bar(self, a, lo, hi, col, cap=6):
        x = self.px(a)
        self.d.line(x, self.py(lo), x, self.py(hi), col, 2.2)
        for v in (lo, hi):
            self.d.line(x - cap, self.py(v), x + cap, self.py(v), col, 2.2)


COL = {"ch01-directed": AMBER, "ch01-random": BLUE, "ch08-coverage": DIM,
       "ch09-sva": VIOLET}


# ---- readers ------------------------------------------------------------

def opening():
    """{tb: (toggle percent, kills)} from opening/run.out."""
    t = data("opening/run.out")
    kills = dict((m.group(1), int(m.group(2))) for m in re.finditer(
        r"^  (ch\S+)\s+4/4 100%.*\s(\d+)/44$", t, re.M))
    tog = dict((m.group(1), float(m.group(2))) for m in re.finditer(
        r"^  (ch\S+)\s+toggle \d+/330 = ([\d.]+)%$", t, re.M))
    check(kills == {"ch01-directed": 34, "ch01-random": 35,
                     "ch08-coverage": 0, "ch09-sva": 22}, kills)
    check(tog == {"ch01-directed": 24.2, "ch01-random": 99.7,
                   "ch08-coverage": 98.8, "ch09-sva": 99.1}, tog)
    check("same line, branch and expression coverage, kills" in t,
          "opening summary line")
    return {k: (tog[k], kills[k]) for k in TB}


def sample():
    """{n: {tb: (k, lo, hi)}} from netlist-sample/run.out."""
    t = data("netlist-sample/run.out")
    out = {}
    for blk in re.split(r"^n = ", t, flags=re.M)[1:]:
        n = int(blk.split()[0])
        out[n] = {m.group(1): (int(m.group(2)), float(m.group(3)),
                               float(m.group(4)))
                  for m in re.finditer(r"^  (ch\S+)\s+(\d+)/\d+ = [\d.]+ "
                                       r"\[([\d.]+), ([\d.]+)\]", blk, re.M)}
    check(sorted(out) == [30, 100, 300, 1000], sorted(out))
    check([out[1000][k][0] for k in TB] == [302, 896, 0, 39],
          "kills at n = 1000")
    check(out[100]["ch01-directed"] == (30, 0.212, 0.400),
          "directed at n = 100")
    check("1000 of 1000 sampled mutations have the verdicts" in t,
          "sample agrees with pop.tsv")
    return out


def population():
    t = data("netlist-population/run.out")
    # The rate from the count, not the printed four decimals, so that
    # a label rounds 8265/9281 = 0.89053 to 0.891 and not 0.8905 to
    # 0.890.
    kills = {m.group(1): int(m.group(2)) for m in re.finditer(
        r"^  (ch\S+)\s+(\d+)/9281 = [\d.]+$", t, re.M)}
    check(kills == {"ch01-directed": 2725, "ch01-random": 8265,
                    "ch08-coverage": 0, "ch09-sva": 351}, kills)
    pop = {k: v / 9281 for k, v in kills.items()}
    check("lowest coverage over every n and testbench: 0.945" in t,
          "lowest coverage")
    return pop


def source_rows():
    """[(mutant, operator)] in file order, and the lint kills."""
    t = data("source-mutants/run.out")
    rows = re.findall(r"^  (m\d\d) ([A-Z]{3})\s+\d+  ", t, re.M)
    lint = set(re.findall(r"^  (m\d\d) rejected [A-Z]+$", t, re.M))
    check(len(rows) == 44 and len(lint) == 7, (len(rows), lint))
    check("lint kills 7 of 44 before any simulation" in t,
          "lint summary line")
    return rows, lint


def sim_matrix():
    t = data("source-sim/run.out")
    mat = {m.group(1): m.group(2).split() for m in re.finditer(
        r"^  (m\d\d) [A-Z]{3}  ([K.] [K.] [K.] [K.])$", t, re.M)}
    check(len(mat) == 44, "44 matrix rows")
    for i, (tb, k) in enumerate(zip(TB, (34, 35, 0, 22))):
        check(sum(v[i] == "K" for v in mat.values()) == k, tb)
    check("killed by no testbench: m05 m09 m11 m13 m32 m36 m43" in t,
          "survivors of every testbench")
    return mat


def prop_set():
    t = data("property-set/run.out")
    res = {}
    for m in re.finditer(r"^  (m\d\d) [A-Z]{3}  (killed by|no counter"
                         r"example|refused)", t, re.M):
        res[m.group(1)] = {"killed by": "K", "no counterexample": ".",
                           "refused": "R"}[m.group(2)]
    check(len(res) == 44, "44 property-set rows")
    check(sum(v == "K" for v in res.values()) == 38,   # 37 and m44
          "38 property-set kills")
    check("counterexamples: 38 of 44; refused by the front end: 2" in t,
          "property-set summary line")
    return res


def miter_class():
    """{mutant: class} from the miter examples."""
    t = data("miter-differ/run.out")
    cls = {m: "differs" for m in re.findall(r"^miter: (m\d\d) differs", t,
                                            re.M)}
    for m in re.findall(r"^front end refuses (m\d\d)", t, re.M):
        cls[m] = "refused"
    check(len(cls) == 39 and "differ: 37, depths 1 to 17" in t,
          "miter-differ classes")
    for rel, want in (("equiv-outright/run.out",
                       {"m32": "outright", "m36": "outright"}),
                      ("equiv-invariant/run.out", {"m43": "invariant"}),
                      ("equiv-reset/run.out", {"m05": "reset model"}),
                      ("white-box/run.out", {"m44": "at the ports"})):
        t = data(rel)
        for m, c in want.items():
            check(re.search(r"^miter: %s proved equivalent" % m, t, re.M), m)
            cls[m] = c
    check(len(cls) == 44, "a class for every mutant")
    return cls


# ---- the figures ------------------------------------------------------

def fig_axes():
    op, smp = opening(), sample()
    W, H = 980, 520
    d = HW(W, H, "Coverage does not predict kills",
           "four testbenches on the repaired FIFO: kill rate against "
           "toggle coverage")
    panels = (("44 source mutants", 110),
              ("1,000 sampled netlist mutations (95% interval)", 590))
    # label placement (dx, dy, anchor) for each testbench, per panel
    place = [{"ch01-directed": (12, 22, "start"),
              "ch01-random": (-12, -10, "end"),
              "ch08-coverage": (-12, -10, "end"),
              "ch09-sva": (-12, 4, "end")},
             {"ch01-directed": (12, 4, "start"),
              "ch01-random": (-14, 4, "end"),
              "ch08-coverage": (-14, -8, "end"),
              "ch09-sva": (-14, -30, "end")}]
    for k, (title, x0) in enumerate(panels):
        ax = Axes(d, x0, 110, 330, 300, (0, 100), (0, 1))
        ax.frame((0, 25, 50, 75, 100), (0, 0.2, 0.4, 0.6, 0.8, 1.0),
                 "toggle coverage (%)", "kill rate" if k == 0 else "",
                 yfmt=lambda v: "%.1f" % v)
        d.text(x0 + 165, 98, title, 14.5, INK, "700", "middle")
        for tb in TB:
            tog, kills = op[tb]
            if k == 0:
                y = kills / 44
                lab = "%s %d/44" % (NICE[tb], kills)
            else:
                kk, lo, hi = smp[1000][tb]
                y = kk / 1000
                ax.bar(tog, lo, hi, COL[tb], 4)
                lab = "%s %d/1000" % (NICE[tb], kk)
            ax.dot(tog, y, COL[tb])
            dx, dy, anc = place[k][tb]
            d.text(ax.px(tog) + dx, ax.py(y) + dy, lab, 12.5, COL[tb]
                   if tb != "ch08-coverage" else INK, "600", anc)
    d.text(110, H - 22, "Toggle coverage is the same in both panels; each "
           "testbench was run as it ships.", 13, DIM)
    d.save("ch25-axes.svg")


def fig_rip():
    rows, _ = source_rows()
    mat = sim_matrix()
    t = data("source-mutants/run.out")
    check(re.search(r"^  m16 VSW  43  mem\[rd_ptr\] <= wr_data;$", t,
                    re.M), "m16 is the write-address swap")
    check(mat["m16"] == ["K", "K", ".", "."], mat["m16"])
    W, H = 980, 700
    d = HW(W, H, "One mutant through reach, infect, propagate, reveal",
           "m16: mem[rd_ptr] <= wr_data, where the design writes "
           "mem[wr_ptr] <= wr_data")
    # -- the datapath ----------------------------------------------------
    wp = d.reg(120, 96, "wr_ptr", w=104)
    rp = d.reg(120, 176, "rd_ptr", w=104)
    mem = d.fifo(330, 134, 16, w=300, h=46, name="mem, 16 words")
    cnt = d.reg(720, 96, "count", w=104)
    d.text(60, 160, "wr_data", 13, INK, "500", "start", MONO)
    d.wire([(120, 166), (300, 166), (330, 160)], "data")
    # the design's write address, struck out
    d.wire([(224, 116), (300, 116), (360, 134)], "plain", arrow=False)
    d.line(268, 106, 292, 126, AMBER, 2.4)
    d.line(268, 126, 292, 106, AMBER, 2.4)
    d.text(228, 104, "wr addr", 11.5, DIM, "400", "start", MONO)
    # the mutant's write address: the read pointer
    d.wire([(224, 196), (300, 196), (380, 180)], "control")
    d.text(258, 224, "write address in m16", 12, AMBER, "700")
    d.wire([(224, 186), (250, 186), (250, 240), (480, 240),
            (480, 180)], "plain")
    d.text(330, 256, "read address", 12, DIM)
    d.wire([(630, 157), (700, 157), (700, 230), (760, 230)], "data")
    d.text(770, 234, "rd_data", 13, INK, "600", "start", MONO)
    d.op(860, 116, "==0", r=22)
    d.wire([(824, 116), (838, 116)], "plain")
    d.text(890, 120, "empty", 13, INK, "600", "start", MONO)
    d.op(860, 176, "==16", r=22)
    d.wire([(800, 136), (800, 176), (838, 176)], "plain")
    d.text(890, 180, "full", 13, INK, "600", "start", MONO)
    # -- the four conditions ---------------------------------------------
    steps = [("reach", "a push executes the\nmutated write"),
             ("infect", "the word lands in\nthe wrong slot"),
             ("propagate", "a pop shows the\nwrong word on rd_data"),
             ("reveal", "a check compares\nrd_data, and fails")]
    bx, by, bw, bh, gap = 150, 300, 180, 76, 20
    for i, (name, sub) in enumerate(steps):
        x = bx + i * (bw + gap)
        d.rect(x, by, bw, bh, GROUND, BLUE, 2, 8)
        d.text(x + bw / 2, by + 24, name, 16, BLUE, "700", "middle")
        for j, ln in enumerate(sub.split("\n")):
            d.text(x + bw / 2, by + 46 + j * 16, ln, 12.5, INK, "400",
                   "middle")
        if i:
            d.wire([(x - gap + 2, by + bh / 2), (x - 2, by + bh / 2)],
                   "plain")
    # -- where each testbench's chain stops -------------------------------
    stop = {"ch08-coverage": 3, "ch09-sva": 3, "ch01-directed": 4,
            "ch01-random": 4}
    why = {"ch08-coverage": "no check at all: survived",
           "ch09-sva": "checks occupancy and flags, not data: survived",
           "ch01-directed": "compares each word it reads back: killed",
           "ch01-random": "compares rd_data with its queue: killed"}
    for r, tb in enumerate(("ch08-coverage", "ch09-sva", "ch01-directed",
                            "ch01-random")):
        y = 420 + r * 64
        verdict = mat["m16"][TB.index(tb)]
        check((verdict == "K") == (stop[tb] == 4), tb)
        d.text(bx - 12, y + 5, NICE[tb], 13.5, INK, "600", "end")
        x1 = bx + stop[tb] * (bw + gap) - gap
        col = GREEN if stop[tb] == 4 else AMBER
        d.raw(f'<rect x="{bx}" y="{y - 7}" width="{x1 - bx}" height="14" '
              f'rx="7" fill="{TRACE}" stroke="{DEEP}" stroke-width="1.2"/>')
        if stop[tb] == 4:
            cx = x1 + 22
            d.raw(f'<path d="M{cx - 10},{y} L{cx - 3},{y + 8} '
                  f'L{cx + 11},{y - 9}" fill="none" stroke="{col}" '
                  'stroke-width="4" stroke-linecap="round"/>')
        else:
            cx = x1 + 22
            d.line(cx - 9, y - 9, cx + 9, y + 9, col, 4)
            d.line(cx - 9, y + 9, cx + 9, y - 9, col, 4)
        d.text(bx + 4, y + 30, why[tb], 12.5, DIM)
    d.save("ch25-rip.svg")


def fig_matrix():
    rows, lint = source_rows()
    mat, prop, cls = sim_matrix(), prop_set(), miter_class()
    order = ["LCR", "LNR", "ARS", "CNG", "CRP", "SDL", "VSW", "AOR", "ROR",
             "CSW"]
    groups = [(o, [m for m, op in rows if op == o]) for o in order]
    check(sum(len(g) for _, g in groups) == 44, "44 mutants grouped")
    CW, RH, GAP, X0 = 16, 24, 8, 165
    W = X0 + 44 * CW + GAP * (len(groups) - 1) + 30
    labels = ["lint", NICE["ch01-directed"], NICE["ch01-random"],
              NICE["ch08-coverage"], NICE["ch09-sva"], "property set",
              "miter class"]
    top = 150
    H = top + RH * len(labels) + 96
    d = HW(W, H, "The kill matrix of the 44 source mutants",
           "dark: killed; light: survived; R: refused by the formal "
           "front end")
    clscol = {"differs": TRACE, "refused": RULE, "outright": GREEN,
              "invariant": VIOLET, "reset model": AMBER,
              "at the ports": DEEP}
    x = X0
    for gi, (op, ms) in enumerate(groups):
        d.text(x + len(ms) * CW / 2, top - 52, op, 12, INK, "700", "middle")
        d.line(x + 1, top - 46, x + len(ms) * CW - 1, top - 46, DIM, 1)
        for m in ms:
            cx = x + CW / 2
            d.raw(f'<text x="{cx + 4:.1f}" y="{top - 6}" font-family='
                  f'"\'JetBrains Mono\', Menlo, monospace" font-size="11.5" '
                  f'fill="{INK}" transform="rotate(-90 {cx + 4:.1f} '
                  f'{top - 6})">{m}</text>')
            cells = (["K" if m in lint else "."] + mat[m] + [prop[m]])
            for r, v in enumerate(cells):
                y = top + r * RH
                fill = BLUE if v == "K" else ("white" if v == "R"
                                              else GROUND)
                d.rect(x + 1, y + 1, CW - 2, RH - 2, fill, RULE, 0.8)
                if v == "R":
                    d.text(cx, y + RH / 2 + 4, "R", 11, INK, "700",
                           "middle")
            y = top + 6 * RH + 6
            d.rect(x + 1, y + 1, CW - 2, RH - 2, clscol[cls[m]], RULE, 0.8)
            x += CW
        x += GAP
    for r, lab in enumerate(labels):
        y = top + r * RH + (6 if r == 6 else 0)
        d.text(X0 - 10, y + RH / 2 + 4, lab, 12.5, INK,
               "700" if r == 6 else "500", "end")
    ly = top + 7 * RH + 44
    items = [("differs", "differs (37)"), ("refused", "refused (2)"),
             ("outright", "equivalent outright"),
             ("invariant", "under an invariant"),
             ("reset model", "under the tool's reset model"),
             ("at the ports", "invariant across copies; Sync_A kills")]
    check(sum(c == "differs" for c in cls.values()) == 37,
          "37 mutants differ")
    lx = X0
    for i, (c, lab) in enumerate(items):
        if i == 3:
            lx, ly = X0, ly + 26
        d.rect(lx, ly - 12, 16, 16, clscol[c], RULE, 0.8)
        d.text(lx + 24, ly + 1, lab, 12.5, INK)
        lx += 250
    d.save("ch25-matrix.svg")


def fig_sampling():
    smp, pop = sample(), population()
    W, H = 980, 500
    d = HW(W, H, "One uniform sample, four sizes, against the truth",
           "95% Clopper-Pearson intervals from one nested sample (seed 1) "
           "of the 9,281 netlist mutations")
    spec = (("ch01-directed", (0, 0.7)), ("ch01-random", (0.6, 1.0)),
            ("ch09-sva", (0, 0.2)))
    ns = [30, 100, 300, 1000]
    for k, (tb, yr) in enumerate(spec):
        x0 = 100 + k * 300
        ax = Axes(d, x0, 128, 220, 272, (18, 1700), yr, xlog=True)
        step = 0.1 if yr[1] - yr[0] > 0.3 else 0.05
        ticks = [round(yr[0] + i * step, 2)
                 for i in range(int(round((yr[1] - yr[0]) / step)) + 1)]
        ax.frame(ns, ticks, "sample size n", "kill rate" if k == 0 else "",
                 xfmt=lambda v: "{:,}".format(v),
                 yfmt=lambda v: "%.2f" % v)
        d.text(x0 + 110, 98, NICE[tb], 14.5, INK, "700", "middle")
        p = pop[tb]
        d.line(ax.px(18), ax.py(p), ax.px(1700), ax.py(p), INK, 1.4, "6 4")
        d.text(x0 + 110, 116, "dashed: population %.3f" % p, 11.5,
               DIM, "600", "middle")
        for n in ns:
            kk, lo, hi = smp[n][tb]
            check(lo <= p <= hi, (tb, n))     # "every bar crosses its line"
            ax.bar(n, lo, hi, COL[tb])
            ax.dot(n, kk / n, COL[tb], 4.5)
    d.text(100, H - 22, "The coverage testbench, at zero in every sample, "
           "is left out.", 13, DIM)
    d.save("ch25-sampling.svg")


FIGS = [fig_axes, fig_rip, fig_matrix, fig_sampling]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
