"""cli.py -- the shell door of the tool layer.

    python3 -m dvh clock-tree   TOP file.sv ...
    python3 -m dvh reset-tree   TOP file.sv ...
    python3 -m dvh crossings    TOP file.sv ...
    python3 -m dvh connections  TOP file.sv ... [--svg out.svg]
    python3 -m dvh read         TOP file.sv ... [--svg out.svg]
                                                  (all of the above)

Every command prints JSON; `read` also prints a short human report and
exits 1 if any crossing is unsynchronized, so it can gate a commit.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import clocks, design, graph


def _report(tree, resets, xings, conn) -> str:
    """A short human report. Everything is printed in sorted order: the
    output is included verbatim in the book, so it must not depend on the
    order a netlist reader happened to produce."""
    lines = [f"clock domains: {len(tree['domains'])}"]
    for dom, regs in sorted(tree["domains"].items()):
        lines.append(f"  {dom}: {len(regs)} registers")
    lines.append(f"registers without reset: {len(resets['no_reset'])}")
    for r in resets["no_reset"]:
        lines.append(f"  {r}")
    lines.append(f"crossings: {len(xings['crossings'])}, "
                 f"unsynchronized: {len(xings['unsynchronized'])}")
    for c in sorted(xings["crossings"],
                    key=lambda c: (c["synchronized"], c["from"], c["to"])):
        mark = "ok  " if c["synchronized"] else "BUG "
        plural = "s" if c["width"] != 1 else ""
        how = "synchronizer" if c["synchronized"] else c["reason"]
        lines.append(f"  {mark} {c['from']} ({c['from_domain']}) -> "
                     f"{c['to']} ({c['to_domain']}), "
                     f"{c['width']} bit{plural}, {how}")
    lines.append(f"instances: {len(conn['instances'])}, "
                 f"connections: {len(conn['edges'])}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dvh")
    ap.add_argument("command", choices=["clock-tree", "reset-tree",
                                        "crossings", "connections", "read"])
    ap.add_argument("top")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--svg", default=None)
    args = ap.parse_args(argv)

    if args.command in ("clock-tree", "reset-tree", "crossings", "read"):
        flat = design.load_flat(args.files, args.top)
    if args.command == "clock-tree":
        print(json.dumps(clocks.clock_tree(flat), indent=2)); return 0
    if args.command == "reset-tree":
        print(json.dumps(clocks.reset_tree(flat), indent=2)); return 0
    if args.command == "crossings":
        print(json.dumps(clocks.crossings(flat), indent=2)); return 0
    mods = design.load_hier(args.files, args.top)
    conn = graph.connections(mods, args.top)
    if args.svg:
        graph.draw(conn, args.svg, f"{args.top} connections")
    if args.command == "connections":
        print(json.dumps(conn, indent=2)); return 0
    tree = clocks.clock_tree(flat)
    resets = clocks.reset_tree(flat)
    xings = clocks.crossings(flat, tree)
    print(_report(tree, resets, xings, conn))
    return 1 if xings["unsynchronized"] else 0


if __name__ == "__main__":
    sys.exit(main())
