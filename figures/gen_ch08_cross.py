#!/usr/bin/env python3
"""Draw figures/ch08-cross.svg: the two crosses of the cross example
(examples/ch08-functional-coverage/cross) as grids of bins, with the cells
its fixed twelve-sample stimulus hits (a in 0..3, b in 0..2). Bin and hit
counts match the example's run.out. Palette and fonts follow the book theme."""
import html
import pathlib

BLUE, DEEP, DIM, TRACE = "#1B4F72", "#123A56", "#7FA3C0", "#DCE9F3"
AMBER, GREEN, INK, GROUND, RULE = "#B7791F", "#2E7D32", "#1C1C1C", "#F4F6F8", "#CBD2D9"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""

C = 24                       # cell size
W, H = 1100, 660
s = []


def text(x, y, t, size=16, fill=INK, weight="400", anchor="start", font=SANS):
    s.append(f'<text x="{x}" y="{y}" {font} font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" fill="{fill}">{html.escape(t)}</text>')


def grid(x0, y0, rows, title, sub, hits_label):
    text(x0, y0 - 76, title, 19, BLUE, "700", "start", MONO)
    text(x0, y0 - 52, sub, 15, DIM)
    # column header: b's ten bins
    for j in range(10):
        text(x0 + 40 + j * C + C / 2, y0 - 8, str(j), 13, DIM, "400", "middle", MONO)
    text(x0 + 40 + 5 * C, y0 - 26, "cb: b in 0..9", 14, INK, "700", "middle")
    for i, a in enumerate(rows):
        y = y0 + i * C
        text(x0 + 32, y + C - 7, str(a), 13, DIM, "400", "end", MONO)
        for j in range(10):
            hit = a <= 3 and j <= 2
            fill = GREEN if hit else ("white" if a <= 3 else GROUND)
            s.append(f'<rect x="{x0 + 40 + j * C}" y="{y}" width="{C}" height="{C}" fill="{fill}" '
                     f'stroke="{RULE}" stroke-width="1"/>')
    s.append(f'<rect x="{x0 + 40}" y="{y0}" width="{10 * C}" height="{len(rows) * C}" fill="none" '
             f'stroke="{BLUE}" stroke-width="2"/>')
    yb = y0 + len(rows) * C
    text(x0 + 40 + 5 * C, yb + 30, hits_label, 17, BLUE, "700", "middle")


s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="Two cross-coverage grids hit by the same twelve samples: 12 of 160 bins and 12 of 40 bins">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')
text(30, 40, "Same twelve samples, two denominators", 21, BLUE, "700")
text(30, 64, "A cross has a bin for every tuple of its coverpoints' bins. The stimulus drives a in 0..3 and b in 0..2.",
     16, INK)

GY = 180
grid(60, GY, list(range(16)), "cg_full.ab", "ca: automatic bins, a in 0..15", "12 of 160 bins hit")
text(60 + 4, GY + 8 * C, "ca", 14, INK, "700", "end")
grid(520, GY, list(range(4)), "cg_small.ab", "ca: bins lo[] = {[0:3]}", "12 of 40 bins hit")

# legend
LX, LY = 520, GY + 4 * C + 90
for k, (fill, label) in enumerate([(GREEN, "bin hit"),
                                   ("white", "bin never hit by this stimulus"),
                                   (GROUND, "bin for a value the test never drives")]):
    y = LY + k * 34
    s.append(f'<rect x="{LX}" y="{y}" width="{C}" height="{C}" fill="{fill}" stroke="{RULE}" stroke-width="1"/>')
    text(LX + C + 12, y + C - 6, label, 16, INK)
text(LX, LY + 3 * 34 + 40, "The 120 grey bins on the left are holes no test", 16, AMBER, "700")
text(LX, LY + 3 * 34 + 62, "was written to fill. Binning ca first removes", 16, AMBER, "700")
text(LX, LY + 3 * 34 + 84, "them from the denominator.", 16, AMBER, "700")

s.append('</svg>')
out = pathlib.Path(__file__).with_name("ch08-cross.svg")
out.write_text("\n".join(s))
print(f"wrote figures/{out.name}")
