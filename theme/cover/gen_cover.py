#!/usr/bin/env python3
"""Generate front.svg and back.svg for the book cover (7x10 in @ 300 px/in => 2100x3000).
Edit the TEXT block below, then run:  python3 theme/cover/gen_cover.py
"""
import random, html, pathlib

W, H = 2100, 3000
OUT = pathlib.Path(__file__).parent

# ---- palette (mirrors design doc §4a) ----
BLUE, DEEP, TRACE, DIM, PAPER, AMBER = "#1B4F72", "#123A56", "#AED6F1", "#6FA3C7", "#F3F7FA", "#E0A83A"

# ---- text ----
TITLE = ("Design", "Verification")
SUBTITLE = "From First Principles to Agentic AI"
AUTHOR = "Mayur Kubavat"
EYEBROW = "OPEN EDITION  ·  v0.1"
FOOT = "Free, open textbook  ·  CC BY-NC-SA 4.0  ·  mayurkubavat.github.io/dv-textbook"
BLURB = ("Verification is where silicon meets reality. Every chip that ships has been proven right, or wrong, "
         "by an engineer who asked the question the designer did not. This book teaches that discipline from the "
         "ground up: how simulators actually schedule events, how to turn a specification into a plan you can "
         "measure, how to build SystemVerilog and UVM environments that scale from a block to an SoC, and when to "
         "reach for formal, emulation, or portable stimulus instead. It then looks forward, to Python and SystemC "
         "flows, to the open-source toolchain, and to the machine learning and agentic AI that are reshaping how "
         "verification gets done. Every listing is runnable, every chapter ends with exercises, and the whole book "
         "is free to read.")
INSIDE = [
    "Foundations: planning, coverage models and simulator internals",
    "SystemVerilog, assertions and UVM, from first principles to SoC-scale reuse",
    "Formal, emulation, low-power, CDC and portable stimulus",
    "cocotb, pyuvm, SystemC and the open-source toolchain",
    "Machine learning and agentic AI applied to real verification work",
]
BIO = ("Mayur Kubavat is a design verification engineer whose work spans high-speed interconnect "
       "verification, including PCIe 6.0 verification IP, and open-source verification tooling.")
VERSION = "Open edition  ·  Version 0.1  ·  2026"
REPO = "Source, examples and errata: github.com/mayurkubavat/dv-textbook"

SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
SERIF = "font-family=\"'Source Serif 4', Georgia, 'Times New Roman', serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, Consolas, monospace\""

def esc(s): return html.escape(s, quote=True)

def wrap(text, chars):
    out, line = [], ""
    for w in text.split():
        if len(line) + len(w) + 1 > chars:
            out.append(line); line = w
        else:
            line = (line + " " + w).strip()
    if line: out.append(line)
    return out

