"""sample.py -- a sampled kill rate, run, and checked against the
population it was drawn from.

    python3 sample.py

Lists the population with Yosys (as netlist-list/ does), draws a
uniform sample of 1,000 mutation numbers with Python's generator at
seed 1, writes a netlist holding those 1,000 mutations behind the
select (their numbers kept), builds the four testbenches against it
once each and runs every sampled mutation. Prints, at n = 30, 100, 300
and 1000 (the first n of the one draw), each testbench's kills and
their 95% Clopper-Pearson interval. Then the cross-check: every
sampled verdict must equal its row of the committed population file,
netlist-population/pop.tsv, which a full run of all 9,281 wrote. A
disagreement means the harness or a tool changed. About 60 seconds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import yosysmut  # noqa: E402

B = HERE / "build"
POP = HERE.parent / "netlist-population" / "pop.tsv"
NS = (30, 100, 300, 1000)
SEED = 1


def main():
    C = mutlib.Checks()
    mutlib.need("yosys")
    print(f"tools: {mutlib.version('yosys')}; "
          f"{mutlib.version('verilator')}")
    B.mkdir(parents=True, exist_ok=True)
    cmds, _ = yosysmut.population(B)
    N = len(cmds) - 1
    draw = yosysmut.uniform(N, max(NS), SEED)
    print(f"population {N}; uniform sample of {max(NS)} without "
          "replacement,")
    print(f"  Python's random.Random({SEED}).sample")
    print(f"  first ten drawn: {' '.join(map(str, draw[:10]))}")
    net = yosysmut.select_netlist([cmds[k] for k in sorted(draw)],
                                  B / "fifo_mut.v")
    print(f"netlist with the {len(draw)} sampled mutations behind "
          f"mutsel: {len(net.read_text().splitlines())} lines")
    dirs = yosysmut.build_netlist(B / "obj", net, mutlib.NAMES)
    v = yosysmut.run_netlist(dirs, [0] + draw)
    ctrl = [v[(0, tb)] for tb in mutlib.NAMES]
    print(mutlib.wrap("control (mutation 0): " + ", ".join(
        f"{tb} {c}" for tb, c in zip(mutlib.NAMES, ctrl))))
    C.pin("control", ctrl, ["survived"] * 4)
    names = mutlib.NAMES + ["union"]

    def dead(k, tb):
        if tb == "union":
            return any(v[(k, t)] in mutlib.DEAD for t in mutlib.NAMES)
        return v[(k, tb)] in mutlib.DEAD

    want = {100: [30, 89, 0, 4, 89], 1000: [302, 896, 0, 39, 900]}
    for n in NS:
        print(f"n = {n} (95% Clopper-Pearson)")
        got = []
        for tb in names:
            k = sum(dead(j, tb) for j in draw[:n])
            got.append(k)
            print(f"  {tb:14s} {mutlib.fmt_cp(k, n)}")
        if n in want:
            C.pin(f"kills at n = {n}", got, want[n])
    pop = {r[0]: r[4:8] for r in
           (x.rstrip("\n").split("\t") for x in POP.open())}
    agree = sum(all(v[(k, tb)] == pop[str(k)][i]
                    for i, tb in enumerate(mutlib.NAMES)) for k in draw)
    print(f"cross-check: {agree} of {len(draw)} sampled mutations have "
          "the verdicts")
    print("  of the committed population file")
    C.pin("agreement with pop.tsv", agree, len(draw))
    C.report()
    print(f"verdict: the sample of {len(draw)} reproduces the "
          "population run")


if __name__ == "__main__":
    main()
