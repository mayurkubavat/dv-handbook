#!/usr/bin/env python3
"""Draw figures/ch05-handles.svg: the four steps of the class-handles
example (examples/ch05-testbench-language/class-handles) as handles and
objects. Values match the example's run.out. Palette and fonts follow the
book theme."""
import html
import pathlib

BLUE, DEEP, DIM, TRACE = "#1B4F72", "#123A56", "#7FA3C0", "#DCE9F3"
AMBER, GREEN, INK, GROUND, RULE = "#B7791F", "#2E7D32", "#1C1C1C", "#F4F6F8", "#CBD2D9"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""

PW, GAP, X0 = 280, 24, 20           # panel width, gap, left margin
W, H = X0 * 2 + 4 * PW + 3 * GAP, 470
s = []


def text(x, y, t, size=16, fill=INK, weight="400", anchor="start", font=SANS):
    s.append(f'<text x="{x}" y="{y}" {font} font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" fill="{fill}">{html.escape(t)}</text>')


def handle(x, y, name):
    s.append(f'<rect x="{x}" y="{y}" width="44" height="40" rx="4" fill="white" '
             f'stroke="{BLUE}" stroke-width="2"/>')
    text(x + 22, y + 27, name, 19, BLUE, "700", "middle", MONO)
    return x + 44, y + 20


def obj(x, y, ident, payload, fresh=False):
    fill = TRACE if fresh else GROUND
    s.append(f'<rect x="{x}" y="{y}" width="120" height="66" rx="10" fill="{fill}" '
             f'stroke="{DEEP}" stroke-width="2"/>')
    text(x + 12, y + 26, "id", 15, DIM, "400", "start", MONO)
    text(x + 12, y + 50, "payload", 15, DIM, "400", "start", MONO)
    text(x + 108, y + 26, ident, 15, INK, "700", "end", MONO)
    text(x + 108, y + 50, payload, 15, INK, "700", "end", MONO)
    return x, y + 33


def link(p, q, color=DIM):
    (x1, y1), (x2, y2) = p, q
    mx = (x1 + x2) / 2
    s.append(f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2 - 10},{y2}" stroke="{color}" '
             f'stroke-width="2.5" fill="none"/>')
    s.append(f'<path d="M{x2 - 11},{y2 - 6} L{x2},{y2} L{x2 - 11},{y2 + 6} Z" fill="{color}"/>')


def null(p):
    x, y = p
    s.append(f'<path d="M{x},{y} H{x + 20}" stroke="{AMBER}" stroke-width="2.5"/>')
    s.append(f'<path d="M{x + 20},{y - 10} V{y + 10}" stroke="{AMBER}" stroke-width="3"/>')
    text(x + 27, y + 6, "null", 15, AMBER, "700", "start", MONO)


def panel(i, step, code, made):
    x = X0 + i * (PW + GAP)
    s.append(f'<rect x="{x}" y="60" width="{PW}" height="{H - 80}" rx="12" fill="white" '
             f'stroke="{RULE}" stroke-width="1.5"/>')
    text(x + 16, 92, step, 17, BLUE, "700")
    for j, ln in enumerate(code):
        text(x + 16, 120 + j * 22, ln, 15, INK, "400", "start", MONO)
    text(x + 16, H - 36, f"packet::made = {made}", 15, DIM, "400", "start", MONO)
    return x


s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="Handles and objects in four steps of the class-handles example">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')
text(X0, 36, "A handle names an object; = copies the name, not the object", 21, BLUE, "700")

HY = [200, 260, 320]                # rows for handles a, b, c

# 1. before new
x = panel(0, "1  Before new", ["packet a, b, c;"], 0)
for row, name in zip(HY, "abc"):
    null(handle(x + 20, row, name))

# 2. new and alias
x = panel(1, "2  An alias", ["a = new(1, 8'h11);", "b = a;"], 1)
o = obj(x + 150, 215, "1", "11")
link(handle(x + 20, HY[0], "a"), o)
link(handle(x + 20, HY[1], "b"), o)

# 3. copy, then write through b
x = panel(2, "3  A copy", ["c = a.copy();", "b.payload = 8'h22;"], 2)
o1 = obj(x + 150, 190, "1", "22")
o2 = obj(x + 150, 300, "1", "11", fresh=True)
link(handle(x + 20, HY[0], "a"), o1)
link(handle(x + 20, HY[1], "b"), o1)
link(handle(x + 20, HY[2], "c"), o2)

# 4. drop a
x = panel(3, "4  Drop one name", ["a = null;"], 2)
o1 = obj(x + 150, 190, "1", "22")
o2 = obj(x + 150, 300, "1", "11", fresh=True)
null(handle(x + 20, HY[0], "a"))
link(handle(x + 20, HY[1], "b"), o1, GREEN)
link(handle(x + 20, HY[2], "c"), o2)

s.append('</svg>')
out = pathlib.Path(__file__).with_name("ch05-handles.svg")
out.write_text("\n".join(s))
print(f"wrote figures/{out.name}")
