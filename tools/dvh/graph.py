"""graph.py -- the instance connection graph of a hierarchical netlist, and a
block diagram drawn with the book's own diagram library (figures/blocks.py).
"""
from __future__ import annotations

import os
import sys

from .design import Module


def connections(mods: dict, top: str) -> dict:
    """Edges between instance ports (and top ports) that share a net."""
    mod = mods[top]
    endpoints = {}   # bit -> list of (owner, port, direction)
    for pname, p in mod.ports.items():
        for b in p["bits"]:
            if isinstance(b, int):
                endpoints.setdefault(b, []).append(
                    ("top", pname, p["direction"]))
    instances = {}
    for cname, cell in mod.cells.items():
        if cell.type not in mods:
            continue                       # only user-module instances
        # A parameterised instance is typed "$paramod\\sync2\\W=4"; the
        # module's own name is what the reader of a block diagram wants.
        pretty = (cell.type.split("\\")[1]
                  if cell.type.startswith("$paramod") else cell.type)
        instances[cname] = pretty
        child = mods[cell.type]
        for port, bits in cell.conns.items():
            d = child.ports[port]["direction"]
            for b in bits:
                if isinstance(b, int):
                    endpoints.setdefault(b, []).append((cname, port, d))
    # one edge per (driver, sink) pair per net name
    edges = {}
    for b, eps in endpoints.items():
        net = mod.net(b)
        # A net is driven by a top-level input or by an instance output.
        drivers = [e for e in eps
                   if (e[0] == "top") == (e[2] == "input")]
        sinks = [e for e in eps if e not in drivers]
        for dv in drivers:
            for sk in sinks:
                key = (dv[0], dv[1], sk[0], sk[1])
                edges.setdefault(key, set()).add(net)
    return {"instances": instances,
            "edges": [{"from": k[0], "from_port": k[1],
                       "to": k[2], "to_port": k[3], "nets": sorted(v)}
                      for k, v in sorted(edges.items())]}


# ---------------------------------------------------------------- layout ---
# Drawing constants, in SVG units. Changing these is the only way the block
# diagram's proportions change; nothing below hard-codes a position.
BOX_W, BOX_H = 210, 76           # an instance
STORE_W, STORE_H = 150, 72       # the top-level port cylinders
COL_GAP, ROW_GAP = 120, 44       # between columns, between stacked instances
MARGIN = 34
CLEAR = 62                       # vertical room reserved for bent arrows


def _merge_edges(conn: dict) -> dict:
    """All nets between the same pair of endpoints, as one edge each."""
    merged = {}
    for e in conn["edges"]:
        merged.setdefault((e["from"], e["to"]), set()).update(e["nets"])
    return merged


def _ranks(instances, merged) -> dict:
    """Column index per instance: the longest path from an instance with no
    instance driving it. Every edge then points rightward, which is what makes
    a single row of boxes safe to draw. Feedback edges (a cycle in the
    hierarchy's connectivity) simply stop lengthening the path."""
    preds = {i: set() for i in instances}
    for (src, dst) in merged:
        if src in preds and dst in preds and src != dst:
            preds[dst].add(src)
    rank = {i: 0 for i in instances}
    for _ in range(len(instances)):
        changed = False
        for i in instances:
            r = max((rank[p] + 1 for p in preds[i]), default=0)
            if r > rank[i]:
                rank[i], changed = r, True
        if not changed:
            break
    return rank


def _label(nets, limit=2) -> str:
    shown = sorted(nets)[:limit]
    return ", ".join(shown) + (" ..." if len(nets) > limit else "")


