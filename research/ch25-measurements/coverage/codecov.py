"""codecov.py -- code coverage of the repaired FIFO under each of the
four testbenches, the number a team would put beside a kill rate.

Each testbench is built with --coverage against fifo_fixed.sv and run
as mutlib runs it (Chapter 8's two mixes merged by verilator_coverage).
The points of the .dat whose file is fifo_fixed.sv are counted by type
(line, branch, toggle, expr): points hit at least once over points.
Also prints each testbench's own coverage report lines (Chapter 1's
occupancy levels, Chapter 8's covergroup percentage, Chapter 9's
covers). Writes nothing but run.out.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402

os.chdir(mutlib.ROOT)
BUILD = os.path.relpath(os.path.join(HERE, "build"), mutlib.ROOT)


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


def main():
    for tb in mutlib.TBS:
        srcs, top, flags, runs, _ = mutlib.TBS[tb]
        mdir = f"{BUILD}/{tb}"
        ok, _, log = mutlib.build(tb, [mutlib.FIXED], mdir, ["--coverage"])
        assert ok, log
        dats = []
        for i, r in enumerate(runs):
            dat = os.path.abspath(f"{mdir}/run{i}.dat")
            p = subprocess.run([os.path.abspath(f"{mdir}/V{top}")] + r
                               + [f"+verilator+coverage+file+{dat}"],
                               cwd=mdir, capture_output=True, text=True)
            dats.append(dat)
            for l in p.stdout.split("\n"):
                if l.startswith(("coverage:", "PASS", "+bias")):
                    print(f"  {tb}: {l}")
        merged = os.path.abspath(f"{mdir}/merged.dat")
        subprocess.run(["verilator_coverage", "--write", merged] + dats,
                       check=True, capture_output=True)
        pts = points(merged)
        print(f"{tb:14s} " + "  ".join(
            f"{t} {h}/{n} ({100.0 * h / n:.0f}%)"
            for t, (h, n) in sorted(pts.items())))
        if tb == "ch09-sva":
            c = subprocess.run(["grep", "-a", "t\x02user", merged],
                               capture_output=True, text=True).stdout
            for l in c.split("\n"):
                if l:
                    name = l.split("' ")[0].split(".")[-1]
                    print(f"  ch09-sva: cover {name} = {l.split()[-1]}")
    os.system(f"rm -rf {BUILD}")


if __name__ == "__main__":
    main()
