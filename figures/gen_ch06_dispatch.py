#!/usr/bin/env python3
"""Draw figures/ch06-dispatch.svg: the chapter opener's one object and three
handles (examples/ch06-oop-testbench-design/three-handles), showing the
two classes a call could be bound to: the handle's declared class, and the
object's run-time class, which is the one a virtual call uses. Palette and
fonts follow the book theme."""
import html
import pathlib

BLUE, DEEP, DIM, TRACE = "#1B4F72", "#123A56", "#7FA3C0", "#DCE9F3"
AMBER, GREEN, INK, GROUND, RULE = "#B7791F", "#2E7D32", "#1C1C1C", "#F4F6F8", "#CBD2D9"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""

W, H = 1200, 560
ROWS = [150, 250, 350]
CX, CW, CH = 40, 300, 64          # class boxes
HX, HW = 520, 170                 # handle boxes
OX, OW = 880, 280                 # the object
s = []


def text(x, y, t, size=16, fill=INK, weight="400", anchor="start", font=SANS):
    s.append(f'<text x="{x}" y="{y}" {font} font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" fill="{fill}">{html.escape(t)}</text>')


def head(x, y, dx, dy, color):
    # a filled triangle at (x, y) pointing along (dx, dy)
    import math
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    a = (x - 12 * ux + 6 * px, y - 12 * uy + 6 * py)
    b = (x - 12 * ux - 6 * px, y - 12 * uy - 6 * py)
    s.append(f'<path d="M{a[0]:.1f},{a[1]:.1f} L{x:.1f},{y:.1f} L{b[0]:.1f},{b[1]:.1f} Z" fill="{color}"/>')


s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="One triangle object named by three handles of different declared classes">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')
text(CX, 40, "A virtual call is bound to the object, not to the handle", 21, BLUE, "700")
text(CX, 100, "classes", 16, DIM, "700")
text(HX, 100, "handles (declared class)", 16, DIM, "700")
text(OX, 100, "the one object", 16, DIM, "700")

classes = [("shape", "0"), ("polygon", "99"), ("triangle", "3")]
handles = [("shape", "a"), ("polygon", "b"), ("triangle", "c")]
for i, ((cname, val), (htype, hname)) in enumerate(zip(classes, handles)):
    y = ROWS[i]
    hot = cname == "triangle"
    s.append(f'<rect x="{CX}" y="{y}" width="{CW}" height="{CH}" rx="8" '
             f'fill="{TRACE if hot else "white"}" stroke="{BLUE}" stroke-width="2"/>')
    text(CX + 16, y + 28, cname, 18, BLUE, "700", "start", MONO)
    text(CX + 16, y + 52, f"sides() returns {val}", 15, INK, "400", "start", MONO)
    if i:
        # extends: an open arrow from the derived class up to its base
        s.append(f'<path d="M{CX + 40},{y} V{ROWS[i - 1] + CH + 12}" stroke="{DIM}" stroke-width="2"/>')
        s.append(f'<path d="M{CX + 33},{ROWS[i - 1] + CH + 13} L{CX + 40},{ROWS[i - 1] + CH + 1} '
                 f'L{CX + 47},{ROWS[i - 1] + CH + 13} Z" fill="white" stroke="{DIM}" stroke-width="2"/>')
        text(CX + 54, y - 12, "extends", 14, DIM)
    # handle box
    s.append(f'<rect x="{HX}" y="{y + 8}" width="{HW}" height="48" rx="6" fill="white" '
             f'stroke="{BLUE}" stroke-width="2"/>')
    text(HX + HW / 2, y + 39, f"{htype} {hname}", 17, BLUE, "700", "middle", MONO)
    # declared class: dashed amber back to its own class row
    s.append(f'<path d="M{HX},{y + 32} H{CX + CW + 12}" stroke="{AMBER}" stroke-width="2" '
             f'stroke-dasharray="7 5"/>')
    head(CX + CW + 1, y + 32, -1, 0, AMBER)

# the object
oy, oh = ROWS[0] + 40, ROWS[2] - ROWS[0] + 10
s.append(f'<rect x="{OX}" y="{oy}" width="{OW}" height="{oh}" rx="14" fill="{GROUND}" '
         f'stroke="{DEEP}" stroke-width="2"/>')
text(OX + OW / 2, oy + 44, "an object of class", 16, INK, "400", "middle")
text(OX + OW / 2, oy + 76, "triangle", 22, BLUE, "700", "middle", MONO)
text(OX + OW / 2, oy + 116, "made once, by c = new;", 15, DIM, "400", "middle", MONO)
text(OX + OW / 2, oy + 140, "b = c; a = c;", 15, DIM, "400", "middle", MONO)
for y in ROWS:
    x1, y1 = HX + HW, y + 32
    x2, y2 = OX, oy + oh / 2
    s.append(f'<path d="M{x1},{y1} C{x1 + 90},{y1} {x2 - 90},{y2} {x2 - 10},{y2}" stroke="{DIM}" '
             f'stroke-width="2.5" fill="none"/>')
head(OX, oy + oh / 2, 1, 0, DIM)

# the two readings
ry = 470
s.append(f'<path d="M{CX},{ry - 6} H{CX + 40}" stroke="{AMBER}" stroke-width="2" stroke-dasharray="7 5"/>')
text(CX + 52, ry, "bound to the handle's declared class:", 16, INK)
for k, t in enumerate(["a.sides() = 0", "b.sides() = 99", "c.sides() = 3"]):
    text(CX + 380 + k * 200, ry, t, 16, AMBER, "700", "start", MONO)
text(CX + 52, ry + 24, "what a non-virtual call does, and what a tool that ignores virtual prints", 14, DIM)
s.append(f'<rect x="{CX}" y="{ry + 38}" width="40" height="14" rx="3" fill="{TRACE}" stroke="{BLUE}" stroke-width="1.5"/>')
text(CX + 52, ry + 52, "bound to the object's run-time class:", 16, INK)
for k, t in enumerate(["a.sides() = 3", "b.sides() = 3", "c.sides() = 3"]):
    text(CX + 380 + k * 200, ry + 52, t, 16, GREEN, "700", "start", MONO)

s.append('</svg>')
out = pathlib.Path(__file__).with_name("ch06-dispatch.svg")
out.write_text("\n".join(s))
print(f"wrote figures/{out.name}")
