"""blocks.py -- the shared visual language for the book's block diagrams.

Four shapes and two arrow kinds, used identically in every figure:

    model(...)   rounded rectangle, silicon blue fill       a generative model
    tool(...)    rectangle, white fill, blue stroke          a tool that runs
    store(...)   cylinder, light ground                      a store of evidence
    gate(...)    diamond, amber                              a human decision
    arrow(...)   solid  = data flows;  dashed = a judgment flows

Every generator script does:

    from blocks import Diagram
    d = Diagram(width, height)
    m = d.model(x, y, "Model")            # returns a Box with .l .r .t .b .cx .cy
    t = d.tool(x, y, "Simulator", w=180)
    d.arrow(m, t, label="run seed 7")
    d.save("ch34-loop.svg")

Palette and fonts follow the design doc (section 4a).
"""
import html
import pathlib

BLUE, DEEP, DIM, TRACE = "#1B4F72", "#123A56", "#7FA3C0", "#DCE9F3"
AMBER, GREEN, VIOLET, INK, GROUND, RULE = "#B7791F", "#2E7D32", "#5B3E8E", "#1C1C1C", "#F4F6F8", "#CBD2D9"
SANS = "font-family=\"'Source Sans 3', 'Helvetica Neue', Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Menlo, monospace\""


class Box:
    def __init__(self, x, y, w, h):
        self.l, self.t, self.w, self.h = x, y, w, h
        self.r, self.b = x + w, y + h
        self.cx, self.cy = x + w / 2, y + h / 2

    def port(self, side):
        return {"l": (self.l, self.cy), "r": (self.r, self.cy),
                "t": (self.cx, self.t), "b": (self.cx, self.b)}[side]


