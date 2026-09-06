"""test_fifo_random.py -- the random FIFO test, in cocotb.

Same three parts as tb_fifo_random.sv: random stimulus, a reference model
(a Python deque), and a note of which occupancy levels the run reached.
"""
import random
from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

DEPTH = 16
CYCLES = 400


@cocotb.test()
async def random_pressure_finds_the_bug(dut):
    seed = 1
    random.seed(seed)
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())

    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    model = deque()
    seen = set()
    writes = 0

    for cycle in range(CYCLES):
        await FallingEdge(dut.clk)
        wr = random.randrange(100) < (90 if cycle < 40 else 55)
        rd = random.randrange(100) < 45
        data = random.randrange(256)
        dut.wr_en.value = wr
        dut.rd_en.value = rd
        dut.wr_data.value = data

        # Read data is visible before the edge; compare it now.
        if rd and model:
            got = int(dut.rd_data.value)
            expected = model[0]
            assert got == expected, (
                f"cycle {cycle}: read {got:02x}, expected {expected:02x}")

        await RisingEdge(dut.clk)
        await Timer(1, "ns")

        # Predict what the edge must have done, then compare the flags.
        if rd and model:
            model.popleft()
        if wr and len(model) < DEPTH:
            model.append(data)
            writes += 1
        full = bool(dut.full.value)
        assert full == (len(model) == DEPTH), (
            f"cycle {cycle}, write {writes}: full={int(full)} with "
            f"{len(model)} entries; spec says full only at {DEPTH}")
        assert bool(dut.empty.value) == (len(model) == 0), (
            f"cycle {cycle}: empty with {len(model)} entries")
        seen.add(len(model))

    dut._log.info("coverage: %d of %d occupancy levels reached, max %d",
                  len(seen), DEPTH + 1, max(seen))
    dut._log.info("PASS: %d cycles, %d writes", CYCLES, writes)
