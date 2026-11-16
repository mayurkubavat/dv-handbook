"""statlib.py -- the statistics the chapter's examples use, written on
the Python standard library alone (the book's environment has no numpy
or scipy), and a small checker that fails a run whose numbers drift.

Each function names the formula it implements. The self-test in
selftest.py checks the special functions against known values, and the
examples check the formulas that matter against simulation.
"""
import math
import sys
from collections import Counter


# ---- special functions ---------------------------------------------

def gammainc_upper_reg(a, x):
    """Q(a, x) = Gamma(a, x) / Gamma(a), the regularized upper incomplete
    gamma function: a series for x < a + 1, a continued fraction
    otherwise (the method of Numerical Recipes, section 6.2)."""
    if x <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(10000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gln)
    b = x + 1 - a
    c = 1e300
    d = 1 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(x, df):
    """P(X >= x) for X ~ chi-square with df degrees of freedom."""
    return gammainc_upper_reg(df / 2.0, x / 2.0)


def normal_sf2(z):
    """Two-sided normal tail, P(|Z| >= |z|)."""
    return math.erfc(abs(z) / math.sqrt(2))


def kolmogorov_sf(lam):
    """P(sqrt(n) D_n > lam) in the limit of large n (Kolmogorov):
    2 * sum_{k>=1} (-1)^(k-1) exp(-2 k^2 lam^2)."""
    if lam < 0.2:
        return 1.0
    s = 0.0
    for k in range(1, 200):
        t = 2 * (-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
        s += t
        if abs(t) < 1e-16:
            break
    return min(1.0, max(0.0, s))


# ---- tests on histograms -------------------------------------------

def _support(counts, probs):
    """Cells the law can produce, and whether a count fell outside them.
    A count in a cell of probability zero rejects the law outright."""
    inside = [(c, p) for c, p in zip(counts, probs) if p > 0]
    outside = any(c for c, p in zip(counts, probs) if p <= 0)
    return inside, len(inside) - 1, outside


def pearson(counts, probs):
    """Pearson's X^2 of counts against a law; (X^2, df, p). Cells of
    probability zero are left out of the sum and of df; a count in one
    gives X^2 = inf and p = 0."""
    cells, df, outside = _support(counts, probs)
    if outside:
        return math.inf, df, 0.0
    n = sum(c for c, _ in cells)
    x = sum((c - n * p) ** 2 / (n * p) for c, p in cells)
    return x, df, chi2_sf(x, df)


def g_test(counts, probs):
    """The likelihood-ratio statistic G = 2 sum c ln(c / n p), which is
    2 n KL(empirical || law) in nats; (G, df, p). Zero-probability
    cells as in pearson()."""
    cells, df, outside = _support(counts, probs)
    if outside:
        return math.inf, df, 0.0
    n = sum(c for c, _ in cells)
    g = 2 * sum(c * math.log(c / (n * p)) for c, p in cells if c > 0)
    return g, df, chi2_sf(g, df)


def ks_uniform(xs, m):
    """Kolmogorov-Smirnov distance of integer draws from the discrete
    uniform law on 0..m-1, and the large-n p-value with Stephens'
    small-sample factor. For a discrete law the p-value is
    conservative."""
    n = len(xs)
    if n == 0:
        raise ValueError("ks_uniform: no draws")
    cnt = [0] * m
    for x in xs:
        cnt[x] += 1
    d = 0.0
    c = 0
    for v in range(m):
        before = c
        c += cnt[v]
        d = max(d, abs(c / n - (v + 1) / m), abs(before / n - v / m))
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    return d, kolmogorov_sf(lam)


def hist(xs, m):
    h = [0] * m
    for x in xs:
        h[x] += 1
    return h


# ---- binomial bounds -----------------------------------------------

def binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p), summed in log space."""
    if k < 0:
        return 0.0
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    lp, lq = math.log(p), math.log1p(-p)
    tot = 0.0
    for i in range(0, min(k, n) + 1):
        lc = (math.lgamma(n + 1) - math.lgamma(i + 1)
              - math.lgamma(n - i + 1))
        tot += math.exp(lc + i * lp + (n - i) * lq)
    return min(1.0, tot)


def _bisect(f, lo, hi, it=100):
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def cp_upper(x, n, alpha):
    """One-sided Clopper-Pearson upper bound: the p at which
    P(X <= x | p) = alpha. For x = 0 this is 1 - alpha**(1/n)."""
    if x >= n:
        return 1.0
    return _bisect(lambda p: binom_cdf(x, n, p) <= alpha, 0.0, 1.0)


def cp_lower(x, n, alpha):
    """One-sided Clopper-Pearson lower bound: the p at which
    P(X >= x | p) = alpha."""
    if x <= 0:
        return 0.0
    return _bisect(lambda p: 1 - binom_cdf(x - 1, n, p) >= alpha,
                   0.0, 1.0)


def cp_interval(x, n, conf=0.95):
    """Two-sided Clopper-Pearson interval, alpha/2 in each tail."""
    a = (1 - conf) / 2
    return cp_lower(x, n, a), cp_upper(x, n, a)


def seeds_to_hit(p, delta):
    """Smallest n with (1 - p)^n <= delta: n >= ln(delta)/ln(1 - p).
    A bin with p = 0 is never hit: None."""
    if p <= 0:
        return None
    if p >= 1:
        return 1
    return math.ceil(math.log(delta) / math.log1p(-p) - 1e-12)


# ---- coupon collector ----------------------------------------------

def coupon_expect_equal(k):
    """E[T] = k * H_k for k equally likely bins."""
    return k * sum(1.0 / i for i in range(1, k + 1))


def coupon_expect(p, steps=200000):
    """E[T] = integral_0^inf (1 - prod_i (1 - exp(-p_i t))) dt, the
    Poissonized form (draws as a rate-1 Poisson process), by the
    trapezoid rule. Equal probabilities are grouped, so a law with few
    distinct values is cheap however many bins it has. A bin with
    p_i = 0 is never hit, and E[T] is infinite."""
    if any(q <= 0 for q in p):
        return math.inf
    groups = Counter(p)
    pmin = min(groups)
    h = 60.0 / pmin / steps
    tot, prev = 0.0, 1.0
    for i in range(1, steps + 1):
        t = i * h
        prod = 1.0
        for q, m in groups.items():
            prod *= (-math.expm1(-q * t)) ** m
        cur = 1.0 - prod
        tot += (prev + cur) * h / 2
        prev = cur
        if cur < 1e-14:
            break
    return tot


def coupon_cdf_poisson(p, n):
    """P(T <= n) ~ prod_i (1 - exp(-n p_i)): exact for a Poisson(n)
    number of draws, close for exactly n."""
    prod = 1.0
    for q in p:
        prod *= -math.expm1(-n * q)
    return prod


def coupon_cdf_exact(p, n):
    """P(T <= n) by inclusion-exclusion over subsets of bins:
    sum over S of (-1)^|S| (1 - p(S))^n. Exponential in len(p)."""
    k = len(p)
    tot = 0.0
    for mask in range(1 << k):
        ps = sum(p[i] for i in range(k) if mask >> i & 1)
        tot += (-1) ** bin(mask).count("1") * max(0.0, 1 - ps) ** n
    return tot


def coupon_cdf_product(p, n):
    """P(every bin hit in n independent tests) if bins were independent
    of each other: prod_i (1 - (1 - p_i)^n)."""
    prod = 1.0
    for q in p:
        prod *= 1 - (1 - q) ** n
    return prod


def first_n(cdf, p, delta, cap=2 ** 40):
    """Smallest n with cdf(p, n) >= 1 - delta (cdf rising in n); None
    if no n up to cap reaches it (a bin of probability zero)."""
    hi = 1
    while cdf(p, hi) < 1 - delta:
        if hi > cap:
            return None
        hi *= 2
    lo = max(1, hi // 2)
    while lo < hi:
        mid = (lo + hi) // 2
        if cdf(p, mid) >= 1 - delta:
            hi = mid
        else:
            lo = mid + 1
    return lo


def union_miss(p, n):
    """The union bound on P(some bin missed in n tests):
    sum_i (1 - p_i)^n, valid under any dependence between bins."""
    return sum((1 - q) ** n for q in p)


def union_sum_draws(p, delta):
    """Smallest n with sum_i (1 - p_i)^n <= delta. Bins with p_i = 0
    make the answer infinite (None)."""
    if any(q <= 0 for q in p):
        return None
    return first_n(lambda q, n: 1 - union_miss(q, n), p, delta)


def union_split_draws(p, delta):
    """The cruder form that gives every one of the k bins an equal
    share delta/k of the risk: max_i ln(k/delta) / -ln(1 - p_i). Bins
    with p_i = 0 make the answer infinite (None)."""
    if any(q <= 0 for q in p):
        return None
    k = len(p)
    return max(seeds_to_hit(q, delta / k) for q in p)


# ---- information ----------------------------------------------------

def entropy(probs):
    """Shannon entropy in bits."""
    return -sum(q * math.log2(q) for q in probs if q > 0)


def kl(p, q):
    """KL(p || q) in bits."""
    return sum(a * math.log2(a / b) for a, b in zip(p, q) if a > 0)


def mutual_info(pairs):
    """Plug-in mutual information, in bits, of a list of (a, b)."""
    n = len(pairs)
    ja, jb, jab = Counter(), Counter(), Counter()
    for a, b in pairs:
        ja[a] += 1
        jb[b] += 1
        jab[(a, b)] += 1
    return sum(c / n * math.log2(c * n / (ja[a] * jb[b]))
               for (a, b), c in jab.items())


# ---- species (unseen-bin) estimators --------------------------------

def chao1(counts, n):
    """Abundance form, counts per bin over n draws: S_obs +
    ((n-1)/n) f1^2/(2 f2), or ((n-1)/n) f1(f1-1)/2 when f2 = 0."""
    if n <= 0:
        raise ValueError("chao1: no draws")
    f1 = sum(1 for c in counts if c == 1)
    f2 = sum(1 for c in counts if c == 2)
    sobs = sum(1 for c in counts if c > 0)
    if f2 > 0:
        return sobs + (n - 1) / n * f1 * f1 / (2 * f2)
    return sobs + (n - 1) / n * f1 * (f1 - 1) / 2


def chao2(inc, t):
    """Incidence form, inc[i] = number of the t units (seeds) that hit
    bin i: S_obs + ((t-1)/t) Q1^2/(2 Q2), or ((t-1)/t) Q1(Q1-1)/2 when
    Q2 = 0. Returns (estimate, Q1, Q2)."""
    if t <= 0:
        raise ValueError("chao2: no sampling units")
    q1 = sum(1 for x in inc if x == 1)
    q2 = sum(1 for x in inc if x == 2)
    sobs = sum(1 for x in inc if x > 0)
    if q2 > 0:
        return sobs + (t - 1) / t * q1 * q1 / (2 * q2), q1, q2
    return sobs + (t - 1) / t * q1 * (q1 - 1) / 2, q1, q2


def good_turing(singletons, n):
    """f1 / n (Good 1953, crediting Turing). For abundance data, one
    class per draw, it estimates the probability that the next draw is
    a class not yet seen. For incidence data, Q1 / T over T seeds, it
    estimates the number of new classes in the next seed, which is an
    upper estimate of the chance that the seed shows any."""
    if n <= 0:
        raise ValueError("good_turing: no draws")
    return singletons / n


def chao2_new(inc, t, m=1):
    """Expected new bins in m more units, Q0 (1 - (1 - Q1/(t Q0 + Q1))^m)
    with Q0 from Chao2 (incidence extrapolation)."""
    est, q1, _ = chao2(inc, t)
    q0 = est - sum(1 for x in inc if x > 0)
    if q0 <= 0 or q1 == 0:
        return 0.0
    return q0 * (1 - (1 - q1 / (t * q0 + q1)) ** m)


# ---- small helpers --------------------------------------------------

def quantile(xs, q):
    """The order statistic at floor(q * len): no interpolation, so the
    value printed is one that occurred. None (a run that never finished
    within its cap) sorts above every number."""
    xs = sorted(xs, key=lambda v: (v is None, v or 0))
    return xs[min(len(xs) - 1, int(q * len(xs)))]


class Checks:
    """The numbers a chapter quotes are checked by the example that
    prints them: pinned (a deterministic run must reproduce it) or held
    to a stated tolerance. A failed check is printed and fails the
    run."""

    def __init__(self):
        self.n, self.bad = 0, []

    def _rec(self, ok, text):
        self.n += 1
        if not ok:
            self.bad.append(text)
            print("CHECK FAILED: " + text)

    def pin(self, name, got, want):
        self._rec(got == want, "%s is %r, pinned at %r" % (name, got, want))

    def near(self, name, got, want, tol):
        self._rec(got is not None and abs(got - want) <= tol,
                  "%s is %r, expected %r +/- %r" % (name, got, want, tol))

    def rel(self, name, got, want, frac):
        self._rec(got is not None and abs(got - want) <= frac * abs(want),
                  "%s is %r, expected %r within %g%%"
                  % (name, got, want, 100 * frac))

    def holds(self, name, ok):
        self._rec(bool(ok), name)

    def report(self):
        print("checks: %d of %d hold" % (self.n - len(self.bad), self.n))
        if self.bad:
            sys.exit(1)
