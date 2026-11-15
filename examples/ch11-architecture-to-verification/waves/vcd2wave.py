#!/usr/bin/env python3
"""vcd2wave.py -- cut a window of cycles out of a VCD into WaveJSON.

Usage: vcd2wave.py <file.vcd> <out.json> <clock> <from> <to> <sig>...

<clock> and each <sig> are hierarchical names as the VCD spells them
(tb_v1.dut.ARVALID). <from> and <to> are clock cycles counted from the
first rising edge, or `first:<sig>` for the cycle that signal first
goes high, with an optional +N or -N. Each signal is sampled once per
cycle, halfway through it, so a value is the one the next rising edge
captures. A one-bit signal becomes 0/1 and a wider one a bus segment
with its value in hex. The JSON is the WaveDrom format's subset the
book's renderer draws, and a text picture of it is printed too, so a
run shows the waveform without any drawing tool.
"""
import json
import re
import sys


def parse(path):
    """Return {name: (width, [(time, value), ...])} for every variable."""
    ids, scope, changes, t = {}, [], {}, 0
    with open(path) as f:
        for line in f:
            w = line.split()
            if not w:
                continue
            if w[0] == "$scope":
                scope.append(w[2])
            elif w[0] == "$upscope":
                scope.pop()
            elif w[0] == "$var":
                name = ".".join(scope + [w[4]])
                ids.setdefault(w[3], []).append((name, int(w[2])))
            elif w[0].startswith("#"):
                t = int(w[0][1:])
            elif w[0][0] in "01xz" and len(w) == 1:
                changes.setdefault(w[0][1:], []).append((t, w[0][0]))
            elif w[0][0] == "b":
                changes.setdefault(w[1], []).append((t, w[0][1:]))
    out = {}
    for code, names in ids.items():
        for name, width in names:
            out[name] = (width, changes.get(code, []))
    return out


def value_at(changes, t):
    v = "x"
    for when, val in changes:
        if when > t:
            break
        v = val
    return v


def main(argv):
    vcd, out, clock, lo, hi, sigs = argv[0], argv[1], argv[2], argv[3], \
        argv[4], argv[5:]
    d = parse(vcd)
    rises = [t for t, v in d[clock][1] if v == "1"]
    period = rises[1] - rises[0]

    def cycle(spec):
        m = re.fullmatch(r"first:([\w.]+)([+-]\d+)?", spec)
        if not m:
            return int(spec)
        when = next(t for t, v in d[m.group(1)][1] if v == "1")
        k = next(i for i, r in enumerate(rises) if r >= when)
        return k + int(m.group(2) or 0)

    a, b = cycle(lo), min(cycle(hi), len(rises) - 2)   # clamp to the run
    rows = [{"name": "clk", "wave": "p" + "." * (b - a)}]
    for s in sigs:
        width, ch = d[s]
        wave, data, last = "", [], None
        for k in range(a, b + 1):
            v = value_at(ch, rises[k] + period // 2)
            if width > 1 and "x" not in v:
                v = f"{int(v, 2):x}"
            if v == last:
                wave += "."
            elif width == 1:
                wave += v
            else:
                wave += "="
                data.append(v)
            last = v
        row = {"name": s.split(".")[-1], "wave": wave}
        if data:
            row["data"] = data
        rows.append(row)
    with open(out, "w") as f:
        json.dump({"signal": rows, "head": {"from": a, "to": b}}, f,
                  indent=1)
        f.write("\n")
    print(f"cycles {a} to {b}, {len(sigs)} signals -> {out}")
    for r in rows[1:]:
        print(f"{r['name']:>8} {picture(r)}")


def picture(row):
    """One character per cycle: _ low, - high; for a bus, = where the
    value changes and - while it holds."""
    out, last = [], "_"
    for c in row["wave"]:
        if c == ".":
            out.append(last if last in "_-x" else "-")
            continue
        last = {"0": "_", "1": "-", "=": "="}.get(c, "x")
        out.append(last)
    vals = row.get("data")
    return "".join(out) + (f"  {' '.join(vals)}" if vals else "")


if __name__ == "__main__":
    main(sys.argv[1:])
