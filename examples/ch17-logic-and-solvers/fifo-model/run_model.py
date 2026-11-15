"""run_model.py -- the first chapter's FIFO as a model.

    python3 run_model.py

Lowers fifo.sv under the wrapper fifo_bmc.sv, prints the model's size
before and after InFormal's bit-level preprocessing, writes the
result as AIGER and checks it with bounded model checking. The AIGER
file must equal ../fifo-unroll/fifo_bmc.aag, which the unrolling
example reads. Prints "skipped" without the tool.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
from informal_model import model  # noqa: E402

FIFO = "../../ch01-what-is-dv/rtl/fifo.sv"
btor2, info = model(HERE, [FIFO, "fifo_bmc.sv"], "fifo_bmc", depth=16,
                    aag_ref="../fifo-unroll/fifo_bmc.aag")
assert (info["state_bits"], info["bad"], info["constraints"]) == (146, 1, 1)
states = [line.split()[3] for line in btor2.splitlines()
          if line.split()[1] == "state"]
memory = sum(".mem[" in s for s in states)
print(f"state variables: {len(states)}, of which {memory} are memory "
      f"entries; the others:")
print("  " + " ".join(s.split(".")[-1] for s in states if ".mem[" not in s))
print("verdict: full is high with fewer than sixteen entries, at depth 16")
