"""worked.py -- the six steps of sizing and signing off the FIFO
regression, read from the runs run_worked.sh makes.

    python3 worked.py size              print only the fresh run's size
    python3 worked.py report <tool> <n> print the six steps

1. pilot: per-bin per-seed rates of fifo_cg from 200 seeds, intervals;
2. size: the union bound for every bin the pilot reached, at 99%, and
   the bins that set it;
3. fresh run of that many seeds, merged: did fifo_cg close?
4. unseen bins: Chao2 and Good-Turing over the fresh run;
5. the driver's own stimulus as a law: op_cp against 1/4 each;
6. the clean-seed sentence, from a checking testbench on the repaired
   FIFO, with the same testbench on the original as the control.
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402
import dat  # noqa: E402

B = HERE / "build"
PILOT = range(5001, 5201)
DELTA = 0.01


def cg(names):
    return [i for i, n in enumerate(names) if n.startswith("fifo_cg.")]


names, prow = dat.table([B / ("pilot_%d.dat" % s) for s in PILOT])
idx = cg(names)
short = {i: names[i].split(".", 1)[1] for i in idx}
rate = {i: sum(1 for r in prow if r[i]) / len(PILOT) for i in idx}
seen = [i for i in idx if rate[i] > 0]
n_fresh = S.union_sum_draws([rate[i] for i in seen], DELTA)
if sys.argv[1] == "size":
    print(n_fresh)
    sys.exit(0)

C = S.Checks()
tool, n = sys.argv[2], int(sys.argv[3])
C.pin("simulator", tool, "Verilator 5.052")
C.pin("fresh-run size handed over", n, n_fresh)
print("%s; the coverage chapter's testbench, +bias=even +n=200" % tool)

print("\n== 1. pilot: seeds %d..%d ==" % (PILOT[0], PILOT[-1]))
print("%-26s %8s  %s" % ("bin (rarest first)", "per seed", "95% CP"))
for i in sorted(seen, key=lambda i: (rate[i], short[i])):
    if rate[i] == 1.0:
        continue
    lo, hi = S.cp_interval(round(rate[i] * len(PILOT)), len(PILOT))
    print("%-26s %8.3f  [%.3f, %.3f]" % (short[i], rate[i], lo, hi))
unseen = [short[i] for i in idx if rate[i] == 0]
print("%d further bins hit by every seed; never hit: %s (the coverage"
      % (sum(1 for i in seen if rate[i] == 1.0), " ".join(unseen)))
print("chapter's exclusion review: unreachable on this RTL)")
C.pin("pilot never-hit bins", unseen, ["occupancy.full_16"])

print("\n== 2. size: union bound for every reached bin, 99% ==")
miss = sorted(((1 - rate[i]) ** n, short[i]) for i in seen)[::-1]
print("smallest n with sum_i (1 - p_i)^n <= %.2f: %d seeds" % (DELTA, n))
print("the bins that set it, by their share of the bound at n:")
tot = sum(m for m, _ in miss)
for m, b in miss[:4]:
    print("  %-26s %.4f  (%.0f%%)" % (b, m, 100 * m / tot))
print("bound at n: %.4f" % tot)
C.pin("union bound from the pilot", n, 32)

print("\n== 3. fresh run: seeds 6001..%d, merged ==" % (6000 + n))
merged = dat.read(B / "merged.dat")
zero = [k.split(".", 1)[1] for k in merged
        if k.startswith("fifo_cg.") and merged[k] == 0]
reach = len(seen)
print("verilator_coverage --write merged.dat (%d files)" % n)
print("fifo_cg bins at zero after the merge: %s"
      % (" ".join(zero) if zero else "none"))
closed = zero == ["occupancy.full_16"]
print("every bin the pilot reached is hit: %s" % ("yes" if closed else "no"))
C.holds("the fresh run closed every reached bin", closed)

print("\n== 4. unseen bins over the fresh run ==")
fnames, frow = dat.table([B / ("fresh_%d.dat" % s)
                          for s in range(6001, 6001 + n)])
fi = cg(fnames)
inc = [sum(1 for r in frow if r[i]) for i in fi]
e2, q1, q2 = S.chao2(inc, n)
print("bins seen %d; Q1 %d, Q2 %d; Chao2 %.1f; Good-Turing chance the "
      "next seed adds\na bin: %.3f" % (sum(1 for x in inc if x), q1, q2,
                                      e2, S.good_turing(q1, n)))
C.holds("Chao2 indicates no unseen reachable bin", e2 <= reach + 1e-9)

print("\n== 5. the driver's stimulus as a law: op_cp against 1/4 each ==")
ops = [merged["fifo_cg.op_cp.%s" % o] for o in ("idle", "push", "pop",
                                                 "both")]
x2, df, p = S.pearson(ops, [0.25] * 4)
print("idle %d, push %d, pop %d, both %d: X2 %.2f, %d df, p %.3f"
      % (*ops, x2, df, p))
print("(each cycle's request is drawn afresh, so cycles are independent"
      " draws here)")
C.holds("op_cp consistent with 1/4 each at 0.01", p > 0.01)

print("\n== 6. the clean-seed sentence ==")
print("the temporal-properties chapter's tb_fifo_sva.sv, 400 cycles (push"
      " 0.8, pop\n0.3 for 200 cycles, then 0.3 and 0.8), its assertions"
      " bound to the design")


def passes(tag):
    lines = (B / ("%s.pass" % tag)).read_text().split("\n")
    return [int(x.split()[1]) for x in lines if x]


def mix(c):
    return (0.8, 0.3) if c < 200 else (0.3, 0.8)


fx, og = passes("fixed"), passes("orig")
nfx, cfx = len(fx), sum(fx)
ub = S.cp_upper(nfx - cfx, nfx, 0.05)
print("repaired FIFO: %d of %d seeds clean; 95%% upper bound %.4f (3/n"
      " %.4f)" % (cfx, nfx, ub, 3 / nfx))
chain = F.p_reach(15, lambda c: mix(c)[0], lambda c: mix(c)[1], 400)
fail = len(og) - sum(og)
lo, hi = S.cp_interval(fail, len(og))
print("original FIFO, same seeds: %d of %d fail; 95%% CP [%.4f, %.4f];"
      % (fail, len(og), lo, hi))
print("  the chain's chance of reaching 15 entries in 400 cycles of this"
      " mix: %.6f" % chain)
short30 = F.p_trigger(0.5, 0.5, 30)
print("release note: after %d clean seeds of this test, the per-seed "
      "failure\nprobability under this generator is below %.4f at 95%%."
      % (cfx, ub))
print("  qualifier: a 30-cycle even generator gives 250 clean seeds with"
      " probability\n  %.2f on the original FIFO; the bound speaks for "
      "the generator, not the design" % ((1 - short30) ** 250))
C.pin("repaired clean seeds", cfx, 1000)
C.pin("op_cp counts", ops, [1603, 1612, 1622, 1563])
C.holds("chain inside the original's interval", lo <= chain <= hi)
C.report()
print("verdict: %d seeds closed fifo_cg; %d of %d clean on the repaired"
      " FIFO" % (n, cfx, nfx))
