"""run_tools.py -- the full adder through three tools' encoders.

    python3 run_tools.py

Yosys maps full_adder.sv to an and-inverter graph, ABC shares its
equal gates and writes clauses, and Yosys' own SAT pass writes the
clauses it would solve. The three sizes differ; the circuit does not.
ABC's file is read back and taken apart here, because it is not an
encoding of the circuit alone: it also asserts both outputs.
Needs yosys and yosys-abc; prints one "skipped" line without them.
"""
import itertools
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
import dimacs  # noqa: E402

SV = "../truth-table/full_adder.sv"
BUILD = HERE / "build"
READ = f"read_verilog -sv {SV}; proc; opt_clean; "

missing = [p for p in ("yosys", "yosys-abc") if not shutil.which(p)]
if missing:
    print("skipped: missing " + ", ".join(missing))
    sys.exit(0)
BUILD.mkdir(exist_ok=True)


def run(*cmd):
    done = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True,
                          check=True)
    return re.sub(r"\x1b\[[0-9;]*m", "", done.stdout)   # no color codes


version = run("yosys", "-V").split()
print(f"tool: {version[0]} {version[1]}")

# 1. Yosys: gates to two-input ANDs and inverters, as ASCII AIGER.
run("yosys", "-q", "-p", READ + "aigmap; opt_clean; "
    "write_aiger -ascii -symbols build/fa.aag; write_aiger build/fa.aig")
aag = (BUILD / "fa.aag").read_text().split("\nc\n")[0] + "\n"
print("yosys aigmap:     " + aag.splitlines()[0])
same = aag == (HERE.parent / "aig" / "fa.aag").read_text()
print("the regenerated graph equals ../aig/fa.aag:", same)
assert same and aag.startswith("aag 12 3 0 2 9\n")

# 2. ABC: structural hashing, then its own conversion to clauses.
# What is reported is read from the file ABC wrote, not from the
# statistics it prints: the file has one clause more than they say.
out = run("yosys-abc", "-c", "read_aiger build/fa.aig; strash; "
          "print_stats; write_cnf build/fa_abc.cnf")
ands = re.search(r"and =\s*(\d+)", out).group(1)
print(f"abc strash:       and = {ands}")
text = (BUILD / "fa_abc.cnf").read_text().splitlines()
header = [x for x in text if x.startswith("p cnf")][0]
nvars, clauses = dimacs.read(BUILD / "fa_abc.cnf")
assert header.split()[2:] == [str(nvars), str(len(clauses))]
gates = [c for c in clauses if len(c) > 1]
units = [c[0] for c in clauses if len(c) == 1]
used = sorted({abs(x) for c in gates for x in c})


def models(cs, variables):
    """The assignments of the variables that satisfy every clause."""
    return [v for bits in itertools.product((0, 1), repeat=len(variables))
            for v in [dict(zip(variables, bits))]
            if all(any((v[abs(x)] == 1) == (x > 0) for x in c) for c in cs)]


rows = models(gates, used)
left = models(clauses, list(range(1, nvars + 1)))
nodes = all(v[3] == v[5] ^ v[6] and v[2] == v[3] ^ v[7]
            and v[4] == (v[5] + v[6] + v[7] >= 2) for v in rows)
inside = [u for u in units if abs(u) in used]
print(f"abc write_cnf:    {header}")
print(f"  {len(gates)} clauses of 3 literals over variables "
      f"{used[0]} to {used[-1]}, with {len(rows)} models; in each,")
print("  x3 = x5 ^ x6, x2 = x3 ^ x7, x4 = majority(x5, x6, x7):", nodes)
print(f"  {len(units)} unit clauses: {' '.join(map(str, units))}; "
      f"{' and '.join(map(str, inside))} assert sum and cout")
print(f"  models of the whole file: {len(left)}, with x5 x6 x7 = "
      + " ".join(str(left[0][v]) for v in (5, 6, 7)))
assert (ands, header) == ("7", "p cnf 8 18") and nodes
assert (len(gates), used, len(rows)) == (14, [2, 3, 4, 5, 6, 7], 8)
assert all(len(c) == 3 for c in gates)
assert (sorted(units), inside, len(left)) == ([-8, -1, 2, 4], [2, 4], 1)

# 3. Yosys' SAT pass on the question "sum and cout with a low".
run("yosys", "-q", "-p", READ + "sat -set sum 1 -set cout 1 -set a 0 "
    "-dump_cnf build/fa_yosys.cnf")
header = [x for x in (BUILD / "fa_yosys.cnf").read_text().splitlines()
          if x.startswith("p cnf")][0]
print("yosys sat:        " + header)
assert header == "p cnf 40 100"
print(f"one circuit: 17 clauses by hand, {len(gates)} for abc's three "
      f"nodes, {header.split()[3]} from yosys")
