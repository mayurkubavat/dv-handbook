"""test_counter.py -- the same smoke test as tb_counter.sv, written in cocotb.

cocotb drives the simulator from Python: each `await` hands control back to
the simulator until the trigger fires.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge


async def reset(dut, cycles=2):
    dut.rst_n.value = 0
    dut.en.value = 0
    await ClockCycles(dut.clk, cycles)
    dut.rst_n.value = 1


@cocotb.test()
async def counts_when_enabled(dut):
    """Count for 10 cycles, pause for 3, count 5 more; expect 15."""
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    await reset(dut)

    dut.en.value = 1
    await ClockCycles(dut.clk, 10)
    dut.en.value = 0
    await ClockCycles(dut.clk, 3)
    assert dut.count.value == 10, \
        f"count={dut.count.value} after pause, expected 10"

    dut.en.value = 1
    await ClockCycles(dut.clk, 5)
    dut.en.value = 0
    await RisingEdge(dut.clk)
    assert dut.count.value == 15, f"count={dut.count.value}, expected 15"
    dut._log.info("PASS: counter reached %d", dut.count.value)
