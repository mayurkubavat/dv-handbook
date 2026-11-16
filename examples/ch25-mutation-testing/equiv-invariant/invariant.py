"""invariant.py -- a mutant equivalent only on the reachable states:
m43, `full` raised at `count >= 16` instead of `count == 16`. The two
agree because the count never exceeds 16, which is a fact about the
states reset can reach, not about every state.

    python3 invariant.py

Six runs on the miter of common/miter.py (or on part of it), each in
a session of its own:
  1. bounded search, 3 s: no difference, and none can ever prove it;
  2. k-induction on the whole miter, 10 s;
  3. the helper count <= 16, on both copies, proved by k-induction;
  4. k-induction on the whole miter with that helper assumed, 10 s;
  5. k-induction on the flag half alone (full and empty compared,
     rd_data not), with no helper;
  6. rIC3's IC3 on the whole miter, which finds its own invariant.
The runs go four at a time. Selects ric3-ic3, so it needs rIC3. About
30 seconds.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
HELP = "a.count <= 5'd16 && b.count <= 5'd16"
FLAGS = "full_a == full_b && empty_a == empty_b"
RUNS = [  # (name, what, assumption, assertion, engine, limit, wanted)
    ("bmc", "bounded search, whole miter", None, miter.EQ,
     "informal-bmc", "3s", "undetermined"),
    ("kind", "k-induction, whole miter", None, miter.EQ,
     "informal-kind", "10s", "undetermined"),
    ("helper", "k-induction, the helper count <= 16 on both copies",
     None, HELP, "informal-kind", "10s", "proven"),
    ("kind_h", "k-induction, whole miter, helper assumed", HELP,
     miter.EQ, "informal-kind", "10s", "undetermined"),
    ("flags", "k-induction, flag half only, no helper", None, FLAGS,
     "informal-kind", "10s", "proven"),
    ("ric3", "rIC3's IC3, whole miter", None, miter.EQ, "ric3-ic3",
     "120s", "proven"),
]


def run(spec, mutant):
    name, _, assume, prop, engine, limit, _ = spec
    tcl = (miter.head() + "design [list "
           + " ".join(map(str, [mutlib.ROOT / mutlib.FIXED, mutant,
                                miter.MITER])) + "] miter\n"
           + (f"assume -name H {{{assume}}}\n" if assume else "")
           + f"assert -name P_A {{{prop}}}\n"
           + f"one {engine} {limit} -all\n" + miter.ROWS + "finish\n")
    rc, out = miter.shell(tcl, B / name)
    return miter.rows(out).get("P_A", ("error", -1))


def main():
    C = mutlib.Checks()
    mutlib.need("informal", "ric3")
    print(f"tools: {mutlib.version('informal')}, rIC3 as ric3-ic3")
    m = {m.id: m for m in srcmut.mutants()}["m43"]
    print(srcmut.describe(m))
    print(miter.show_eq())
    print(f"helper: {HELP}")
    f = miter.rename(srcmut.single(m), B)
    res = mutlib.pmap(lambda s: run(s, f), RUNS)
    for k, (spec, (st, d)) in enumerate(zip(RUNS, res), 1):
        _, what, _, _, engine, limit, want = spec
        shown = {"proven": "proven", "undetermined":
                 f"no verdict in {limit}",
                 "cex": f"differs at depth {d}"}.get(st, st)
        print(f"  {k}. {what} ({engine}): {shown}")
        C.pin(f"run {k}", st, want)
    if res[-1][0] == "proven":
        print("miter: m43 proved equivalent (ric3-ic3)")
    C.report()
    print("verdict: m43 is equivalent on the reachable states; rIC3 "
          "proves it")


if __name__ == "__main__":
    main()
