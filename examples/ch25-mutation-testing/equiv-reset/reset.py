"""reset.py -- a mutant equivalent only under the tool's reset model:
m05, the asynchronous reset made synchronous (`or negedge rst_n`
dropped from the sensitivity list).

    python3 reset.py

1. The miter of common/miter.py by bounded search (3 s) and by rIC3's
   IC3, then the tool's reset model measured on the same miter: a
   cover of !rst_n and an assertion of rst_n. The tool applies the
   reset at the start of every trace and holds rst_n high after it,
   so no trace has a second reset, and the one input on which the two
   designs differ, a reset that falls between clock edges, never
   occurs.
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


# The reset model as a measurement: after the tool's reset, can rst_n
# ever be low again?
PROBES = [("C_second_reset", "cover", "!rst_n"),
          ("A_reset_released", "assert", "rst_n")]


def reset_model(mutant, work):
    """{probe: (status, depth)} of PROBES on the miter, by rIC3."""
    tcl = (miter.head() + "design [list "
           + " ".join(map(str, [mutlib.ROOT / mutlib.FIXED, mutant,
                                miter.MITER])) + "] miter\n"
           + "".join(f"{k} -name {n} {{{e}}}\n" for n, k, e in PROBES)
           + "one ric3-ic3 60s -all\n"
           + miter.ROWS.replace(" -include {type assert}", "")
           + "finish\n")
    return miter.rows(miter.shell(tcl, work)[1])


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
    print("   the reset model, on the same miter after its reset:")
    rm = reset_model(miter.rename(srcmut.single(m), B / "f"), B / "rm")
    for name, kind, expr in PROBES:
        print(f"  {kind} {{{expr}}}: {rm[name][0]} (ric3-ic3)")
    C.pin("reset model", [rm[n][0] for n, _, _ in PROBES],
          ["unreachable", "proven"])
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
