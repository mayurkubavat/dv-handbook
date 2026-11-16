"""selftest.py -- the shared library checked against values known in
closed form, and the exercises' answers computed by the same code.
Python only; under a second. Every line it prints is also a check: a
value outside its tolerance fails the run."""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402

C = S.Checks()


def show(text, got, want, tol):
    print("%-52s %.6g" % (text, got))
    C.near(text, got, want, tol)


def show_is(text, got, want):
    """For a value that must be exactly want (a string, None, inf)."""
    print("%-52s %s" % (text, got))
    C.pin(text, got, want)


print("== special functions against tabulated values ==")
show("chi-square sf at 5.9915, 2 df (0.05)", S.chi2_sf(5.991465, 2),
     0.05, 1e-6)
show("chi-square sf at 3.8415, 1 df (0.05)", S.chi2_sf(3.841459, 1),
     0.05, 1e-6)
show("chi-square sf at 82.529, 63 df (0.05)", S.chi2_sf(82.5287, 63),
     0.05, 1e-4)
show("Kolmogorov sf at 1.3581 (0.05)", S.kolmogorov_sf(1.358099),
     0.05, 1e-5)

print("== binomial bounds ==")
for n in (30, 250, 600):
    cp = S.cp_upper(0, n, 0.05)
    show("CP upper, 0 of %d, 95%%" % n, cp, 1 - 0.05 ** (1 / n), 1e-12)
lo, hi = S.cp_interval(5, 20, 0.95)
show("CP 95% interval for 5 of 20, lower (0.0866)", lo, 0.086571, 1e-5)
show("CP 95% interval for 5 of 20, upper (0.4910)", hi, 0.491046, 1e-5)
show("seeds to hit a 1% bin with 95% chance", S.seeds_to_hit(0.01, 0.05),
     299, 0)

print("== coupon collector ==")
show("E[T], six equal bins, 6 H_6", S.coupon_expect_equal(6), 14.7, 0.0001)
show("E[T], six equal bins, by the integral", S.coupon_expect([1 / 6] * 6),
     S.coupon_expect_equal(6), 1e-6)
show("P(all of 6:3:1 in 44), inclusion-exclusion",
     S.coupon_cdf_exact([0.6, 0.3, 0.1], 44), 0.990302, 1e-6)
show("union bound, 28 bins at 0.187, 99%",
     S.union_split_draws([0.187] * 28, 0.01), 39, 0)

print("== the FIFO chain ==")
show("P(push while full in 200 cycles), even mix",
     F.p_trigger(0.5, 0.5, 200), 0.242060, 5e-7)
show("pmf of the first trigger sums to P(trigger)",
     sum(F.trigger_pmf(0.5, 0.5, 200)), F.p_trigger(0.5, 0.5, 200), 1e-15)
show("P(reach 16) with full at 15 is zero",
     F.p_reach(16, 0.9, 0.1, 400), 0.0, 0)

print("== estimators and information ==")
inc = [1] * 4 + [2] * 2 + [5] * 54        # 60 seen; Q1 = 4, Q2 = 2
show("Chao2, 10 seeds, 60 seen, Q1 4, Q2 2", S.chao2(inc, 10)[0], 63.6,
     1e-9)
show("Good-Turing, 3 singletons in 200 seeds", S.good_turing(3, 200),
     0.015, 1e-12)
h = S.entropy([0.6, 0.3, 0.1])
show("entropy of 6:3:1, bits", h, 1.29546, 1e-5)
show("effective number of values, 2^H", 2 ** h, 2.4546, 1e-4)
x2, _, p = S.pearson([6076, 2940, 984], [0.6, 0.3, 0.1])
show("Pearson X2 of 6076, 2940, 984 against 6:3:1", x2, 2.4187, 1e-4)
g, _, _ = S.g_test([6076, 2940, 984], [0.6, 0.3, 0.1])
show("G of the same counts", g, x2, 0.01)
show("mutual information of a bit with itself",
     S.mutual_info([(0, 0), (1, 1)] * 50), 1.0, 1e-12)
lb = math.prod(sorted([6, 4, 3, 3, 2])[-2:])
show("pairwise lower bound for levels 6, 4, 3, 3, 2", lb, 24, 0)

print("== edge cases: an unreachable bin, an empty sample ==")


def raises(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


none = (S.seeds_to_hit(0, 0.01), S.union_sum_draws([0.5, 0], 0.01),
        S.union_split_draws([0.5, 0], 0.01),
        S.first_n(S.coupon_cdf_poisson, [0.5, 0], 0.01))
show_is("p = 0: seeds_to_hit, union sum, union split, first_n",
        " ".join(map(str, sorted(set(map(str, none))))), "None")
show_is("E[T] with an unreachable bin", S.coupon_expect([0.5, 0.5, 0]),
        math.inf)
show_is("chao1, chao2, good_turing, ks_uniform on no data",
        " ".join(sorted({raises(lambda: S.chao1([], 0)),
                         raises(lambda: S.chao2([], 0)),
                         raises(lambda: S.good_turing(0, 0)),
                         raises(lambda: S.ks_uniform([], 4))})),
        "ValueError")
show_is("Pearson p with a count in a zero-probability cell",
        S.pearson([5, 5, 1], [0.5, 0.5, 0])[2], 0.0)
show_is("Pearson ignores an empty zero-probability cell",
        S.pearson([5, 5, 0], [0.5, 0.5, 0]) == S.pearson([5, 5], [0.5, 0.5]),
        True)
show_is("quantile with a run that never finished",
        S.quantile([3, None, 1, 2], 0.9), None)
C.report()
print("self-test: the library reproduces every tabulated value")
