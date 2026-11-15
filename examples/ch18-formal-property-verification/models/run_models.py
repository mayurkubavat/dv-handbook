"""run_models.py -- regenerate the chapter's small models and compare
them with the files under version control.

    python3 run_models.py

The Python examples of this chapter read AIGER files from ../common,
so they need no tool. This script is the proof that those files are
what the tool makes of fifo_ptrs.sv: it lowers the wrapper to Btor2
with `informal lower`, preprocesses and prints it as AIGER with
`informal simp --aag`, and fails on any difference. Prints "skipped"
without the tool.
"""
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
COMMON = HERE.parent / "common"
FIFO = "../../ch09-temporal-properties/rtl/fifo_fixed.sv"
MODELS = [("fifo_ptrs2.aag", []),
          ("count_ptrs2.aag", ["-D", "COUNT"]),
          ("fifo_ptrs2_h.aag", ["-D", "HELPER"]),
          ("fifo_ptrs4.aag", ["-D", "DEPTH=4"]),
          ("fifo_ptrs4_h.aag", ["-D", "DEPTH=4", "-D", "HELPER"])]

if not shutil.which("informal"):
    print("skipped: informal is not on the PATH")
    sys.exit(0)


def informal(*args):
    done = subprocess.run(["informal", *args], cwd=HERE, text=True,
                          capture_output=True)
    assert done.returncode == 0, done.stderr
    return done.stdout, done.stderr


print("tool: " + informal("--version")[0].strip())
build = HERE / "build"
build.mkdir(exist_ok=True)
different = 0
for name, defines in MODELS:
    btor2 = f"build/{name[:-4]}.btor2"
    text, _ = informal("lower", FIFO, "../common/fifo_ptrs.sv", "--top",
                       "fifo_ptrs", *defines)
    (HERE / btor2).write_text(text)
    aag, sizes = informal("simp", btor2, "--aag")
    same = aag == (COMMON / name).read_text()
    different += not same
    print(f"$ informal lower ... {' '.join(defines)} > {btor2}".replace(
        "  ", " "))
    for line in sizes.splitlines():         # two size lines, no times
        print("  " + re.sub(r" \(.*\)$", "", line))
    print(f"  {aag.splitlines()[0]}")
    print(f"  equal to common/{name}: {same}")
    latches = int(aag.split()[3])
    listed = len((COMMON / name).with_suffix(".names").read_text().split())
    assert latches == listed, f"{name}: {latches} latches, {listed} names"
if different:
    print(f"FAILED: {different} models differ from the checked-in files")
    sys.exit(1)
print(f"all {len(MODELS)} regenerated models equal the checked-in files")
