"""nformal.py -- the formal half of the netlist population, on a
uniform sample: which sampled mutations are equivalent (the miter),
and which the property set kills.

    python3 nformal.py              recompute and spot-check (about
                                    a minute and a half)
    MEASURE=1 python3 nformal.py    first the whole sample of 100,
                                    into measure.out (several minutes
                                    on four cores)

The sample: 100 mutation numbers drawn uniformly from the 9,281 of
netlist-list/ with Python's generator at seed 25. For each, a netlist
with that one mutation applied (module fifo_m, wrapped as module fifo
by common/fifo_fwrap.sv for the property set):
  property set  every property by bounded search, 3 s each;
  miter         bounded search 10 s, then rIC3's IC3 120 s.
measure.out holds one row for each sampled mutation. From it and the
committed population file the default run recomputes the three
numbers of a sampled population: the kill rate of each testbench over
the sample's non-equivalent mutations, the equivalent fraction, and
the property set's kill rate, each with its 95% Clopper-Pearson
interval; it checks them against the summary measure.out printed;
it lists the non-equivalent mutations the property set missed, with
the depth of the miter's difference and the random test's verdict;
and it reruns four rows by rIC3: two equivalents proved again, and the
two deepest differences found again at the depth recorded. That depth
(31) is the length of rIC3's trace, past what bounded search reached
in its 10 s; an IC3 trace is not always the shortest, so it bounds the
shortest difference from above. Last, it runs a_integrity alone on
each miss with more time (bounded search 30 s, then rIC3 120 s), to
show that each miss is a bound of the 3 s search and not a gap in the
property set. Selects ric3-ic3, so it needs rIC3.
"""
import datetime
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import yosysmut  # noqa: E402
import miter  # noqa: E402

B = HERE / "build"
POP = HERE.parent / "netlist-population" / "pop.tsv"
MEASURE = HERE / "measure.out"
N_SAMPLE, SEED = 100, 25
# SHA-256 of the committed measure.out and population file: an edit to
# any row, depth or cost line fails the default run. A MEASURE=1 run
# prints the new digest of measure.out to put here.
MEASURE_SHA = "3912e3080c76403a115f18b36d47bf89b1101eb118fd864bd948f2dc43dcd61a"
POP_SHA = "4cf0247fe0c8965ca6cd46a102e9802c90e452e661c6f68df65a2ebd5c8f8677"


def one(arg):
    k, cmd = arg
    d = B / str(k)
    d.mkdir(parents=True, exist_ok=True)
    net = yosysmut.single_netlist(cmd, d / "fifo_m.v")
    rc, out = miter.shell(miter.kill_all_tcl([net, miter.FWRAP], "3s"),
                          d / "k")
    r = miter.rows(out)
    cex = ",".join(f"{p}@{dep}" for p, (s, dep) in r.items()
                   if s == "cex") or "-"
    (st, dep), _ = miter.miter(net, d / "bmc", "informal-bmc", "10s")
    if st == "cex":
        verdict = f"differs@{dep}"
    else:
        (st, dep), _ = miter.miter(net, d / "ric3", "ric3-ic3", "120s")
        verdict = {"proven": "equivalent", "cex": f"differs@{dep}"}.get(
            st, "undecided")
    return k, cex, verdict


def sample(cmds):
    return sorted(yosysmut.uniform(len(cmds) - 1, N_SAMPLE, SEED))


def summary(rows, pop):
    """The lines of the three numbers, from measure.out's rows."""
    n = len(rows)
    eq = [k for k, _, v in rows if v == "equivalent"]
    und = [k for k, _, v in rows if v == "undecided"]
    ne = [(k, c) for k, c, v in rows if v.startswith("differs")]
    m = len(ne)
    out = [f"sample: {n} of {len(pop)} netlist mutations, uniform, "
           f"seed {SEED}",
           f"equivalent: {len(eq)}, undecided: {len(und)}; equivalent "
           f"fraction {mutlib.fmt_cp(len(eq), n)}",
           f"  equivalent: {' '.join(map(str, eq))}",
           f"score: kills among the {m} non-equivalent mutations"]
    names = mutlib.NAMES

    def dead(k, tb):
        return pop[k][names.index(tb)] in mutlib.DEAD
    for tb in names:
        k = sum(dead(j, tb) for j, _ in ne)
        out.append(f"  {tb:14s} {mutlib.fmt_cp(k, m)}")
    union = sum(any(dead(j, tb) for tb in names) for j, _ in ne)
    out.append(f"  {'union':14s} {mutlib.fmt_cp(union, m)}")
    fk = sum(c != "-" for _, c in ne)
    out.append(f"  {'property set':14s} {mutlib.fmt_cp(fk, m)}")
    both = sum(c != "-" or any(dead(j, tb) for tb in names)
               for j, c in ne)
    out.append(f"  {'sim + formal':14s} {both}/{m}")
    ek = [k for k, c, _ in rows if k in eq and
          (c != "-" or any(dead(k, tb) for tb in names))]
    out.append(f"equivalent mutations killed by some check: {len(ek)}")
    return out


