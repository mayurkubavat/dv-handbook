"""seed_unit.py -- the coverage chapter's fifo_cg under 1000 seeds of
one generator, read back from one coverage database per seed: per-bin
hit rates per cycle and per seed, what a model of independent cycles
predicts from the first, the seeds needed to close the covergroup by
four arguments, and the bug trigger's per-seed rate against the exact
chain. Writes data.tsv and curve.tsv (for the figures) and counts.tsv
(the seed-by-bin table the unseen-bin example reads)."""
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402
import dat  # noqa: E402

SEEDS, CYCLES, PYSEED, RESAMPLES = 1000, 200, 2026, 2000
C = S.Checks()
print("%s; the coverage chapter's tb_fifo_cov.sv on the first chapter's"
      % sys.argv[1])
print("fifo.sv; generator +bias=even +n=%d, seeds 1..%d; python seed %d"
      % (CYCLES, SEEDS, PYSEED))
C.pin("simulator", sys.argv[1], "Verilator 5.052")

build = HERE / "build"
names, rows = dat.table([build / ("even200_%d.dat" % s)
                         for s in range(1, SEEDS + 1)])
trig = [int(x.split()[1]) for x in
        (build / "even200.trig").read_text().split("\n") if x]
dat.write_tsv(HERE / "counts.tsv", names, rows, range(1, SEEDS + 1),
              "fifo_cg and fill_cg bin counts per seed, +bias=even +n=200,"
              " Verilator 5.052")
cg = [i for i, n in enumerate(names) if n.startswith("fifo_cg.")]
short = {i: names[i].split(".", 1)[1] for i in range(len(names))}

# ---- per-bin rates ---------------------------------------------------
pc = {i: sum(r[i] for r in rows) / (SEEDS * CYCLES) for i in cg}
iid = {i: 1 - (1 - pc[i]) ** CYCLES for i in cg}
ps = {i: sum(1 for r in rows if r[i]) / SEEDS for i in range(len(names))}
reach = [i for i in cg if ps[i] > 0]
never = [short[i] for i in cg if ps[i] == 0]
print("\n== 1. fifo_cg: %d bins, %d hit in some seed; never hit: %s =="
      % (len(cg), len(reach), " ".join(never)))
print("%-28s %8s %9s %9s  %s" % ("bin (rarest first)", "p/cycle",
                                 "iid seed", "measured", "95% CP"))
order = sorted(reach, key=lambda i: (ps[i], short[i]))
for i in order:
    if ps[i] == 1.0:
        continue
    lo, hi = S.cp_interval(round(ps[i] * SEEDS), SEEDS)
    print("%-28s %8.5f %9.3f %9.3f  [%.3f, %.3f]"
          % (short[i], pc[i], iid[i], ps[i], lo, hi))
always = sum(1 for i in reach if ps[i] == 1.0)
print("%d further bins hit by every seed" % always)
over = sum(1 for i in reach if iid[i] > ps[i] + 1e-12)
print("bins whose iid-cycle prediction exceeds the measured seed rate:\n"
      "  %d of the %d not hit by every seed" % (over, len(reach) - always))
climb = names.index("fill_cg.level.climb")
print("fill_cg's climb (0 => 1 => 2 => 3) hit by %.3f of seeds"
      % ps[climb])

with open(HERE / "data.tsv", "w") as f:
    f.write("# per bin of fifo_cg: per-cycle rate, the per-seed rate a\n"
            "# model of independent cycles predicts from it, and the\n"
            "# measured per-seed rate; +bias=even +n=200, 1000 seeds\n")
    f.write("bin\tp_cycle\tiid_seed\tmeasured_seed\n")
    for i in order:
        f.write("%s\t%.6f\t%.6f\t%.6f\n" % (short[i], pc[i], iid[i], ps[i]))

alm = names.index("fifo_cg.occupancy.almost")
pxf = names.index("fifo_cg.op_x_full.push_x_full")
C.pin("reachable bins", len(reach), 28)
C.pin("never hit", never, ["occupancy.full_16"])
C.pin("almost: seeds", round(ps[alm] * SEEDS), 271)
C.near("almost: per-cycle rate", pc[alm], 0.0113, 0.00005)
C.near("almost: iid prediction", iid[alm], 0.898, 0.0005)
C.pin("push_x_full: seeds", round(ps[pxf] * SEEDS), 187)
C.holds("the iid model over-predicts every bin not always hit",
        over == len(reach) - always)

