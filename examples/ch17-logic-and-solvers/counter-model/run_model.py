"""run_model.py -- a counter, from SystemVerilog to a model and a bug.

    python3 run_model.py

counter.btor2 and ../fifo-unroll/counter.aag are kept under version
control so that the chapter can print them and the unrolling example
can run where InFormal is not installed; this run regenerates both
and fails if either has changed. Prints "skipped" without the tool.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
from informal_model import model  # noqa: E402

btor2, info = model(HERE, ["counter.sv"], "counter", depth=6,
                    btor2_ref="counter.btor2",
                    aag_ref="../fifo-unroll/counter.aag")
assert (info["state_bits"], info["bad"]) == (3, 1)
print("verdict: the counter reaches 6 in six steps from its first state")
