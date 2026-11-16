"""fifth.py -- closing the gap the survivors name: the temporal-
properties chapter's traffic and checker, unchanged and read by path,
plus a data check (fifo_data_sva.sv, bound by fifo_data_bind.sv).

    python3 fifth.py

1. Control: the fifth testbench passes the repaired FIFO and fails the
   first chapter's original FIFO.
2. The 44 source mutants (the source schema), the checker as shipped
   beside the fifth testbench: default initial values, and randomized
   ones (+verilator+rand+reset+2, seeds 1-5; a mutant counts as killed
   when some seed kills it).
3. The uniform sample of 1,000 netlist mutations of netlist-sample/
   (seed 1), the same two testbenches.
4. The kills at the ports: the fifth testbench again, with the checker
   bound by fifo_port_bind.sv, which ties Sync_A's count to the
   checker's own, so that the white-box Sync_A cannot fail. With the
   five equivalent mutants of the miter examples, the score.
5. tbl-ch25-report.md, the before-and-after table.
About a minute.
"""
import pathlib
import sys
import textwrap

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import yosysmut  # noqa: E402

B = HERE / "build"
C09 = mutlib.CHK09
FIFTH = f"{mutlib.CH}/fifth-tb"
TBS = {
    "ch09-sva": mutlib.TBS["ch09-sva"],
    "fifth": ([f"{C09}/fifo_sva.sv", f"{C09}/fifo_bind.sv",
               f"{FIFTH}/fifo_data_sva.sv", f"{FIFTH}/fifo_data_bind.sv",
               f"{C09}/tb_fifo_sva.sv"],
              "tb_fifo_sva", ["-Wno-SYNCASYNCNET"],
              [["+verilator+seed+1"]], "PASS"),
}
NAMES = list(TBS)
SEEDS = range(1, 6)
# The fifth testbench with Sync_A made vacuous: the kills at the ports.
PORTS = {"ports": ([f"{FIFTH}/fifo_port_bind.sv" if x.endswith(
    "/fifo_bind.sv") else x for x in TBS["fifth"][0]],) + TBS["fifth"][1:]}
# Proved equivalent by the miter examples (equiv-outright,
# equiv-invariant, equiv-reset, white-box).
EQUIV = ["m05", "m32", "m36", "m43", "m44"]


def rnd(s):
    return [["+verilator+rand+reset+2", f"+verilator+seed+{s}"]]


