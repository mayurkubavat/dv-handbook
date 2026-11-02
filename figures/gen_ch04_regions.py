#!/usr/bin/env python3
"""Draw figures/ch04-regions.svg: one timestep as the order of its regions,
the two loops inside it, and what runs in each region. The content is the
region table of Chapter 4 (after Cummings and Salz), drawn rather than
listed. Palette and fonts follow the book theme."""
import html
import pathlib

BLUE, DEEP, DIM, TRACE = "#1B4F72", "#123A56", "#7FA3C0", "#DCE9F3"
AMBER, GREEN, VIOLET, INK, GROUND = "#B7791F", "#2E7D32", "#5B3E8E", "#1C1C1C", "#F4F6F8"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""

W, H = 1200, 1080
BX, BW, BH = 300, 230, 54          # region boxes: left edge, width, height
NX = BX + BW + 40                  # notes column
s = []


def text(x, y, t, size=17, fill=INK, weight="400", anchor="start", font=SANS):
    s.append(f'<text x="{x}" y="{y}" {font} font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" fill="{fill}">{html.escape(t)}</text>')


def arrow_head(x, y, direction, color):
    d = {"down": f"M{x-7},{y-11} L{x},{y} L{x+7},{y-11} Z",
         "up": f"M{x-7},{y+11} L{x},{y} L{x+7},{y+11} Z",
         "right": f"M{x-11},{y-7} L{x},{y} L{x-11},{y+7} Z"}[direction]
    s.append(f'<path d="{d}" fill="{color}"/>')


def down(x, y1, y2, color=DIM):
    s.append(f'<path d="M{x},{y1} V{y2 - 10}" stroke="{color}" stroke-width="2.5"/>')
    arrow_head(x, y2, "down", color)


def region(y, name, note, fill="white", tcol=INK, ncol=INK):
    s.append(f'<rect x="{BX}" y="{y}" width="{BW}" height="{BH}" rx="8" fill="{fill}" '
             f'stroke="{BLUE}" stroke-width="2"/>')
    text(BX + BW / 2, y + BH / 2 + 6, name, 19, tcol, "700", "middle")
    for i, ln in enumerate(note.split("\n")):
        text(NX, y + BH / 2 + 6 + (i - (len(note.split(chr(10))) - 1) / 2) * 21, ln, 16, ncol)
    return y, y + BH


def group(y1, y2, label, sub):
    s.append(f'<rect x="{BX - 30}" y="{y1}" width="{W - BX - 90}" height="{y2 - y1}" rx="14" '
             f'fill="{GROUND}" stroke="{DIM}" stroke-width="1.5" stroke-dasharray="7 5"/>')
    text(BX - 40, y1 + 30, label, 18, BLUE, "700", "end")
    text(BX - 40, y1 + 52, sub, 15, DIM, "400", "end")


s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="The regions of one SystemVerilog timestep, in order, with the loops between them">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')
text(30, 40, "One timestep", 22, BLUE, "700")
text(30, 64, "Order between regions is fixed. Order within a region is not.", 16, INK)

cx = BX + BW / 2
y = 100
pre = region(y, "Preponed", "sample the values concurrent assertions will use;\nonce per timestep")

# The design's set: Active, Inactive, NBA
g1 = pre[1] + 40
group(g1, g1 + 3 * BH + 2 * 30 + 40, "Active set", "the design")
act = region(g1 + 20, "Active", "blocking assignments; right side of <=;\ncontinuous assignments; $display",
             fill=BLUE, tcol="white")
ina = region(act[1] + 30, "Inactive", "anything scheduled by #0")
nba = region(ina[1] + 30, "NBA", "the update half of <=")
down(cx, pre[1], act[0])
down(cx, act[1], ina[0])
down(cx, ina[1], nba[0])
# loop: new work goes back to Active
lx = BX + BW + 14
s.append(f'<path d="M{BX + BW},{nba[0] + BH / 2} H{lx} V{act[0] + BH / 2} H{BX + BW + 12}" '
         f'stroke="{GREEN}" stroke-width="2.5" fill="none"/>')
s.append(f'<path d="M{BX + BW + 12},{act[0] + BH / 2 - 7} L{BX + BW + 1},{act[0] + BH / 2} '
         f'L{BX + BW + 12},{act[0] + BH / 2 + 7} Z" fill="{GREEN}"/>')

obs_y = nba[1] + 60
obs = region(obs_y, "Observed", "evaluate concurrent assertions")
down(cx, nba[1], obs[0])

# The testbench's set: Reactive, Re-Inactive, Re-NBA
g2 = obs[1] + 40
group(g2, g2 + 3 * BH + 2 * 30 + 40, "Reactive set", "the testbench's dual")
rea = region(g2 + 20, "Reactive", "code in a program block;\nassertion action blocks",
             fill=VIOLET, tcol="white")
rin = region(rea[1] + 30, "Re-Inactive", "the testbench's counterpart of Inactive")
rnb = region(rin[1] + 30, "Re-NBA", "the testbench's counterpart of NBA")
down(cx, obs[1], rea[0])
down(cx, rea[1], rin[0])
down(cx, rin[1], rnb[0])
s.append(f'<path d="M{BX + BW},{rnb[0] + BH / 2} H{lx} V{rea[0] + BH / 2} H{BX + BW + 12}" '
         f'stroke="{GREEN}" stroke-width="2.5" fill="none"/>')
s.append(f'<path d="M{BX + BW + 12},{rea[0] + BH / 2 - 7} L{BX + BW + 1},{rea[0] + BH / 2} '
         f'L{BX + BW + 12},{rea[0] + BH / 2 + 7} Z" fill="{GREEN}"/>')

# the testbench may wake the design again: back to Active
# Drawn outside both set boxes, on the right, from Re-NBA's row to Active's.
bx = W - 45
ya, yr = act[0] + BH / 2, rnb[0] + BH / 2
s.append(f'<path d="M{W - 110},{yr} H{bx} V{ya} H{W - 98}" '
         f'stroke="{AMBER}" stroke-width="2.5" fill="none" stroke-dasharray="9 6"/>')
s.append(f'<path d="M{W - 98},{ya - 7} L{W - 109},{ya} L{W - 98},{ya + 7} Z" fill="{AMBER}"/>')
text(bx - 14, (obs[0] + obs[1]) / 2 - 4, "the testbench may", 15, AMBER, "700", "end")
text(bx - 14, (obs[0] + obs[1]) / 2 + 16, "wake the design again", 15, AMBER, "700", "end")

post_y = rnb[1] + 60
post = region(post_y, "Postponed", "$strobe and $monitor; read-only:\nnothing may schedule new work here")
down(cx, rnb[1], post[0])
down(cx, post[1], post[1] + 50, BLUE)
text(cx, post[1] + 74, "time advances only when every region is empty", 16, BLUE, "700", "middle")

# legend for the loop arrows
ly = H - 22
s.append(f'<path d="M30,{ly - 5} H70" stroke="{GREEN}" stroke-width="2.5"/>')
text(78, ly, "new work in the same set: iterate within the timestep", 15, INK)
s.append(f'<path d="M520,{ly - 5} H560" stroke="{AMBER}" stroke-width="2.5" stroke-dasharray="9 6"/>')
text(568, ly, "testbench activity that wakes design processes", 15, INK)

s.append('</svg>')
out = pathlib.Path(__file__).with_name("ch04-regions.svg")
out.write_text("\n".join(s))
print(f"wrote figures/{out.name}")
