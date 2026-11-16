"""sim.py -- the 44 source mutants of the repaired FIFO against the
book's four FIFO testbenches: the kill matrix.

    python3 sim.py              the schema run (about 40 seconds)
    MEASURE=1 python3 sim.py    also one build for every mutant and
                                testbench (180 builds, several
                                minutes), written to measure.out

The default run builds the source schema (common/srcmut.py) once for
each testbench and runs it 45 times, +mut=0 being the repaired FIFO,
the control every testbench must pass. Then Chapter 1's random test
alone on mutant m35 under seeds 1 to 100, given as its only +seed=,
to find the first seed whose traffic drains the FIFO after the first
push. Last, the matrix the per-mutant builds wrote to the committed
measure.out is compared with the schema's, cell by cell: the schema
is a harness, and the per-mutant builds are what it stands in for.
"""
import datetime
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402

B = HERE / "build"
CODE = {"killed": "K", "timeout": "T", "survived": ".",
        "stillborn": "x"}
# The matrix the research runs measured with one build per mutant;
# K killed, . survived; columns ch01-directed, ch01-random,
# ch08-coverage, ch09-sva.
# The SHA-256 of the committed measure.out; a MEASURE=1 run prints the
# new one to put here.
MEASURE_SHA = "7d94b540d0c3dd33afb9732948f2bd832dd866da6e505eb6a3e9ba0c8868f0d4"
WANT = ("KK.K KK.K KK.K KK.K .... KK.K KK.K KK.. .... KK.. .... .K.K "
        "....  " + "KK.. " * 12 + "KK.K " * 6 + ".... KK.. KK.K K..K "
        ".... " + "KK.K " * 5 + ".K.K .... ...K").split()


def matrix_lines(ms, v):
    rows = []
    for n, m in enumerate(ms, 1):
        rows.append(f"  {m.id} {m.op}  " + " ".join(
            CODE[v[(n, tb)]] for tb in mutlib.NAMES))
    return rows


def summary(ms, v, C, tag):
    n = len(ms)
    kills = {}
    for tb in mutlib.NAMES:
        k = sum(v[(i, tb)] in mutlib.DEAD for i in range(1, n + 1))
        kills[tb] = k
        print(f"  {tb:14s} killed {k:2d} of {n} ({100.0 * k / n:5.1f}%)")
    u = sum(any(v[(i, tb)] in mutlib.DEAD for tb in mutlib.NAMES)
            for i in range(1, n + 1))
    print(f"  {'union':14s} killed {u:2d} of {n} ({100.0 * u / n:5.1f}%)")
    alive = [ms[i - 1].id for i in range(1, n + 1)
             if not any(v[(i, tb)] in mutlib.DEAD for tb in mutlib.NAMES)]
    print(f"  killed by no testbench: {' '.join(alive)}")
    C.pin(f"{tag} kills", [kills[t] for t in mutlib.NAMES] + [u],
          [34, 35, 0, 22, 37])
    C.pin(f"{tag} survivors", alive,
          ["m05", "m09", "m11", "m13", "m32", "m36", "m43"])


def measure(ms, C):
    """One build for every (mutant, testbench), as the research ran
    it: the slow harness the schema replaces."""
    t0 = time.time()
    src = B / "single"
    os.makedirs(src, exist_ok=True)
    designs = {0: mutlib.FIXED}
    for n, m in enumerate(ms, 1):
        p = src / f"{m.id}.sv"
        p.write_text(srcmut.single(m))
        designs[n] = p

    def job(j):
        n, tb = j
        mdir = B / "obj" / f"{n}-{tb}"
        ok, bt, _ = mutlib.build(tb, [designs[n]], mdir, ["-Wno-fatal"])
        v = mutlib.run(tb, mdir)[0] if ok else "stillborn"
        os.system(f"rm -rf {mdir}")
        return v, bt

    jobs = [(n, tb) for n in designs for tb in mutlib.NAMES]
    res = mutlib.pmap(job, jobs)
    v = {j: r[0] for j, r in zip(jobs, res)}
    btime = sum(r[1] for r in res)
    lines = [f"measure.out -- written by MEASURE=1 make run on "
             f"{datetime.date.today().isoformat()}",
             f"tools: {mutlib.version('verilator')}",
             mutlib.wrap(f"builds: {len(jobs)}, one for each mutant and"
                         f" testbench; build time {btime:.0f} s summed"
                         f" over 4 workers, wall {time.time() - t0:.0f} s"),
             mutlib.wrap("control: " + ", ".join(
                 f"{tb} {v[(0, tb)]}" for tb in mutlib.NAMES)),
             "per-mutant matrix (K killed, . survived):"]
    lines += matrix_lines(ms, v)
    (HERE / "measure.out").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return v


