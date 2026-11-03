"""hw.py -- hardware drawing on top of blocks.py, for the microarchitecture
figures of Chapter 11 and any later chapter that draws RTL.

blocks.py draws the book's flow diagrams (models, tools, stores, gates).
A microarchitecture diagram needs a different vocabulary, and draws it
the way logic designers have drawn it for decades:

    reg(...)      register: a box with a clock wedge on its lower edge
    mux(...)      multiplexer: a trapezoid, wide side to the inputs
    fifo(...)     FIFO: a box divided into its entries
    op(...)       an operator in a circle: +1, -1, ==0, <
    unit(...)     a block of logic (an FSM, an arbiter, a decoder)
    wire(...)     solid blue = data; dashed amber = control
    bus(...)      a wire with a slash and its width, for a multi-bit bus

and three helpers that are whole drawings in themselves:

    fsm_state / fsm_arc    state bubbles and labelled transitions
    lifeline / message     a sequence diagram
    wave(...)              a WaveJSON waveform (the subset vcd2wave.py
                           writes: p . 0 1 = and data)

Every figure is a HW object; its title and subtitle sit at the top left
as in every other figure of the book.
"""
import html
import math

from blocks import (AMBER, BLUE, DEEP, DIM, GREEN, GROUND, INK, MONO, RULE,
                    SANS, TRACE, VIOLET, Box, Diagram)

AMBER_T, GREEN_T, VIOLET_T = "#FBF1DC", "#E6F2E7", "#EEE8F6"
__all__ = ["HW", "Box", "AMBER", "BLUE", "DEEP", "DIM", "GREEN", "GROUND",
           "INK", "MONO", "RULE", "SANS", "TRACE", "VIOLET", "AMBER_T",
           "GREEN_T", "VIOLET_T"]


def esc(t):
    return html.escape(str(t))


