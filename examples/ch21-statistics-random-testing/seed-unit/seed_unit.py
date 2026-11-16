"""seed_unit.py -- the coverage chapter's fifo_cg under 1000 seeds of
one generator, read back from one coverage database per seed: per-bin
hit rates per cycle and per seed, what a model of independent cycles
predicts from the first, the seeds needed to close the covergroup by
four arguments, and the bug trigger's per-seed rate against the exact
chain. Writes data.tsv and curve.tsv (for the figures) and counts.tsv
(the seed-by-bin table the unseen-bin example reads)."""
import math
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402
import dat  # noqa: E402

SEEDS, CYCLES = 1000, 200
C = S.Checks()
print("%s; the coverage chapter's tb_fifo_cov.sv on the first chapter's"
      % sys.argv[1])
print("fifo.sv; generator +bias=even +n=%d, seeds 1..%d"
      % (CYCLES, SEEDS))
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
ratio = {short[i]: iid[i] / ps[i] for i in reach if ps[i] < 0.3}
C.holds("iid over measured: 1.85 to 2.4 for op_x_full, above 3 for"
        " full and almost",
        all(1.85 <= v <= 2.4 for k, v in ratio.items() if "x_full" in k)
        and all(v > 3 for k, v in ratio.items() if "x_full" not in k)
        and len(ratio) == 6)

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
C.near("P(before cycle 40 | trigger)", sum(pmf[:39]) / chain, 0.0031,
       0.00005)
C.holds("hazard rises more than sixfold from cycle 50 to 200",
        haz[2] > 6 * haz[0])

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
print("  of %d cycles that showed full, %d pushed: z = %.2f against the\n"
      "  measured per-cycle push share %.3f" % (nf, npf, z, pc[pp]))
C.holds("per-seed product overstates the joint by > 0.05",
        ps[pp] * ps[fl] - ps[pxf] > 0.05)
C.holds("per-cycle joint within two sd of the product (|z| < 2)",
        abs(z) < 2)

# ---- seeds to close the covergroup ------------------------------------
# The measured answer: seeds drawn independently from the thousand that
# ran, each with probability 1/1000 (the bootstrap law of a fresh seed).
# Its closure law is exact by inclusion-exclusion over the bins that not
# every seed hits: P(all hit in n) = sum_S (-1)^|S| (N_S / N)^n, with N_S
# the seeds that hit none of S. Bin i alone is missed with probability
# (1 - p_i)^n, so the union bound and the product are exact statements
# about this law, not about an estimate of it.
print("\n== 4. seeds until every reachable fifo_cg bin is hit, 99% ==")
p_seed = [ps[i] for i in reach]


def closure_law(bins, nmax):
    """[P(every bin in bins hit within n seeds) for n = 1..nmax] when
    seeds are drawn independently from the measured ones."""
    k = len(bins)
    masks = Counter(sum(1 << j for j, i in enumerate(bins) if r[i])
                    for r in rows)
    terms = [((-1) ** bin(s).count("1"),
              sum(c for m, c in masks.items() if not m & s) / SEEDS)
             for s in range(1 << k)]
    return [sum(sg * q ** n for sg, q in terms) for n in range(1, nmax + 1)]


def first_at(law, level):
    return next(n for n, v in enumerate(law, 1) if v >= level)


var = [i for i in reach if ps[i] < 1.0]
law = closure_law(var, 80)
lawc = closure_law(var + [climb], 80)
u_sum = S.union_sum_draws(p_seed, 0.01)
u_split = S.union_split_draws(p_seed, 0.01)
prod = S.first_n(S.coupon_cdf_product, p_seed, 0.01)
pcy = [pc[i] for i in reach]
cy_prod = S.first_n(S.coupon_cdf_product, pcy, 0.01)
cy_sum = S.union_sum_draws(pcy, 0.01)
q50, q99 = first_at(law, 0.5), first_at(law, 0.99)
print("seed level, from the measured per-seed rates:")
print("  union bound, sum_i (1-p_i)^n <= 0.01:      %3d seeds" % u_sum)
print("  union bound, 0.01/%d for each bin:          %3d seeds"
      % (len(reach), u_split))
