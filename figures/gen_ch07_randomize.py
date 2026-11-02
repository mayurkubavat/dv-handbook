#!/usr/bin/env python3
"""Draw figures/ch07-randomize.svg: what one randomize() call does on the
book's simulator, from the constraints to the return value, with the two
ways it returns 0. The content is Chapter 7's account of the methods and
the solver pipeline. Palette and fonts follow the book theme."""
import html
import pathlib

BLUE, DEEP, DIM, TRACE = "#1B4F72", "#123A56", "#7FA3C0", "#DCE9F3"
AMBER, GREEN, VIOLET, INK, GROUND = "#B7791F", "#2E7D32", "#5B3E8E", "#1C1C1C", "#F4F6F8"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""

W, H = 1200, 520
s = []


def text(x, y, t, size=16, fill=INK, weight="400", anchor="start", font=SANS):
    s.append(f'<text x="{x}" y="{y}" {font} font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" fill="{fill}">{html.escape(t)}</text>')


def box(x, y, w, h, title, lines, fill="white", stroke=BLUE, tcol=BLUE, mono=False):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="2"/>')
    text(x + w / 2, y + 28, title, 18, tcol, "700", "middle")
    for i, ln in enumerate(lines):
        text(x + w / 2, y + 54 + i * 21, ln, 15, INK, "400", "middle", MONO if mono else SANS)
    return x, y, w, h


def arrow(x1, y1, x2, y2, color=DIM, label=None, dash=False, lx=None, ly=None):
    d = ' stroke-dasharray="8 6"' if dash else ""
    if y1 == y2:
        s.append(f'<path d="M{x1},{y1} H{x2 - 10}" stroke="{color}" stroke-width="2.5"{d}/>')
        s.append(f'<path d="M{x2 - 11},{y2 - 6} L{x2},{y2} L{x2 - 11},{y2 + 6} Z" fill="{color}"/>')
    else:
        s.append(f'<path d="M{x1},{y1} V{y2 - 10}" stroke="{color}" stroke-width="2.5"{d}/>')
        s.append(f'<path d="M{x2 - 6},{y2 - 11} L{x2},{y2} L{x2 + 6},{y2 - 11} Z" fill="{color}"/>')
    if label:
        text(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else y1 - 10,
             label, 14, color, "700", "middle")


s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="The path of one randomize() call through the simulator and an external solver">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')
text(30, 40, "One call to randomize()", 21, BLUE, "700")
text(30, 64, "The simulator states the problem; an external solver answers it; the call reports which happened.",
     16, INK)

Y, BH = 110, 130
a = box(30, Y, 250, BH, "The class", ["rand / randc members", "constraint blocks", "randomize() with { ... }"],
        fill=GROUND)
b = box(340, Y, 230, BH, "Simulator runtime", ["writes the constraints", "as SMT-LIB", "over a pipe"])
c = box(630, Y, 220, BH, "External solver", ["z3 --in", "by default;", "VERILATOR_SOLVER", "names another"],
        fill=TRACE)
d = box(910, Y, 260, BH, "A model", ["one satisfying", "assignment"], fill=GROUND)
arrow(280, Y + BH / 2, 340, Y + BH / 2)
arrow(570, Y + BH / 2, 630, Y + BH / 2)
arrow(850, Y + BH / 2, 910, Y + BH / 2)

# outcomes
OY, OH = 340, 120
ok = box(910, OY, 260, OH, "Returns 1", ["every rand and randc member", "assigned from the model"],
         stroke=GREEN, tcol=GREEN)
un = box(560, OY, 300, OH, "Returns 0: no solution", ["constraints contradict;", "no member is updated"],
         stroke=AMBER, tcol=AMBER)
ns = box(210, OY, 300, OH, "Returns 0: no solver", ["a warning, and", "no member is updated"],
         stroke=AMBER, tcol=AMBER)
arrow(1040, Y + BH, 1040, OY, GREEN, "satisfiable", lx=1080, ly=(Y + BH + OY) / 2 + 5)
arrow(740, Y + BH, 740, OY, AMBER, "unsatisfiable", lx=790, ly=(Y + BH + OY) / 2 + 5)
arrow(455, Y + BH, 455, OY, AMBER, "cannot start the solver", dash=True,
      lx=455, ly=(Y + BH + OY) / 2 + 5)
s.append(f'<rect x="{455 - 95}" y="{(Y + BH + OY) / 2 - 12}" width="190" height="22" fill="white"/>')
text(455, (Y + BH + OY) / 2 + 4, "cannot start the solver", 14, AMBER, "700", "middle")

text(30, H - 24, "A caller that ignores the return value runs on whatever the members held before the call.",
     16, BLUE, "700")

s.append('</svg>')
out = pathlib.Path(__file__).with_name("ch07-randomize.svg")
out.write_text("\n".join(s))
print(f"wrote figures/{out.name}")