class Diagram:
    def __init__(self, width, height, title=None):
        self.w, self.h = width, height
        self.parts = [f'<rect width="{width}" height="{height}" fill="white"/>']
        self.title = title
        self._defs = ('<defs>'
                      f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
                      f'<path d="M0,0 L10,5 L0,10 Z" fill="{DIM}"/></marker>'
                      f'<marker id="ahj" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
                      f'<path d="M0,0 L10,5 L0,10 Z" fill="{VIOLET}"/></marker>'
                      '</defs>')

    # ---- text helpers -------------------------------------------------
    def _lines(self, cx, cy, text, size, fill, weight="400", font=SANS, dy=None):
        lines = text.split("\n")
        dy = dy or size * 1.25
        y0 = cy - (len(lines) - 1) * dy / 2 + size * 0.35
        for i, ln in enumerate(lines):
            self.parts.append(f'<text x="{cx}" y="{y0 + i*dy:.1f}" {font} font-size="{size}" '
                              f'font-weight="{weight}" text-anchor="middle" fill="{fill}">{html.escape(ln)}</text>')

    def label(self, x, y, text, size=14, fill=INK, weight="400", anchor="start", font=SANS):
        for i, ln in enumerate(text.split("\n")):
            self.parts.append(f'<text x="{x}" y="{y + i*size*1.3:.1f}" {font} font-size="{size}" font-weight="{weight}" '
                              f'text-anchor="{anchor}" fill="{fill}">{html.escape(ln)}</text>')

    def caption(self, x, y, text, size=16, fill=DIM):
        self.label(x, y, text, size=size, fill=fill)

    # ---- the four shapes ------------------------------------------------
    def model(self, x, y, text, w=160, h=64, sub=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{BLUE}" stroke="{DEEP}" stroke-width="2"/>')
        self._lines(x + w/2, y + h/2 - (9 if sub else 0), text, 20, "white", "700")
        if sub:
            self._lines(x + w/2, y + h/2 + 17, sub, 14, TRACE)
        return Box(x, y, w, h)

    def tool(self, x, y, text, w=160, h=64, sub=None, fill="white"):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{BLUE}" stroke-width="2"/>')
        self._lines(x + w/2, y + h/2 - (9 if sub else 0), text, 19, INK, "600")
        if sub:
            self._lines(x + w/2, y + h/2 + 17, sub, 14, DIM, font=MONO)
        return Box(x, y, w, h)

    def store(self, x, y, text, w=150, h=70, sub=None):
        ry = 10
        self.parts.append(f'<path d="M{x},{y+ry} A{w/2},{ry} 0 0 1 {x+w},{y+ry} V{y+h-ry} A{w/2},{ry} 0 0 1 {x},{y+h-ry} Z" fill="{GROUND}" stroke="{BLUE}" stroke-width="2"/>')
        self.parts.append(f'<path d="M{x},{y+ry} A{w/2},{ry} 0 0 0 {x+w},{y+ry}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
        self._lines(x + w/2, y + h/2 + 4 - (8 if sub else 0), text, 19, INK, "600")
        if sub:
            self._lines(x + w/2, y + h/2 + 20, sub, 14, DIM)
        return Box(x, y, w, h)

    def gate(self, x, y, text, w=150, h=80):
        cx, cy = x + w/2, y + h/2
        self.parts.append(f'<path d="M{cx},{y} L{x+w},{cy} L{cx},{y+h} L{x},{cy} Z" fill="#FBF1DC" stroke="{AMBER}" stroke-width="2.5"/>')
        self._lines(cx, cy, text, 16, "#6B4A0E", "700")
        return Box(x, y, w, h)

    def region(self, x, y, w, h, title, stroke=DIM):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="6 5"/>')
        self.label(x + 12, y + 22, title, size=16, fill=stroke, weight="700")

    # ---- arrows -------------------------------------------------------------
    def arrow(self, a, b, label=None, kind="data", sides=None, bend=None, label_dy=-8):
        """Draw from box a to box b. sides=('r','l') chooses ports; bend adds a
        midpoint offset (dx, dy) for a curved route; kind='judgment' dashes it."""
        if sides is None:
            sides = ("r", "l") if b.l >= a.r else ("l", "r") if b.r <= a.l else ("b", "t") if b.t >= a.b else ("t", "b")
        (x1, y1), (x2, y2) = a.port(sides[0]), b.port(sides[1])
        dash = ' stroke-dasharray="7 5"' if kind == "judgment" else ""
        col = VIOLET if kind == "judgment" else DIM
        mk = "ahj" if kind == "judgment" else "ah"
        if bend:
            mx, my = (x1 + x2)/2 + bend[0], (y1 + y2)/2 + bend[1]
            self.parts.append(f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" fill="none" stroke="{col}" stroke-width="2.2"{dash} marker-end="url(#{mk})"/>')
            lx, ly = (x1 + 2*mx + x2)/4, (y1 + 2*my + y2)/4
        else:
            self.parts.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{col}" stroke-width="2.2"{dash} marker-end="url(#{mk})"/>')
            lx, ly = (x1 + x2)/2, (y1 + y2)/2
        if label:
            self._lines(lx, ly + label_dy, label, 15, col if kind == "judgment" else INK, font=SANS)

    def note(self, x, y, text, w=260, size=15):
        """A small explanatory note in a light box."""
        lines = text.split("\n"); h = 14 + len(lines) * size * 1.35
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h:.0f}" rx="6" fill="{GROUND}" stroke="{RULE}"/>')
        self.label(x + 10, y + 12 + size * 0.7, text, size=size, fill=INK)
        return Box(x, y, w, h)

    def failure_mark(self, x, y, n):
        """A numbered amber marker for a failure point."""
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{AMBER}"/>')
        self._lines(x, y, str(n), 15, "white", "700")

    def legend(self, x, y):
        self.parts.append(f'<rect x="{x}" y="{y}" width="44" height="22" rx="11" fill="{BLUE}"/>'); self.label(x + 52, y + 16, "model", 14)
        self.parts.append(f'<rect x="{x+120}" y="{y}" width="44" height="22" rx="4" fill="white" stroke="{BLUE}" stroke-width="1.5"/>'); self.label(x + 172, y + 16, "tool", 14)
        self.parts.append(f'<path d="M{x+230},{y+5} A22,5 0 0 1 {x+274},{y+5} V{y+17} A22,5 0 0 1 {x+230},{y+17} Z" fill="{GROUND}" stroke="{BLUE}" stroke-width="1.5"/>'); self.label(x + 282, y + 16, "evidence store", 14)
        self.parts.append(f'<path d="M{x+402},{y} L{x+424},{y+11} L{x+402},{y+22} L{x+380},{y+11} Z" fill="#FBF1DC" stroke="{AMBER}" stroke-width="1.5"/>'); self.label(x + 432, y + 16, "human gate", 14)
        self.parts.append(f'<path d="M{x+520},{y+11} H{x+560}" stroke="{DIM}" stroke-width="2" marker-end="url(#ah)"/>'); self.label(x + 568, y + 16, "data", 14)
        self.parts.append(f'<path d="M{x+610},{y+11} H{x+650}" stroke="{VIOLET}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ahj)"/>'); self.label(x + 658, y + 16, "judgment", 14)

    def save(self, name):
        body = "\n".join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
               f'role="img" aria-label="{html.escape(self.title or name)}">\n{self._defs}\n{body}\n</svg>\n')
        pathlib.Path(__file__).with_name(name).write_text(svg)
        print("wrote figures/" + name)
