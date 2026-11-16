"""differ.py -- the miter refutes: every source mutant that differs
from the repaired FIFO at the ports, found by bounded model checking
with the depth of the shortest trace that tells them apart.

    python3 differ.py

For each of the 44 mutants, the miter of common/miter.py (full and
empty compared always, rd_data whenever the original is not empty),
proved by informal-bmc with 10 s. Three outcomes: a counterexample at
some depth (the mutant is not equivalent: the trace is a test that
kills it); the front end refuses the mutant (m06, m07); or no
counterexample in the limit, which bounded search can never turn into
a proof (the equiv-* and white-box examples prove those with rIC3).

Last, the comparison the miter does not make: rd_data on every cycle,
the original FIFO against an unmutated copy of itself. About 20
seconds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
LIMIT = "10s"
# Depth of the shortest distinguishing trace, from the research run.
WANT = dict(zip(
    "m01 m02 m03 m04 m08 m09 m10 m11 m12 m13 m14 m15 m16 m17 m18 m19 "
    "m20 m21 m22 m23 m24 m25 m26 m27 m28 m29 m30 m31 m33 m34 m35 m37 "
    "m38 m39 m40 m41 m42".split(),
    [2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 3, 3, 3, 3, 4, 2, 3, 3, 3, 3,
     3, 3, 2, 3, 3, 3, 2, 1, 1, 1, 2, 1, 1, 1, 17]))


def job(m):
    f = miter.rename(srcmut.single(m), B / m.id)
    (st, d), out = miter.miter(f, B / m.id, "informal-bmc", LIMIT)
    if st == "error":
        return "refused", miter.refusal(out)
    return st, d


def main():
    C = mutlib.Checks()
    mutlib.need("informal")
    print(f"tools: {mutlib.version('informal')}")
    print(miter.show_eq())
    print(f"engine: informal-bmc, limit {LIMIT} for each mutant")
    ms = srcmut.mutants()
    res = dict(zip([m.id for m in ms], mutlib.pmap(job, ms)))
    differ, refused, open_ = {}, [], []
    for m in ms:
        st, d = res[m.id]
        if st == "cex":
            differ[m.id] = d
            print(f"miter: {m.id} differs at depth {d}")
        elif st == "refused":
            refused.append(m.id)
            print(mutlib.wrap(f"front end refuses {m.id}, {d}"))
        else:
            open_.append(m.id)
            print(f"  {m.id} no difference found in {LIMIT}: bounded "
                  "search cannot decide it")
    deep = max(differ, key=differ.get)
    print(mutlib.wrap(f"differ: {len(differ)}, depths "
                      f"{min(differ.values())} to {max(differ.values())} "
                      f"(deepest {deep}); refused: {' '.join(refused)}; "
                      f"undecided: {' '.join(open_)}"))
    C.pin("depths", differ, WANT)
    C.pin("refused", refused, ["m06", "m07"])
    C.pin("undecided", open_, ["m05", "m32", "m36", "m43", "m44"])

    # The comparison the miter leaves out: rd_data on every cycle,
    # the original against an unmutated copy of itself.
    same = miter.rename(mutlib.ROOT.joinpath(mutlib.FIXED).read_text(),
                        B / "self")
    eq = "full_a == full_b && empty_a == empty_b && rd_a == rd_b"
    (st, d), _ = miter.miter(same, B / "self", "informal-bmc", LIMIT, eq)
    print(f"rd_data compared on every cycle, the original against "
          f"itself: {'differs at depth %d' % d if st == 'cex' else st}")
    C.pin("self-miter on every cycle", (st, d), ("cex", 1))
    C.report()
    print(f"verdict: {len(differ)} mutants differ; bounded search "
          "decides none of the other five")


if __name__ == "__main__":
    main()
