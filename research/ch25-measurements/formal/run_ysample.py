"""run_ysample.py -- the formal half for a uniform random sample of
the Yosys netlist population: for each sampled mutation, a netlist
with that one mutation applied (module fifo_m), the book's FIFO
property set against it by BMC (3 s per property), and the miter
against the repaired FIFO (BMC 10 s, in-house IC3 30 s, rIC3 120 s).

  run_ysample.py N SEED    sample N of the mutations listed in
                           ../yosys-mutants/mutants.txt.gz

Writes ysample.tsv: id, the properties that found a counterexample
(or '-'), the miter verdict and its detail, the seconds each took.
"""
import gzip
import os
import random
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402
import formal  # noqa: E402

BUILD = os.path.join(HERE, "build-y")
LIST = os.path.join(HERE, "..", "yosys-mutants", "mutants.txt.gz")


def netlist(k, cmd):
    """The netlist with mutation K applied, module renamed fifo_m."""
    out = os.path.join(BUILD, f"y{k}.v")
    cmd = re.sub(r"-ctrl mutsel 14 \d+ ", "", cmd.strip())
    ys = (f"read_verilog -sv {mutlib.FIXED}; prep -top fifo; {cmd}; "
          f"rename fifo fifo_m; write_verilog -noattr {out}")
    subprocess.run(["yosys", "-q", "-p", ys], cwd=mutlib.ROOT,
                   capture_output=True, check=True)
    return out


def job(arg):
    k, cmd = arg
    path = netlist(k, cmd)
    r, tk, out = formal.kill(("net", path), f"{BUILD}/k/{k}", bmc="3s")
    if not r:
        return k, "ERROR " + out[-200:].replace("\n", " "), "", "", tk, 0
    cex = [f"{p}@{d}" for p, (s, d) in r.items() if s == "cex"]
    v, det, te = formal.equiv(("net", path), f"{BUILD}/e/{k}")
    return k, ",".join(cex) or "-", v, det, tk, te


def main():
    n, seed = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    os.makedirs(BUILD, exist_ok=True)
    cmds = gzip.open(LIST, "rt").read().split("\n")
    cmds = [c for c in cmds if c and "mode none" not in c]
    pick = sorted(random.Random(seed).sample(range(1, len(cmds) + 1), n))
    res = mutlib.pmap(job, [(k, cmds[k - 1]) for k in pick])
    with open(os.path.join(HERE, "ysample.tsv"), "w") as f:
        f.write("id\tkilled_by\tmiter\tdetail\tkill_s\tmiter_s\n")
        for k, cex, v, det, tk, te in res:
            f.write(f"{k}\t{cex}\t{v}\t{det}\t{tk:.1f}\t{te:.1f}\n")
    print(f"sample: {n} of {len(cmds)} mutations, seed {seed}")
    print(f"property set kills {sum(r[1] != '-' for r in res)} of {n}")
    for v in ("differs", "equivalent", "unknown", "error"):
        print(f"  miter {v}: {sum(r[2] == v for r in res)}")
    print(f"wall {time.time() - t0:.0f} s, 4 workers")
    os.system(f"rm -rf {BUILD}")


if __name__ == "__main__":
    main()
