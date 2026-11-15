#!/usr/bin/env python3
"""Generate the figures of the logic-and-solvers chapter (ch17-*.svg).

ch17-map.svg          three questions, one formula, four representations
ch17-tseitin.svg      the full adder with a variable on every wire
ch17-search.svg       dpll.py's search tree on the 2-bit adder miter
ch17-implication.svg  one conflict of cdcl.py as an implication graph
ch17-learning.svg     decisions and conflicts against width, three solvers
ch17-hard.svg         adder against multiplier; random 3-SAT by density
ch17-bdd.svg          one carry function under two variable orders
ch17-aig.svg          the full adder as an and-inverter graph
ch17-unroll.svg       a sequential circuit copied once per cycle
ch17-bound.svg        the FIFO's unrolling, bound by bound

Every number drawn is read from an example's run.out or source file,
or computed by running the example's own code, and each figure checks
itself against the run.out where both state the same thing.

    python3 figures/gen_ch17_figures.py [name ...]
"""
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import (AMBER, AMBER_T, BLUE, DEEP, DIM, GREEN, GREEN_T,  # noqa
                GROUND, HW, INK, MONO, RULE, TRACE, VIOLET)

EX = (pathlib.Path(__file__).resolve().parent.parent / "examples" /
      "ch17-logic-and-solvers")
for sub in ("common", "dpll", "cdcl", "bdd"):
    sys.path.insert(0, str(EX / sub))


def out(example):
    return (EX / example / "run.out").read_text()


def ints(text):
    return [int(x.replace(",", "")) for x in re.findall(r"[\d,]*\d", text)]


def arrow(d, x1, y1, x2, y2, col=DIM, sw=1.6, dash=None, shrink=0):
    """A straight arrow, shortened by `shrink` at its head."""
    length = math.hypot(x2 - x1, y2 - y1) or 1
    x2 -= (x2 - x1) * shrink / length
    y2 -= (y2 - y1) * shrink / length
    mk = {DIM: "ah", BLUE: "ahd", AMBER: "ahc", INK: "ahg"}.get(col, "ah")
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    d.raw(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" fill="none" '
          f'stroke="{col}" stroke-width="{sw}"{dd} '
          f'marker-end="url(#{mk})"/>')


def node(d, cx, cy, label, r=20, fill="white", stroke=DEEP, sw=2, size=13):
    d.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{sw}"/>')
    d.text(cx, cy + size * 0.36, label, size, INK, "600", "middle", MONO)


# ---- a line chart with a logarithmic or linear y axis -----------------
class Chart:
    def __init__(self, d, x, y, w, h, xr, yr, log=True):
        self.d, self.x, self.y, self.w, self.h = d, x, y, w, h
        self.xr, self.yr, self.log = xr, yr, log
        d.rect(x, y, w, h, "white", RULE, 1)

    def px(self, v):
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def py(self, v):
        lo, hi = self.yr
        if self.log:
            f = (math.log10(v) - math.log10(lo)) / (math.log10(hi)
                                                    - math.log10(lo))
        else:
            f = (v - lo) / (hi - lo)
        return self.y + self.h - f * self.h

    def xticks(self, values, label, fmt=str):
        for v in values:
            self.d.line(self.px(v), self.y + self.h, self.px(v),
                        self.y + self.h + 5, DIM)
            self.d.text(self.px(v), self.y + self.h + 20, fmt(v), 12, INK,
                        "400", "middle", MONO)
        self.d.text(self.x + self.w / 2, self.y + self.h + 40, label, 13,
                    DIM, "400", "middle")

    def yticks(self, values, label=None, right=False, col=INK):
        for v in values:
            yy = self.py(v)
            if not right:
                self.d.line(self.x, yy, self.x + self.w, yy, GROUND)
            xx = self.x + self.w + 8 if right else self.x - 8
            self.d.text(xx, yy + 4, f"{v:,}", 12, col, "400",
                        "start" if right else "end", MONO)
        if label:
            self.d.text(self.x + (self.w if right else 0), self.y - 10,
                        label, 13, col if right else DIM, "400",
                        "end" if right else "start")

    def series(self, points, col, name=None, dash=None, at=None):
        pts = [(self.px(a), self.py(b)) for a, b in points]
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.d.raw('<polyline points="'
                   + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
                   + f'" fill="none" stroke="{col}" stroke-width="2.4"{dd}/>')
        for a, b in pts:
            self.d.raw(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3.4" '
                       f'fill="{col}"/>')
        if name:
            ax, ay = at or (pts[-1][0] + 8, pts[-1][1] + 4)
            self.d.text(ax, ay, name, 13, col, "600", "start", MONO)


