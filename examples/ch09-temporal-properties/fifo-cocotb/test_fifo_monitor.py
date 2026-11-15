"""test_fifo_monitor.py -- the FIFO checker as a cocotb monitor.

Icarus runs no concurrent assertion, so the
checks of fifo_sva.sv are written here the same way in Python: state
in variables, one sample per clock, a plain condition on each sample. The
monitor samples after the falling edge, when every signal holds the
value the next rising edge will capture, which is the value an
assertion clocked on that edge would sample.

The monitor records what it sees and the test decides: a failed check
is appended to a list that the test asserts is empty, so a check can
not be lost inside a background task.
"""
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly

DEPTH = 16
CYCLES = 400


class FifoMonitor:
    def __init__(self, dut):
        self.dut = dut
        self.failures = []
        self.covers = {"FullReached_C": 0, "PushFull_C": 0, "PopEmpty_C": 0}

    def check(self, name, ok, cycle):
        if not ok:
            self.failures.append(f"{name} at sample {cycle}")

    async def run(self):
        dut = self.dut
        occ = 0                 # the monitor's own occupancy
        prev = None             # the sample before this one
        cycle = 0
        while True:
            await FallingEdge(dut.clk)
            await ReadOnly()
            if not int(dut.rst_n.value):
                occ, prev = 0, None
                continue
            cycle += 1
            wr, rd = int(dut.wr_en.value), int(dut.rd_en.value)
            full, empty = int(dut.full.value), int(dut.empty.value)

            # A condition on this sample.
            self.check("NoOverflow_A", occ <= DEPTH, cycle)
            self.check("FullForward_A", occ != DEPTH or full, cycle)
            self.check("FullBackward_A", not full or occ == DEPTH, cycle)
            self.check("EmptyExact_A", bool(empty) == (occ == 0), cycle)
            # A condition on the sample before and on this one: |=>.
            if prev and prev["wr"] and prev["full"] and not prev["rd"]:
                self.check("PushFull_A", full, cycle)
            if prev and prev["rd"] and prev["empty"] and not prev["wr"]:
                self.check("PopEmpty_A", empty, cycle)

            self.covers["FullReached_C"] += occ == DEPTH
            self.covers["PushFull_C"] += bool(wr and full and not rd)
            self.covers["PopEmpty_C"] += bool(rd and empty and not wr)

            # What the coming edge does to the occupancy.
            occ += (wr and not full) - (rd and not empty)
            prev = {"wr": wr, "rd": rd, "full": full, "empty": empty}


@cocotb.test()
async def random_traffic_under_the_monitor(dut):
    random.seed(1)
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    mon = FifoMonitor(dut)
    cocotb.start_soon(mon.run())
    for _ in range(2):
        await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    for cycle in range(CYCLES):
        await FallingEdge(dut.clk)
        early = cycle < CYCLES // 2
        dut.wr_en.value = random.randrange(100) < (80 if early else 30)
        dut.rd_en.value = random.randrange(100) < (30 if early else 80)
        dut.wr_data.value = random.randrange(256)
    await FallingEdge(dut.clk)

    for name, hits in mon.covers.items():
        dut._log.info("cover %s: %d", name, hits)
    for line in mon.failures[:3]:
        dut._log.info("failed %s", line)
    dut._log.info("%d checks failed", len(mon.failures))
    assert all(mon.covers.values()), "a cover was never hit"
    assert not mon.failures, mon.failures[0]
