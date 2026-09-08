"""cli.py -- the shell door of the tool layer.

    python3 -m dvh clock-tree   TOP file.sv ...
    python3 -m dvh reset-tree   TOP file.sv ...
    python3 -m dvh crossings    TOP file.sv ...
    python3 -m dvh connections  TOP file.sv ... [--svg out.svg]
    python3 -m dvh read         TOP file.sv ... [--svg out.svg]
                                                  (all of the above)

Add --validate to check the JSON against its published schema before it is
printed (see schema.py). The tests always do; a caller that has pinned a
schema URL may want to as well.

Every command prints JSON; `read` also prints a short human report and
exits 1 if any crossing is unsynchronized, so it can gate a commit.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import clocks, design, graph, schema


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


def _emit(command: str, payload: dict, check: bool) -> int:
    """Print one command's JSON, optionally checking it against its schema."""
    if check:
        problems = schema.validate(command, payload)
        for p in problems:
            print(f"schema: {p}", file=sys.stderr)
        if problems:
            return 2
    print(json.dumps(payload, indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dvh")
    ap.add_argument("command", choices=["clock-tree", "reset-tree",
                                        "crossings", "connections", "read"])
    ap.add_argument("top")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--svg", default=None)
    ap.add_argument("--validate", action="store_true",
                    help="check the output against its schema")
    args = ap.parse_args(argv)

    if args.command in ("clock-tree", "reset-tree", "crossings", "read"):
        flat = design.load_flat(args.files, args.top)
    if args.command == "clock-tree":
        return _emit(args.command, clocks.clock_tree(flat), args.validate)
    if args.command == "reset-tree":
        return _emit(args.command, clocks.reset_tree(flat), args.validate)
    if args.command == "crossings":
        return _emit(args.command, clocks.crossings(flat), args.validate)
    mods = design.load_hier(args.files, args.top)
    conn = graph.connections(mods, args.top)
    if args.svg:
        graph.draw(conn, args.svg, f"{args.top} connections")
    if args.command == "connections":
        return _emit(args.command, conn, args.validate)
    tree = clocks.clock_tree(flat)
    resets = clocks.reset_tree(flat)
    xings = clocks.crossings(flat, tree)
    print(_report(tree, resets, xings, conn))
    return 1 if xings["unsynchronized"] else 0


if __name__ == "__main__":
    sys.exit(main())
