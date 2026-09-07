#!/usr/bin/env python3
"""Draw figures/ch02-traceability.svg: the chain from a specification
requirement to a regression result, with the suspect-link feedback."""
import pathlib, html
BLUE, DIM, AMBER, GREEN, INK = "#1B4F72", "#7FA3C0", "#B7791F", "#2E7D32", "#1C1C1C"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""
W, H = 1400, 400
boxes = [("Specification", "requirement", "\"full shall be 1 when all\nDEPTH entries are occupied\""),
         ("Feature", "extracted", "full flag"),
         ("Plan item", "FIFO-005", "stimulus / checking /\ncoverage / closure"),
         ("Tests and coverage", "named in the item", "sv-random, cocotb\ncoverage: prose intent"),
         ("Regression result", "joined by name", "tests fail")]
n=len(boxes); bw, bh, gap, x0, y0 = 232, 118, 56, 30, 110
s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Traceability chain from requirement to regression result">',
   f'<rect width="{W}" height="{H}" fill="white"/>']
for i,(title, sub, body) in enumerate(boxes):
    x = x0 + i*(bw+gap)
    hot = i == 2
    s.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="8" fill="{BLUE if hot else "white"}" stroke="{BLUE}" stroke-width="2"/>')
    tc = "white" if hot else INK
    s.append(f'<text x="{x+bw/2}" y="{y0+28}" {SANS} font-size="18" font-weight="700" text-anchor="middle" fill="{tc}">{html.escape(title)}</text>')
    s.append(f'<text x="{x+bw/2}" y="{y0+48}" {SANS} font-size="13" text-anchor="middle" fill="{"#DCE9F3" if hot else DIM}">{html.escape(sub)}</text>')
    for j,ln in enumerate(body.split("\n")):
        s.append(f'<text x="{x+bw/2}" y="{y0+76+j*18}" {MONO} font-size="13" text-anchor="middle" fill="{tc}">{html.escape(ln)}</text>')
    if i < n-1:
        ax = x+bw
        s.append(f'<path d="M{ax+4},{y0+bh/2} H{ax+gap-10}" stroke="{DIM}" stroke-width="2.5"/>')
        s.append(f'<path d="M{ax+gap-12},{y0+bh/2-6} L{ax+gap-4},{y0+bh/2} L{ax+gap-12},{y0+bh/2+6} Z" fill="{DIM}"/>')
# change marker on the requirement, suspect band over everything downstream
s.append(f'<text x="{x0+bw/2}" y="{y0-24}" {SANS} font-size="15" font-weight="700" text-anchor="middle" fill="{AMBER}">specification changes here</text>')
s.append(f'<path d="M{x0+bw/2},{y0-14} V{y0-4}" stroke="{AMBER}" stroke-width="3"/>')
sx = x0 + (bw+gap); ex = x0 + n*(bw+gap) - gap
s.append(f'<rect x="{sx-8}" y="{y0+bh+26}" width="{ex-sx+16}" height="34" rx="6" fill="none" stroke="{AMBER}" stroke-width="2" stroke-dasharray="7 5"/>')
s.append(f'<text x="{(sx+ex)/2}" y="{y0+bh+49}" {SANS} font-size="15" text-anchor="middle" fill="{AMBER}">every downstream link is suspect until re-examined; closure requires none left</text>')
# result feeds back to the item
px = x0 + 4*(bw+gap) + bw/2; ix = x0 + 2*(bw+gap) + bw/2; fy = y0 + bh + 100
s.append(f'<path d="M{px},{y0+bh+62} V{fy} H{ix} V{y0+bh+62}" stroke="{GREEN}" stroke-width="2.5" fill="none"/>')
s.append(f'<path d="M{ix-6},{y0+bh+70} L{ix},{y0+bh+58} L{ix+6},{y0+bh+70} Z" fill="{GREEN}"/>')
s.append(f'<text x="{(ix+px)/2}" y="{fy+22}" {SANS} font-size="15" fill="{GREEN}" text-anchor="middle">results are reported against the item, not the test</text>')
s.append('</svg>')
pathlib.Path(__file__).with_name("ch02-traceability.svg").write_text("\n".join(s)); print("wrote figures/ch02-traceability.svg")
