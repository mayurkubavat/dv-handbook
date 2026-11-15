"""unroll_z3.py -- the FIFO's occupancy logic, unrolled by hand.

    python3 unroll_z3.py [bug|fixed] [max_bound]

The state is the design's count register and the checker's occ. One
step of the design is a function from (state, inputs) to the next
state, written here with z3 bit-vectors straight from the RTL. State
0 is the state after reset: both registers zero. Bound k chains k
steps, each with its own copy of the inputs, and asks whether the
state after them can be bad. Prints "skipped" without z3.
"""
import sys

try:
    import z3
except ImportError:
    print("skipped: the z3 Python package is not installed")
    sys.exit(0)


def unroll(bug, max_bound):
    """The first bound with a counterexample, or None."""
    width = 4 if bug else 5             # width of the count register
    full_at = 15 if bug else 16         # the value full is decoded from

    def step(count, occ, wr_en, rd_en):
        """Next (count, occ) after one clock edge out of reset."""
        full, empty = count == full_at, count == 0
        do_write = z3.And(wr_en, z3.Not(full))
        do_read = z3.And(rd_en, z3.Not(empty))
        nxt = z3.If(z3.And(do_write, z3.Not(do_read)), count + 1,
                    z3.If(z3.And(do_read, z3.Not(do_write)), count - 1,
                          count))
        occ_nxt = (occ + z3.If(do_write, z3.BitVecVal(1, 5), 0)
                   - z3.If(do_read, z3.BitVecVal(1, 5), 0))
        return nxt, occ_nxt

    count, occ = z3.BitVecVal(0, width), z3.BitVecVal(0, 5)
    for k in range(max_bound + 1):
        s = z3.Solver()
        s.add(count == full_at, occ != 16)      # full, and not sixteen
        if s.check() == z3.sat:
            if k:
                print(f"   bounds 0 to {k - 1}: unsat")
            print(f"   bound {k}: sat")
            return k
        wr_en, rd_en = z3.Bools(f"wr_en@{k} rd_en@{k}")
        count, occ = step(count, occ, wr_en, rd_en)
    print(f"   bounds 0 to {max_bound}: unsat")
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        unroll(sys.argv[1] == "bug", int(sys.argv[2]))
        sys.exit(0)
    print("1. the FIFO as shipped: full decoded from count == 15")
    k = unroll(True, 20)
    assert k == 15
    print(f"   full with occ != 16 is reachable {k} steps after reset")
    print("2. the FIFO repaired: a 5-bit count, full at 16")
    k = unroll(False, 20)
    assert k is None
    print("   no counterexample within 20 steps of reset")
