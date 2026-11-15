"""run_reach.py -- the two-entry FIFO's state graph, by enumeration.

    python3 run_reach.py

Counts the states, the reachable ones and the bad ones, names the six
states the design can be in after reset, and asks of three candidate
sets the three questions that make a set an inductive invariant.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from ts import (Aig, evaluate, explicit, fields, initial, names,  # noqa
                show, unpack)

MODEL = HERE.parent / "common" / "fifo_ptrs2.aag"
aig, name = Aig(MODEL), names(MODEL)
n, inputs = len(aig.latches), range(1 << len(aig.inputs))
states = range(1 << n)
print(f"model: {MODEL.name}, {len(aig.inputs)} inputs, {n} latches, "
      f"{len(aig.ands)} ANDs")
print("latches: " + " ".join(name))


def reg(s):
    return fields(unpack(s, n), name)


def text(s):
    return show(unpack(s, n)[1:], name[1:])     # without `started`


def steps(s):
    """The successors of s under the inputs the environment allows."""
    return {nxt for nxt, ok, _ in (evaluate(aig, s, x) for x in inputs)
            if ok}


def is_bad(s):
    return any(ok and bad for _, ok, bad in
               (evaluate(aig, s, x) for x in inputs))


# The names are a sidecar file, so check them against the logic: the
# reset cycle leads to the empty state, and from there one accepted
# write moves the write pointer and the count and nothing else.
empty = next(iter(steps(initial(aig)[0])))
assert reg(empty) == {"started": 1, "wr_ptr": 0, "rd_ptr": 0, "count": 0}
after = sorted(text(s) for s in steps(empty) if s != empty)
assert after == ["wr_ptr=1 rd_ptr=0 count=1"], after
print(f"check of the names: from the empty state the only move is to "
      f"{after[0]}")

reach, first_bad = explicit(aig)
assert first_bad is None
bad = {s for s in states if is_bad(s)}
post = [s for s in states if reg(s)["started"]]
print(f"states: {len(states)}; reachable: {len(reach)}; bad: {len(bad)}")
print(f"  reset cycle (started=0): {len(states) - len(post)} states, "
      f"{sum(s not in post for s in reach)} reachable, "
      f"{sum(s not in post for s in bad)} bad")
live = sorted((s for s in post if s in reach), key=lambda s: (reach[s], s))
idle = [s for s in post if s not in reach and s not in bad]
print(f"  after reset (started=1): {len(post)} states, {len(live)} "
      f"reachable, {sum(s in post for s in bad)} bad, {len(idle)} "
      f"neither")
print("the reachable states after reset, by the step that first "
      "reaches them:")
for s in live:
    print(f"  step {reach[s]}  {text(s)}")
print("the bad states:")
for s in sorted(bad):
    print(f"          {text(s)}")
print("allowed by the property and never reached:")
for s in idle:
    print(f"          {text(s)}")
print(f"deepest reachable state: step {max(reach.values())} "
      f"(the reset cycle is step 0)")


def distance(a, b):
    """Steps on a shortest path from a to b."""
    seen, front, d = {a}, [a], 0
    while b not in seen:
        front = [t for s in front for t in sorted(steps(s))
                 if t not in seen and not seen.add(t)]
        d += 1
    return d


far = max(distance(a, b) for a in live for b in live)
print(f"longest shortest path between two of the {len(live)}: "
      f"{far} steps")


# ---- three candidate sets, three questions each -----------------------
def ask(title, keep):
    """keep(registers) chooses among the states after reset; every
    reset-cycle state is in the set."""
    inside = {s for s in states if s not in post or keep(reg(s))}
    starts = all(s in inside for s in initial(aig))
    leak = sorted((s, t) for s in inside for t in steps(s)
                  if t not in inside)
    safe = not (inside & bad)
    yes = {True: "yes", False: "NO"}
    print(f"{title}: {sum(s in post for s in inside)} states after "
          f"reset")
    print(f"  contains the reset states: {yes[starts]};  closed under "
          f"a step: {yes[not leak]};  excludes bad: {yes[safe]}")
    if leak:
        s, t = leak[0]
        print(f"  a step that leaves it: {text(s)}  ->  {text(t)}")
    return starts, not leak, safe


print("candidate invariants:")
a = ask("the property (empty implies equal pointers)",
        lambda r: r["count"] != 0 or r["wr_ptr"] == r["rd_ptr"])
b = ask("the helper (count[0] == wr_ptr ^ rd_ptr)",
        lambda r: r["count"] & 1 == r["wr_ptr"] ^ r["rd_ptr"])
c = ask("the reachable states",
        lambda r: any(reg(s) == r for s in live))
assert (len(states), len(reach), len(live), len(bad), len(idle)) == \
    (32, 22, 6, 2, 8)
assert a == (True, False, True) and b == c == (True, True, True)
print("verdict: the property is true, and it is not inductive")
