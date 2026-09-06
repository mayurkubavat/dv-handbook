#!/usr/bin/env python3
"""Draw figures/ch01-lifecycle.svg: the silicon lifecycle with the span that
verification occupies. Palette and fonts follow the book theme."""
import pathlib, html
BLUE, DIM, AMBER, GREEN, INK, GROUND = "#1B4F72", "#7FA3C0", "#B7791F", "#2E7D32", "#1C1C1C", "#F4F6F8"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
W, H = 1400, 470
stages = ["Specification", "Architecture", "RTL design", "Functional\nverification",
          "Synthesis and\nphysical design", "Tapeout", "Post-silicon\nvalidation", "Production\ntest"]
n = len(stages); bw, bh, gap, x0, y0 = 150, 84, 22, 30, 150
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Silicon lifecycle with the verification span">',
     f'<rect width="{W}" height="{H}" fill="white"/>']
# verification span: starts at Specification (the plan), ends after post-silicon validation
sx, ex = x0, x0 + 7*(bw+gap) - gap
s.append(f'<rect x="{sx-10}" y="{y0-70}" width="{ex-sx+20}" height="{bh+140}" rx="14" fill="{GROUND}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="8 6"/>')
s.append(f'<text x="{sx+4}" y="{y0-44}" {SANS} font-size="20" font-weight="700" fill="{BLUE}">Verification span</text>')
s.append(f'<text x="{sx+4}" y="{y0-22}" {SANS} font-size="15" fill="{INK}">plan → testbench alongside RTL → sign-off → learn from escapes</text>')
for i, name in enumerate(stages):
    x = x0 + i*(bw+gap)
    hot = name.startswith("Functional")
    fill = BLUE if hot else "white"; stroke = BLUE; tcol = "white" if hot else INK
    s.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    lines = name.split("\n")
    for j, ln in enumerate(lines):
        ty = y0 + bh/2 + (j - (len(lines)-1)/2)*20 + 6
        s.append(f'<text x="{x+bw/2}" y="{ty}" {SANS} font-size="17" font-weight="{"700" if hot else "400"}" text-anchor="middle" fill="{tcol}">{html.escape(ln)}</text>')
    if i < n-1:
        ax = x + bw
        s.append(f'<path d="M{ax+3},{y0+bh/2} H{ax+gap-8}" stroke="{DIM}" stroke-width="2.5"/>')
        s.append(f'<path d="M{ax+gap-10},{y0+bh/2-6} L{ax+gap-2},{y0+bh/2} L{ax+gap-10},{y0+bh/2+6} Z" fill="{DIM}"/>')
# sign-off gate between verification and tapeout
gx = x0 + 5*(bw+gap) - gap/2
s.append(f'<line x1="{gx}" y1="{y0-8}" x2="{gx}" y2="{y0+bh+8}" stroke="{AMBER}" stroke-width="4"/>')
s.append(f'<text x="{gx}" y="{y0+bh+30}" {SANS} font-size="15" font-weight="700" text-anchor="middle" fill="{AMBER}">sign-off</text>')
# feedback arrow from post-silicon validation back to verification
vx = x0 + 3*(bw+gap) + bw/2; px = x0 + 6*(bw+gap) + bw/2; fy = y0 + bh + 62
s.append(f'<path d="M{px},{y0+bh} V{fy} H{vx} V{y0+bh+14}" stroke="{GREEN}" stroke-width="2.5" fill="none"/>')
s.append(f'<path d="M{vx-6},{y0+bh+18} L{vx},{y0+bh+6} L{vx+6},{y0+bh+18} Z" fill="{GREEN}"/>')
s.append(f'<text x="{(vx+px)/2}" y="{fy+22}" {SANS} font-size="15" fill="{GREEN}" text-anchor="middle">escapes come back as questions: why did the testbench not find this?</text>')
# below: what each side hands over
s.append(f'<text x="{x0}" y="{H-40}" {SANS} font-size="15" fill="{INK}">Verification receives: specification, RTL drops, firmware.  Verification delivers: plan, testbench, regressions, coverage, bug reports, sign-off evidence.</text>')
s.append('</svg>')
pathlib.Path(__file__).with_name("ch01-lifecycle.svg").write_text("\n".join(s))
print("wrote figures/ch01-lifecycle.svg")
