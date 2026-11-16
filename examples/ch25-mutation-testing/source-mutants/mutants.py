"""mutants.py -- the source-level fault model on the repaired FIFO:
the 44 mutants of common/srcmut.py, what the book's lint makes of
each, and which of them a synthesis tool cannot tell from the
original or from each other.

    python3 mutants.py

1. The list: each mutant as the line it changes, generated from
   fifo_fixed.sv as it stands when the run starts.
2. Counts by operator, and tbl-ch25-operators.md, the chapter's
   operator table, written from them.
3. Lint: verilator --lint-only with the book's flags on each
   single-edit copy. A mutant whose warning -Wall makes fatal is
   killed by the build before any simulation; the run prints those
   apart, with the warning's name.
4. Trivial compiler equivalence, in hardware form: each copy and the
   original through one Yosys script (prep, opt -full, opt_clean
   -purge), the netlist written as JSON, and a structural hash of it
   that ignores the names Yosys gives internal wires (a
   Weisfeiler-Lehman refinement over cells and bits, with port names
   and cell types as the labels). Equal hashes: netlists the same up
   to renaming. About 15 seconds in all.
"""
import collections
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402

B = HERE / "build"
MEANING = {
    "LCR": ("logical connector replacement", "`&&` and `||` exchanged"),
    "LNR": ("negation removal", "a unary `!` removed"),
    "CNG": ("condition negation", "`if (c)` made `if (!(c))`"),
    "ROR": ("relational operator replacement",
            "`==` made `!=`, `<`, `<=`, `>`, `>=`"),
    "AOR": ("arithmetic operator replacement", "`+` and `-` exchanged"),
    "CRP": ("constant replacement", "`1'b1` made `2'd2`; `'0` made `'1`"),
    "SDL": ("statement deletion", "one assignment deleted"),
    "VSW": ("variable replacement", "`wr_ptr` and `rd_ptr` exchanged"
            " in a use"),
    "ARS": ("asynchronous reset made synchronous (HDL)",
            "`or negedge rst_n` dropped"),
    "CSW": ("case item exchange (HDL)", "labels `2'b10` and `2'b01`"
            " exchanged"),
}
# (operator, line) of m01..m44, as the research run listed them.
WANT = ("LCR33 LNR33 LCR34 LNR34 ARS36 LNR37 CNG37 CRP38 SDL38 CRP39 "
        "SDL39 CRP40 SDL40 CNG42 SDL43 VSW43 AOR44 CRP44 SDL44 VSW44 "
        "CNG46 AOR47 CRP47 SDL47 VSW47 AOR50 CRP50 SDL50 AOR51 CRP51 "
        "SDL51 SDL52 VSW57 ROR58 ROR58 ROR58 ROR58 ROR58 ROR59 ROR59 "
        "ROR59 ROR59 ROR59 CSW50").split()


def ranges(ids):
    """m14, m15, m16 -> m14-m16: runs of consecutive names joined."""
    out, run = [], []
    for k in [int(i[1:]) for i in ids] + [None]:
        if run and k == run[-1] + 1:
            run.append(k)
            continue
        if run:
            out += ([f"m{k:02d}" for k in run] if len(run) < 3
                    else [f"m{run[0]:02d}-m{run[-1]:02d}"])
        run = [k]
    return ", ".join(out)


def lint(path):
    cmd = (["verilator", "--lint-only"] + mutlib.VFLAGS[1:]
           + ["--top-module", "fifo", mutlib.rel(path)])
    p = subprocess.run(cmd, cwd=mutlib.ROOT, capture_output=True,
                       text=True)
    warn = sorted(set(re.findall(r"%Warning-([A-Z]+):", p.stderr)))
    if p.returncode == 0:
        return "clean"
    return "rejected " + ",".join(warn) if warn else "error"


def h(s):
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def wl_hash(path, rounds=8):
    """A hash of a one-module Yosys JSON netlist that is the same for
    two netlists equal up to the names of internal wires and cells."""
    d = json.loads(pathlib.Path(path).read_text())
    (mod,) = d["modules"].values()
    lab, adj = {}, collections.defaultdict(list)
    for pn, p in mod["ports"].items():
        for i, b in enumerate(p["bits"]):
            if isinstance(b, int):
                lab[("b", b)] = f"port:{pn}:{i}"
    for cn, c in mod["cells"].items():
        n = ("c", cn)
        par = ",".join(f"{k}={v}" for k, v in sorted(c["parameters"]
                                                    .items()))
        lab[n] = f"cell:{c['type']}:{par}"
        for pn, bits in sorted(c["connections"].items()):
            for i, b in enumerate(bits):
                if isinstance(b, int):
                    lab.setdefault(("b", b), "bit")
                    adj[n].append((f"{pn}{i}", ("b", b)))
                    adj[("b", b)].append((f"~{pn}{i}", n))
                else:
                    lab[n] += f"|{pn}{i}={b}"
    for _ in range(rounds):
        lab = {n: h(x + "#" + ",".join(sorted(e + ":" + lab[m]
                                              for e, m in adj[n])))
               for n, x in lab.items()}
    return h(",".join(sorted(lab.values())))


