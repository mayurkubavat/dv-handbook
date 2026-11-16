"""pitfalls.py -- two ways a mutation harness changes the score by
itself, each shown on the smallest case that has it.

    python3 pitfalls.py

(a) A harness that kills. Yosys writes each $pmux of a netlist as a
    casez with a "synopsys parallel_case" pragma, and Verilator turns
    that pragma into an assertion. Two netlist mutations force a
    select bit of the counter's case to 1 (const1 on the S port of the
    $pmux built from line 49 of fifo_fixed.sv), so two items match at
    once. The coverage chapter's testbench, which has no checker, is
    built against a netlist holding them twice: without and with
    --no-assert-case.
(b) A harness that hides kills. tb_plusarg.sv shows which value
    $value$plusargs returns for a plusarg given twice. Then the first
    chapter's random test on source mutant m35 (empty stuck low), from
    the source schema: +seed=2 alone, and +seed=1 followed by +seed=2,
    the command line a sweep makes when it appends its seed to the
    testbench's own.
Yosys and Verilator; about 20 seconds.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import yosysmut  # noqa: E402

B = HERE / "build"
PLUS = {"plusarg": ([f"{mutlib.CH}/harness-pitfalls/tb_plusarg.sv"],
                    "tb_plusarg", [], [[]], None)}


def why(out):
    m = re.search(r"Assertion failed in [^:]*: (.*)", out)
    return m.group(1) if m else ""


def main():
    C = mutlib.Checks()
    mutlib.need("yosys")
    print(f"tools: {mutlib.version('yosys')}; "
          f"{mutlib.version('verilator')}")
    B.mkdir(parents=True, exist_ok=True)
    cmds, _ = yosysmut.population(B)
    ks = [k for k, c in enumerate(cmds) if "-mode const1" in c
          and "-cell $procmux$" in c and "-port S " in c
          and "fifo_fixed.sv:49." in c]
    print("(a) select-bit mutations of the counter's $pmux (const1, "
          f"port S): {' '.join(map(str, ks))}")
    C.pin("mutations found", ks, [7572, 7576])
    net = yosysmut.select_netlist([cmds[k] for k in ks], B / "fifo_mut.v")
    loose = [f for f in yosysmut.NET_FLAGS if f != "--no-assert-case"]
    got = {}
    for tag, flags in (("default flags", loose),
                       ("--no-assert-case", yosysmut.NET_FLAGS)):
        d = yosysmut.build_netlist(B / tag.split()[0].strip("-"), net,
                                   ["ch08-coverage"], flags=flags)
        for k in [0] + ks:
            v, _, out = mutlib.run("ch08-coverage", d["ch08-coverage"],
                                   [f"+mut={k}"])
            got[(tag, k)] = v
            print(f"  {tag:16s} mutation {k:4d} under ch08-coverage: {v}")
            if why(out):
                print(f"    {why(out)}")
    C.pin("pragma kills", [got[("default flags", k)] for k in [0] + ks],
          ["survived", "killed", "killed"])
    C.pin("no pragma kills", [got[("--no-assert-case", k)]
                              for k in [0] + ks], ["survived"] * 3)

    print("(b) a plusarg given twice")
    d = B / "plusarg"
    ok, _, log = mutlib.build("plusarg", [], d, tbs=PLUS)
    assert ok, log[-2000:]
    _, _, out = mutlib.run("plusarg", d, ["+seed=1", "+seed=7"], tbs=PLUS)
    line = out.strip().splitlines()[0]
    print(f"  +seed=1 +seed=7: {line}")
    C.pin("first match wins", line.endswith("returned 1"), True)
    dirs, _ = srcmut.build_schema(B / "schema", ["ch01-random"])
    m35 = [m.id for m in srcmut.mutants()].index("m35") + 1
    res = {}
    for args in (["+seed=2"], ["+seed=1", "+seed=2"]):
        v, _, _ = mutlib.run("ch01-random", dirs["ch01-random"],
                             [f"+mut={m35}"], runs=[args])
        res[" ".join(args)] = v
        print(f"  ch01-random on m35 with {' '.join(args):15s}: {v}")
    C.pin("sweep hides the kill", res, {"+seed=2": "killed",
                                        "+seed=1 +seed=2": "survived"})
    C.report()
    print("verdict: the pragma assertion kills in a checkless testbench,")
    print("  and a second +seed= is ignored")


if __name__ == "__main__":
    main()
