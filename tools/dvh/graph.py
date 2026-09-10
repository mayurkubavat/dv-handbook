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
        # A parameterized instance is typed "$paramod\\sync2\\W=4"; the
        # module's own name is what the reader of a block diagram wants.
        pretty = (cell.type.split("\\")[1]
                  if cell.type.startswith("$paramod") else cell.type)
        instances[cname] = {"module": pretty, "src": cell.src}
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
# The diagram flows top to bottom, not left to right. A book page is
# portrait: a wide drawing is scaled down until its type is unreadable, so
# dataflow rank runs down the page and instances sharing a rank sit side by
# side. Ranks become rows; the drawing stays narrow however deep it gets.
BOX_W, BOX_H = 210, 74           # an instance
STORE_W, STORE_H = 150, 66       # the top-level port cylinders
ROW_GAP, COL_GAP = 76, 40        # between ranks, between peers in one rank
MARGIN = 26
CLEAR = 116                      # side room reserved for routed arrows


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
    arrows, flowing down the page. Instances are placed in rows by dataflow
    rank, so boxes never overlap and an edge that skips a rank is routed
    clear of the boxes it passes."""
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "..", "figures"))
    from blocks import Diagram, DIM                 # noqa: E402

    merged = _merge_edges(conn)
    inst = sorted(conn["instances"])
    rank = _ranks(inst, merged)
    rows = {}
    for name in inst:
        rows.setdefault(rank[name], []).append(name)
    nrows = max(rows) + 1 if rows else 0

    widest = max((len(v) for v in rows.values()), default=1)
    band = widest * BOX_W + (widest - 1) * COL_GAP
    width = CLEAR + band + CLEAR
    mid = CLEAR + band / 2

    def row_y(r):
        return MARGIN + STORE_H + ROW_GAP + r * (BOX_H + ROW_GAP)

    out_y = row_y(nrows - 1) + BOX_H + ROW_GAP if nrows else row_y(0)

    ins = sorted({e["from_port"] for e in conn["edges"] if e["from"] == "top"})
    outs = sorted({e["to_port"] for e in conn["edges"] if e["to"] == "top"})
    # Port names sit beside the cylinders, so only the deeper of the two lists
    # can push the drawing past the bottom store.
    tail_text = (len(_stack(outs).split("\n")) - 2) * 18
    height = out_y + STORE_H + max(0, tail_text) + MARGIN

    d = Diagram(width, height, title)
    boxes = {}
    for r, names in sorted(rows.items()):
        span = len(names) * BOX_W + (len(names) - 1) * COL_GAP
        x0 = mid - span / 2
        for k, name in enumerate(names):
            x = x0 + k * (BOX_W + COL_GAP)
            boxes[name] = d.tool(x, row_y(r), name, w=BOX_W, h=BOX_H,
                                 sub=conn["instances"][name]["module"])

    store_x = mid - STORE_W / 2
    boxes["top"] = d.store(store_x, MARGIN, "inputs", w=STORE_W, h=STORE_H)
    tout = d.store(store_x, out_y, "outputs", w=STORE_W, h=STORE_H)
    # Port names sit beside their cylinder, so the list can grow without ever
    # colliding with the cylinder's own label.
    d.label(store_x + STORE_W + 16, MARGIN + 22, _stack(ins), size=14, fill=DIM)
    d.label(store_x + STORE_W + 16, out_y + 22, _stack(outs), size=14, fill=DIM)

    # An edge that skips a rank, or joins two instances in the same rank, is
    # bent clear of the boxes between its ends. A quadratic curve reaches only
    # half its control offset, so the control point is twice the clearance
    # wanted. The side alternates so two routed arrows do not overlap.
    clearance = 2 * (band / 2 + 52)
    side = 1
    for (src, dst), nets in sorted(merged.items()):
        a = boxes.get(src)
        b = tout if dst == "top" else boxes.get(dst)
        if a is None or b is None or src == dst:
            continue
        ra = -1 if src == "top" else rank[src]
        rb = nrows if dst == "top" else rank[dst]
        skips = rb - ra > 1
        peers = src != "top" and dst != "top" and rank[src] == rank[dst]
        bend = (side * clearance, 0) if (skips or peers) else None
        if bend:
            side = -side
        d.arrow(a, b, label=_label(nets), bend=bend, label_dy=-10)

    # No title is drawn inside the drawing: where this is used as a book
    # figure the caption sits outside it, and two titles read as a mistake.
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
