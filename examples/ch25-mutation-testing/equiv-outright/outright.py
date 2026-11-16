"""outright.py -- two source mutants that are equivalent outright:
no input sequence from any state tells them from the repaired FIFO.

    python3 outright.py

  m32  the case's default `count <= count;` deleted: a clocked block
       holds its value anyway when no branch assigns it;
  m36  `count <= '0` for `count == '0`: on an unsigned count the two
       are the same test.

For each, the miter of common/miter.py by bounded search (3 s: no
difference found, which decides nothing) and then by rIC3's IC3,
whose proof is the equivalence. The two mutants run side by side.
Selects ric3-ic3, so it needs rIC3. About 25 seconds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
IDS = ["m32", "m36"]


def main():
    C = mutlib.Checks()
    mutlib.need("informal", "ric3")
    print(f"tools: {mutlib.version('informal')}, rIC3 as ric3-ic3")
    print(miter.show_eq())
    ms = {m.id: m for m in srcmut.mutants()}
    res = mutlib.pmap(lambda i: miter.bmc_then_ric3(
        miter.rename(srcmut.single(ms[i]), B / i), B / i), IDS)
    for i, runs in zip(IDS, res):
        print(srcmut.describe(ms[i]))
        for (e, st, d), lim in zip(runs, ["3s", "120s"]):
            print(f"  {miter.say(e, st, d, lim)}")
        C.pin(f"{i} runs", [(e, st) for e, st, _ in runs],
              [("informal-bmc", "undetermined"), ("ric3-ic3", "proven")])
        if runs[-1][1] == "proven":
            print(f"miter: {i} proved equivalent (ric3-ic3)")
    C.report()
    print("verdict: m32 and m36 are equivalent outright")


if __name__ == "__main__":
    main()
