"""list.py -- the netlist fault model's population for the repaired
FIFO: every mutation Yosys's `mutate -list` makes after `prep`.

    python3 list.py

Asks for 100,000 mutations, more than exist, so that Yosys lists every
one and says how many it could make. Prints the list's SHA-256, then
the counts by mutation mode, by cell type and by the source line each
mutation's cell came from, and the share on the memory's lines.
Last, a check of the numbering every netlist example relies on: the
mode, line and cell of each listed mutation equal the columns of the
committed population file, netlist-population/pop.tsv, row for row.
About two seconds.
"""
import collections
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import yosysmut  # noqa: E402

B = HERE / "build"
POP = HERE.parent / "netlist-population" / "pop.tsv"
# The memory's lines of fifo_fixed.sv: its declaration, the clocked
# block that writes it, the write enable, the write and the read.
# Counted by line, not by cell, so the count is approximate: line 36
# also holds the pointer and count registers, and line 42 the write
# pointer's enable.
MEMORY = {"29", "36", "42", "43", "57"}


def main():
    C = mutlib.Checks()
    mutlib.need("yosys")
    print(f"tools: {mutlib.version('yosys')}")
    B.mkdir(parents=True, exist_ok=True)
    cmds, warn = yosysmut.population(B)
    N = len(cmds) - 1
    print(f"design: {mutlib.FIXED},")
    print("  after prep -top fifo")
    print("mutate -list 100000 -seed 1 -none:")
    print(f"  {warn.strip()}")
    print(f"population: {N} mutations, numbered 1-{N} "
          "(0 is the unmutated design)")
    sha = hashlib.sha256((B / "list.txt").read_bytes()).hexdigest()
    print(f"list SHA-256: {sha[:16]}...")
    C.pin("population size", N, 9281)
    rows = [yosysmut.parse(c) for c in cmds[1:]]

    def show(title, key, label=lambda k: k):
        cnt = collections.Counter(key(r) for r in rows)
        print(title)
        for k, n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {label(k):40s} {n:5d}  {100.0 * n / N:5.1f}%")
        return cnt

    modes = show("by mode", lambda r: r[0])
    C.pin("by mode", dict(modes), {"inv": 2046, "const0": 2046,
                                   "const1": 2046, "cnot0": 1573,
                                   "cnot1": 1570})
    show("by cell type", lambda r: r[2],
         lambda k: "(no cell name: memory mapping)" if k == "auto"
         else f"${k}")
    src = mutlib.ROOT.joinpath(mutlib.FIXED).read_text().splitlines()
    lines = show("by source line of the cell", lambda r: r[1],
                 lambda k: "(no source tag)" if k == "-" else
                 f"{k:>3s} {src[int(k) - 1].strip()[:34]}")
    mem = sum(n for k, n in lines.items() if k in MEMORY)
    print(mutlib.wrap(f"on the memory's lines ({', '.join(sorted(MEMORY))}"
                      f"; 36 and 42 also hold the pointer and count "
                      f"registers and the write pointer's enable): {mem} "
                      f"of {N} ({100.0 * mem / N:.1f}%); with no source "
                      f"tag: {lines['-']}"))
    C.pin("memory mutations", mem, 6849)
    C.pin("untagged", lines["-"], 1868)

    pop = [x.rstrip("\n").split("\t") for x in POP.open()][1:]
    same = sum(1 for k, r in enumerate(rows, 1)
               if pop[k - 1][:4] == [str(k), r[0], r[1], r[2]])
    print(f"numbering: {same} of {N} mutations match the committed "
          "population file")
    C.pin("numbering agrees with pop.tsv", (same, len(pop)), (N, N))
    C.report()
    print(f"verdict: {N} mutations, {100.0 * mem / N:.1f}% on the "
          "memory's lines")


if __name__ == "__main__":
    main()