print("  bins taken as independent (product):       %3d seeds" % prod)
print("  measured, the exact law of the 1000 seeds: median %d, q99 %d"
      % (q50, q99))
print("  with fill_cg's climb as well:              median %d, q99 %d"
      % (first_at(lawc, 0.5), first_at(lawc, 0.99)))
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
# How far the sum is from the law at q99: the runs that miss two or more
# bins are the ones the sum counts more than once.
masks = Counter(sum(1 << j for j, i in enumerate(var) if r[i]) for r in rows)
miss1 = 0.0
for s in range(1, 1 << len(var)):
    m = bin(s).count("1")
    q = sum(c for k, c in masks.items() if not k & s) / SEEDS
    miss1 += (-1) ** (m - 1) * m * q ** q99
some = 1 - law[q99 - 1]
print("at %d seeds: sum_i (1-p_i)^n %.4f; P(some bin missed) %.4f, of"
      " which\n  two or more %.4f" % (q99, S.union_miss(p_seed, q99), some,
                                     some - miss1))
oxf = [i for i in reach if ".op_x_full." in names[i]
       and not names[i].endswith("not_full")]
fs = [r for r in rows if r[fl]]
all4 = sum(1 for r in fs if all(r[i] for i in oxf))
ind4 = math.prod(sum(1 for r in fs if r[i]) / len(fs) for i in oxf)
lone = sum(1 for r in rows if not r[fl] and any(r[i] for i in oxf))
same = all((r[fl] > 0) == (r[alm] > 0) for r in rows)
print("seeds that show full: %d, %s also almost; %d show an op_x_full"
      " cell without\n  it; %d hit all four op_x_full cells (%.2f; %.2f if"
      " independent given full)" % (len(fs), "each" if same else "not all",
                                     lone, all4, all4 / len(fs), ind4))
with open(HERE / "curve.tsv", "w") as f:
    f.write("# P(every reachable fifo_cg bin hit within n seeds):\n"
            "# measured (exact law of seeds drawn from the 1000),\n"
            "# independent-bins product, union-bound guarantee\n"
            "# (1 - sum), and the independent-cycles model\n")
    f.write("seeds\tmeasured\tproduct\tunion\tcycle_iid\n")
    for n in range(1, 61):
        f.write("%d\t%.4f\t%.4f\t%.4f\t%.4f\n" % (
            n, law[n - 1], S.coupon_cdf_product(p_seed, n),
            max(0.0, 1 - S.union_miss(p_seed, n)),
            S.coupon_cdf_product(pcy, n * CYCLES)))
C.pin("union bound, sum form", u_sum, 27)
C.pin("union bound, split form", u_split, 39)
C.pin("product", prod, 27)
C.pin("measured median", q50, 5)
C.pin("measured q99", q99, 25)
C.pin("with climb, median and q99", (first_at(lawc, 0.5),
                                     first_at(lawc, 0.99)), (9, 46))
C.holds("the union-bound guarantee is never above the exact law",
        all(1 - S.union_miss(p_seed, n) <= law[n - 1] + 1e-12
            for n in range(1, 81)))
C.near("cycle-model product, seeds", cy_prod / CYCLES, 10.6, 0.05)
C.near("P(some bin missed) at q99", some, 0.0099, 0.00005)
C.near("P(two or more missed) at q99", some - miss1, 0.0028, 0.00005)
C.pin("full seeds; all four op_x_full; op_x_full without full",
      (len(fs), all4, lone), (271, 137, 0))
C.holds("full and almost hit by the same seeds", same)
C.near("all four if independent given full", ind4, 0.34, 0.005)
C.report()
print("verdict: %d of %d seeds triggered the bug; %d bins reachable; "
      "q99 %d seeds" % (x, SEEDS, len(reach), q99))
