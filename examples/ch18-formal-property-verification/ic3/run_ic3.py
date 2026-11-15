"""run_ic3.py -- IC3 on the two-entry FIFO, with every event printed.

    python3 run_ic3.py

Prints each bad state found in the frontier, each proof obligation,
each lemma before and after generalization, and the number of lemmas
in each frame; then the invariant, decoded and compared with the
reachable set; then three other models in a line each.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from ts import Aig, QUERIES, explicit, names, show  # noqa: E402
from ic3 import Ic3, certify  # noqa: E402

COMMON = HERE.parent / "common"
CH17 = HERE.parent.parent / "ch17-logic-and-solvers" / "fifo-unroll"
MODEL = COMMON / "fifo_ptrs2.aag"
aig, name = Aig(MODEL), names(MODEL)


def text(cube):
    """A cube by latch name. Every cube of this model has started=1,
    which is left out."""
    return " ".join(f"{name[i]}={v}" for i, v in cube if name[i]
                    != "started") or "started=1"


def state(cube):
    """A whole state by register: count[1] and count[0] as count."""
    return show([v for _, v in cube][1:], name[1:])


def sizes(e):
    return " ".join(f"{i}:{len(level)}"
                    for i, level in enumerate(e.frames) if i)


def event(what, i, *rest):
    if what == "bad":
        print(f"  bad state in F{i}: {state(rest[0])}")
    elif what == "obligation":
        print(f"    predecessor of ({state(rest[1])}) in F{i}: "
              f"{state(rest[0])}")
    elif what == "lemma":
        print(f"    ({state(rest[0])}) has no predecessor in F{i - 1}; "
              f"lemma at level {i}:\n"
              f"        never {text(rest[1])}")
    elif what == "frontier":
        print(f"frontier {i} is clear.  lemmas by level: {sizes(engine)}")
    elif what == "pushed":
        print(f"         after propagation:    {sizes(engine)}")
    elif what == "fixed":
        print(f"         after propagation:    {sizes(engine)}\n"
              f"level {i} is empty: F{i} = F{i + 1}, a fixed point")


print(f"=== IC3 on {MODEL.name}")
QUERIES[0] = 0
engine = Ic3(aig, event)
verdict, inv = engine.run()
search = QUERIES[0]
checks = certify(aig, inv)
print(f"{verdict}: an invariant of {len(inv)} lemmas, "
      f"frontier {len(engine.frames) - 2}")
print(f"queries: {search} in the search, {QUERIES[0] - search} in "
      f"the three checks")
assert (verdict, len(inv), search, QUERIES[0]) == ("proven", 6, 153, 160)

print("=== the invariant, decoded")
for n, cube in enumerate(inv, 1):
    inside = [m for m, other in enumerate(inv, 1)
              if other != cube and set(other) <= set(cube)]
    note = f"   (follows from lemma {inside[0]})" if inside else ""
    print(f"  {n}. never {text(cube)}{note}")
assert all(dict(c).get(0) == 1 for c in inv)    # each has started=1
reach, _ = explicit(aig)
allowed = {s for s in range(1 << len(aig.latches))
           if not any(all((s >> i) & 1 == v for i, v in c) for c in inv)}
print(f"states the lemmas allow: {len(allowed)};  reachable states: "
      f"{len(reach)};  the same set: {allowed == set(reach)}")
print(f"the three checks: reset inside {checks[0]}, closed under a "
      f"step {checks[1]}, no bad state {checks[2]}")
assert allowed == set(reach) and len(allowed) == 22 and all(checks)

print("=== other models, one line each")
want = {"counter.aag": ("cex", 6), "fifo_bmc.aag": ("cex", 16),
        "count_ptrs2.aag": ("proven", 5), "fifo_ptrs4.aag": ("proven", 32)}
for path in (CH17 / "counter.aag", CH17 / "fifo_bmc.aag",
             COMMON / "count_ptrs2.aag", COMMON / "fifo_ptrs4.aag"):
    QUERIES[0] = 0
    model = Aig(path)
    e = Ic3(model)
    verdict, what = e.run()
    if verdict == "cex":
        size = len(what) - 1
        line = f"cex, {size} steps"
    else:
        size = len(what)
        assert all(certify(model, what))    # counted in the queries
        line = f"proven, {size} lemmas, frontier {len(e.frames) - 2}"
    print(f"  {path.name} ({len(model.latches)} latches): {line}; "
          f"{QUERIES[0]} queries")
    assert (verdict, size) == want[path.name], (verdict, size)
print("verdict: the invariant IC3 built allows exactly the reachable "
      "states")
