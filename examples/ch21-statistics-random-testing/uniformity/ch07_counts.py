"""ch07_counts.py -- goodness-of-fit tests on the counts the
constrained-random chapter printed, read from its run.out files by path:
the two dist forms of its distribution example, the packet kind mix of
its packet stream, and the dist, implication and solve...before forms.
Percentages of the low bits are rounded in that output and are not
re-tested here. A run.out whose format has changed fails the run."""
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402

C = S.Checks()
C7 = HERE.parent.parent / "ch07-constrained-random"


def grab(name, pattern):
    text = (C7 / name / "run.out").read_text()
    m = re.search(pattern, text, re.M)
    C.holds("%s/run.out still prints %r" % (name, pattern), m)
    return [int(x) for x in m.groups()] if m else None


def binom_two_sided(x, n, p):
    """Exact two-sided binomial p-value, by doubling the smaller tail."""
    lo = S.binom_cdf(x, n, p)
    hi = 1 - S.binom_cdf(x - 1, n, p)
    return min(1.0, 2 * min(lo, hi))


def show(what, test, stat, p, log10p=None):
    pt = "p=%.3g" % p if log10p is None else "p=10^%.0f" % log10p
    print("  %-40s %-10s %-13s %s" % (what, test, stat, pt))
    return p


print("== 1. the constrained-random chapter's printed counts ==")
d = grab("distribution", r"^dist :/\s+\[0:9\]\s+(\d+)\s+\[10:99\]\s+(\d+)"
         r"\s+\[100:255\]\s+(\d+)")
x, df, p_div = S.pearson(d, [0.25, 0.25, 0.5])
show("dist :/ %s vs 1:1:2" % "/".join(map(str, d)), "chi-square",
     "X2=%.2f df=%d" % (x, df), p_div)
d = grab("distribution", r"^dist :=\s+\[0:9\]\s+(\d+)\s+\[10:99\]\s+(\d+)"
         r"\s+\[100:255\]\s+(\d+)")
x, df, p_asg = S.pearson(d, [10 / 412, 90 / 412, 312 / 412])
show("dist := %s vs 10:90:312" % "/".join(map(str, d)), "chi-square",
     "X2=%.2f df=%d" % (x, df), p_asg)
kinds = [0, 0, 0]
for s in (3, 4):                # the third line repeats seed 3
    k = grab("packet-stream", r"^seed %d: 64 packets, 0 errors; kinds "
             r"0:(\d+) 1:(\d+) 2:(\d+) 3:0" % s)
    kinds = [a + b for a, b in zip(kinds, k)]
x, df, p_kind = S.pearson(kinds, [0.6, 0.3, 0.1])
show("kinds %s, seeds 3, 4, vs 6:3:1" % "/".join(map(str, kinds)),
     "chi-square", "X2=%.2f df=%d" % (x, df), p_kind)
a = grab("constraint-forms", r"^dist :=\s+\[0:3\] (\d+) times, 9 (\d+)")
x, df, p_fa = S.pearson(a, [0.8, 0.2])
show("forms dist := %d/%d vs 4:1" % tuple(a), "chi-square",
     "X2=%.2f df=%d" % (x, df), p_fa)
a = grab("constraint-forms", r"^dist :/\s+\[0:3\] (\d+) times, 9 (\d+)")
x, df, p_fd = S.pearson(a, [0.5, 0.5])
show("forms dist :/ %d/%d vs 1:1" % tuple(a), "chi-square",
     "X2=%.2f df=%d" % (x, df), p_fd)
s1 = grab("constraint-forms", r"^2000 draws:\s+s=1 (\d+) times without "
          r"solve before, (\d+) with")
p_imp = show("s=1 %d of 2000, no ordering, vs 1/257" % s1[0], "binomial",
             "", binom_two_sided(s1[0], 2000, 1 / 257))
# 0 of 2000 at p = 1/2 underflows a float: its two-sided p-value is
# 2 * 0.5^2000, printed by its logarithm.
p_sb = show("s=1 %d of 2000, solve before, vs 1/2" % s1[1], "binomial",
            "", binom_two_sided(s1[1], 2000, 0.5),
            math.log10(2) + 2000 * math.log10(0.5) if s1[1] == 0 else None)
ps = [p_div, p_asg, p_kind, p_fa, p_fd, p_imp]
print("  every law but solve...before: smallest p %.3g of %d tests; "
      "Bonferroni\n  threshold 0.05/%d = %.4f" % (min(ps), len(ps),
                                                 len(ps), 0.05 / len(ps)))
C.near("forms dist := p-value", p_fa, 0.0339, 0.00005)
C.near("dist :/ p-value", p_div, 0.0782, 0.00005)
C.holds("no printed count but solve...before rejected at Bonferroni",
        min(ps) > 0.05 / len(ps))
C.holds("solve...before rejected below 1e-100", p_sb < 1e-100)
C.report()
