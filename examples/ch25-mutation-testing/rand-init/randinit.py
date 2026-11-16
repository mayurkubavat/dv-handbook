"""randinit.py -- the simulator's initial values are part of the
oracle: the source mutants no testbench killed, run again with every
variable starting from a random value instead of zero.

    python3 randinit.py

The source schema is built once for each testbench with the book's
flags unchanged (no --x-initial option: its default, unique, already
initializes through a function), and each of the seven survivors,
m44 and the control is run twice over:
  default     as the book runs them: the function returns zero;
  randomized  +verilator+rand+reset+2 with +verilator+seed+S, S = 1
              to 5: the function returns values drawn from the seed.
The seed is given once: where a testbench's own runs already carry a
+verilator+seed+, it is replaced, not followed by a second one.
The repaired FIFO is the control and must pass every run.

Then tbl-ch25-survivors.md: each of these mutants with the miter's
verdict, read from the committed run.out of the miter examples
(miter-differ/, equiv-*/, white-box/), and the two simulation
verdicts. About 20 seconds.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import srcmut  # noqa: E402

B = HERE / "build"
IDS = ["m05", "m09", "m11", "m13", "m32", "m36", "m43", "m44"]
SEEDS = range(1, 6)
WANT = {  # seeds that kill, per testbench, from the research run
    "m09": ["1-5", "1-5", "-", "-"], "m11": ["1-5", "1-5", "-", "-"],
    "m13": ["1-5", "1-5", "-", "1-5"], "m44": ["-", "-", "-", "1-5"]}
CLASS = {"m05": "equivalent only under the tool's reset model",
         "m09": "not equivalent: a missing reset",
         "m11": "not equivalent: a missing reset",
         "m13": "not equivalent: a missing reset",
         "m32": "equivalent outright",
         "m36": "equivalent outright",
         "m43": "equivalent under a reachable-state invariant",
         "m44": "equivalent under a reachable-state invariant "
                "relating the copies; killed by Sync_A"}


def seeded(tb, s):
    """The testbench's own runs with one +verilator+seed+S each."""
    runs = mutlib.TBS[tb][3]
    return [[a for a in r if not a.startswith("+verilator+seed+")]
            + ["+verilator+rand+reset+2", f"+verilator+seed+{s}"]
            for r in runs]


def span(seeds):
    if not seeds:
        return "-"
    if seeds == list(range(seeds[0], seeds[-1] + 1)) and len(seeds) > 1:
        return f"{seeds[0]}-{seeds[-1]}"
    return ",".join(map(str, seeds))


def miter_verdicts():
    """{mutant: verdict} from the 'miter: ' lines of the committed
    run.out files of the miter examples."""
    out = {}
    for d in ("miter-differ", "equiv-outright", "equiv-invariant",
              "equiv-reset", "white-box"):
        p = HERE.parent / d / "run.out"
        if p.exists():
            for m in re.finditer(r"^miter: (m\d\d) (.*)$", p.read_text(),
                                 re.M):
                out[m.group(1)] = m.group(2)
    return out


def main():
    C = mutlib.Checks()
    print(f"tools: {mutlib.version('verilator')}")
    ms = srcmut.mutants()
    num = {m.id: n for n, m in enumerate(ms, 1)}
    dirs, _ = srcmut.build_schema(B, mutlib.NAMES)
    print("schema built with the book's flags; no --x-initial option")
    ids = ["orig"] + IDS
    jobs = [(i, tb, s) for i in ids for tb in mutlib.NAMES
            for s in [0] + list(SEEDS)]

    def one(j):
        i, tb, s = j
        k = 0 if i == "orig" else num[i]
        runs = None if s == 0 else seeded(tb, s)
        return mutlib.run(tb, dirs[tb], [f"+mut={k}"], runs=runs)[0]
    res = dict(zip(jobs, mutlib.pmap(one, jobs)))
    print("seeds (of 1-5) whose randomized run kills; 'default' is the")
    print("book's run, K killed, . survived")
    print(f"  {'':5s}{'':9s}" + "".join(f"{tb:>15s}" for tb in
                                         mutlib.NAMES))
    table = {}
    for i in ids:
        d = ["K" if res[(i, tb, 0)] in mutlib.DEAD else "."
             for tb in mutlib.NAMES]
        r = [span([s for s in SEEDS if res[(i, tb, s)] in mutlib.DEAD])
             for tb in mutlib.NAMES]
        table[i] = (d, r)
        print(f"  {i:5s}{'default':9s}" + "".join(f"{x:>15s}" for x in d))
        print(f"  {'':5s}{'random':9s}" + "".join(f"{x:>15s}" for x in r))
        C.pin(f"{i} randomized", r, WANT.get(i, ["-"] * 4))
    C.pin("control default", table["orig"][0], ["."] * 4)
    killed = [i for i in IDS if any(x != "-" for x in table[i][1])]
    print(f"killed only with randomized initial values: "
          f"{' '.join(i for i in killed if i != 'm44')}")
    C.pin("killed with randomized values", killed,
          ["m09", "m11", "m13", "m44"])

    mv = miter_verdicts()
    rows = []
    for i in IDS:
        d, r = table[i]
        dk = [tb for tb, x in zip(mutlib.NAMES, d) if x == "K"]
        rk = [tb for tb, x in zip(mutlib.NAMES, r) if x != "-"]
        rows.append([f"`{i}`", mv.get(i, "?"), ", ".join(dk) or "none",
                     ", ".join(rk) or "none", CLASS[i]])
    missing = [i for i in IDS if i not in mv]
    print(f"miter verdicts read from the committed run.out files: "
          f"{len(IDS) - len(missing)} of {len(IDS)}")
    C.pin("miter verdicts found", missing, [])
    mutlib.table_md(
        HERE / "tbl-ch25-survivors.md",
        ["mutant", "miter", "killed by (default values)",
         "killed by (randomized values)", "class"], rows,
        "The seven source mutants no testbench killed, and m44: the "
        "miter's verdict and the simulation verdicts {#tbl-ch25-"
        "survivors}", widths=[6, 22, 14, 14, 22])
    C.report()
    print("verdict: m09, m11 and m13 die with randomized initial values")


if __name__ == "__main__":
    main()