# ---- the bug trigger -------------------------------------------------
x = sum(trig)
lo, hi = S.cp_interval(x, SEEDS)
chain = F.p_trigger(0.5, 0.5, CYCLES)
print("\n== 2. the bug trigger, push while full ==")
print("seeds that pushed while full: %d of %d, %.3f; 95%% CP [%.4f, %.4f]"
      % (x, SEEDS, x / SEEDS, lo, hi))
print("exact chain, even mix, %d cycles: %.4f (inside the interval: %s)"
      % (CYCLES, chain, "yes" if lo <= chain <= hi else "no"))
bxf = names.index("fifo_cg.op_x_full.both_x_full")
agree = all(t == (r[pxf] > 0 or r[bxf] > 0) for t, r in zip(trig, rows))
print("trigger line agrees with push_x_full or both_x_full in every .dat:"
      " %s" % ("yes" if agree else "no"))
streaks, cur = [], 0
for t in trig:
    if t:
        streaks.append(cur)
        cur = 0
    else:
        cur += 1
p = x / SEEDS
mean = sum(streaks) / len(streaks)
print("clean streaks before a trigger, in seed order: %d, longest %d, "
      "mean %.2f" % (len(streaks), max(streaks), mean))
print("  (geometric law for independent seeds: mean (1-p)/p = %.2f)"
      % ((1 - p) / p))
pmf = F.trigger_pmf(0.5, 0.5, CYCLES)
cum, med = 0.0, None
first = next(c for c, q in enumerate(pmf, 1) if q > 0)
for c, q in enumerate(pmf, 1):
    cum += q
    if med is None and cum >= chain / 2:
        med = c
win = [sum(pmf[a:a + 50]) / chain for a in range(0, CYCLES, 50)]
print("first trigger, from the chain (the testbench prints no cycle):")
print("  earliest possible cycle %d; P(before cycle 40 | trigger) = %.4f;"
      " median %d" % (first, sum(pmf[:39]) / chain, med))
print("  share in cycles 1-50, 51-100, 101-150, 151-200: %s"
      % ", ".join("%.3f" % w for w in win))
haz = [pmf[c] / (1 - sum(pmf[:c])) for c in (49, 99, 199)]
print("  per-cycle hazard at cycles 50, 100, 200: %s"
      % ", ".join("%.5f" % h for h in haz))
C.pin("trigger seeds", x, 247)
C.holds("chain inside the CP interval", lo <= chain <= hi)
C.holds("trigger line equals the .dat cells", agree)
C.rel("streak mean against the geometric mean", mean, (1 - p) / p, 0.10)
C.pin("chain median first-trigger cycle", med, 137)

# ---- a cross cell is joint, not a product -----------------------------
pp = names.index("fifo_cg.op_cp.push")
fl = names.index("fifo_cg.full_cp.full")
print("\n== 3. a cross cell's probability is joint ==")
print("per seed: push_x_full %.3f; P(push) x P(full) = %.3f x %.3f = %.3f"
      % (ps[pxf], ps[pp], ps[fl], ps[pp] * ps[fl]))
print("per cycle: push_x_full %.5f; P(push) x P(full) = %.5f"
      % (pc[pxf], pc[pp] * pc[fl]))
# Per cycle the request is drawn afresh, so it is independent of the
# flag: among the cycles that showed full, push should be a binomial
# share, P(push), of them.
nf = sum(r[fl] for r in rows)
npf = sum(r[pxf] for r in rows)
z = (npf - nf * pc[pp]) / math.sqrt(nf * pc[pp] * (1 - pc[pp]))
print("  of %d cycles that showed full, %d pushed: z = %.2f against a\n"
      "  binomial share %.3f" % (nf, npf, z, pc[pp]))
C.holds("per-seed product overstates the joint by > 0.05",
        ps[pp] * ps[fl] - ps[pxf] > 0.05)
C.holds("per-cycle joint consistent with the product (|z| < 3)", abs(z) < 3)

