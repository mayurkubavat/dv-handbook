"""fifo_chain.py -- an exact Markov chain of the first chapter's FIFO
under a random push/pop mix, the formula the simulator runs are checked
against.

The state is the occupancy the monitor counts. Each sampled cycle draws
a push request with probability pw and a pop request with probability
pr, independently. A push is accepted when the FIFO does not show full,
a pop when it does not show empty. The buggy FIFO shows full at 15
entries (full_at=15), the repaired one at 16.

Two events are computed exactly:
  trigger   a push requested while the FIFO shows full, which is the
            "push while full" line of the coverage chapter's testbench;
  reach     the occupancy reaching a level, which is what a checker of
            the full flag reports as the bug (it sees full raised at
            15 entries).
"""


def _step(dist, pw, pr, full_at):
    """One cycle: (new distribution, probability of a trigger now)."""
    new = [0.0] * len(dist)
    trig = 0.0
    for o, m in enumerate(dist):
        if m == 0.0:
            continue
        full = o == full_at
        for w, pwk in ((1, pw), (0, 1 - pw)):
            for r, prk in ((1, pr), (0, 1 - pr)):
                q = m * pwk * prk
                if w and full:
                    trig += q         # absorbed: the event has happened
                    continue
                o2 = o + (1 if w and not full else 0) - (1 if r and o else 0)
                new[o2] += q
    return new, trig


def trigger_pmf(pw, pr, cycles, full_at=15):
    """P(the first trigger is at sampled cycle c), c = 1..cycles."""
    dist = [0.0] * (full_at + 1)
    dist[0] = 1.0
    out = []
    for _ in range(cycles):
        dist, t = _step(dist, pw, pr, full_at)
        out.append(t)
    return out


def p_trigger(pw, pr, cycles, full_at=15):
    """P(at least one push requested while full within cycles)."""
    return sum(trigger_pmf(pw, pr, cycles, full_at))


def p_reach(level, pw_of, pr_of, cycles, full_at=15):
    """P(the occupancy reaches level within cycles), where pw_of(c) and
    pr_of(c) give the push and pop probabilities at cycle c (0-based);
    a number stands for a constant. A random test that fills early and
    drains late changes them part way through."""
    if not callable(pw_of):
        pw_of = (lambda v: lambda c: v)(pw_of)
    if not callable(pr_of):
        pr_of = (lambda v: lambda c: v)(pr_of)
    dist = [0.0] * (full_at + 1)
    dist[0] = 1.0
    hit = 0.0
    for c in range(cycles):
        pw, pr = pw_of(c), pr_of(c)
        new = [0.0] * len(dist)
        for o, m in enumerate(dist):
            if m == 0.0:
                continue
            full = o == full_at
            for w, pwk in ((1, pw), (0, 1 - pw)):
                for r, prk in ((1, pr), (0, 1 - pr)):
                    q = m * pwk * prk
                    o2 = o + (1 if w and not full else 0) \
                        - (1 if r and o else 0)
                    if o2 >= level:
                        hit += q
                    else:
                        new[o2] += q
        dist = new
    return hit
