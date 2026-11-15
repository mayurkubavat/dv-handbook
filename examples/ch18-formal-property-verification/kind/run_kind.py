"""run_kind.py -- induction on the two-entry FIFO: where the step
case fails, what its model looks like, and what makes it succeed.

    python3 run_kind.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from ts import Aig, QUERIES, explicit, names, show  # noqa: E402
from kind import kind  # noqa: E402

COMMON = HERE.parent / "common"
CH17 = HERE.parent.parent / "ch17-logic-and-solvers" / "fifo-unroll"
MODEL = COMMON / "fifo_ptrs2.aag"
aig, name = Aig(MODEL), names(MODEL)
reach, _ = explicit(aig)


def text(bits):
    return show(bits[1:], name[1:])         # without `started`


def reachable(bits):
    return sum(b << i for i, b in enumerate(bits)) in reach


def run(simple, max_k):
    """One run, printed a line per k; returns kind()'s result."""
    QUERIES[0] = 0

    def line(msg):
        head, sep, bits = msg.partition(", from state ")
        if sep:
            state = tuple(int(b) for b in bits)
            msg = f"{head}, starting in {text(state)}"
        print("  " + msg)
    result = kind(aig, max_k, simple, line)
    print(f"  {result[0]} at k = {result[1]}, {QUERIES[0]} queries")
    return result


def path(title, states):
    print(title)
    for i, s in enumerate(states):
        note = "" if reachable(s) else "   not reachable"
        if i == len(states) - 1:
            note += "   BAD: empty, pointers apart"
        print(f"  state {i}  {text(s)}{note}")
    twice = sorted((i, j) for i in range(len(states))
                   for j in range(i + 1, len(states))
                   if states[i] == states[j])
    print("  repeated states: " + (", ".join(
        f"{i} and {j}" for i, j in twice) if twice else "none"))
    return twice


print(f"=== induction on {MODEL.name}, k = 0 to 8")
plain = run(False, 8)
assert plain[:2] == ("undetermined", 8)

print("=== the step case at k = 3, decoded")
QUERIES[0] = 0
_, _, p3 = kind(aig, 3)
twice = path("a counterexample to induction: three good states, "
             "then a bad one", p3)
assert text(p3[0]) == "wr_ptr=1 rd_ptr=1 count=3" and twice == [(0, 2)]
assert not any(reachable(s) for s in p3)

print("=== the same with pairwise different states")
simple = run(True, 8)
assert simple[:2] == ("proven", 7) and QUERIES[0] == 16

print("=== the step case at k = 3 with different states, decoded")
_, _, s3 = kind(aig, 3, simple=True)
assert path("three good states, all different, then a bad one",
            s3) == []
assert not reachable(s3[0])

print("=== a design with a bug: the first chapter's FIFO")
QUERIES[0] = 0
verdict, k, trace = kind(Aig(CH17 / "fifo_bmc.aag"), 20)
print(f"  {verdict}: the base case is satisfiable at k = {k}, "
      f"{QUERIES[0]} queries")
assert (verdict, k, len(trace)) == ("cex", 16, 17)
print("verdict: not inductive at any k tried; proven at k = 7 with "
      "unique states")
