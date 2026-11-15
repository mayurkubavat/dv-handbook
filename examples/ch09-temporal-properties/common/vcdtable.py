#!/usr/bin/env python3
"""vcdtable.py -- print a counterexample trace as a table.

    vcdtable.py TRACE.vcd SIGNAL [SIGNAL ...]

InFormal writes one VCD file for each counterexample and each covered
cover. This script prints one row per clock cycle with the value each
named signal holds in that cycle, in decimal. A signal is named by the
end of its hierarchical path, `full` or `u_sva.occ`; where a name is
declared more than once the first declaration is the one read, which
also steps over the second `clk` these files declare. A cycle is ten
time units long and cycle 0 is the reset cycle.
"""
import sys

PERIOD = 10


def read(path):
    """Return ({full name: code}, {code: [(time, value)]})."""
    names, changes, scope, now = {}, {}, [], 0
    with open(path) as vcd:
        for line in vcd:
            word = line.split()
            if not word:
                continue
            if word[0] == "$scope":
                scope.append(word[2])
            elif word[0] == "$upscope":
                scope.pop()
            elif word[0] == "$var":
                names.setdefault(".".join(scope + [word[4]]), word[3])
            elif word[0][0] == "#":
                now = int(word[0][1:])
            elif word[0][0] == "b":
                changes.setdefault(word[1], []).append((now, word[0][1:]))
            elif word[0][0] in "01xz":
                changes.setdefault(word[0][1:], []).append((now, word[0][0]))
    return names, changes


def value_at(history, time):
    value = "x"
    for when, bits in history:
        if when > time:
            break
        value = bits
    return str(int(value, 2)) if set(value) <= set("01") else "x"


def main():
    names, changes = read(sys.argv[1])
    wanted = sys.argv[2:]
    codes = []
    for want in wanted:
        full = [n for n in names if n == want or n.endswith("." + want)]
        if not full:
            sys.exit(f"vcdtable: no signal named {want}")
        codes.append(names[full[0]])
    last = max(t for h in changes.values() for t, _ in h)
    width = [max(len(w.split(".")[-1]), 5) for w in wanted]
    print("cycle  " + "  ".join(w.split(".")[-1].rjust(n)
                                for w, n in zip(wanted, width)))
    for cycle in range(last // PERIOD + 1):
        row = [value_at(changes.get(c, []), cycle * PERIOD) for c in codes]
        print(f"{cycle:5d}  " + "  ".join(v.rjust(n)
                                          for v, n in zip(row, width)))


if __name__ == "__main__":
    main()
