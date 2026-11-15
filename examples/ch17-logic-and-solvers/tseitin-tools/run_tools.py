"""run_tools.py -- the full adder through three tools' encoders.

    python3 run_tools.py

Yosys maps full_adder.sv to an and-inverter graph, ABC shares its
equal gates and writes clauses, and Yosys' own SAT pass writes the
clauses it would solve. The three sizes differ; the circuit does not.
Needs yosys and yosys-abc; prints one "skipped" line without them.
"""
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
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
out = run("yosys-abc", "-c", "read_aiger build/fa.aig; strash; "
          "print_stats; write_cnf build/fa_abc.cnf")
ands = re.search(r"and =\s*(\d+)", out).group(1)
stats = re.search(r"Vars =\s*(\d+)\. Clauses =\s*(\d+)\.", out)
print(f"abc strash:       and = {ands}")
print(f"abc write_cnf:    Vars = {stats.group(1)}. "
      f"Clauses = {stats.group(2)}.")
assert (ands, stats.groups()) == ("7", ("8", "17"))

# 3. Yosys' SAT pass on the question "sum and cout with a low".
run("yosys", "-q", "-p", READ + "sat -set sum 1 -set cout 1 -set a 0 "
    "-dump_cnf build/fa_yosys.cnf")
header = [x for x in (BUILD / "fa_yosys.cnf").read_text().splitlines()
          if x.startswith("p cnf")][0]
print("yosys sat:        " + header)
assert header == "p cnf 40 100"
print("one circuit: 17 clauses by hand, 17 others from abc, 100 from yosys")
