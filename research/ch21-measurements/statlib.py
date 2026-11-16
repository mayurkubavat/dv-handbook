"""statlib.py -- the few statistical functions the Chapter 21 experiments
need, written on the standard library alone (the book's Python
environment has no numpy or scipy).

Each function names the formula it implements; the experiments check
the ones that matter against simulation.
"""
import math


# ---- special functions ---------------------------------------------

def gammainc_upper_reg(a, x):
    """Q(a, x) = Gamma(a, x) / Gamma(a), the regularized upper incomplete
    gamma function, by series for x < a + 1 and by continued fraction
    otherwise (Numerical Recipes, section 6.2, rewritten)."""
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


def kolmogorov_sf(lam):
    """P(sqrt(n) D_n > lam) in the limit n -> infinity (Kolmogorov 1933):
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


# ---- binomial bounds -----------------------------------------------

def binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p), summed in log space."""
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    lp, lq = math.log(p), math.log1p(-p)
    tot = 0.0
    for i in range(0, k + 1):
        lc = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
        tot += math.exp(lc + i * lp + (n - i) * lq)
    return min(1.0, tot)


def _bisect(f, lo, hi, it=200):
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
    a = (1 - conf) / 2
    return cp_lower(x, n, a), cp_upper(x, n, a)


# ---- coupon collector ----------------------------------------------

def coupon_expect_equal(k):
    """E[T] = k * H_k for k equally likely bins."""
    return k * sum(1.0 / i for i in range(1, k + 1))


def coupon_expect(p, steps=200000):
    """E[T] = integral_0^inf (1 - prod_i (1 - exp(-p_i t))) dt
    (Flajolet, Gardy and Thimonier 1992), by the trapezoid rule on a
    range that reaches far past the slowest bin."""
    pmin = min(q for q in p if q > 0)
    tmax = 60.0 / pmin
    h = tmax / steps
    tot = 0.0
    prev = 1.0
    for i in range(1, steps + 1):
        t = i * h
        prod = 1.0
        for q in p:
            prod *= -math.expm1(-q * t)
        cur = 1.0 - prod
        tot += (prev + cur) * h / 2
        prev = cur
        if cur < 1e-14:
            break
    return tot


def coupon_cdf_poisson(p, n):
    """P(T <= n) ~ prod_i (1 - exp(-n p_i)): the Poissonization, exact
    for a Poisson(n) number of draws and close for n draws."""
    prod = 1.0
    for q in p:
        prod *= -math.expm1(-n * q)
    return prod


def coupon_cdf_exact(p, n):
    """P(T <= n) by inclusion-exclusion over subsets: sum over S of
    (-1)^|S| (1 - p(S))^n. Exponential in len(p); use for <= 20 bins."""
    k = len(p)
    tot = 0.0
    for mask in range(1 << k):
        ps = 0.0
        bits = 0
        for i in range(k):
            if mask >> i & 1:
                ps += p[i]
                bits += 1
        tot += (-1) ** bits * (1 - ps) ** n
    return tot


def draws_for_all(p, delta, cdf=coupon_cdf_poisson):
    """Smallest n with P(every bin hit within n draws) >= 1 - delta."""
    lo, hi = 1, 1
    while cdf(p, hi) < 1 - delta:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if cdf(p, mid) >= 1 - delta:
            hi = mid
        else:
            lo = mid + 1
    return lo


def union_bound_draws(p, delta):
    """n >= max_i ln(k/delta)/(-ln(1-p_i)): every bin's miss probability
    held below delta/k, so the union bound gives P(any miss) <= delta."""
    k = len(p)
    return max(math.ceil(math.log(k / delta) / -math.log1p(-q)) for q in p)


# ---- information ----------------------------------------------------

def entropy(probs):
    return -sum(q * math.log2(q) for q in probs if q > 0)


def kl(p, q):
    return sum(a * math.log2(a / b) for a, b in zip(p, q) if a > 0)
