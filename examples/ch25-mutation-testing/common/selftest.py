"""selftest.py -- the chapter's shared Python checks itself.

    python3 selftest.py

1. srcmut.py makes 44 mutants from fifo_fixed.sv, each changing what
   it says it changes, and a schema whose +mut=0 is the repaired FIFO:
   all four testbenches built against the schema pass it.
2. The Clopper-Pearson interval comes from the statistics chapter's
   library by path; one value the sampling section prints is checked.
3. yosysmut.py parses a `mutate -list` line as the population file
   records it.
About fifteen seconds: four Verilator builds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import yosysmut  # noqa: E402

C = mutlib.Checks()
print(f"tools: {mutlib.version('verilator')}")
ms = srcmut.mutants()
print(f"1. srcmut: {len(ms)} mutants of {mutlib.FIXED}")
C.pin("mutant count", len(ms), 44)
src = srcmut.source()
changed = [sum(a != b for a, b in zip(src, m.body)) for m in ms]
C.pin("lines each mutant changes", sorted(set(changed)), [1, 2])
C.pin("the one mutant that changes two lines", [m.id for m, c in
                                              zip(ms, changed) if c == 2],
      ["m44"])
dirs, _ = srcmut.build_schema(HERE / "build", mutlib.NAMES)
v = srcmut.run_schema(dirs, [0])
for tb in mutlib.NAMES:
    print(f"  schema +mut=0 under {tb}: {v[(0, tb)]}")
C.pin("schema control", [v[(0, tb)] for tb in mutlib.NAMES],
      ["survived"] * 4)
print(f"2. Clopper-Pearson 95%, 30 of 100: "
      f"[{mutlib.cp(30, 100)[0]:.3f}, {mutlib.cp(30, 100)[1]:.3f}]")
C.pin("CP(30, 100)", tuple(round(x, 3) for x in mutlib.cp(30, 100)),
      (0.212, 0.400))
line = ("mutate -ctrl mutsel 14 2 -mode const0 -module fifo -cell "
        "$add$examples/ch09-temporal-properties/rtl/fifo_fixed.sv:44$15 "
        "-port A -portbit 0 -src "
        "examples/ch09-temporal-properties/rtl/fifo_fixed.sv:44.24-44.37")
print(f"3. yosysmut.parse: {yosysmut.parse(line)}")
C.pin("parse", yosysmut.parse(line), ("const0", "44", "add"))
C.report()
print("self-test: the shared library holds")
