"""test_stream.py -- a weighted random stream in cocotb.

There is no constraint solver here and none is needed: the stimulus is
drawn by Python's random module, which cocotb seeds once per run from
COCOTB_RANDOM_SEED (or the clock, when it is unset) and reports in its
log. The weights are a call to
random.choices, the check is a deque, and the seed is printed so that a
failing run can be repeated exactly.
"""
import os
import random
from collections import Counter, deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CYCLES = 200
KINDS = (0, 1, 2)          # kind 3 is reserved: never generated
WEIGHTS = (6, 3, 1)        # the mix asked for


@cocotb.test()
async def weighted_stream(dut):
    seed = os.environ.get("COCOTB_RANDOM_SEED", "unset")
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())

    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    model = deque()
    kinds = Counter()
    writes = reads = mismatches = 0

    for _ in range(CYCLES):
        await FallingEdge(dut.clk)
        wr = random.random() < 0.6 and not bool(dut.full.value)
        rd = random.random() < 0.5 and not bool(dut.empty.value)
        kind = random.choices(KINDS, WEIGHTS)[0]
        data = (kind << 6) | random.randrange(1, 64)
        dut.wr_en.value = wr
        dut.rd_en.value = rd
        dut.wr_data.value = data
        if rd:
            got = int(dut.rd_data.value)
            if got != model[0]:
                mismatches += 1
        await RisingEdge(dut.clk)
        await Timer(1, "ns")
        if rd:
            model.popleft()
            reads += 1
        if wr:
            model.append(data)
            kinds[kind] += 1
            writes += 1

    dut._log.info("seed %s: %d writes, %d reads, kinds 0:%d 1:%d 2:%d, "
                  "%d mismatches", seed, writes, reads, kinds[0], kinds[1],
                  kinds[2], mismatches)
    assert mismatches == 0