class HW(Diagram):
    def __init__(self, w, h, title, sub=None, alt=None):
        super().__init__(w, h, alt or title)
        self._defs = self._defs.replace("</defs>", (
            '<marker id="ahd" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 Z" fill="{BLUE}"/></marker>'
            '<marker id="ahc" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 Z" fill="{AMBER}"/></marker>'
            '<marker id="ahg" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 Z" fill="{INK}"/></marker>'
            '<pattern id="hatch" width="6" height="6" '
            'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<line x1="0" y1="0" x2="0" y2="6" stroke="{RULE}" '
            'stroke-width="2"/></pattern></defs>'))
        self.label(30, 40, title, 21, BLUE, "700")
        if sub:
            self.label(30, 64, sub, 16, INK)

    # ---- primitives ---------------------------------------------------
    def raw(self, s):
        self.parts.append(s)

    def text(self, x, y, t, size=14, fill=INK, weight="400", anchor="start",
             font=SANS, italic=False):
        st = ' font-style="italic"' if italic else ""
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" {font} font-size="{size}" '
                 f'font-weight="{weight}" text-anchor="{anchor}" '
                 f'fill="{fill}"{st}>{esc(t)}</text>')

    def rect(self, x, y, w, h, fill="white", stroke=BLUE, sw=2, rx=0,
             dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                 f'height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=RULE, sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                 f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    # ---- hardware shapes ----------------------------------------------
    def reg(self, x, y, name, w=96, h=40, sub=None, fill="white",
            stroke=DEEP):
        """A register: name centred, optional width below, clock wedge."""
        self.rect(x, y, w, h, fill, stroke, 2, 3)
        self._lines(x + w / 2, y + h / 2 - (7 if sub else 0), name, 15, INK,
                    "600", font=MONO)
        if sub:
            self._lines(x + w / 2, y + h / 2 + 10, sub, 12, DIM, font=MONO)
        cx = x + 14
        self.raw(f'<path d="M{cx - 6},{y + h} L{cx},{y + h - 8} '
                 f'L{cx + 6},{y + h}" fill="none" stroke="{stroke}" '
                 'stroke-width="1.5"/>')
        return Box(x, y, w, h)

    def mux(self, x, y, h=70, w=28, sel=None, n=2):
        """A multiplexer, inputs on the left; returns its box. in_y(i)
        gives the y of input i."""
        k = h * 0.22
        self.raw(f'<path d="M{x},{y} L{x + w},{y + k} L{x + w},{y + h - k} '
                 f'L{x},{y + h} Z" fill="{TRACE}" stroke="{DEEP}" '
                 'stroke-width="2"/>')
        b = Box(x, y, w, h)
        b.in_y = lambda i: y + h * (i + 1) / (n + 1)
        if sel:
            self.text(x + w / 2, y + h + 16, sel, 12, AMBER, "600", "middle",
                      MONO)
        return b

    def fifo(self, x, y, depth, w=150, h=48, name=None, entry=None,
             fill_n=0):
        """A FIFO drawn as `depth` entries left to right; fill_n of them
        shaded to show occupancy."""
        cw = w / depth
        for i in range(depth):
            f = TRACE if i < fill_n else "white"
            self.rect(x + i * cw, y, cw, h, f, DEEP, 1.5)
            if entry:
                self._lines(x + (i + 0.5) * cw, y + h / 2, entry, 12, INK,
                            font=MONO)
        self.rect(x, y, w, h, "none", DEEP, 2.5)
        if name:
            self.text(x + w / 2, y - 10, name, 15, INK, "700", "middle")
        return Box(x, y, w, h)

    def op(self, cx, cy, sym, r=17, fill="white"):
        self.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                 f'stroke="{DEEP}" stroke-width="2"/>')
        self._lines(cx, cy, sym, 13, INK, "700", font=MONO)
        return Box(cx - r, cy - r, 2 * r, 2 * r)

    def unit(self, x, y, w, h, name, sub=None, fill=GROUND, stroke=BLUE,
             top=False):
        """A block of logic. top=True puts the name at the top so the
        block can hold other shapes."""
        self.rect(x, y, w, h, fill, stroke, 2, 8)
        if top:
            self.text(x + 12, y + 22, name, 16, stroke if stroke != BLUE
                      else BLUE, "700")
            if sub:
                self.text(x + 12, y + 40, sub, 13, DIM, font=MONO)
        else:
            self._lines(x + w / 2, y + h / 2 - (8 if sub else 0), name, 16,
                        INK, "700")
            if sub:
                self._lines(x + w / 2, y + h / 2 + 12, sub, 12, DIM,
                            font=MONO)
        return Box(x, y, w, h)

    # ---- wires --------------------------------------------------------
    def wire(self, pts, kind="data", label=None, at=None, arrow=True,
             anchor="middle", lsize=13, both=False):
        """A routed wire through the points. kind: data (solid blue),
        control (dashed amber), plain (thin grey), check (violet)."""
        col, dash, mk, sw = {
            "data": (BLUE, "", "ahd", 2.2),
            "control": (AMBER, ' stroke-dasharray="6 4"', "ahc", 1.8),
            "plain": (INK, "", "ahg", 1.4),
            "check": (VIOLET, ' stroke-dasharray="6 4"', "ahj", 1.8),
        }[kind]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        m = f' marker-end="url(#{mk})"' if arrow else ""
        if both:
            m += f' marker-start="url(#{mk})"'
        self.raw(f'<path d="{d}" fill="none" stroke="{col}" '
                 f'stroke-width="{sw}"{dash}{m}/>')
        if label:
            if at is None:
                (x1, y1), (x2, y2) = pts[0], pts[1]
                at = ((x1 + x2) / 2, (y1 + y2) / 2 - 7)
            self.text(at[0], at[1], label, lsize,
                      INK if kind in ("data", "plain") else col, "500",
                      anchor, MONO)

    def bus(self, pts, width, label=None, at=None, kind="data", **kw):
        """A multi-bit wire: a slash on its first segment with the width."""
        self.wire(pts, kind, label, at, **kw)
        (x1, y1), (x2, y2) = pts[0], pts[1]
        mx, my = x1 + (x2 - x1) * 0.3, y1 + (y2 - y1) * 0.3
        self.line(mx - 5, my + 7, mx + 5, my - 7, BLUE, 1.5)
        self.text(mx + 4, my + 18 if y1 == y2 else my, str(width), 11, DIM,
                  "400", "start", MONO)

    def legend_hw(self, x, y, items=("data", "control", "reg", "mux",
                                     "fifo")):
        cx = x
        for it in items:
            if it == "data":
                self.wire([(cx, y), (cx + 36, y)], "data")
                self.text(cx + 44, y + 5, "data", 14)
                cx += 100
            elif it == "control":
                self.wire([(cx, y), (cx + 36, y)], "control")
                self.text(cx + 44, y + 5, "control", 14)
                cx += 120
            elif it == "check":
                self.wire([(cx, y), (cx + 36, y)], "check")
                self.text(cx + 44, y + 5, "observed by the testbench", 14)
                cx += 240
            elif it == "reg":
                self.reg(cx, y - 13, "", w=34, h=26)
                self.text(cx + 42, y + 5, "register", 14)
                cx += 120
            elif it == "mux":
                self.mux(cx, y - 15, h=30, w=16)
                self.text(cx + 24, y + 5, "multiplexer", 14)
                cx += 125
            elif it == "fifo":
                self.fifo(cx, y - 12, 2, w=40, h=24)
                self.text(cx + 48, y + 5, "FIFO", 14)
                cx += 100

    # ---- state machines -----------------------------------------------
    @staticmethod
    def _mk(col):
        return {AMBER: "ahc", BLUE: "ahd", VIOLET: "ahj"}.get(col, "ahg")

    def fsm_state(self, cx, cy, name, sub=None, r=46, fill="white",
                  stroke=BLUE, initial=False):
        self.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="2.5"/>')
        self._lines(cx, cy - (8 if sub else 0), name, 15, INK, "700",
                    font=MONO)
        if sub:
            self._lines(cx, cy + 12, sub, 12, DIM, font=MONO)
        if initial:
            self.wire([(cx - r - 40, cy - r - 20),
                       (cx - r * 0.72, cy - r * 0.72)], "plain")
            self.text(cx - r - 44, cy - r - 26, "reset", 12, DIM, "400",
                      "end", MONO)
        b = Box(cx - r, cy - r, 2 * r, 2 * r)
        b.r_ = r
        return b

    def fsm_arc(self, a, b, label=None, bend=0, col=INK, lpos=0.5,
                ldx=0, ldy=0, sw=2, lcol=None, anchor="middle"):
        """Arc from state a to state b, curved by `bend` pixels to the
        left of the direction of travel; label at fraction lpos."""
        ax, ay, bx, by = a.cx, a.cy, b.cx, b.cy
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        mx, my = (ax + bx) / 2 + nx * bend, (ay + by) / 2 + ny * bend

        def edge(px, py, qx, qy, r):
            vx, vy = qx - px, qy - py
            vl = math.hypot(vx, vy)
            return px + vx / vl * r, py + vy / vl * r
        x1, y1 = edge(ax, ay, mx, my, a.r_)
        x2, y2 = edge(bx, by, mx, my, b.r_ + 3)
        self.raw(f'<path d="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} '
                 f'{x2:.1f},{y2:.1f}" fill="none" stroke="{col}" '
                 f'stroke-width="{sw}" marker-end="url(#{self._mk(col)})"/>')
        if label:
            t = lpos
            lx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
            ly = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
            for i, ln in enumerate(label.split("\n")):
                self.text(lx + ldx, ly + ldy + i * 15, ln, 12.5,
                          lcol or col, "500", anchor, MONO)

    def fsm_loop(self, s, side="t", label=None, col=INK, sw=2, lcol=None):
        """A self-loop on side t/b/l/r of state s."""
        r = s.r_
        ang = {"t": -90, "b": 90, "l": 180, "r": 0}[side]
        a1, a2 = math.radians(ang - 28), math.radians(ang + 28)
        x1, y1 = s.cx + r * math.cos(a1), s.cy + r * math.sin(a1)
        x2, y2 = s.cx + r * math.cos(a2), s.cy + r * math.sin(a2)
        ca = math.radians(ang)
        k = r * 1.05
        c1x, c1y = x1 + k * math.cos(ca - 0.5), y1 + k * math.sin(ca - 0.5)
        c2x, c2y = x2 + k * math.cos(ca + 0.5), y2 + k * math.sin(ca + 0.5)
        self.raw(f'<path d="M{x1:.1f},{y1:.1f} C{c1x:.1f},{c1y:.1f} '
                 f'{c2x:.1f},{c2y:.1f} {x2:.1f},{y2:.1f}" fill="none" '
                 f'stroke="{col}" stroke-width="{sw}" '
                 f'marker-end="url(#{self._mk(col)})"/>')
        if label:
            lx = s.cx + (r + k * 0.95) * math.cos(ca)
            ly = s.cy + (r + k * 0.95) * math.sin(ca)
            anchor = {"t": "middle", "b": "middle", "l": "end",
                      "r": "start"}[side]
            ly += {"t": -6, "b": 14, "l": 4, "r": 4}[side]
            for i, ln in enumerate(label.split("\n")):
                self.text(lx, ly + i * 15, ln, 12.5, lcol or col, "500",
                          anchor, MONO)

    # ---- sequence diagrams --------------------------------------------
    def lifeline(self, x, y0, y1, name, sub=None, w=150, fill="white"):
        self.rect(x - w / 2, y0, w, 44, fill, BLUE, 2, 6)
        self._lines(x, y0 + 22 - (7 if sub else 0), name, 15, INK, "700",
                    font=MONO)
        if sub:
            self._lines(x, y0 + 32, sub, 11, DIM)
        self.line(x, y0 + 44, x, y1, DIM, 1.5, "5 4")

    def message(self, x1, x2, y, label, kind="plain", above=True,
                size=12.5):
        self.wire([(x1, y), (x2 - (4 if x2 > x1 else -4), y)], kind)
        self.text((x1 + x2) / 2, y - 6 if above else y + 16, label, size,
                  INK if kind in ("plain", "data") else
                  {"control": AMBER, "check": VIOLET}[kind], "500",
                  "middle", MONO)

    def activation(self, x, y0, y1, fill=TRACE):
        self.rect(x - 6, y0, 12, y1 - y0, fill, BLUE, 1.2)

    # ---- waveforms ----------------------------------------------------
    def wave(self, x, y, wj, cw=34, rh=30, namew=96, first=None,
             marks=None, hl_rows=()):
        """Draw a WaveJSON dict at (x, y). Returns (x0, y0, cw, rh) so a
        figure can annotate cycle k at x0 + k*cw. first labels cycle
        numbers from that value. hl_rows tints rows by name."""
        rows = wj["signal"]
        n = len(rows[0]["wave"])
        x0 = x + namew
        h = rh * len(rows)
        # grid at every rising edge
        for k in range(n + 1):
            self.line(x0 + k * cw, y - 4, x0 + k * cw, y + h, "#E3E7EB", 1)
        if first is not None:
            for k in range(n):
                if (first + k) % 2 == 0:
                    self.text(x0 + k * cw + cw / 2, y - 10, first + k, 10,
                              DIM, "400", "middle", MONO)
        for i, r in enumerate(rows):
            ty = y + i * rh
            if r["name"] in hl_rows:
                self.rect(x - 6, ty + 2, namew + n * cw + 12, rh - 4,
                          AMBER_T, AMBER_T, 0, 4)
            self.text(x0 - 10, ty + rh / 2 + 5, r["name"], 13, INK, "600",
                      "end", MONO)
            self._wave_row(x0, ty + 5, cw, rh - 10, r)

    def _wave_row(self, x0, y, cw, h, r):
        w = r["wave"]
        if w[0] == "p":
            d = ""
            for k in range(len(w)):
                xa = x0 + k * cw
                d += (f"M{xa:.1f},{y + h} L{xa:.1f},{y} L{xa + cw / 2:.1f},"
                      f"{y} L{xa + cw / 2:.1f},{y + h} L{xa + cw:.1f},{y + h} ")
            self.raw(f'<path d="{d}" fill="none" stroke="{DIM}" '
                     'stroke-width="1.3"/>')
            return
        data = list(r.get("data", []))
        segs, cur = [], None
        for k, c in enumerate(w):
            if c == ".":
                cur[2] = k + 1
            else:
                cur = [c, k, k + 1]
                segs.append(cur)
        if all(s[0] in "01x" for s in segs):
            pts, lvl = [], None
            for c, a, b in segs:
                yy = y if c == "1" else y + h
                if c == "x":
                    self.rect(x0 + a * cw, y, (b - a) * cw, h, "url(#hatch)",
                              "none", 0)
                    continue
                if lvl is not None and lvl != yy:
                    pts.append((x0 + a * cw, yy))
                elif lvl is None:
                    pts.append((x0 + a * cw, yy))
                pts.append((x0 + b * cw, yy))
                lvl = yy
            d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
            # vertical edges: insert points at transitions
            path, prev = [], None
            for px, py in pts:
                if prev and prev[1] != py:
                    path.append((px, prev[1]))
                path.append((px, py))
                prev = (px, py)
            d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in path)
            self.raw(f'<path d="{d}" fill="none" stroke="{BLUE}" '
                     'stroke-width="2"/>')
            return
        di = 0
        for c, a, b in segs:
            xa, xb = x0 + a * cw, x0 + b * cw
            e = min(4, (xb - xa) / 3)
            self.raw(f'<path d="M{xa:.1f},{y + h / 2} L{xa + e:.1f},{y} '
                     f'L{xb - e:.1f},{y} L{xb:.1f},{y + h / 2} '
                     f'L{xb - e:.1f},{y + h} L{xa + e:.1f},{y + h} Z" '
                     f'fill="{"white" if c == "=" else GROUND}" '
                     f'stroke="{BLUE}" stroke-width="1.6"/>')
            if c == "=" and di < len(data):
                v = data[di]
                di += 1
                if (xb - xa) >= 9 * len(v) * 0.75:
                    self.text((xa + xb) / 2, y + h / 2 + 4.5, v, 12, INK,
                              "500", "middle", MONO)
