"""run_src.py -- the formal half for the 44 source mutants: the book's
FIFO property set against each mutant by BMC (5 s per property), and
the miter of each mutant against the repaired FIFO (BMC 10 s, then
in-house IC3 30 s, then rIC3 120 s). The repaired FIFO itself is the
control for the property set (no counterexample expected).

Writes src_formal.tsv: id, the properties that found a counterexample
with their depths (or '-'), the miter verdict and its detail, and the
seconds each part took. A mutant InFormal's front end refuses is
recorded as rejected, with the tool's message.
"""
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402
import formal  # noqa: E402

BUILD = os.path.join(HERE, "build")
SRC = os.path.join(BUILD, "src")


def job(mid):
    path = (f"{mutlib.ROOT}/{mutlib.FIXED}" if mid == "orig"
            else f"{SRC}/{mid}.sv")
    r, tk, out = formal.kill(("src", path), f"{BUILD}/k/{mid}")
    if not r:
        return mid, "ERROR " + out[-200:].replace("\n", " "), "", "", tk, 0
    if any(s == "error" for s, _ in r.values()):
        m = re.search(r"svlang: \S*?(\d+): ([^\n]*)", out)
        why = f"line {m.group(1)}: {m.group(2)}" if m else "error"
        return mid, "rejected", "-", why, tk, 0
    cex = [f"{p}@{d}" for p, (s, d) in r.items() if s == "cex"]
    if mid == "orig":
        return mid, ",".join(cex) or "-", "control", "", tk, 0
    v, det, te = formal.equiv(("src", path), f"{BUILD}/e/{mid}")
    return mid, ",".join(cex) or "-", v, det, tk, te


def main():
    t0 = time.time()
    os.system(f"python3 {HERE}/../src-mutants/mutate_src.py {SRC}"
              " >/dev/null")
    rows = [l.split("\t")[0] for l in
            open(f"{HERE}/../src-mutants/mutants.tsv")][1:]
    res = mutlib.pmap(job, ["orig"] + rows)
    with open(os.path.join(HERE, "src_formal.tsv"), "w") as f:
        f.write("id\tkilled_by\tmiter\tdetail\tkill_s\tmiter_s\n")
        for mid, cex, v, det, tk, te in res:
            f.write(f"{mid}\t{cex}\t{v}\t{det}\t{tk:.1f}\t{te:.1f}\n")
    live = res[1:]
    k = sum(c != "-" for _, c, *_ in live)
    print(f"control: {res[0][1]} (expected '-')")
    print(f"property set kills {k} of {len(live)} source mutants")
    for v in ("differs", "equivalent", "unknown", "error"):
        print(f"  miter {v}: {sum(r[2] == v for r in live)}")
    print(f"wall {time.time() - t0:.0f} s, 4 workers")
    os.system(f"rm -rf {BUILD}")


if __name__ == "__main__":
    main()
