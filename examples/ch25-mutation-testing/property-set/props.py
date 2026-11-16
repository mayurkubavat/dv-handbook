"""props.py -- the formal property set as a fifth judge of the 44
source mutants.

    python3 props.py             stop at the first kill (about 60 s)
    MEASURE=1 python3 props.py   also every property on every mutant,
                                 5 s each, into measure.out (several
                                 minutes)

The set is the formal-techniques chapter's (common/miter.py): the
temporal-properties chapter's checker bound as it ships, the pointer
property EmptyPtrs_A and the tracked-word check a_integrity. For each
mutant, and for the repaired FIFO as the control, the properties are
tried one at a time in a fixed order by bounded model checking, 2 s
each, and the run stops at the first counterexample. A mutant with no
counterexample to any property in that bound has not been killed; it
has not been shown to survive either, which only a proof could show
(the miter examples). A mutant the tool's front end refuses is
counted apart, as a kill by the tool, not a counterexample. The
default run cross-checks its first kills against the committed
measure.out: each must be among the properties the full run refuted.
"""
import datetime
import os
import pathlib
import sys
import textwrap
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
LIMIT = "2s"
# SHA-256 of the committed measure.out: the chapter prints which
# properties kill which mutants from it, and the default run re-derives
# only the first kill, so an edit to any other line fails here. A
# MEASURE=1 run prints the new digest to put here.
MEASURE_SHA = "f746f3a14e5f39ad08810eacbd0761121e4894523c9b9df98330bf0f5fbbfebd"


def design(name, text):
    d = B / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "fifo.sv").write_text(text)
    return d


def first_kill(arg):
    name, text = arg
    d = design(name, text)
    rc, out = miter.shell(miter.kill_first_tcl([d / "fifo.sv"], LIMIT),
                          d / "k")
    got = miter.first(out)
    if got[0] == "refused":
        return "refused", miter.refusal(out)
    return got


def all_props(arg):
    name, text = arg
    d = design(name, text)
    rc, out = miter.shell(miter.kill_all_tcl([d / "fifo.sv"], "5s"),
                          d / "a")
    why = miter.refusal(out)
    if why:
        return "refused " + why
    r = miter.rows(out)
    cex = [f"{p}@{dep}" for p, (s, dep) in r.items() if s == "cex"]
    return ",".join(cex) or "-"


def measure(jobs):
    t0 = time.time()
    res = mutlib.pmap(all_props, jobs)
    lines = [f"measure.out -- written by MEASURE=1 make run on "
             f"{datetime.date.today().isoformat()}",
             f"tools: {mutlib.version('informal')}",
             "every property of the set on every mutant, informal-bmc, "
             "5 s each;",
             f"wall {time.time() - t0:.0f} s on 4 workers",
             "mutant: the properties refuted, at their depths"]
    for (n, _), r in zip(jobs, res):
        lines += textwrap.wrap(f"{n} {r.replace(',', ', ')}", 72,
                               initial_indent="  ",
                               subsequent_indent="       ",
                               break_on_hyphens=False)
    (HERE / "measure.out").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def committed():
    rows = {}
    path = HERE / "measure.out"
    key = None
    if path.exists():
        for line in path.read_text().splitlines():
            p = line.split(None, 1)
            if line.startswith("       ") and key:
                rows[key] += " " + line.strip()
            elif len(p) == 2 and (p[0] == "orig" or p[0][1:].isdigit()):
                key = p[0]
                rows[key] = p[1]
            else:
                key = None
    return rows


def main():
    C = mutlib.Checks()
    mutlib.need("informal")
    ms = srcmut.mutants()
    print(f"tools: {mutlib.version('informal')}")
    print(f"property set, in the order tried: {' '.join(miter.PROPS[:4])}")
    print(f"  {' '.join(miter.PROPS[4:])}")
    print(f"each by informal-bmc, {LIMIT} for each property; stop at the "
          "first counterexample")
    jobs = [("orig", (mutlib.ROOT / mutlib.FIXED).read_text())]
    jobs += [(m.id, srcmut.single(m)) for m in ms]
    res = dict(zip([n for n, _ in jobs], mutlib.pmap(first_kill, jobs)))
    p, d = res["orig"]
    print(f"control (the repaired FIFO): "
          f"{'no counterexample' if p == '-' else p}")
    C.pin("control", p, "-")
    cex, refused, none = [], [], []
    for m in ms:
        p, d = res[m.id]
        if p == "refused":
            refused.append(m.id)
            print("  " + mutlib.wrap(f"{m.id} {m.op}  refused by the front "
                                     f"end, {d}", "    "))
        elif p == "-":
            none.append(m.id)
            print(f"  {m.id} {m.op}  no counterexample in {LIMIT} for any "
                  "property")
        else:
            cex.append(m.id)
            print(f"  {m.id} {m.op}  killed by {p} at depth {d}")
    print(f"counterexamples: {len(cex)} of {len(ms)}; refused by the "
          f"front end: {len(refused)} ({' '.join(refused)})")
    print(f"no counterexample: {len(none)} ({' '.join(none)})")
    sync = [k for k in cex if res[k][0] == "Sync_A"]
    print(f"killed first by Sync_A: {' '.join(sync)}")
    C.pin("counterexamples", len(cex), 38)
    C.pin("refused", refused, ["m06", "m07"])
    C.pin("no counterexample", none, ["m05", "m32", "m36", "m43"])
    C.pin("m44 killed by", res["m44"][0], "Sync_A")
    if os.environ.get("MEASURE") == "1":
        measure(jobs)
    full = committed()
    agree = sum(1 for k in cex if f"{res[k][0]}@" in full.get(k, ""))
    agree += sum(1 for k in none if full.get(k) == "-")
    agree += sum(1 for k in refused
                 if full.get(k, "").startswith("refused"))
    print(f"the full run (committed measure.out) agrees on {agree} of "
          f"{len(ms)} mutants")
    C.pin("agreement with measure.out", agree, len(ms))
    mutlib.pin_measured(C, HERE / "measure.out", MEASURE_SHA)
    C.report()
    print("verdict: the property set kills every non-equivalent mutant")


if __name__ == "__main__":
    main()
