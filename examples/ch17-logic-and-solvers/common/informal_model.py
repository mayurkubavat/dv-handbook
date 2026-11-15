"""informal_model.py -- SystemVerilog to a model, with InFormal.

Runs the four commands the chapter reads: `informal lower` (to
Btor2), `info` (its size), `simp` (bit level, before and after
preprocessing; `--aag` prints the result as AIGER) and `check` with
the bounded model checking engine. Timing fields are removed so that
two runs print the same text. A caller names the files the results
must equal and the depth at which the property must fail.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ENGINES = pathlib.Path(__file__).parent.parent.parent / "mk" / \
    "informal-engines.toml"         # the book's engine list


def run(args, cwd):
    done = subprocess.run(["informal"] + args, cwd=cwd, text=True,
                          capture_output=True)
    return done.stdout, done.stderr, done.returncode


def show(args):
    """Print a command as it was run, folded to fit the page."""
    line = "$ informal"
    for arg in args:
        if len(line) + len(arg) > 76:
            print(line + " \\")
            line = "   "
        line += " " + arg
    print(line)


def model(here, sources, top, depth, btor2_ref=None, aag_ref=None):
    """Lower, measure, simplify and check; return (Btor2 text, info)."""
    if not shutil.which("informal"):
        print("skipped: informal is not on the PATH")
        sys.exit(0)
    build = here / "build"
    build.mkdir(exist_ok=True)
    file = f"build/{top}.btor2"
    args = ["lower"] + sources + ["--top", top]
    btor2, err, rc = run(args, here)
    assert rc == 0, err
    (here / file).write_text(btor2)
    show(args + [">", file])
    print(f"{len(btor2.splitlines())} lines of Btor2")
    if btor2_ref:
        same = btor2 == (here / btor2_ref).read_text()
        print(f"the regenerated Btor2 equals {btor2_ref}: {same}")
        assert same

    out, err, rc = run(["info", file], here)
    info = json.loads(out)
    show(["info", file])
    print(", ".join(f'"{k}": {info[k]}' for k in (
        "inputs", "states", "state_bits", "bad", "constraints")))

    out, err, rc = run(["simp", file, "--aag"], here)
    show(["simp", file, "--aag", ">", f"build/{top}.aag"])
    for line in err.splitlines():       # the two size lines, no times
        line = re.sub(r" \([0-9.]+ ms(, )?", " (", line).replace(" ()", "")
        if len(line) > 80:              # wrap before the parenthesis
            line = line.replace(" (", "\n    (", 1)
        print(line)
    (build / f"{top}.aag").write_text(out)
    print(out.splitlines()[0])
    if aag_ref:
        same = out == (here / aag_ref).read_text()
        print(f"the regenerated AIGER equals {aag_ref}: {same}")
        assert same

    engines = pathlib.Path("../..") / "mk" / ENGINES.name
    args = ["check", "--engines", str(engines), "--only", "informal-bmc",
            file]
    out, err, rc = run(args, here)
    verdict = [x for x in out.splitlines() if x.startswith(("SAFE",
                                                            "UNSAFE"))]
    show(args)
    print(verdict[0])
    assert verdict[0] == f"UNSAFE (by informal-bmc, depth {depth})"
    return btor2, info
