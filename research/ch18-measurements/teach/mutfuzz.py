"""mutfuzz.py -- every single-edge mutant of a model: flip the
inversion of one AND input or one latch's next-state literal, then
compare the teaching IC3 with explicit-state search.

    python3 mutfuzz.py model.aag
"""
import collections
import copy
import sys
from ts import Aig, explicit
import ic3 as ic3mod
from fuzz import check_trace, check_inv

base = Aig(sys.argv[1])
tally = collections.Counter()
sites = [("and", i, j) for i in range(len(base.ands)) for j in (1, 2)] + \
        [("latch", i, 1) for i in range(len(base.latches))] + [("bad", 0, 0)]
for kind, i, j in sites:
    aig = copy.deepcopy(base)
    if kind == "and":
        aig.ands[i][j] ^= 1
    elif kind == "latch":
        aig.latches[i][1] ^= 1
    else:
        aig.bads[0] ^= 1
    reach, depth = explicit(aig)
    want = "proven" if depth is None else "cex"
    e = ic3mod.Ic3(aig)
    verdict, what = e.run()
    ok = verdict == want
    if ok and verdict == "cex":
        ok = check_trace(aig, what) and len(what) - 1 == depth
    if ok and verdict == "proven":
        ok = check_inv(aig, what, reach) and all(ic3mod.certify(aig, what))
        tally["lemmas max"] = max(tally["lemmas max"], len(what))
        tally["frames max"] = max(tally["frames max"], len(e.frames) - 1)
    tally[verdict] += 1
    tally["WRONG"] += not ok
    tally["cex depth max"] = max(tally["cex depth max"], depth or 0)
print(sys.argv[1], dict(tally))
