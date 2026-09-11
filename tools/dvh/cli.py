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

Every command but `read` prints JSON validated against a published schema;
`read` prints a short human report instead, so it can gate a commit: it
exits 0 when there is nothing to review, 1 when some crossing's shape is not
recognized, and 2 when the tool could not answer at all. The third is not a
finding about the design, and a gate has to tell it from one.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import clocks, design, graph, schema


def _at(src: str) -> str:
    """A finding names the RTL that produced it, when the netlist knows it.

    Only the file and the first line: the column range Yosys records is
    noise in a report a person reads."""
    if not src:
        return ""
    file, _, span = src.partition(":")
    return f"  [{file}:{span.split('.')[0]}]" if span else f"  [{file}]"


def _display_names(domains) -> dict:
    """Readable names for domains, disambiguated only where they collide.

    A domain's identity is its clock net, so two different networks can
    share a label. Printing the net every time is noise; printing it only
    where two labels would otherwise be identical keeps the report readable
    and still tells two networks apart when it matters.
    """
    from .clocks import _pretty                            # noqa: PLC0415
    seen = {}
    for key in domains:
        seen.setdefault(_pretty(key), []).append(key)
    return {key: (label if len(keys) == 1 else key)
            for label, keys in seen.items() for key in keys}


def _report(tree, resets, xings, conn) -> str:
    """A short human report. Everything is printed in sorted order: the
    output is included verbatim in the book, so it must not depend on the
    order a netlist reader happened to produce."""
    show = _display_names(tree["domains"])
    lines = [f"clock domains: {len(tree['domains'])}"]
    for dom, regs in sorted(tree["domains"].items(),
                            key=lambda kv: show[kv[0]]):
        lines.append(f"  {show[dom]}: {len(regs)} registers")
    lines.append(f"registers without reset: {len(resets['no_reset'])}")
    for r in resets["no_reset"]:
        lines.append(f"  {r['name']}{_at(r['src'])}")
    unknown = sum(1 for c in xings["crossings"]
                  if not c["shape_recognized"])
    gated = unknown - len(xings["unrecognized"])
    tail = f", {gated} of them one clock gated differently" if gated else ""
    lines.append(f"crossings: {len(xings['crossings'])}, "
                 f"shape not recognized: {unknown}{tail}")
    for c in sorted(xings["crossings"],
                    key=lambda c: (c["shape_recognized"], c["from"],
                                   c["to"])):
        mark = "known" if c["shape_recognized"] else "CHECK"
        plural = "s" if c["width"] != 1 else ""
        how = ("two-flop synchronizer" if c["shape_recognized"]
               else c["note"])
        a = show.get(c["from_domain"], c["from_domain"])
        b = show.get(c["to_domain"], c["to_domain"])
        lines.append(f"  {mark} {c['from']} ({a}) -> {c['to']} ({b}), "
                     f"{c['width']} bit{plural}, {how}{_at(c['src'])}")
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
    """Exit 0 clean, 1 findings, 2 the tool could not answer.

    The three are kept apart because a project that gates its build on this
    has to tell them apart. An earlier version let an unreadable file and an
    unanticipated register type escape as a Python traceback and exit 1 --
    the same code a finding uses -- so a crash read as a crossing.
    """
    try:
        return _main(argv)
    except design.DesignError as e:
        print(f"dvh: {e}", file=sys.stderr)
        return 2
    except Exception as e:                                 # noqa: BLE001
        print(f"dvh: {type(e).__name__}: {e}", file=sys.stderr)
        print("dvh: this is a defect in the tool, not a finding about the "
              "design", file=sys.stderr)
        return 2


def _main(argv) -> int:
    ap = argparse.ArgumentParser(prog="dvh")
    ap.add_argument("command", choices=["clock-tree", "reset-tree",
                                        "crossings", "connections", "read"])
    ap.add_argument("top")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--svg", default=None)
    ap.add_argument("--validate", action="store_true",
                    help="check the output against its schema")
    ap.add_argument("--clock", action="append", default=[], metavar="NAME",
                    help="a clock of this design, from its specification; "
                         "repeat for each. Without these the walk has to "
                         "guess which input of a gate is the clock, and "
                         "says so where it cannot tell")
    args = ap.parse_args(argv)
    clk = tuple(args.clock)

    if args.command in ("clock-tree", "reset-tree", "crossings", "read"):
        flat = design.load_flat(args.files, args.top)
    if args.command == "clock-tree":
        return _emit(args.command, clocks.clock_tree(flat, clk),
                     args.validate)
    if args.command == "reset-tree":
        return _emit(args.command, clocks.reset_tree(flat, clk),
                     args.validate)
    if args.command == "crossings":
        return _emit(args.command, clocks.crossings(flat, None, clk),
                     args.validate)
    mods = design.load_hier(args.files, args.top)
    conn = graph.connections(mods, args.top)
    if args.svg:
        graph.draw(conn, args.svg, f"{args.top} connections")
    if args.command == "connections":
        return _emit(args.command, conn, args.validate)
    tree = clocks.clock_tree(flat, clk)
    resets = clocks.reset_tree(flat, clk)
    xings = clocks.crossings(flat, tree)
    print(_report(tree, resets, xings, conn))
    return 1 if xings["unrecognized"] else 0


if __name__ == "__main__":
    sys.exit(main())