# ---------------- motif: handshake waveform + boxed SVA -> coverage grid, over a git->CI strip ----------------
def motif(x0=180, y0=1230):
    s = []
    lane_h, gap = 86, 58
    cyc = 80; ncyc = 9
    wx0 = x0 + 250; wx1 = wx0 + cyc * ncyc
    X = lambda i: wx0 + cyc * i
    lanes = ["clk", "rst_n", "valid", "ready", "data[31:0]", "xfer", "sva"]
    ys = [y0 + i * (lane_h + gap) for i in range(len(lanes))]
    top, bot = ys[0] - 30, ys[-1] + lane_h + 30
    st = f'stroke="{TRACE}" stroke-width="6" fill="none" stroke-linejoin="round" stroke-linecap="round"'
    thin = f'stroke="{DIM}" stroke-width="2" stroke-opacity="0.28"'
    for i in range(ncyc + 1):
        s.append(f'<line x1="{X(i)}" y1="{top}" x2="{X(i)}" y2="{bot}" {thin}/>')
    for name, y in zip(lanes, ys):
        s.append(f'<text x="{x0}" y="{y + lane_h/2 + 12}" {MONO} font-size="36" fill="{DIM}">{esc(name)}</text>')
    def sq(y, segs):
        d = []; first = True
        for a, b, lv in segs:
            yy = y if lv else y + lane_h
            if first: d.append(f"M{X(a)},{yy} H{X(b)}"); first = False
            else: d.append(f"V{yy} H{X(b)}")
        s.append(f'<path d="{" ".join(d)}" {st}/>')
    y = ys[0]; d = [f"M{X(0)},{y+lane_h}"]
    for i in range(ncyc):
        d.append(f"V{y} H{X(i)+cyc/2} V{y+lane_h} H{X(i+1)}")
    s.append(f'<path d="{" ".join(d)}" {st}/>')
    sq(ys[1], [(0, 1.5, 0), (1.5, 9, 1)])
    sq(ys[2], [(0, 2, 0), (2, 7, 1), (7, 9, 0)])
    sq(ys[3], [(0, 3, 1), (3, 5, 0), (5, 9, 1)])
    y = ys[4]; k = 16
    for val, a, b in [("--", 0, 2), ("1A2B3C4D", 2, 5), ("DEADBEEF", 5, 7), ("--", 7, 9)]:
        xa, xb = X(a), X(b)
        if val == "--":
            s.append(f'<path d="M{xa},{y+lane_h/2} H{xb}" {st} stroke-dasharray="12 12"/>')
        else:
            s.append(f'<path d="M{xa},{y+lane_h/2} L{xa+k},{y} H{xb-k} L{xb},{y+lane_h/2} L{xb-k},{y+lane_h} H{xa+k} Z" {st}/>')
            fs = 34
            s.append(f'<text x="{(xa+xb)/2}" y="{y+lane_h/2+12}" {MONO} font-size="{fs}" text-anchor="middle" fill="{PAPER}">{val}</text>')
    y = ys[5]; d = [f"M{X(0)},{y+lane_h}"]
    for i in range(ncyc):
        if i in (2, 5, 6): d.append(f"H{X(i)} V{y} H{X(i)+cyc*0.45} V{y+lane_h}")
    d.append(f"H{X(ncyc)}"); s.append(f'<path d="{" ".join(d)}" {st}/>')
    y = ys[6]; ya = y + lane_h*0.55
    s.append(f'<path d="M{X(3)},{y+lane_h} V{ya} H{X(5)} V{y+lane_h}" {st}/>')
    s.append(f'<text x="{(X(3)+X(5))/2}" y="{y+30}" {MONO} font-size="26" text-anchor="middle" fill="{TRACE}">$stable(data)</text>')
    s.append(f'<text x="{X(5)+22}" y="{ya+10}" {SANS} font-size="44" font-weight="700" fill="{TRACE}">&#10003;</text>')
    # cursor
    cx = X(4)
    s.append(f'<line x1="{cx}" y1="{top}" x2="{cx}" y2="{bot}" stroke="{AMBER}" stroke-width="3"/>')
    s.append(f'<rect x="{cx-52}" y="{top-46}" width="104" height="32" rx="4" fill="{AMBER}"/>')
    s.append(f'<text x="{cx}" y="{top-23}" {MONO} font-size="24" text-anchor="middle" fill="{DEEP}">40 ns</text>')
    # boxed SVA property inside the viewer, under the lanes
    bx, by, bw, bh = x0, bot + 26, wx1 - x0, 124
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="{DEEP}" stroke="{TRACE}" stroke-width="3"/>')
    s.append(f'<rect x="{bx+18}" y="{by-16}" width="108" height="32" rx="6" fill="{TRACE}"/>')
    s.append(f'<text x="{bx+72}" y="{by+7}" {SANS} font-size="24" font-weight="700" letter-spacing="3" text-anchor="middle" fill="{DEEP}">SVA</text>')
    s.append(f'<text x="{bx+28}" y="{by+58}" {MONO} font-size="28" fill="{PAPER}">assert property (@(posedge clk) disable iff (!rst_n)</text>')
    s.append(f'<text x="{bx+28}" y="{by+100}" {MONO} font-size="28" fill="{PAPER}">  valid &amp;&amp; !ready |=&gt; $stable(data));</text>')
    # coverage grid
    gx0, gy0, cell, cg, cols = x0 + 1290, top, 44, 12, 11
    grid_bot = by + bh
    rows = int((grid_bot - top + cg) // (cell + cg))
    rng = random.Random(1800)
    amber_cells = {(2, 8), (7, 3), (11, 9)}
    hit = 0
    for r in range(rows):
        for c_ in range(cols):
            x = gx0 + c_ * (cell + cg); y = gy0 + r * (cell + cg)
            if (r, c_) in amber_cells:
                s.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{AMBER}"/>')
            elif rng.random() < 0.62:
                hit += 1
                s.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{TRACE}" fill-opacity="0.9"/>')
            else:
                s.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="none" stroke="{DIM}" stroke-width="3"/>')
    gy_end = gy0 + rows * (cell + cg) - cg
    s.append(f'<text x="{gx0}" y="{gy_end+52}" {MONO} font-size="30" fill="{DIM}">{hit} / {rows*cols} bins</text>')
    # software-engineering strip: git graph -> CI pipeline
    gy = max(grid_bot, gy_end) + 150; r = 11
    dots = [(x0+20 + 80*i, gy) for i in range(5)]
    s.append(f'<path d="M{dots[0][0]},{gy} H{dots[-1][0]}" stroke="{TRACE}" stroke-width="4" fill="none"/>')
    s.append(f'<path d="M{dots[1][0]},{gy} C{dots[1][0]+36},{gy} {dots[1][0]+36},{gy-50} {dots[2][0]},{gy-50} H{dots[2][0]+24} C{dots[3][0]-36},{gy-50} {dots[3][0]-36},{gy} {dots[3][0]},{gy}" stroke="{DIM}" stroke-width="4" fill="none"/>')
    for (dx, dy) in dots:
        s.append(f'<circle cx="{dx}" cy="{dy}" r="{r}" fill="{BLUE}" stroke="{TRACE}" stroke-width="4"/>')
    s.append(f'<circle cx="{dots[2][0]+12}" cy="{gy-50}" r="{r}" fill="{BLUE}" stroke="{DIM}" stroke-width="4"/>')
    ax = dots[-1][0] + 36
    s.append(f'<path d="M{ax},{gy} H{ax+64}" stroke="{TRACE}" stroke-width="4"/>')
    s.append(f'<path d="M{ax+54},{gy-12} L{ax+76},{gy} L{ax+54},{gy+12} Z" fill="{TRACE}"/>')
    stages = [("Lint", "&#10003;"), ("Sim", "&#10003;"), ("Cov", "96%"), ("Formal", "&#10003;"), ("Release", "v0.1")]
    sx = ax + 104; sh, sg = 76, 24
    widths = [210, 210, 222, 226, 262]
    x = sx
    for i, (name, mark) in enumerate(stages):
        sw = widths[i]; last = i == len(stages) - 1
        s.append(f'<rect x="{x}" y="{gy-sh/2}" width="{sw}" height="{sh}" rx="10" fill="{PAPER if last else "none"}" stroke="{TRACE}" stroke-width="4"/>')
        s.append(f'<text x="{x+20}" y="{gy+11}" {SANS} font-size="34" font-weight="600" fill="{DEEP if last else PAPER}">{name}</text>')
        s.append(f'<text x="{x+sw-20}" y="{gy+11}" {MONO} font-size="28" text-anchor="end" fill="{DEEP if last else TRACE}">{mark}</text>')
        if not last:
            s.append(f'<path d="M{x+sw},{gy} H{x+sw+sg}" stroke="{DIM}" stroke-width="4"/>')
        x += sw + sg
    return "\n".join(s)

def front():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="7in" height="10in" role="img" aria-label="Front cover: Design Verification, From First Principles to Agentic AI, by {esc(AUTHOR)}">',
             f'<rect width="{W}" height="{H}" fill="{BLUE}"/>',
             f'<rect y="{H-420}" width="{W}" height="420" fill="{DEEP}"/>',
             f'<text x="180" y="270" {SANS} font-size="44" font-weight="600" letter-spacing="8" fill="{TRACE}">{esc(EYEBROW)}</text>',
             f'<text x="172" y="600" {SANS} font-size="270" font-weight="800" letter-spacing="-6" fill="{PAPER}">{TITLE[0]}</text>',
             f'<text x="172" y="860" {SANS} font-size="270" font-weight="800" letter-spacing="-6" fill="{PAPER}">{TITLE[1]}</text>',
             f'<text x="180" y="1010" {SERIF} font-size="96" font-style="italic" fill="{TRACE}">{esc(SUBTITLE)}</text>',
             f'<line x1="180" y1="1110" x2="{W-180}" y2="1110" stroke="{DIM}" stroke-width="3"/>',
             motif(),
             f'<text x="180" y="{H-250}" {SANS} font-size="88" font-weight="600" fill="{PAPER}">{esc(AUTHOR)}</text>',
             f'<text x="180" y="{H-150}" {MONO} font-size="36" fill="{TRACE}">{esc(FOOT)}</text>',
             '</svg>']
    return "\n".join(parts)

