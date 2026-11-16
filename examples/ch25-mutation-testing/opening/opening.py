"""opening.py -- the chapter's first table: code coverage of the
repaired FIFO beside the kill count, for the book's four testbenches.

    python3 opening.py

1. Coverage: each testbench built with --coverage against
   fifo_fixed.sv and run as the kill runs run it (the coverage
   chapter's two mixes merged by verilator_coverage). The points of
   the database whose file is fifo_fixed.sv are counted by type
   (Verilator's line, branch, expression and toggle points): points
   hit at least once over points. Each testbench's own report lines
   are printed beside it.
2. Kills: the 44 source mutants through the source schema, as
   source-sim/ runs them.
Then the table, one row for each testbench. Verilator only; about 30
seconds.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402

B = HERE / "build"
TYPES = ["line", "branch", "expr", "toggle"]


def points(dat):
    """{type: (hit, total)} over fifo_fixed.sv's points in DAT."""
    out = {}
    for line in open(dat, encoding="latin-1"):
        if not line.startswith("C '"):
            continue
        key, cnt = line[3:].rsplit("' ", 1)
        f = dict(x.split("\x02", 1) for x in key.split("\x01")[1:])
        if not f.get("f", "").endswith("fifo_fixed.sv"):
            continue
        h, t = out.get(f["t"], (0, 0))
        out[f["t"]] = (h + (int(cnt) > 0), t + 1)
    return out


def cover(tb):
    srcs, top, flags, runs, _ = mutlib.TBS[tb]
    mdir = B / "cov" / tb
    ok, _, log = mutlib.build(tb, [mutlib.FIXED], mdir, ["--coverage"],
                              [f for f in flags if f != "--coverage"])
    assert ok, log[-2000:]
    dats, said = [], []
    for i, r in enumerate(runs):
        dat = mdir / f"run{i}.dat"
        r = [a for a in r if a != mutlib.NOCOV]
        p = subprocess.run([str(mdir / f"V{top}")] + r
                           + [f"+verilator+coverage+file+{dat}"],
                           cwd=mdir, capture_output=True, text=True)
        dats.append(str(dat))
        said += [x for x in p.stdout.splitlines()
                 if x.startswith(("coverage:", "PASS", "+bias"))]
    merged = mdir / "merged.dat"
    subprocess.run(["verilator_coverage", "--write", str(merged)] + dats,
                   check=True, capture_output=True)
    covers = []
    if tb == "ch09-sva":
        for line in open(merged, encoding="latin-1"):
            if "t\x02user" in line and "_C" in line:
                name = line.split("' ")[0].split("\x02")[-1].split(".")[-1]
                covers.append(f"cover {name} = {line.split()[-1]}")
    return points(merged), said, covers


def main():
    C = mutlib.Checks()
    print(f"tools: {mutlib.version('verilator')}")
    print(f"design: {mutlib.FIXED}")
    cov = dict(zip(mutlib.NAMES, mutlib.pmap(cover, mutlib.NAMES)))
    dirs, _ = srcmut.build_schema(B / "schema", mutlib.NAMES)
    n = len(srcmut.mutants())
    v = srcmut.run_schema(dirs, range(n + 1))
    kills = {tb: sum(v[(k, tb)] in mutlib.DEAD for k in range(1, n + 1))
             for tb in mutlib.NAMES}
    C.pin("control", [v[(0, tb)] for tb in mutlib.NAMES],
          ["survived"] * 4)
    print("1. each testbench's own report")
    for tb in mutlib.NAMES:
        pts, said, covers = cov[tb]
        for x in said + covers:
            print(f"  {tb}: {x}")
    print("2. coverage of fifo_fixed.sv (Verilator points hit / points)")
    print("   and kills of the 44 source mutants")
    print(f"  {'testbench':14s}" + "".join(f"{t:>13s}" for t in TYPES)
          + "  kills")
    got = {}
    for tb in mutlib.NAMES:
        pts = cov[tb][0]
        got[tb] = [pts.get(t, (0, 0)) for t in TYPES]
        print(f"  {tb:14s}" + "".join(
            f"{f'{h}/{t} {round(100.0 * h / t)}%':>13s}"
            for h, t in got[tb]) + f"  {kills[tb]:2d}/{n}")
    for tb in mutlib.NAMES:
        h, t = got[tb][3]
        print(f"  {tb:14s} toggle {h}/{t} = {100.0 * h / t:.1f}%")
    C.pin("coverage points", got, {
        "ch01-directed": [(4, 4), (6, 6), (7, 8), (80, 330)],
        "ch01-random": [(4, 4), (6, 6), (8, 8), (329, 330)],
        "ch08-coverage": [(4, 4), (6, 6), (8, 8), (326, 330)],
        "ch09-sva": [(4, 4), (6, 6), (8, 8), (327, 330)]})
    C.pin("kills", [kills[tb] for tb in mutlib.NAMES], [34, 35, 0, 22])
    C.report()
    print("verdict: equal code coverage, kills from 0 to 35 of 44")


if __name__ == "__main__":
    main()