# ---- seeds to close the covergroup ------------------------------------
print("\n== 4. seeds until every reachable fifo_cg bin is hit, 99% ==")
p_seed = [ps[i] for i in reach]
masks = [sum(1 << k for k, i in enumerate(reach) if r[i]) for r in rows]
full = (1 << len(reach)) - 1
cmask = [m | (1 << len(reach)) if r[climb] else m
         for m, r in zip(masks, rows)]
rng = random.Random(PYSEED)


def to_close(ms, goal):
    order = list(range(SEEDS))
    rng.shuffle(order)
    acc = 0
    for t, s in enumerate(order, 1):
        acc |= ms[s]
        if acc == goal:
            return t
    return None


need = [to_close(masks, full) for _ in range(RESAMPLES)]
needc = [to_close(cmask, (full << 1) | 1) for _ in range(RESAMPLES)]
u_sum = S.union_sum_draws(p_seed, 0.01)
u_split = S.union_split_draws(p_seed, 0.01)
prod = S.first_n(S.coupon_cdf_product, p_seed, 0.01)
pcy = [pc[i] for i in reach]
cy_prod = S.first_n(S.coupon_cdf_product, pcy, 0.01)
cy_sum = S.union_sum_draws(pcy, 0.01)
q50, q99 = S.quantile(need, 0.5), S.quantile(need, 0.99)
print("seed level, from the measured per-seed rates:")
print("  union bound, sum_i (1-p_i)^n <= 0.01:      %3d seeds" % u_sum)
print("  union bound, 0.01/%d for each bin:          %3d seeds"
      % (len(reach), u_split))
print("  bins taken as independent (product):       %3d seeds" % prod)
print("  measured by resampling (%d orders):       median %d, q99 %d"
      % (RESAMPLES, q50, q99))
print("  with fill_cg's climb as well:              median %d, q99 %d"
      % (S.quantile(needc, 0.5), S.quantile(needc, 0.99)))
print("cycle level, from the per-cycle rates (independent cycles):")
cy_split = S.union_split_draws(pcy, 0.01)
print("  product: %d cycles = %.1f seeds; union: %d cycles = %.1f seeds"
      % (cy_prod, cy_prod / CYCLES, cy_sum, cy_sum / CYCLES))
print("  union with 0.01/%d for each bin: %d cycles = %.1f seeds"
      % (len(reach), cy_split, cy_split / CYCLES))
print("  measured q99 over cycle-model product: %.1f times"
      % (q99 / (cy_prod / CYCLES)))
print("rarest bin %s at %.3f: alone it needs %d seeds for 99%%"
      % (short[order[0]], ps[order[0]], S.seeds_to_hit(ps[order[0]], 0.01)))
print("almost at its measured rate %.3f needs %d seeds for 99%%"
      % (ps[alm], S.seeds_to_hit(ps[alm], 0.01)))
with open(HERE / "curve.tsv", "w") as f:
    f.write("# P(every reachable fifo_cg bin hit within n seeds):\n"
            "# resampled, independent-bins product, union-bound\n"
            "# guarantee (1 - sum), and the independent-cycles model\n")
    f.write("seeds\tresampled\tproduct\tunion\tcycle_iid\n")
    for n in range(1, 61):
        f.write("%d\t%.4f\t%.4f\t%.4f\t%.4f\n" % (
            n, sum(1 for t in need if t <= n) / RESAMPLES,
            S.coupon_cdf_product(p_seed, n),
            max(0.0, 1 - S.union_miss(p_seed, n)),
            S.coupon_cdf_product(pcy, n * CYCLES)))
C.pin("union bound, sum form", u_sum, 27)
C.pin("union bound, split form", u_split, 39)
C.pin("product", prod, 27)
C.pin("resampled median", q50, 5)
C.pin("resampled q99", q99, 26)
C.holds("union bound is not below the measured q99", u_sum >= q99)
C.near("cycle-model product, seeds", cy_prod / CYCLES, 10.6, 0.05)
C.report()
print("verdict: %d of %d seeds triggered the bug; %d bins reachable; "
      "q99 %d seeds" % (x, SEEDS, len(reach), q99))
