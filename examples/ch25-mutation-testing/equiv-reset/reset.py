"""reset.py -- a mutant equivalent only under the tool's reset model:
m05, the asynchronous reset made synchronous (`or negedge rst_n`
dropped from the sensitivity list).

    python3 reset.py

1. The miter of common/miter.py by bounded search (3 s) and by rIC3's
   IC3. The formal tool models an asynchronous reset as one seen at
   the clock, so under its model the two designs are the same.
2. The source schema under tb_async_reset.sv, a testbench that drops
   rst_n between two clock edges and reads empty before the next one:
   the repaired FIFO (+mut=0) and m05.
Selects ric3-ic3, so it needs rIC3; the simulation half needs
Verilator. About 30 seconds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
TB = {"async-reset": ([f"{mutlib.CH}/equiv-reset/tb_async_reset.sv"],
                      "tb_async_reset", [], [[]], "PASS")}


def main():
    C = mutlib.Checks()
    mutlib.need("informal", "ric3")
    print(f"tools: {mutlib.version('informal')}, rIC3 as ric3-ic3; "
          f"{mutlib.version('verilator')}")
    ms = srcmut.mutants()
    m = ms[4]
    C.pin("m05 is the reset mutant", (m.id, m.op), ("m05", "ARS"))
    print(srcmut.describe(m))
    print(miter.show_eq(lead="1. miter compares: "))
    runs = miter.bmc_then_ric3(miter.rename(srcmut.single(m), B / "f"),
                               B / "f")
    for (e, st, d), lim in zip(runs, ["3s", "120s"]):
        print(f"  {miter.say(e, st, d, lim)}")
    C.pin("miter runs", [(e, st) for e, st, _ in runs],
          [("informal-bmc", "undetermined"), ("ric3-ic3", "proven")])
    if runs[-1][1] == "proven":
        print("miter: m05 proved equivalent (ric3-ic3) under the tool's "
              "reset model")
    print("2. simulation: rst_n dropped and raised between two edges")
    dirs, _ = srcmut.build_schema(B / "sim", ["async-reset"], tbs=TB)
    got = {}
    for k, name in ((0, "repaired FIFO"), (5, "m05")):
        v, _, out = mutlib.run("async-reset", dirs["async-reset"],
                               [f"+mut={k}"], tbs=TB)
        line = next(x for x in out.splitlines() if x.startswith("after"))
        got[k] = v
        print(f"  {name:13s} {line}: {v}")
    C.pin("simulation verdicts", (got[0], got[5]), ("survived", "killed"))
    C.report()
    print("verdict: m05 is equivalent to the tool, and a reset pulse "
          "kills it")


if __name__ == "__main__":
    main()