def misses(rows, pop, cmds, C):
    """The non-equivalent mutations no property refuted, one line each,
    and where the property set's kills end and its misses begin."""
    rnd = mutlib.NAMES.index("ch01-random")
    miss = [(k, int(v.split("@")[1])) for k, c, v in rows
            if c == "-" and v.startswith("differs")]
    hit = [int(v.split("@")[1]) for k, c, v in rows
           if c != "-" and v.startswith("differs")]
    data = [int(v.split("@")[1]) for k, c, v in rows
            if "a_integrity@" in c and v.startswith("differs")]
    print(f"missed by the property set: {len(miss)} non-equivalent "
          "mutations")
    print("  mutation  mode    line  cell     miter depth  ch01-random")
    for k, d in miss:
        mode, line, cell = yosysmut.parse(cmds[k])
        print(f"  {k:<8d}  {mode:6s}  {line:4s}  {cell:7s}  {d:11d}  "
              f"{pop[k][rnd]}")
    lo, hi = min(d for _, d in miss), max(d for _, d in miss)
    print(f"  the mutations a_integrity kills differ at depth {max(data)} "
          f"or less (the")
    print(f"  property set's kills: {max(hit)} or less); the misses only "
          f"at depth {lo} to {hi}")
    C.pin("property-set misses", len(miss), 14)
    C.pin("kill and miss depths", (max(data), max(hit), lo, hi),
          (15, 18, 16, 31))
    C.pin("the random test kills every miss",
          sum(pop[k][rnd] in mutlib.DEAD for k, _ in miss), len(miss))
    return miss


def integrity(arg):
    """a_integrity alone on one mutation, with more time than the
    measured run's 3 s: bounded search for 30 s, then rIC3 for 120 s if
    that found nothing. Returns (engine, status, depth)."""
    k, cmd = arg
    d = B / f"ai{k}"
    d.mkdir(parents=True, exist_ok=True)
    net = yosysmut.single_netlist(cmd, d / "fifo_m.v")
    for engine, limit in (("informal-bmc", "30s"), ("ric3-ic3", "120s")):
        tcl = (miter.head() + miter.setup_tcl([net, miter.FWRAP])
               + f"one {engine} {limit} -property [full a_integrity]\n"
               + miter.ROWS + "finish\n")
        _, out = miter.shell(tcl, d / engine)
        st, dep = miter.rows(out).get("a_integrity", ("error", -1))
        if st == "cex":
            break
    return engine, st, dep


def read_measure():
    rows, summ, inside = [], [], False
    for line in MEASURE.read_text().splitlines():
        p = line.split()
        if line.startswith("row "):
            rows.append((int(p[1]), p[2], p[3]))
        elif line.startswith("--- summary"):
            inside = True
        elif inside:
            summ.append(line)
    return rows, summ