def committed(ms):
    """The matrix rows of the committed measure.out."""
    rows = {}
    if not (HERE / "measure.out").exists():
        return rows
    for line in (HERE / "measure.out").read_text().splitlines():
        p = line.split()
        if len(p) == 6 and p[0].startswith("m") and p[0][1:].isdigit():
            rows[p[0]] = "".join(p[2:])
    return rows


def main():
    C = mutlib.Checks()
    ms = srcmut.mutants()
    print(f"tools: {mutlib.version('verilator')}")
    print(f"design: {mutlib.FIXED}, {len(ms)} source mutants")
    print("testbenches: " + ", ".join(mutlib.NAMES))
    print("  (ch01-random at +seed=1, 400 cycles, this chapter's copy)")
    dirs, warn = srcmut.build_schema(B, mutlib.NAMES)
    print(f"schema: one build for each testbench; warnings it draws: "
          f"{', '.join(warn)}")
    v = srcmut.run_schema(dirs, range(len(ms) + 1))
    ctrl = [v[(0, tb)] for tb in mutlib.NAMES]
    print(mutlib.wrap("control (+mut=0, the repaired FIFO): " + ", ".join(
        f"{tb} {c}" for tb, c in zip(mutlib.NAMES, ctrl))))
    C.pin("control", ctrl, ["survived"] * 4)
    print("kill matrix (K killed, . survived); columns")
    print("  " + " ".join(mutlib.NAMES))
    rows = matrix_lines(ms, v)
    print("\n".join(rows))
    got = ["".join(r.split()[2:]) for r in rows]
    C.pin("schema matrix equals the research's per-mutant matrix",
          got, WANT)
    print("schema kills:")
    summary(ms, v, C, "schema")

    # m35, empty stuck low: the first seed of the random test that
    # kills it. Each seed is the run's only +seed= plusarg.
    m35 = [m.id for m in ms].index("m35") + 1
    seeds = range(1, 101)
    res = mutlib.pmap(lambda s: mutlib.run(
        "ch01-random", dirs["ch01-random"], [f"+mut={m35}"],
        runs=[[f"+seed={s}"]])[0], seeds)
    kill = [s for s, r in zip(seeds, res) if r in mutlib.DEAD]
    print(f"m35 under ch01-random, seeds 1-100: first killing seed "
          f"{kill[0]};")
    print(f"  killed by {len(kill)} of 100 seeds")
    C.pin("m35 first killing seed", kill[0], 2)

    if os.environ.get("MEASURE") == "1":
        measure(ms, C)
    per = committed(ms)
    same = sum(per.get(m.id) == g for m, g in zip(ms, got))
    print(f"per-mutant builds (committed measure.out) agree with the "
          f"schema on")
    print(f"  {same} of {len(ms)} mutants")
    C.pin("per-mutant agreement", same, len(ms))
    # The cost lines and the control cannot be re-derived from a
    # default run, so the whole committed file is pinned.
    mutlib.pin_measured(C, HERE / "measure.out", MEASURE_SHA)
    C.report()
    print("verdict: the schema reproduces the per-mutant kill matrix")


if __name__ == "__main__":
    main()
