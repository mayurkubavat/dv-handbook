"""test_counter_pyuvm.py -- the UVM smoke test again, in pyuvm.

pyuvm reproduces the UVM class library in Python on top of cocotb. The cocotb
test at the bottom is the equivalent of run_test() in tb_top.sv.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from pyuvm import uvm_test, uvm_root, uvm_report_object


class CounterSmokeTest(uvm_test):
    """Drives the pins directly; later chapters add agents and a scoreboard."""

    async def run_phase(self):
        self.raise_objection()
        dut = cocotb.top
        cocotb.start_soon(Clock(dut.clk, 10, "ns").start())

        dut.rst_n.value = 0
        dut.en.value = 0
        await ClockCycles(dut.clk, 2)
        dut.rst_n.value = 1

        dut.en.value = 1
        await ClockCycles(dut.clk, 10)
        dut.en.value = 0
        await ClockCycles(dut.clk, 1)

        count = int(dut.count.value)
        if count == 10:
            self.logger.info(f"PASS: count = {count}")
        else:
            self.logger.error(f"FAIL: count = {count}, expected 10")
            assert False
        self.drop_objection()


@cocotb.test()
async def run_uvm_test(_):
    await uvm_root().run_test("CounterSmokeTest")