def main():
    C = mutlib.Checks()
    mutlib.need("yosys", "informal", "ric3")
    print(mutlib.wrap(f"tools: {mutlib.version('yosys')}; "
                      f"{mutlib.version('informal')}, rIC3 as ric3-ic3"))
    B.mkdir(parents=True, exist_ok=True)
    cmds, _ = yosysmut.population(B)
    pick = sample(cmds)
    pop = {int(r[0]): r[4:8] for r in
           (x.rstrip("\n").split("\t") for x in list(POP.open())[1:])}
    if os.environ.get("MEASURE") == "1":
        t0 = time.time()
        res = mutlib.pmap(one, [(k, cmds[k]) for k in pick])
        lines = [f"measure.out -- written by MEASURE=1 make run on "
                 f"{datetime.date.today().isoformat()}",
                 f"tools: {mutlib.version('yosys')}; "
                 f"{mutlib.version('informal')}, rIC3 as ric3-ic3",
                 "property set: informal-bmc 3 s for each property; "
                 "miter: informal-bmc 10 s, then ric3-ic3 120 s",
                 f"wall {time.time() - t0:.0f} s on 4 workers",
                 "row: mutation, properties refuted at their depths, "
                 "miter verdict"]
        lines += [f"row {k} {c} {v}" for k, c, v in res]
        lines += ["--- summary"] + summary(res, pop)
        MEASURE.write_text("\n".join(lines) + "\n")
    rows, summ = read_measure()
    C.pin("sample in measure.out is this run's draw",
          [k for k, _, _ in rows], pick)
    print(f"from the committed measure.out ({len(rows)} rows) and "
          "netlist-population/pop.tsv:")
    again = summary(rows, pop)
    print("\n".join(again))
    C.pin("summary recomputed equals measure.out's", again, summ)
    miss = misses(rows, pop, cmds, C)
    mutlib.pin_measured(C, MEASURE, MEASURE_SHA)
    mutlib.pin_measured(C, POP, POP_SHA)

    eq = [k for k, _, v in rows if v == "equivalent"][:2]
    deep = sorted(((int(v.split("@")[1]), k) for k, _, v in rows
                   if v.startswith("differs")), reverse=True)[:2]
    jobs = ([(k, "ric3-ic3", "120s") for k in eq]
            + [(k, "ric3-ic3", "120s") for _, k in deep])

    def rerun(j):
        k, engine, limit = j
        d = B / f"re{k}"
        d.mkdir(parents=True, exist_ok=True)
        net = yosysmut.single_netlist(cmds[k], d / "fifo_m.v")
        return miter.miter(net, d / "m", engine, limit)[0]
    print("rerun now by rIC3: two equivalents, and the two deepest")
    print("  differences (beyond what 10 s of bounded search reached)")
    for (k, engine, limit), (st, dep) in zip(jobs,
                                             mutlib.pmap(rerun, jobs)):
        print(f"  mutation {k} ({' '.join(yosysmut.parse(cmds[k]))}): "
              f"{miter.say(engine, st, dep, limit)}")
        want = dict((kk, ("cex", d)) for d, kk in deep)
        C.pin(f"rerun {k}", (st, dep) if k in want else st,
              want.get(k, "proven"))
    # The deepest first, so that the two longest jobs start at once.
    order = [k for k, _ in sorted(miss, key=lambda x: -x[1])]
    ai = dict(zip(order, mutlib.pmap(integrity,
                                     [(k, cmds[k]) for k in order])))
    print(f"rerun now: a_integrity alone on the {len(miss)} misses, by "
          "bounded")
    print("  search for 30 s, then by rIC3 for 120 s where that finds "
          "nothing")
    bmc = sorted(dep for e, st, dep in ai.values()
                 if e == "informal-bmc" and st == "cex")
    ic3 = sorted((dep, k) for k, (e, st, dep) in ai.items()
                 if e == "ric3-ic3" and st == "cex")
    by = ", ".join(f"{d} ({bmc.count(d)})" for d in sorted(set(bmc)))
    print(f"  bounded search refutes {len(bmc)}, each at its miter depth: "
          f"{by}")
    print(f"  rIC3 refutes the other {len(ic3)}: "
          + ", ".join(f"{k} at depth {d}" for d, k in ic3))
    C.pin("a_integrity refutes every miss given time",
          (len(bmc), [k for _, k in ic3]), (12, [7759, 8394]))
    C.pin("a_integrity depths", (bmc, [d for d, _ in ic3]),
          ([16] * 7 + [17] * 4 + [18], [29, 31]))
    C.pin("bounded search refutes each at its miter depth",
          [k for k, d in miss if ai[k][0] == "informal-bmc"
           and ai[k][2] != d], [])
    head = MEASURE.read_text().splitlines()[2:4]
    print("the measured run's settings and cost (committed measure.out):")
    for part in "; ".join(head).split("; "):
        print(mutlib.wrap("  " + part, indent="    "))
    C.report()
    print("verdict: the formal sample's summary is reproduced,")
    print("  four of its rows rerun as recorded, and a_integrity, given")
    print("  more time, refutes every miss")


if __name__ == "__main__":
    main()
