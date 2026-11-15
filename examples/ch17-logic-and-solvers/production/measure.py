"""measure.py -- the chapter's instances under two production solvers.

    python3 measure.py

Writes the four tables the chapter includes (tbl-*.md), with the
solver versions and the date in each caption. The numbers are facts
about those versions on one machine: another release of either solver
gives other conflict counts, and another machine other seconds. That
is why they are in tables with captions and not in any run.out.

Needs `cadical` and `z3` on the PATH and the z3 Python package;
prints "skipped" without them. The book's checker therefore skips
this example wherever CaDiCaL is not installed, and the tables under
version control stay as measured.
"""
import datetime
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
import dimacs  # noqa: E402
import gen  # noqa: E402

LIMIT = 120                             # seconds for one solver call
try:
    import z3
except ImportError:
    z3 = None
missing = [p for p in ("cadical", "z3") if not shutil.which(p)]
if missing or z3 is None:
    print("skipped: missing " + ", ".join(missing or ["z3 for Python"]))
    sys.exit(0)
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)


def tool(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=LIMIT).stdout
    except subprocess.TimeoutExpired:
        return ""


def conflicts(cnf):
    """Conflicts of (z3, CaDiCaL) on one formula; None past the limit."""
    path = str(BUILD / "f.cnf")
    dimacs.write(path, cnf.nvars, cnf.clauses)
    a = re.search(r":sat-conflicts\s+(\d+)", tool("z3", "-st", path))
    b = re.search(r"c conflicts:\s+(\d+)", tool("cadical", path))
    return [int(m.group(1)) if m else None for m in (a, b)]


def cell(n):
    return f"> {LIMIT} s" if n is None else f"{n:,}"


def table(name, header, rows, caption):
    lines = ["| " + " | ".join(header) + " |",
             "|" + "---:|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    (HERE / name).write_text("\n".join(lines) + f"\n\n: {caption}\n")
    print(f"wrote {name}: {len(rows)} rows")


Z3V = z3.get_version_string()
CAV = tool("cadical", "--version").strip()
WHEN = datetime.date.today().isoformat()
WHO = (f"Measured on {WHEN} with z3 {Z3V} and CaDiCaL {CAV} on one "
       f"four-core Linux machine; other versions give other counts.")

rows = []
for n in (8, 16, 32, 64, 128):
    cnf = gen.adder_miter(n)
    rows.append([str(n), f"{cnf.nvars:,}", f"{len(cnf.clauses):,}"]
                + [cell(c) for c in conflicts(cnf)])
table("tbl-adder.md", ["bits", "variables", "clauses", "z3 conflicts",
                       "CaDiCaL conflicts"], rows,
      "The adder miter of this section under two production solvers, "
      "from 8 to 128 bits. " + WHO + " {#tbl-ch17-adder}")

rows = []
for n in range(4, 11):
    cnf = gen.pigeonhole(n)
    rows.append([str(n), str(cnf.nvars), str(len(cnf.clauses))]
                + [cell(c) for c in conflicts(cnf)])
table("tbl-php.md", ["holes", "variables", "clauses", "z3 conflicts",
                     "CaDiCaL conflicts"], rows,
      "Pigeonhole formulas under two production solvers. " + WHO
      + " {#tbl-ch17-php}")

rows = []
for n in range(4, 11):
    cnf = gen.multiplier_miter(n)
    rows.append([str(n), f"{cnf.nvars:,}", f"{len(cnf.clauses):,}"]
                + [cell(c) for c in conflicts(cnf)])
table("tbl-mul.md", ["bits", "variables", "clauses", "z3 conflicts",
                     "CaDiCaL conflicts"], rows,
      "The multiplier miter (is `a*b` equal to `b*a`?) under two "
      "production solvers. " + WHO + " {#tbl-ch17-mul}")


def shift_add(a, b, w):
    acc = z3.BitVecVal(0, w)
    for i in range(w):
        acc = acc + z3.If(z3.Extract(i, i, b) == 1, a << i,
                          z3.BitVecVal(0, w))
    return acc


def seconds(formula):
    s = z3.SolverFor("QF_BV")
    s.set("timeout", LIMIT * 1000)
    s.add(formula)
    start = time.time()
    verdict = str(s.check())
    took = time.time() - start
    return (f"{verdict}, {took:.2f} s" if verdict == "unsat"
            else f"no answer in {LIMIT} s")


rows = []
for w in (4, 6, 8, 9, 10, 11, 32, 64):
    a, b = z3.BitVecs("a b", w)
    row = [str(w), seconds(a * b != b * a)]
    row.append(seconds(shift_add(a, b, w) != shift_add(b, a, w))
               if w <= 11 else "not run")
    rows.append(row)
table("tbl-word.md", ["bits", "`a*b != b*a`",
                      "`shift_add(a,b) != shift_add(b,a)`"], rows,
      "One theorem asked of z3 in two forms: with the solver's own "
      "multiplication on both sides, and with a shift-and-add "
      f"multiplier written out in word-level operators. z3 {Z3V}, "
      f"{WHEN}, one four-core Linux machine, limit {LIMIT} seconds; "
      "the seconds are that machine's. {#tbl-ch17-word}")