def draw(conn: dict, out_svg: str, title: str = "connections") -> None:
    """Block diagram: instances as tool boxes, top ports as stores, nets as
    arrows. Instances are placed in columns by dataflow rank, so boxes never
    overlap each other or the port cylinders however many there are, and an
    edge that skips a column is routed clear of the boxes it passes."""
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "..", "figures"))
    from blocks import Diagram, DIM                 # noqa: E402

    merged = _merge_edges(conn)
    inst = sorted(conn["instances"])
    rank = _ranks(inst, merged)
    columns = {}
    for name in inst:
        columns.setdefault(rank[name], []).append(name)
    ncols = max(columns) + 1 if columns else 0

    def col_x(c):
        return MARGIN + STORE_W + COL_GAP + c * (BOX_W + COL_GAP)

    out_x = col_x(ncols - 1) + BOX_W + COL_GAP if ncols else col_x(0)
    width = out_x + STORE_W + MARGIN
    tallest = max((len(v) for v in columns.values()), default=1)
    body_h = max(tallest * BOX_H + (tallest - 1) * ROW_GAP, STORE_H)

    ins = sorted({e["from_port"] for e in conn["edges"] if e["from"] == "top"})
    outs = sorted({e["to_port"] for e in conn["edges"] if e["to"] == "top"})
    # Port names go under their cylinder, not inside it, so the list can grow
    # without ever colliding with the cylinder's own label.
    caption_h = 15 * 1.3 * max(len(_stack(ins).split("\n")),
                               len(_stack(outs).split("\n")))

    mid = MARGIN + CLEAR + body_h / 2
    # Below the boxes, the routed arrows and the port captions share one band.
    height = mid + body_h / 2 + max(CLEAR, 14 + caption_h) + MARGIN

    d = Diagram(width, height, title)
    boxes = {}
    for c, names in sorted(columns.items()):
        span = len(names) * BOX_H + (len(names) - 1) * ROW_GAP
        y0 = mid - span / 2
        for k, name in enumerate(names):
            y = y0 + k * (BOX_H + ROW_GAP)
            boxes[name] = d.tool(col_x(c), y, name, w=BOX_W, h=BOX_H,
                                 sub=conn["instances"][name])

    store_y = mid - STORE_H / 2
    boxes["top"] = d.store(MARGIN, store_y, "inputs", w=STORE_W, h=STORE_H)
    tout = d.store(out_x, store_y, "outputs", w=STORE_W, h=STORE_H)
    for x, ports in ((MARGIN, ins), (out_x, outs)):
        d.label(x + STORE_W / 2, store_y + STORE_H + 22, _stack(ports),
                size=14, fill=DIM, anchor="middle")

    # An edge that skips a column, or joins two instances in the same column,
    # is bent clear of the boxes between its ends. A quadratic curve reaches
    # only half its control offset, so the control point is set to twice the
    # clearance actually wanted. The side alternates so two routed arrows do
    # not land their labels in the same place.
    clearance = 2 * (body_h / 2 + 30)
    side = 1
    for (src, dst), nets in sorted(merged.items()):
        a = boxes.get(src)
        b = tout if dst == "top" else boxes.get(dst)
        if a is None or b is None or src == dst:
            continue
        ra = -1 if src == "top" else rank[src]
        rb = ncols if dst == "top" else rank[dst]
        skips = rb - ra > 1
        same_column = src != "top" and dst != "top" and rank[src] == rank[dst]
        bend = (0, side * clearance) if (skips or same_column) else None
        if bend:
            side = -side
        d.arrow(a, b, label=_label(nets), bend=bend,
                label_dy=-8 if not bend or bend[1] < 0 else 18)

    d.caption(MARGIN, height - 12, title, size=15, fill=DIM)
    _save_to(d, out_svg)


def _stack(ports, limit=4) -> str:
    shown = ports[:limit]
    return "\n".join(shown) + ("\n..." if len(ports) > limit else "")


def _save_to(d, path):
    import pathlib
    body = "\n".join(d.parts)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="0 0 {d.w} {d.h}" '
           f'width="{d.w}" height="{d.h}" role="img">\n'
           f'{d._defs}\n{body}\n</svg>\n')
    pathlib.Path(path).write_text(svg)
