"""run_helper.py -- one helper invariant, and what it buys.

    python3 run_helper.py

The helper says that the low bits of the occupancy are the distance
between the pointers. Three runs of kind.py: the helper alone, as an
assertion; the pointer property with the helper assumed, at two
entries and at four; and, by enumeration, where the helper's states
lie among the property's.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for sub in ("common", "kind"):
    sys.path.insert(0, str(HERE.parent / sub))
from ts import (Aig, QUERIES, evaluate, explicit, fields,  # noqa: E402
                names, show, unpack)
from kind import kind  # noqa: E402

COMMON = HERE.parent / "common"


def prove(file, what, want_k):
    QUERIES[0] = 0
    verdict, k, _ = kind(Aig(COMMON / file), 8)
    print(f"{what}\n  {file}: {verdict} at k = {k}, {QUERIES[0]} queries")
    assert (verdict, k) == ("proven", want_k), (verdict, k)


print("=== the helper alone: CountPtrs_A asserted, nothing assumed")
prove("count_ptrs2.aag", "two entries", 1)
print("=== the pointer property with the helper as a constraint")
prove("fifo_ptrs2_h.aag", "two entries", 0)
prove("fifo_ptrs4_h.aag", "four entries", 0)
print("  k = 0: no state that satisfies the helper is bad, so the "
      "proof needs no step")

print("=== the helper's states among the property's, two entries")
MODEL = COMMON / "fifo_ptrs2.aag"
aig, name = Aig(MODEL), names(MODEL)
n, inputs = len(aig.latches), range(1 << len(aig.inputs))
reach, _ = explicit(aig)
post = [s for s in range(1 << n) if s & 1]      # started = 1


def reg(s):
    return fields(unpack(s, n), name)


prop = {s for s in post
        if reg(s)["count"] != 0 or reg(s)["wr_ptr"] == reg(s)["rd_ptr"]}
helper = {s for s in post
          if reg(s)["count"] & 1 == reg(s)["wr_ptr"] ^ reg(s)["rd_ptr"]}
live = {s for s in post if s in reach}
print(f"  allowed by the property: {len(prop)}; by the helper: "
      f"{len(helper)}; reachable: {len(live)}")
print(f"  reachable within helper within property: "
      f"{live < helper < prop}")
closed = all(nxt in helper for s in helper for nxt, ok, _ in
             (evaluate(aig, s, x) for x in inputs) if ok)
print(f"  a step from a helper state stays in the helper: {closed}")
print("  helper states that are never reached:")
for s in sorted(helper - live):
    print("    " + show(unpack(s, n)[1:], name[1:]))
assert (len(prop), len(helper), len(live)) == (14, 8, 6)
assert live < helper < prop and closed
print("verdict: the helper is inductive, and with it the property "
      "needs no induction")
