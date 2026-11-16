"""coupon.py -- how many draws until every bin is hit: E[T] = k H_k for
equal bins, the Poissonized integral for unequal ones, the exact law by
inclusion-exclusion for a few bins, the union bound in its two forms,
each against simulation. The cases are the constrained-random
chapter's: its packet kind mix and an 8-bit value under its two dist
forms. Python only; a few seconds."""
import bisect
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "common"))
import statlib as S  # noqa: E402

PYSEED = 2026
rng = random.Random(PYSEED)
C = S.Checks()
print("python seed %d" % PYSEED)


def simulate(p, trials):
    """Draw from p until every bin is hit; the list of draw counts."""
    cum, c = [], 0.0
    for q in p:
        c += q
        cum.append(c)
    out = []
    for _ in range(trials):
        seen, left, t = bytearray(len(p)), len(p), 0
        while left:
            t += 1
            i = bisect.bisect_left(cum, rng.random() * c)
            if not seen[i]:
                seen[i] = 1
                left -= 1
        out.append(t)
    return out


# The simulated figures the chapter quotes; the run is deterministic.
SIM = {"equal, k=8": ("22.0", "1.45", 53),
       "equal, k=64": ("305.4", "1.44", 574),
       "equal, k=256": ("1568.6", "0.08", 2666),
       "kind 0/1/2": ("10.8", "-0.86", 45),
       "v dist := {1,1,2}": ("2140.0", "-0.20", 3770),
       "v dist :/ {1,1,2}": ("2031.9", "0.34", 3532)}


def row(name, p, trials):
    """Print one case; return (E[T] formula, simulated mean, its se,
    n99 by Poisson, simulated q99, union sum, union split)."""
    sims = simulate(p, trials)
    mean = sum(sims) / trials
    se = math.sqrt(sum((x - mean) ** 2 for x in sims) / (trials - 1)
                   / trials)
    e = S.coupon_expect(p)
    n99 = S.first_n(S.coupon_cdf_poisson, p, 0.01)
    q99 = S.quantile(sims, 0.99)
    us, usp = S.union_sum_draws(p, 0.01), S.union_split_draws(p, 0.01)
    z = (mean - e) / se
    print("%-20s k=%3d  E[T] %7.1f  sim %7.1f (se %5.2f, z %+5.2f)"
          % (name, len(p), e, mean, se, z))
    print("%-20s equal-p k H_k %7.1f;  99%%: Poisson %d, sim q99 %d,"
          % ("", S.coupon_expect_equal(len(p)), n99, q99))
    print("%-20s union sum %d, union split %d; %d trials"
          % ("", us, usp, trials))
    C.holds("%s: formula within 2 se of simulation" % name, abs(z) <= 2)
    C.pin("%s: simulated mean, z and q99" % name,
          ("%.1f" % mean, "%.2f" % z, q99), SIM[name])
    return e, mean, se, n99, q99, us, usp


print("\n== 1. equal probabilities: E[T] = k H_k, about k ln k ==")
for k, trials in ((8, 4000), (64, 4000), (256, 1000)):
    e = row("equal, k=%d" % k, [1.0 / k] * k, trials)[0]
    C.rel("k=%d integral equals k H_k" % k, e, S.coupon_expect_equal(k),
          1e-6)

print("\n== 2. the packet kind mix 6:3:1 ==")
p = [0.6, 0.3, 0.1]
e, _, _, n99, q99, us, usp = row("kind 0/1/2", p, 4000)
ex = S.first_n(S.coupon_cdf_exact, p, 0.01)
print("  exact 99%% point by inclusion-exclusion: %d packets" % ex)
for n in (10, 20, 30, 44, 64):
    print("  P(all three kinds within %2d packets): exact %.4f,"
          " Poisson %.4f" % (n, S.coupon_cdf_exact(p, n),
                             S.coupon_cdf_poisson(p, n)))
C.near("packet E[T]", e, 11.0, 0.05)
C.pin("packet exact n99", ex, 44)
C.pin("packet Poisson n99", n99, 47)
C.pin("packet union split", usp, 55)
C.pin("packet union sum", us, 44)

print("\n== 3. every value of an 8-bit v under the two dist forms ==")
assign = [1 / 412] * 100 + [2 / 412] * 156     # := 1, 1, 2 per value
divide = [0.25 / 10] * 10 + [0.25 / 90] * 90 + [0.5 / 156] * 156
eq = S.coupon_expect_equal(256)
for name, law in (("v dist := {1,1,2}", assign),
                  ("v dist :/ {1,1,2}", divide)):
    e = row(name, law, 1000)[0]
    print("  E[T] is %.0f%% above the equal-p k H_k (k H_k is %.0f%% low)"
          % (100 * (e / eq - 1), 100 * (1 - eq / e)))
    C.holds("%s: E[T] 25-40%% above k H_k" % name,
            0.25 <= e / eq - 1 <= 0.40)
C.report()
print("verdict: the 6:3:1 packet mix needs %d packets for 99%%, exactly"
      % ex)
