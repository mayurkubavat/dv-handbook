"""test_fifo_cov.py -- the FIFO coverage model of the chapter's worked
example, in Python with cocotb-coverage.

The same bins as the SystemVerilog covergroup: occupancy bands on the
count the monitor keeps itself, the requested op, the DUT's full and
empty flags, op crossed with each flag, and the climb from empty to
almost-full as a point over the last four occupancy bands. A monitor
coroutine samples once per cycle; the driver never touches coverage;
nothing here checks the FIFO. Two phases in one test: 50/50 push and
pop, then push-biased, with the report after each.
"""
import random
import re
import xml.etree.ElementTree as ET

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db

CYCLES = 200
XML = "build/coverage.xml"

# The sample function's arguments are what the monitor observed; each
# CoverPoint picks one with xf. Range bins need a relation (rel).
in_range = lambda v, b: b[0] <= v <= b[1]            # noqa: E731


@CoverPoint("top.occupancy", xf=lambda occ, op, full, empty: occ,
            bins=[(0, 0), (1, 7), (8, 14), (15, 15), (16, 16)],
            bins_labels=["empty", "low", "high", "almost", "full_16"],
            rel=in_range)
@CoverPoint("top.op", xf=lambda occ, op, full, empty: op,
            bins=["idle", "push", "pop", "both"])
@CoverPoint("top.full", xf=lambda occ, op, full, empty: full,
            bins=[False, True], bins_labels=["not_full", "full"])
@CoverPoint("top.empty", xf=lambda occ, op, full, empty: empty,
            bins=[False, True], bins_labels=["not_empty", "empty"])
@CoverCross("top.op_x_full", items=["top.op", "top.full"])
@CoverCross("top.op_x_empty", items=["top.op", "top.empty"])
def sample(occ, op, full, empty):
    pass


# cocotb-coverage has no transition bins; the last four bands the
# monitor passed through, as a tuple, cover the same climb.
@CoverPoint("top.fill", xf=lambda bands: bands, bins=[(0, 1, 2, 3)],
            bins_labels=["climb"])
def sample_fill(bands):
    pass


def band(occ):
    return 0 if occ == 0 else 1 if occ <= 7 else 2 if occ <= 14 \
        else 3 if occ == 15 else 4


class Monitor:
    """Watches the ports; counts the pushes and pops it sees accepted."""

    def __init__(self, dut):
        self.dut = dut
        self.occ = 0
        self.bands = [0]
        self.push_while_full_at = None

    async def run(self):
        dut = self.dut
        while True:
            # Once per cycle, in the read-only phase before the rising
            # edge: the driver's request and the flags the DUT shows.
            await FallingEdge(dut.clk)
            await ReadOnly()
            if not dut.rst_n.value:
                continue
            wr, rd = bool(dut.wr_en.value), bool(dut.rd_en.value)
            full, empty = bool(dut.full.value), bool(dut.empty.value)
            op = ["idle", "push", "pop", "both"][(rd << 1) | wr]
            sample(self.occ, op, full, empty)
            if wr and full and self.push_while_full_at is None:
                self.push_while_full_at = self.occ
            self.occ += (wr and not full) - (rd and not empty)
            if band(self.occ) != self.bands[-1]:
                self.bands.append(band(self.occ))
                sample_fill(tuple(self.bands[-4:]))


def report(log, phase):
    """coverage_db's own report, with the object addresses removed."""
    log.info("--- %s", phase)
    coverage_db.report_coverage(
        lambda s: log.info(re.sub(r"<[^>]*>, ", "", s).rstrip()))
    hits = coverage_db["top.occupancy"].detailed_coverage
    log.info("occupancy bins: %s",
             " ".join(f"{k}={v}" for k, v in hits.items()))
    hits = coverage_db["top.op_x_full"].detailed_coverage
    for flag in ("not_full", "full"):
        log.info("op_x_full with %s: %s", flag, " ".join(
            f"{op}={v}" for (op, f), v in hits.items() if f == flag))


async def drive(dut, cycles, push_biased):
    for _ in range(cycles):
        await FallingEdge(dut.clk)
        if push_biased:
            dut.wr_en.value = random.randrange(100) < 90
            dut.rd_en.value = random.randrange(100) < 25
        else:
            dut.wr_en.value = random.randrange(2)
            dut.rd_en.value = random.randrange(2)
        dut.wr_data.value = random.randrange(256)


@cocotb.test()
async def fifo_coverage(dut):
    random.seed(1)
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    mon = Monitor(dut)
    cocotb.start_soon(mon.run())
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    await drive(dut, CYCLES, push_biased=False)
    report(dut._log, "phase A: 50/50 push and pop, %d cycles" % CYCLES)
    await drive(dut, CYCLES, push_biased=True)
    report(dut._log, "phase B: push-biased, %d more cycles" % CYCLES)
    await FallingEdge(dut.clk)
    dut.wr_en.value = 0
    dut.rd_en.value = 0

    coverage_db.export_to_xml(XML)
    top = ET.parse(XML).getroot()
    dut._log.info("coverage.xml written: top size=%s coverage=%s (%s%%)",
                  top.get("size"), top.get("coverage"),
                  top.get("cover_percentage"))
    if mon.push_while_full_at is not None:
        dut._log.info("covered: push while full at occupancy %d "
                      "(a coverage hit, not a check)",
                      mon.push_while_full_at)
    zero = [f"{name}.{b}" for name, item in coverage_db.items()
            if hasattr(item, "detailed_coverage")
            for b, n in item.detailed_coverage.items() if n == 0]
    dut._log.info("verdict: the push-biased phase closed every bin "
                  "but %s", ", ".join(zero) if zero else "none")