def main():
    C = mutlib.Checks()
    mutlib.need("yosys")
    print(f"tools: {mutlib.version('verilator')}; "
          f"{mutlib.version('yosys')}")
    print("fifth testbench: the traffic of tb_fifo_sva.sv, the checker of")
    print("  fifo_sva.sv, and the data check of fifo_data_sva.sv")

    print("1. control")
    ctl = {}
    for name, rtl in (("repaired FIFO", mutlib.FIXED),
                      ("original FIFO", mutlib.ORIG)):
        d = B / "ctl" / name.split()[0]
        ok, _, log = mutlib.build("fifth", [rtl], d, tbs=TBS)
        assert ok, log[-2000:]
        v, _, out = mutlib.run("fifth", d, tbs=TBS)
        fired = sorted({x.split("Assertion failed in ")[1].split(":")[0]
                        .split(".")[-1] for x in out.splitlines()
                        if "Assertion failed in " in x})
        ctl[name] = v
        print(f"  {name}: {'passes' if v == 'survived' else 'fails'}"
              + (f" ({', '.join(fired)})" if fired else ""))
    C.pin("control", (ctl["repaired FIFO"], ctl["original FIFO"]),
          ("survived", "killed"))

    ms = srcmut.mutants()
    n = len(ms)
    dirs, _ = srcmut.build_schema(B / "src", NAMES, tbs=TBS)
    jobs = [(k, tb, s) for k in range(n + 1) for tb in NAMES
            for s in [0] + list(SEEDS)]
    res = dict(zip(jobs, mutlib.pmap(lambda j: mutlib.run(
        j[1], dirs[j[1]], [f"+mut={j[0]}"],
        runs=None if j[2] == 0 else rnd(j[2]), tbs=TBS)[0], jobs)))

    def dead(k, tb, s):
        return res[(k, tb, s)] in mutlib.DEAD
    print("2. source mutants (44); default and randomized initial values")
    C.pin("schema control", [res[(0, tb, s)] for tb in NAMES
                             for s in [0] + list(SEEDS)],
          ["survived"] * 12)
    src = {}
    for tb in NAMES:
        kd = [m.id for k, m in enumerate(ms, 1) if dead(k, tb, 0)]
        kr = [m.id for k, m in enumerate(ms, 1)
              if any(dead(k, tb, s) for s in SEEDS)]
        alive_d = [m.id for m in ms if m.id not in kd]
        alive_r = [m.id for m in ms if m.id not in kr]
        src[tb] = (len(kd), len(kr))
        for tag, k, alive in (("default", kd, alive_d),
                              ("randomized", kr, alive_r)):
            print(f"  {tb:9s} {tag:10s} {len(k)}/{n}; survivors:")
            print(textwrap.fill(" ".join(alive), 72,
                                initial_indent="    ",
                                subsequent_indent="    "))
    gained = [m.id for k, m in enumerate(ms, 1)
              if dead(k, "fifth", 0) and not dead(k, "ch09-sva", 0)]
    print("  killed by the fifth and not by the checker as shipped:")
    print(textwrap.fill(" ".join(gained), 72, initial_indent="    ",
                        subsequent_indent="    "))
    C.pin("source kills", src, {"ch09-sva": (22, 23),
                                "fifth": (37, 40)})

    print("3. netlist sample: 1,000 mutations, uniform, seed 1")
    B.mkdir(parents=True, exist_ok=True)
    cmds, _ = yosysmut.population(B)
    draw = yosysmut.uniform(len(cmds) - 1, 1000, 1)
    net = yosysmut.select_netlist([cmds[k] for k in sorted(draw)],
                                  B / "fifo_mut.v")
    nd = yosysmut.build_netlist(B / "net", net, NAMES, tbs=TBS)
    v = yosysmut.run_netlist(nd, [0] + draw, tbs=TBS)
    C.pin("netlist control", [v[(0, tb)] for tb in NAMES],
          ["survived"] * 2)
    net_k = {}
    for tb in NAMES:
        k = sum(v[(j, tb)] in mutlib.DEAD for j in draw)
        net_k[tb] = k
        print(f"  {tb:9s} {mutlib.fmt_cp(k, 1000)}")
    C.pin("netlist kills", net_k, {"ch09-sva": 39, "fifth": 899})

    print("4. kills at the ports: the fifth testbench with Sync_A tied to")
    print("   the checker's own count (fifo_port_bind.sv)")
    pd, _ = srcmut.build_schema(B / "ports", ["ports"], tbs=PORTS)
    pj = [(k, s) for k in range(n + 1) for s in [0] + list(SEEDS)]
    pr = dict(zip(pj, mutlib.pmap(lambda j: mutlib.run(
        "ports", pd["ports"], [f"+mut={j[0]}"],
        runs=None if j[1] == 0 else rnd(j[1]), tbs=PORTS)[0], pj)))
    C.pin("ports control", [pr[(0, s)] for s in [0] + list(SEEDS)],
          ["survived"] * 6)
    ne = len(ms) - len(EQUIV)
    port = {}
    for tag, seeds in (("default", [0]), ("randomized", SEEDS)):
        k = [m.id for i, m in enumerate(ms, 1)
             if any(pr[(i, s)] in mutlib.DEAD for s in seeds)]
        alive = [m.id for m in ms if m.id not in k]
        kne = len([x for x in k if x not in EQUIV])
        port[tag] = (len(k), kne)
        print(f"  {tag:10s} {len(k)}/{n} at the ports; non-equivalent "
              f"killed {kne}/{ne}")
        print(textwrap.fill("survivors: " + " ".join(alive), 72,
                            initial_indent="    ",
                            subsequent_indent="      "))
    wb = [m.id for i, m in enumerate(ms, 1)
          if dead(i, "fifth", 0) and pr[(i, 0)] not in mutlib.DEAD]
    print(f"  killed only by the white-box Sync_A: {' '.join(wb)}")
    C.pin("port kills", port, {"default": (36, 36),
                               "randomized": (39, 39)})
    C.pin("white-box only", wb, ["m44"])

    rows = []
    for tb, label in (("ch09-sva", "the checker as shipped"),
                      ("fifth", "the checker plus the data check")):
        lo, hi = mutlib.cp(net_k[tb], 1000)
        rows.append([label, f"{src[tb][0]} of 44", f"{src[tb][1]} of 44",
                     f"{net_k[tb]} of 1000 [{lo:.3f}, {hi:.3f}]"])
    mutlib.table_md(
        HERE / "tbl-ch25-report.md",
        ["testbench (traffic of tb_fifo_sva.sv)", "source, default",
         "source, randomized", "netlist sample, 95% interval"], rows,
        "Kills before and after the data check: 44 source mutants at "
        "default and randomized initial values (seeds 1-5), and a "
        "uniform sample of 1,000 netlist mutations (seed 1) "
        "{#tbl-ch25-report}", widths=[18, 10, 10, 18])
    C.report()
    print(f"verdict: the data check raises the source kills from "
          f"{src['ch09-sva'][0]} to {src['fifth'][0]} of 44")


if __name__ == "__main__":
    main()