def synth(name, path):
    """Yosys's netlist hash for one design, or the front end's error."""
    out = B / f"{name}.json"
    p = subprocess.run(
        ["yosys", "-q", "-p", f"read_verilog -sv {mutlib.rel(path)}; "
         "prep -top fifo; opt -full; opt_clean -purge; "
         f"write_json {mutlib.rel(out)}"],
        cwd=mutlib.ROOT, capture_output=True, text=True)
    if p.returncode:
        err = re.search(r"ERROR: (.*)", p.stdout + p.stderr)
        return "refused: " + (err.group(1).replace(name + ".sv", "")
                              if err else "?")
    return wl_hash(out)


def main():
    C = mutlib.Checks()
    mutlib.need("yosys")
    print(f"tools: {mutlib.version('verilator')}; "
          f"{mutlib.version('yosys')}")
    ms = srcmut.mutants()
    print(f"design: {mutlib.FIXED}")
    print(f"1. source mutants: {len(ms)}, one change each, made when "
          "the run started")
    for m in ms:
        print("  " + srcmut.describe(m))
    C.pin("mutant count", len(ms), 44)
    C.pin("operators and lines", [f"{m.op}{m.line}" for m in ms], WANT)

    print("2. mutants by operator")
    by = collections.OrderedDict()
    for m in ms:
        by.setdefault(m.op, []).append(m.id)
    for op, ids in by.items():
        print(f"  {op} {len(ids):2d}  {MEANING[op][0]}")
    C.pin("counts by operator", {k: len(v) for k, v in by.items()},
          {"LCR": 2, "LNR": 3, "ARS": 1, "CNG": 3, "CRP": 7, "SDL": 9,
           "VSW": 4, "AOR": 4, "ROR": 10, "CSW": 1})
    rows = []
    for op, ids in by.items():
        names = ranges(ids)
        rows.append([op, MEANING[op][0], MEANING[op][1], str(len(ids)),
                     names])
    mutlib.table_md(HERE / "tbl-ch25-operators.md",
                    ["operator", "name", "change", "sites", "mutants"],
                    rows, "The source operators and their sites in the "
                    "repaired FIFO {#tbl-ch25-operators}",
                    widths=[8, 24, 24, 5, 20])

    os.makedirs(B, exist_ok=True)
    paths = {"orig": mutlib.ROOT / mutlib.FIXED}
    for m in ms:
        paths[m.id] = B / f"{m.id}.sv"
        paths[m.id].write_text(srcmut.single(m))
    print("3. lint: verilator --lint-only with the book's -Wall flags")
    res = dict(zip(paths, mutlib.pmap(lint, list(paths.values()))))
    print(f"  original: {res['orig']}")
    rej = [(k, v) for k, v in res.items() if v.startswith("rejected")]
    for k, v in rej:
        print(f"  {k} {v}")
    print(f"  lint kills {len(rej)} of {len(ms)} before any simulation")
    C.pin("original lint", res["orig"], "clean")
    C.pin("lint rejections", rej,
          [("m15", "rejected UNDRIVEN"), ("m18", "rejected WIDTHEXPAND"),
           ("m23", "rejected WIDTHEXPAND"), ("m27", "rejected WIDTHEXPAND"),
           ("m30", "rejected WIDTHEXPAND"), ("m35", "rejected UNSIGNED"),
           ("m38", "rejected UNSIGNED")])

    print("4. trivial compiler equivalence: one Yosys script, netlists")
    print("   compared up to the names of internal wires and cells")
    hs = dict(zip(paths, mutlib.pmap(lambda k: synth(k, paths[k]),
                                     list(paths))))
    refused = [k for k, v in hs.items() if v.startswith("refused")]
    for k in refused:
        print(f"  {k} {hs[k].split(': ')[0]} by Yosys's front end:")
        print(f"    {hs[k].split(': ', 1)[1]}")
    same = [k for k in ms if hs[k.id] == hs["orig"]]
    print(f"  identical to the original: "
          f"{' '.join(m.id for m in same) or 'none'}")
    groups = collections.defaultdict(list)
    for k, v in hs.items():
        if k != "orig" and not v.startswith("refused") \
                and v != hs["orig"]:
            groups[v].append(k)
    dup = [g for g in groups.values() if len(g) > 1]
    print(f"  duplicate groups among the rest: "
          f"{'; '.join(' '.join(g) for g in dup) or 'none'}")
    print(f"  distinct netlists: {len(groups)} mutants, plus the "
          f"original's")
    C.pin("refused by Yosys", refused, ["m06", "m07"])
    C.pin("identical to the original", [m.id for m in same], ["m32"])
    C.pin("duplicate groups", dup, [])
    C.report()
    print(f"verdict: {len(ms)} mutants; lint kills {len(rej)}; "
          f"synthesis finds {len(same)} identical to the original")


if __name__ == "__main__":
    main()
