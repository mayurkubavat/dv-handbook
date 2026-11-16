"""whitebox.py -- an equivalent mutant that a white-box assertion
kills: m44, the counter's case labels 2'b10 and 2'b01 exchanged, so a
push decrements count and a pop increments it.

    python3 whitebox.py

1. The miter of common/miter.py: bounded search (3 s), then rIC3's
   IC3. At the ports the mutant is the repaired FIFO: its count holds
   minus the occupancy modulo 32, and full and empty test only 0 and
   16, the two values negation modulo 32 leaves where they are.
2. The property set of common/miter.py on m44, every property by
   bounded search for 2 s: Sync_A, which compares the checker's
   occupancy with the design's internal count, fails; no other
   property does within the bound.
3. The count itself, from a short simulation of the source schema
   (tb_count.sv): three pushes, a pop and an idle cycle, for the
   repaired FIFO and for m44.
Selects ric3-ic3, so it needs rIC3. About 30 seconds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
TB = {"count": ([f"{mutlib.CH}/white-box/tb_count.sv"], "tb_count", [],
                [[]], "PASS")}


def props(m):
    d = B / "props"
    d.mkdir(parents=True, exist_ok=True)
    (d / "fifo.sv").write_text(srcmut.single(m))
    rc, out = miter.shell(miter.kill_all_tcl([d / "fifo.sv"], "2s"),
                          d / "k")
    return miter.rows(out)


def main():
    C = mutlib.Checks()
    mutlib.need("informal", "ric3")
    print(f"tools: {mutlib.version('informal')}, rIC3 as ric3-ic3; "
          f"{mutlib.version('verilator')}")
    ms = srcmut.mutants()
    m = ms[43]
    C.pin("m44 is the case-label exchange", (m.id, m.op), ("m44", "CSW"))
    print(srcmut.describe(m))
    f = miter.rename(srcmut.single(m), B / "miter")
    eq, pr = mutlib.pmap(lambda job: job(), [
        lambda: miter.bmc_then_ric3(f, B / "miter"), lambda: props(m)], 2)
    print(miter.show_eq(lead="1. miter compares: "))
    for (e, st, d), lim in zip(eq, ["3s", "120s"]):
        print(f"  {miter.say(e, st, d, lim)}")
    C.pin("miter runs", [(e, st) for e, st, _ in eq],
          [("informal-bmc", "undetermined"), ("ric3-ic3", "proven")])
    if eq[-1][1] == "proven":
        print("miter: m44 proved equivalent (ric3-ic3) at the ports")
    print("2. the property set on m44, informal-bmc, 2s for each")
    for p in miter.PROPS:
        st, d = pr[p]
        print(f"  {p:15s} " + (f"counterexample at depth {d}"
                               if st == "cex" else "no counterexample"))
    C.pin("refuted", [p for p in miter.PROPS if pr[p][0] == "cex"],
          ["Sync_A"])
    C.pin("Sync_A depth", pr["Sync_A"][1], 2)
    print("3. count, full and empty after each clock edge")
    dirs, _ = srcmut.build_schema(B / "sim", ["count"], tbs=TB)
    traces = {}
    for k, name in ((0, "repaired FIFO"), (44, "m44")):
        v, _, out = mutlib.run("count", dirs["count"], [f"+mut={k}"],
                               tbs=TB)
        print(f"  {name}:")
        lines = [x for x in out.splitlines() if "count=" in x]
        print("\n".join(lines))
        traces[k] = [int(x.split("count=")[1].split()[0]) for x in lines]
        C.pin(f"{name} trace ran", v, "survived")
    C.pin("repaired count", traces[0], [0, 1, 2, 3, 2, 2])
    C.pin("m44 count", traces[44], [0, 31, 30, 29, 30, 30])
    C.report()
    print("verdict: m44 is equivalent at the ports and killed by Sync_A")


if __name__ == "__main__":
    main()