# ---- F1: the chapter in one picture -----------------------------------
def fig_map():
    d = HW(1000, 500, "Three questions, one question",
           "Each becomes a formula and the question whether some "
           "assignment makes it true.",
           "Three boxes on the left, always true, the same, reachable "
           "in k steps, with arrows into one box, is the formula "
           "satisfiable, and from it to four boxes: clauses and search, "
           "decision diagrams, and-inverter graphs and word-level "
           "bit-vectors, with the book's tools attached to two of them")
    qs = [("Is it always true?", "validity: no input falsifies F"),
          ("Are these two the same?", "equivalence: no input tells them apart"),
          ("Can it get there in k steps?", "reachability: a trace of length k")]
    boxes = []
    for i, (q, sub) in enumerate(qs):
        boxes.append(d.unit(30, 110 + i * 120, 290, 76, q, sub))
    mid = d.unit(400, 210, 190, 116, "Is this formula\nsatisfiable?",
                 fill=TRACE)
    d.text(495, 350, "yes: an assignment,", 13, DIM, "400", "middle")
    d.text(495, 367, "which is the counterexample", 13, DIM, "400",
           "middle")
    d.text(495, 384, "no: there is none", 13, DIM, "400", "middle")
    for b in boxes:
        d.wire([(b.r, b.cy), (mid.l, mid.cy + (b.cy - mid.cy) * 0.3)],
               "data")
    reps = [("Clauses and search", "CNF, a SAT solver",
             "the chapter's solvers"),
            ("Decision diagrams", "a canonical form: BDD",
             "the chapter's package"),
            ("And-inverter graphs", "the circuit itself: AIG",
             "InFormal: Btor2, then AIGER"),
            ("Words, not bits", "bit-vector SMT",
             "Verilator randomize(): z3")]
    for i, (name, sub, who) in enumerate(reps):
        b = d.unit(680, 100 + i * 96, 290, 70, name, sub,
                   fill="white" if i < 3 else GROUND)
        d.wire([(mid.r, mid.cy + (b.cy - mid.cy) * 0.3), (b.l, b.cy)],
               "data")
        d.text(b.r, b.b + 15, who, 12, AMBER, "600", "end")
    d.text(30, 478, "amber: where this book's tools use each "
           "representation, as measured in its examples", 13, DIM)
    d.save("ch17-map.svg")


