"""dimacs.py -- read and write CNF in the DIMACS format.

A file is a header "p cnf VARIABLES CLAUSES" and then the clauses,
each a list of nonzero integers ended by 0. The integer v is variable
v, -v is its complement. Lines that start with "c" are comments.
"""


def read(path):
    """Return (number of variables, list of clauses) from a .cnf file."""
    nvars, clauses, cur = 0, [], []
    with open(path) as f:
        for line in f:
            if line.startswith("c") or not line.strip():
                continue
            if line.startswith("p"):
                nvars = int(line.split()[2])
                continue
            for tok in line.split():
                if tok == "0":
                    clauses.append(cur)
                    cur = []
                else:
                    cur.append(int(tok))
    return nvars, clauses


def write(path, nvars, clauses, comment=""):
    with open(path, "w") as f:
        for line in comment.splitlines():
            f.write(f"c {line}\n")
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")