def back():
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="7in" height="10in" role="img" aria-label="Back cover">',
         f'<rect width="{W}" height="{H}" fill="{BLUE}"/>',
         f'<rect y="{H-420}" width="{W}" height="420" fill="{DEEP}"/>',
         f'<text x="180" y="270" {SANS} font-size="44" font-weight="600" letter-spacing="8" fill="{TRACE}">DESIGN VERIFICATION  ·  FROM FIRST PRINCIPLES TO AGENTIC AI</text>']
    y = 420
    for ln in wrap(BLURB, 60):
        p.append(f'<text x="180" y="{y}" {SERIF} font-size="56" fill="{PAPER}">{esc(ln)}</text>'); y += 78
    y += 60
    p.append(f'<text x="180" y="{y}" {SANS} font-size="48" font-weight="700" letter-spacing="6" fill="{TRACE}">INSIDE THIS BOOK</text>'); y += 90
    for item in INSIDE:
        p.append(f'<rect x="180" y="{y-34}" width="18" height="18" fill="{AMBER}"/>')
        for k, ln in enumerate(wrap(item, 62)):
            p.append(f'<text x="240" y="{y}" {SANS} font-size="52" fill="{PAPER}">{esc(ln)}</text>'); y += 70
        y += 14
    y += 40
    p.append(f'<line x1="180" y1="{y}" x2="{W-180}" y2="{y}" stroke="{DIM}" stroke-width="3"/>'); y += 100
    for ln in wrap(BIO, 78):
        p.append(f'<text x="180" y="{y}" {SERIF} font-size="44" fill="{TRACE}">{esc(ln)}</text>'); y += 62
    # footer band
    fy = H - 420
    p.append(f'<rect x="180" y="{fy+90}" width="520" height="110" rx="10" fill="none" stroke="{PAPER}" stroke-width="4"/>')
    p.append(f'<text x="440" y="{fy+162}" {SANS} font-size="46" font-weight="700" text-anchor="middle" fill="{PAPER}">CC BY-NC-SA 4.0</text>')
    p.append(f'<text x="180" y="{fy+270}" {SANS} font-size="40" fill="{TRACE}">{esc(VERSION)}</text>')
    p.append(f'<text x="180" y="{fy+340}" {MONO} font-size="34" fill="{DIM}">{esc(REPO)}</text>')
    qx, qy, qs = W-180-300, fy+60, 300
    p.append(f'<rect x="{qx}" y="{qy}" width="{qs}" height="{qs}" rx="8" fill="{PAPER}"/>')
    for (ox, oy) in [(0,0),(qs-84,0),(0,qs-84)]:
        p.append(f'<rect x="{qx+24+ox}" y="{qy+24+oy}" width="60" height="60" fill="none" stroke="{BLUE}" stroke-width="10"/>')
        p.append(f'<rect x="{qx+44+ox}" y="{qy+44+oy}" width="20" height="20" fill="{BLUE}"/>')
    p.append(f'<text x="{qx+qs/2}" y="{qy+qs/2+14}" {SANS} font-size="34" font-weight="600" text-anchor="middle" fill="{BLUE}">web edition</text>')
    p.append('</svg>')
    return "\n".join(p)

if __name__ == "__main__":
    (OUT / "front.svg").write_text(front())
    (OUT / "back.svg").write_text(back())
    print("wrote", OUT / "front.svg", OUT / "back.svg")