# ---- F2: the full adder, a variable on every wire ---------------------
def fig_tseitin():
    text = (EX / "tseitin" / "full_adder.cnf").read_text().splitlines()
    num = {name: int(n) for n, name in
           re.findall(r"(\d+)=(\w+)", text[1])}
    groups, cur = [], None
    for line in text[3:]:
        if line.startswith("c "):
            cur = [line[2:], []]
            groups.append(cur)
        else:
            cur[1].append(line[:-2])
    assert len(groups) == 5 and sum(len(g[1]) for g in groups) == 17
    d = HW(1000, 490, "One variable for every wire",
           "Each gate becomes the few clauses that tie its output "
           "variable to its inputs.",
           "The full adder as five gates with every wire numbered 1 to "
           "8, and beside it the seventeen clauses in five groups, one "
           "group per gate")

    def gate(x, y, kind, name):
        d.rect(x, y, 78, 52, TRACE, DEEP, 2, 8)
        d.text(x + 39, y + 24, kind, 15, INK, "700", "middle")
        d.text(x + 39, y + 42, f"{name} = {num[name]}", 12, DEEP, "600",
               "middle", MONO)

    def dot(x, y):
        d.raw(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{BLUE}"/>')

    for name, y in (("a", 132), ("b", 172), ("cin", 262)):
        d.text(40, y + 5, f"{name} = {num[name]}", 14, INK, "600", "start",
               MONO)
    gate(230, 126, "XOR", "p")
    gate(420, 150, "XOR", "sum")
    gate(230, 330, "AND", "g")
    gate(420, 250, "AND", "t")
    gate(540, 320, "OR", "cout")
    d.wire([(112, 132), (230, 132)])                    # a
    d.wire([(140, 132), (140, 342), (230, 342)])
    dot(140, 132)
    d.wire([(112, 172), (230, 172)])                    # b
    d.wire([(170, 172), (170, 370), (230, 370)])
    dot(170, 172)
    d.wire([(308, 152), (360, 152), (360, 162), (420, 162)])   # p
    d.wire([(360, 162), (360, 262), (420, 262)])
    dot(360, 162)
    d.wire([(112, 262), (200, 262), (200, 300), (390, 300), (390, 290),
            (420, 290)])                                # cin
    d.wire([(390, 290), (390, 190), (420, 190)])
    dot(390, 290)
    d.wire([(498, 176), (610, 176)])                    # sum
    d.wire([(498, 276), (520, 276), (520, 332), (540, 332)])   # t
    d.wire([(308, 356), (540, 356)])                    # g
    d.wire([(618, 346), (650, 346)])                    # cout
    d.text(40, 430, "an inverter needs no variable: negate the literal",
           13, DIM)
    d.text(40, 450, f"{len(num)} variables, 17 clauses; the question is "
           "added as unit clauses", 13, DIM)
    x, y = 690, 108
    for title, clauses in groups:
        d.text(x, y, title, 14, BLUE, "700")
        for i, c in enumerate(clauses):
            d.text(x + 14 + (i % 2) * 130, y + 20 + (i // 2) * 19,
                   f"({c})", 13, INK, "400", "start", MONO)
        y += 30 + ((len(clauses) + 1) // 2) * 19 + 12
    d.save("ch17-tseitin.svg")


# ---- F3: the search tree of dpll.py on the 2-bit miter ----------------
def fig_search():
    import gen
    from dpll import Dpll
    cnf = gen.adder_miter(2)
    s = Dpll(cnf.nvars, cnf.clauses)
    s.log = []
    assert s.solve() is False
    value, leaves = {}, []
    for why, what in s.log:
        if why in ("decide", "flip"):
            for v in [v for v in value if v > abs(what)]:
                del value[v]
            value[abs(what)] = what > 0
        elif why == "conflict":
            leaves.append(tuple(value[v] for v in (1, 2, 3, 4)))
    row = re.search(r"^ +2 +24 +71 +(\d+) +(\d+)", out("dpll"), re.M)
    if (s.decisions, len(leaves)) != tuple(map(int, row.groups())) \
            or len(set(leaves)) != 16:
        sys.exit("ch17-search: the tree is not the one run.out counts")
    d = HW(1000, 430, "Search without memory",
           "dpll.py on the 2-bit adder miter: 15 decisions, and a "
           "conflict under every one of the 16 input values.",
           "A complete binary tree four levels deep over the inputs a0, "
           "a1, b0, b1, the left branch true and the right false, with "
           "sixteen leaves, each a conflict, numbered in the order the "
           "search reached them")
    names = ["a0", "a1", "b0", "b1"]
    x0, x1, ys = 90, 970, [110, 180, 250, 320, 384]

    def pos(depth, index):
        width = (x1 - x0) / 2 ** depth
        return x0 + width * (index + 0.5), ys[depth]

    for depth in range(4):
        d.text(30, ys[depth] + 5, names[depth], 15, INK, "700", "start",
               MONO)
        for index in range(2 ** depth):
            x, y = pos(depth, index)
            for k in (0, 1):
                cx, cy = pos(depth + 1, index * 2 + k)
                end = cy - (12 if depth < 3 else 13)
                d.line(x, y + 11, cx, end, DIM, 1.5)
                if depth < 2:
                    d.text((x + cx) / 2 + (-14 if k == 0 else 14),
                           (y + cy) / 2 - 6, "1" if k == 0 else "0", 13,
                           INK, "600", "middle", MONO)
    for depth in range(4):
        for index in range(2 ** depth):
            x, y = pos(depth, index)
            d.raw(f'<circle cx="{x:.1f}" cy="{y}" r="11" fill="{TRACE}" '
                  f'stroke="{DEEP}" stroke-width="2"/>')
    d.text(30, ys[4] + 5, "end", 13, DIM, "400", "start")
    for order, leaf in enumerate(leaves, start=1):
        index = sum((not bit) << (3 - i) for i, bit in enumerate(leaf))
        x, y = pos(4, index)
        d.rect(x - 17, y - 12, 34, 24, AMBER_T, AMBER, 1.6, 4)
        d.text(x, y + 5, str(order), 13, INK, "600", "middle", MONO)
    d.text(90, 420, "left branch: the variable is 1; right: 0. Amber: a "
           "conflict, numbered in the order the search met it.", 13, DIM)
    d.save("ch17-search.svg")


# ---- F4: one conflict as an implication graph -------------------------
def fig_implication():
    text = out("cdcl")
    part = text.split("2. the adder miter")[0]
    trail = [(int(a), b) for a, b in
             re.findall(r"^ +(-?\d+)   (decision|\([^)]*\))", part, re.M)]
    signed = [int(x) for x in re.search(r"learned clause: \((.*?)\)",
                                        part).group(1).split()]
    conflict = [int(x) for x in re.search(r"falsified clause: \((.*)\)",
                                          part).group(1).split()]
    uip = int(re.search(r"implication point: (-?\d+)", part).group(1))
    here = {abs(lit) for lit, _ in trail}
    depth, parents = {}, {}
    for lit, why in trail:
        if why == "decision":
            depth[lit], parents[lit] = 0, []
            continue
        others = [-int(x) for x in why.strip("()").split() if int(x) != lit]
        parents[lit] = others
        depth[lit] = 1 + max(depth[p] for p in others if abs(p) in here)
    parents["K"] = [-x for x in conflict]
    depth["K"] = 1 + max(depth[p] for p in parents["K"])
    outside = [-x for x in signed if abs(x) not in here]
    after = {lit for lit, _ in trail if depth[lit] > depth[uip]} | {"K"}
    d = HW(1000, 510, "Why the conflict happened",
           "Conflict 20 of cdcl.py on the 3-bit adder miter. An arrow "
           "runs from each cause to the assignment it forced.",
           "A graph in seven columns from the decision b1 = 1 on the "
           "left to the conflict on the right. Every path from the "
           "decision to the conflict passes through x37 = 1, which is "
           "marked as the first unique implication point; three "
           "assignments from decision level 1 feed the part after it")
    name = {1: "a0", 2: "a1", 3: "a2", 4: "b0", 5: "b1", 6: "b2"}

    def label(lit):
        v = abs(lit)
        return f"{name.get(v, 'x' + str(v))}={int(lit > 0)}"

    cols = {}
    for lit in list(depth):
        cols.setdefault(depth[lit], []).append(lit)
    pos = {}
    for c, lits in cols.items():
        for i, lit in enumerate(lits):
            pos[lit] = (75 + c * 142,
                        330 + (i - (len(lits) - 1) / 2) * 96)
    for i, lit in enumerate(outside):
        pos[lit] = (75 + 142 * (3.5 + i * 0.75), 122)
    cut = 75 + 142 * (depth[uip] + 0.5)
    d.line(cut, 150, cut, 492, AMBER, 1.6, "7 5")
    d.text(cut + 8, 488, "the cut: everything to the right follows from "
           "x37 = 1 and level 1", 13, AMBER, "600")
    for lit, ps in parents.items():
        for p in ps:
            if p not in pos:
                continue                # an earlier level, not in the cut
            hot = lit in after
            (x1, y1), (x2, y2) = pos[p], pos[lit]
            if y1 == y2 and x2 - x1 > 200:      # would run through a node
                d.raw(f'<path d="M{x1 + 22:.1f},{y1 + 14:.1f} '
                      f'Q{(x1 + x2) / 2:.1f},'
                      f'{y1 + 190:.1f} {x2 - 20:.1f},{y2 + 22:.1f}" '
                      f'fill="none" stroke="{BLUE}" stroke-width="1.8" '
                      'marker-end="url(#ahd)"/>')
                continue
            arrow(d, x1, y1, x2, y2, BLUE if hot else RULE,
                  1.8 if hot else 1.3, shrink=31)
    for lit, (x, y) in pos.items():
        if lit == "K":
            d.rect(x - 34, y - 20, 68, 40, AMBER_T, AMBER, 2.4, 6)
            d.text(x, y + 5, "conflict", 13, INK, "700", "middle")
            continue
        fill = GROUND if lit in outside else "white"
        stroke, sw = (AMBER, 3.2) if lit == uip else (DEEP, 2)
        d.raw(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="30" ry="19" '
              f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        d.text(x, y + 4.5, label(lit), 12.5, INK, "600", "middle", MONO)
    x, y = pos[trail[0][0]]
    d.text(x, y + 38, "decision,", 13, DIM, "400", "middle")
    d.text(x, y + 54, "level 2", 13, DIM, "400", "middle")
    x, y = pos[uip]
    d.text(x, y - 30, "first UIP", 13, AMBER, "700", "middle")
    x, y = pos[outside[0]]
    d.text(x - 44, y + 5, "from level 1:", 13, DIM, "400", "end")
    words = " or ".join(("" if x > 0 else "not ") + label(x)[:-2]
                        for x in sorted(signed, key=abs))
    d.text(30, 96, f"learned clause: {words}", 14, INK, "600", "start",
           MONO)
    d.save("ch17-implication.svg")


# ---- F5: what each idea bought ----------------------------------------
def adder_table():
    rows = {}
    for line in out("cdcl").split("2. the adder miter")[1] \
            .split("3. the miter")[0].splitlines():
        cells = line.split()
        if cells and cells[0].isdigit():
            rows[int(cells[0])] = [None if c == "-" else
                                   int(c.replace(",", ""))
                                   for c in cells[3:6]]
    return rows


def fig_learning():
    rows = adder_table()
    d = HW(1000, 470, "Three ideas, three curves",
           "The adder miter, unsatisfiable at every width: work against "
           "the width of the adders, on a logarithmic axis.",
           "Line chart with a logarithmic vertical axis. Decisions of "
           "dpll.py rise steeply from 15 at 2 bits to 16,383 at 7; "
           "conflicts of cdcl.py rise half as steeply to 12,820 at 12 "
           "bits; conflicts of cdcl_vsids.py stay between 13 and 2,410 "
           "out to 32 bits")
    c = Chart(d, 90, 110, 760, 290, (2, 32), (10, 100000))
    c.xticks([2, 4, 6, 8, 10, 12, 16, 24, 32], "width of each adder, bits")
    c.yticks([10, 100, 1000, 10000, 100000], "decisions or conflicts")
    series = [[(n, r[k]) for n, r in rows.items() if r[k]] for k in range(3)]
    c.series(series[0], AMBER, "dpll.py",
             at=(c.px(7) + 10, c.py(series[0][-1][1]) + 4))
    c.series(series[1], BLUE, "cdcl.py",
             at=(c.px(12) + 10, c.py(series[1][-1][1]) + 4))
    c.series(series[2], GREEN, "cdcl_vsids.py",
             at=(c.px(32) - 100, c.py(series[2][-1][1]) - 12))
    d.text(865, 130, "search:", 13, AMBER, "700")
    d.text(865, 147, f"{series[0][-1][1]:,} decisions", 13, INK)
    d.text(865, 164, f"at {series[0][-1][0]} bits", 13, INK)
    d.text(865, 200, "+ learning:", 13, BLUE, "700")
    d.text(865, 217, f"{series[1][-1][1]:,} conflicts", 13, INK)
    d.text(865, 234, f"at {series[1][-1][0]} bits", 13, INK)
    d.text(865, 270, "+ heuristic:", 13, GREEN, "700")
    d.text(865, 287, f"{series[2][-1][1]:,} conflicts", 13, INK)
    d.text(865, 304, f"at {series[2][-1][0]} bits", 13, INK)
    d.save("ch17-learning.svg")


# ---- F6: where it is hard ---------------------------------------------
def fig_hard():
    text = out("hard")
    mul = [ints(x) for x in text.split("2. is a*b")[1]
           .split("3. random")[0].splitlines() if x.split()[:1]
           and x.split()[0].isdigit()]
    rnd = [x.split() for x in text.split("3. random")[1].splitlines()
           if re.match(r" +\d\.\d", x)]
    d = HW(1000, 470, "Hardness is a property of the formula",
           "Left: two circuits of the same width. Right: random 3-SAT "
           "with 60 variables and a growing number of clauses.",
           "Two charts. Left, logarithmic: conflicts of cdcl.py on the "
           "adder miter grow from 12 to 410 between 2 and 7 bits and on "
           "the multiplier miter from 8 to 3,655, with cdcl_vsids.py on "
           "the multiplier higher still. Right: the number of "
           "satisfiable formulas out of 30 falls from 30 to 0 as the "
           "ratio of clauses to variables goes from 3.0 to 5.8, and the "
           "median conflicts peak near 4.6")
    c = Chart(d, 80, 120, 340, 270, (2, 7), (5, 10000))
    c.xticks(range(2, 8), "width, bits")
    c.yticks([10, 100, 1000, 10000], "conflicts")
    c.series([(r[0], r[2]) for r in mul], GREEN, "adder",
             at=(c.px(6.1), c.py(105)))
    c.series([(r[0], r[5]) for r in mul], BLUE, "a*b = b*a",
             at=(c.px(5.45), c.py(300)))
    c.series([(r[0], r[6]) for r in mul], AMBER, "with the heuristic",
             dash="5 4", at=(c.px(3.55), c.py(2600)))
    c2 = Chart(d, 560, 120, 340, 270, (2.8, 6.0), (0, 30), log=False)
    c2.xticks([float(r[0]) for r in rnd], "clauses per variable")
    c2.yticks([0, 10, 20, 30], "satisfiable, of 30")
    for r in rnd:
        x, n = c2.px(float(r[0])), int(r[2])
        d.rect(x - 11, c2.py(n), 22, c2.py(0) - c2.py(n), TRACE, DIM, 1)
    c3 = Chart.__new__(Chart)
    c3.__dict__.update(c2.__dict__)
    c3.yr = (0, 120)
    c3.yticks([0, 40, 80, 120], "median conflicts", right=True, col=AMBER)
    c3.series([(float(r[0]), int(r[5])) for r in rnd], AMBER)
    d.save("ch17-hard.svg")


# ---- F7: one function, two variable orders ----------------------------
def fig_bdd():
    from robdd import AND, OR, XOR, Bdd
    sizes = [ints(x) for x in out("bdd").split("2. decision")[1]
             .split("3. decision")[0].splitlines()[2:]]
    want = {r[0]: (r[1], r[3]) for r in sizes}[3]
    d = HW(1000, 560, "One function, two variable orders",
           "The carry out of a 3-bit adder. Solid edge: the variable is "
           "1; dashed: 0.",
           "Two decision diagrams of the same function. With the "
           "operand bits interleaved the diagram is a narrow ladder of "
           "8 nodes; with all of a before all of b it fans out to four "
           "nodes at a2 and four at b0, 14 nodes in all")
    n = 3
    a = [f"a{i}" for i in range(n)]
    b = [f"b{i}" for i in range(n)]
    orders = [[v for pair in zip(a, b) for v in pair], a + b]
    x0 = [40, 470]
    width = [330, 500]
    got = []
    for k, order in enumerate(orders):
        m = Bdd(order)
        c = 0
        for x, y in zip(a, b):
            p = m.apply(XOR, m.var(x), m.var(y))
            c = m.apply(OR, m.apply(AND, m.var(x), m.var(y)),
                        m.apply(AND, p, c))
        nodes = m.reachable(c)
        got.append(len(nodes))
        by_level = {}
        for f in nodes:
            by_level.setdefault(m.nodes[f][0], []).append(f)
        pos, pull = {}, {c: [0.5]}      # node -> where its parents sit
        for lv in sorted(by_level):
            fs = sorted(by_level[lv],
                        key=lambda f: sum(pull[f]) / len(pull[f]))
            for i, f in enumerate(fs):
                frac = (i + 0.5) / len(fs)
                pos[f] = (x0[k] + 70 + width[k] * frac, 125 + lv * 62)
                for child, shift in ((m.nodes[f][2], -0.02),
                                     (m.nodes[f][1], 0.02)):
                    pull.setdefault(child, []).append(frac + shift)
        pos[1] = (x0[k] + 70 + width[k] * 0.3, 505)
        pos[0] = (x0[k] + 70 + width[k] * 0.7, 505)
        for lv, name in enumerate(order):
            d.text(x0[k] + 28, 130 + lv * 62, name, 14, INK, "700", "start",
                   MONO)
        for f in nodes:
            _, low, high = m.nodes[f]
            for child, dash in ((high, None), (low, "5 4")):
                (x1, y1), (x2, y2) = pos[f], pos[child]
                d.line(x1, y1, x2, y2, BLUE if dash is None else DIM, 1.7,
                       dash)
        for f in nodes:
            x, y = pos[f]
            d.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" '
                  f'fill="{TRACE}" stroke="{DEEP}" stroke-width="2"/>')
            d.text(x, y + 4, order[m.nodes[f][0]], 11, INK, "600", "middle",
                   MONO)
        for t in (0, 1):
            x, y = pos[t]
            d.rect(x - 15, y - 14, 30, 28, "white", DEEP, 2, 3)
            d.text(x, y + 5, str(t), 14, INK, "700", "middle", MONO)
        d.text(x0[k] + 70 + width[k] / 2, 545,
               f"order {' '.join(order)}: {len(nodes)} decision nodes", 14,
               INK, "600", "middle")
    if tuple(got) != want:
        sys.exit(f"ch17-bdd: drew {got}, run.out says {want}")
    d.save("ch17-bdd.svg")


# ---- F8: the full adder as an and-inverter graph ----------------------
def fig_aig():
    from aiger import Aig
    aig = Aig(EX / "aig" / "fa.aag")
    first, dup = {}, {}
    for o, x, y in aig.ands:
        key = tuple(sorted((x, y)))
        if key in first:
            dup[o >> 1] = first[key]
        first.setdefault(key, o >> 1)
    said = re.search(r"(\d+) ANDs -> (\d+) ANDs", out("aig")).groups()
    if (len(aig.ands), len(aig.ands) - len(dup)) != tuple(map(int, said)):
        sys.exit("ch17-aig: the duplicates are not the ones run.out counts")
    d = HW(1000, 490, "The full adder with one kind of gate",
           "Every node is a two-input AND. A dotted edge with a ring is "
           "inverted. As Yosys writes it: 9 ANDs, two of them twice.",
           "A graph of nine AND nodes from the inputs a, b and cin on "
           "the left to the outputs sum and cout on the right; dotted "
           "edges are inverted; two nodes are outlined in amber and "
           "labeled as copies of two others")
    pos = {1: (70, 150), 2: (70, 250), 3: (420, 425),
           4: (250, 120), 5: (250, 215), 6: (420, 168),
           7: (590, 150), 8: (590, 245), 9: (760, 198),
           10: (250, 330), 11: (590, 400), 12: (760, 340)}
    assert set(pos) == {x >> 1 for x in aig.inputs} | \
        {o >> 1 for o, _, _ in aig.ands}

    def edge(src_lit, x2, y2, shrink=22):
        x1, y1 = pos[src_lit >> 1]
        inv = src_lit & 1
        length = math.hypot(x2 - x1, y2 - y1)
        ex = x2 - (x2 - x1) * shrink / length
        ey = y2 - (y2 - y1) * shrink / length
        d.line(x1, y1, ex, ey, BLUE if not inv else DIM, 1.8,
               "2 4" if inv else None)
        if inv:
            d.raw(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" '
                  f'fill="white" stroke="{DEEP}" stroke-width="1.6"/>')

    for o, x, y in aig.ands:
        for src in (x, y):
            edge(src, *pos[o >> 1])
    outs = [(aig.outputs[0], 900, 198), (aig.outputs[1], 900, 340)]
    for k, (lit, x, y) in enumerate(outs):
        edge(lit, x - 40, y, shrink=0)
        d.text(x - 30, y + 5, aig.names[f"o{k}"], 15, INK, "700", "start",
               MONO)
    for k, lit in enumerate(aig.inputs):
        x, y = pos[lit >> 1]
        d.rect(x - 34, y - 17, 68, 34, "white", DEEP, 2, 4)
        d.text(x, y + 5, f"{aig.names[f'i{k}']}  {lit}", 13, INK, "600",
               "middle", MONO)
    for o, x, y in aig.ands:
        v = o >> 1
        cx, cy = pos[v]
        stroke, sw = (AMBER, 3) if v in dup else (DEEP, 2)
        d.raw(f'<circle cx="{cx}" cy="{cy}" r="21" fill="{TRACE}" '
              f'stroke="{stroke}" stroke-width="{sw}"/>')
        d.text(cx, cy + 5, str(o), 13, INK, "700", "middle", MONO)
        if v in dup:
            d.text(cx, cy + 40, f"same inputs as {2 * dup[v]}", 12, AMBER,
                   "700", "middle")
    d.text(40, 478, "The number in a node is its literal in the file: "
           "twice its variable index. An odd literal is the inverted "
           "signal.", 13, DIM)
    d.save("ch17-aig.svg")


# ---- F9: unrolling ----------------------------------------------------
def fig_unroll():
    d = HW(1000, 430, "A clock, removed by copying",
           "The combinational logic is copied once per cycle; a "
           "register becomes the wire between two copies.",
           "Three copies of a block of logic side by side, labeled "
           "frame 0, frame 1 and frame k. Each takes its own inputs "
           "from above; the next-state outputs of one feed the state "
           "inputs of the next; the first takes the initial state; the "
           "bad output of the last is the question")
    xs = [150, 430, 760]
    names = ["0", "1", "k"]
    boxes = []
    for x, name in zip(xs, names):
        b = d.unit(x, 180, 190, 110, f"logic, frame {name}",
                   "every AND, copied", fill=TRACE)
        boxes.append(b)
        d.wire([(b.cx, 120), (b.cx, b.t)], "data")
        d.text(b.cx, 112, f"inputs{name}", 14, INK, "600", "middle", MONO)
        d.wire([(b.cx - 55, b.b), (b.cx - 55, b.b + 44)], "control")
        d.text(b.cx - 55, b.b + 62, "constraint = 1", 12, AMBER, "600",
               "middle", MONO)
    d.rect(30, 205, 76, 60, "white", DEEP, 2, 4)
    d.text(68, 231, "initial", 13, INK, "600", "middle")
    d.text(68, 249, "state", 13, INK, "600", "middle")
    d.wire([(106, 235), (boxes[0].l, 235)], "data")
    d.wire([(boxes[0].r, 235), (boxes[1].l, 235)], "data", label="state1",
           at=(385, 226))
    d.wire([(boxes[1].r, 235), (675, 235)], "data", label="state2",
           at=(650, 226))
    d.text(700, 240, "...", 20, DIM, "700", "middle")
    d.wire([(725, 235), (boxes[2].l, 235)], "data")
    d.wire([(boxes[2].cx + 60, boxes[2].b), (boxes[2].cx + 60, 345)],
           "data")
    d.rect(boxes[2].cx + 5, 345, 110, 40, AMBER_T, AMBER, 2.4, 6)
    d.text(boxes[2].cx + 60, 370, "bad = 1 ?", 14, INK, "700", "middle",
           MONO)
    d.text(30, 400, "Bound k: k transitions, k + 1 frames. State t+1 is "
           "frame t's next-state wires, so a register adds no clause.",
           13, DIM)
    d.save("ch17-unroll.svg")


# ---- F10: the FIFO, bound by bound ------------------------------------
def fig_bound():
    part = out("fifo-unroll").split("2. the FIFO")[1].split("each further")[0]
    rows = [x.split() for x in part.splitlines() if x.split()[:1]
            and x.split()[0].isdigit()]
    assert rows[-1][3] == "SAT" and all(r[3] == "UNSAT" for r in rows[:-1])
    d = HW(1000, 430, "Sixteen questions with the answer no, then a yes",
           "The first chapter's FIFO, unrolled: conflicts of cdcl.py at "
           "each bound, and the size of the formula it was given.",
           "Bar chart over bounds 0 to 16. The bars grow from 1 "
           "conflict to 185 at bound 15, all unsatisfiable, and the "
           "last bar, bound 16, is satisfiable with 195 conflicts; the "
           "formula grows by 105 variables per bound to 1,795")
    c = Chart(d, 80, 120, 860, 230, (-0.7, 16.7), (0, 200), log=False)
    c.yticks([0, 50, 100, 150, 200], "conflicts")
    for r in rows:
        k, nvars, conflicts, sat = int(r[0]), int(r[1]), int(r[5]), \
            r[3] == "SAT"
        x = c.px(k)
        d.rect(x - 16, c.py(conflicts), 32, c.py(0) - c.py(conflicts),
               AMBER_T if sat else TRACE, AMBER if sat else DIM,
               2.2 if sat else 1)
        d.text(x, c.py(conflicts) - 6, str(conflicts), 12, INK, "600",
               "middle", MONO)
        d.text(x, c.y + c.h + 18, str(k), 12, INK, "400", "middle", MONO)
        d.text(x, c.y + c.h + 38, f"{nvars:,}", 10.5, DIM, "400", "middle",
               MONO)
    d.text(c.x - 8, c.y + c.h + 18, "bound", 12, DIM, "400", "end")
    d.text(c.x - 8, c.y + c.h + 38, "variables", 12, DIM, "400", "end")
    d.text(80, 415, "blue: unsatisfiable, no trace of that length ends "
           "in a violation. Amber: satisfiable, and the assignment is "
           "the trace.", 13, DIM)
    d.save("ch17-bound.svg")


FIGS = [fig_map, fig_tseitin, fig_search, fig_implication, fig_learning,
        fig_hard, fig_bdd, fig_aig, fig_unroll, fig_bound]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
