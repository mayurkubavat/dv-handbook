"""test_dma_v2.py -- version 2 of the DMA against the same plan, in
cocotb on Icarus, a second simulator and a second language.

The pieces are the SystemVerilog testbench's, smaller: an APB master,
an AXI4-Lite memory with two ready styles and error injection, a
reference model that predicts each channel's writes from the spec, and
cocotb-coverage points for the plan's length, outcome and style bins.
Every component works on the falling edge: it drives, waits for the
values to settle (ReadOnly), and reads what the next rising edge will
capture, so a handshake is seen exactly when the DUT sees it.
"""
import random
import re

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db

SRC, DST, LEN, CTRL, STATUS = 0x00, 0x04, 0x08, 0x0C, 0x10
START, IRQ_EN, BUSY, DONE, ERROR = 1, 2, 1, 2, 4
STRIDE, SLVERR = 0x20, 2
in_range = lambda v, b: b[0] <= v <= b[1]            # noqa: E731


@CoverPoint("dma.len", xf=lambda n, out, style: n, rel=in_range,
            bins=[(0, 0), (1, 1), (2, 15), (16, 65535)],
            bins_labels=["zero", "one", "few", "many"])
@CoverPoint("dma.outcome", xf=lambda n, out, style: out,
            bins=["ok", "rd_err", "wr_err"])
@CoverPoint("dma.style", xf=lambda n, out, style: style,
            bins=["wait_valid", "ready_first"])
@CoverCross("dma.len_x_outcome", items=["dma.len", "dma.outcome"])
def sample(n, out, style):
    pass


async def cycle(dut):
    """Advance to the next falling edge."""
    await FallingEdge(dut.PCLK)


class Apb:
    def __init__(self, dut):
        self.d = dut

    async def xfer(self, write, addr, data=0):
        d = self.d
        await cycle(d)
        d.PSEL.value, d.PENABLE.value = 1, 0
        d.PWRITE.value, d.PADDR.value, d.PWDATA.value = write, addr, data
        await cycle(d)
        d.PENABLE.value = 1
        while True:
            await ReadOnly()
            if d.PREADY.value:
                rdata, err = int(d.PRDATA.value), int(d.PSLVERR.value)
                break
            await cycle(d)
        await cycle(d)
        d.PSEL.value, d.PENABLE.value = 0, 0
        return rdata, err


class Memory:
    """AXI4-Lite memory, one read and one write in flight at a time."""

    def __init__(self, dut):
        self.d, self.mem, self.rd_err, self.wr_err = dut, {}, set(), set()
        self.style, self.writes = "wait_valid", []

    def ready(self, valid):
        return 1 if self.style == "ready_first" else int(valid)

    async def reads(self):
        d, addr = self.d, None
        d.ARREADY.value, d.RVALID.value = 0, 0
        arv = arr = rv = rr = 0
        while True:
            await cycle(d)                      # act on the last cycle
            if addr is None and arv and arr:
                addr = int(d.ARADDR.value)
                d.ARREADY.value = 0
                d.RDATA.value = self.mem.get(addr, 0)
                d.RRESP.value = SLVERR if addr in self.rd_err else 0
                d.RVALID.value = 1
            elif addr is not None and rv and rr:
                addr = None
                d.RVALID.value = 0
                d.ARREADY.value = self.ready(0)
            elif addr is None:
                d.ARREADY.value = self.ready(arv)
            await ReadOnly()                    # then watch this one
            arv, arr = int(d.ARVALID.value), int(d.ARREADY.value)
            rv, rr = int(d.RVALID.value), int(d.RREADY.value)

    async def writes_side(self):
        d = self.d
        self.a = self.w = None
        self.pending = False
        d.AWREADY.value, d.WREADY.value, d.BVALID.value = 0, 0, 0
        awv = awr = wv = wr = bv = br = awaddr = wdata = 0
        while True:
            await cycle(d)
            self.write_step(awv, awr, wv, wr, bv, br, awaddr, wdata)
            await ReadOnly()
            awv, awr = int(d.AWVALID.value), int(d.AWREADY.value)
            wv, wr = int(d.WVALID.value), int(d.WREADY.value)
            bv, br = int(d.BVALID.value), int(d.BREADY.value)
            awaddr, wdata = int(d.AWADDR.value), int(d.WDATA.value)

    def write_step(self, awv, awr, wv, wr, bv, br, awaddr, wdata):
        d = self.d
        if self.pending:
            if bv and br:
                self.pending = False
                d.BVALID.value = 0
                d.AWREADY.value = self.ready(0)
                d.WREADY.value = self.ready(0)
            return
        a, w = self.a, self.w
        if a is None and awv and awr:
            a = awaddr
        if w is None and wv and wr:
            w = wdata
        if a is not None and w is not None:
            self.writes.append((a, w))
            if a not in self.wr_err:
                self.mem[a] = w
            d.BRESP.value = SLVERR if a in self.wr_err else 0
            d.BVALID.value, self.pending = 1, True
            d.AWREADY.value, d.WREADY.value = 0, 0
            a = w = None
        else:
            d.AWREADY.value = 0 if a is not None else self.ready(awv)
            d.WREADY.value = 0 if w is not None else self.ready(wv)
        self.a, self.w = a, w


def predict(mem, src, dst, n):
    """The writes the spec owes: every word before the first error."""
    owed = []
    for i in range(n):
        ra, wa = src + 4 * i, dst + 4 * i
        if ra in mem.rd_err:
            return owed, True
        owed.append((wa, mem.mem.get(ra, 0)))
        if wa in mem.wr_err:
            return owed, True
    return owed, False


async def setup(dut):
    cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())
    dut.PRESETn.value = 0
    dut.PSEL.value = dut.PENABLE.value = dut.PWRITE.value = 0
    dut.PADDR.value = dut.PWDATA.value = 0
    mem = Memory(dut)
    cocotb.start_soon(mem.reads())
    cocotb.start_soon(mem.writes_side())
    for _ in range(3):
        await cycle(dut)
    dut.PRESETn.value = 1
    return Apb(dut), mem


async def run_channels(apb, mem, jobs):
    """Start each (ch, src, dst, n), wait for all, check each."""
    mem.writes.clear()
    want = {}
    for ch, src, dst, n in jobs:
        want[ch] = predict(mem, src, dst, n)
        base = ch * STRIDE
        await apb.xfer(1, base + SRC, src)
        await apb.xfer(1, base + DST, dst)
        await apb.xfer(1, base + LEN, n)
        await apb.xfer(1, base + CTRL, START | IRQ_EN)
    fails = 0
    for ch, src, dst, n in jobs:
        status = BUSY
        for _ in range(5000):
            status, _ = await apb.xfer(0, ch * STRIDE + STATUS)
            if not status & BUSY:
                break
        owed, err = want[ch]
        seen = [w for w in mem.writes if dst <= w[0] < dst + 4 * n]
        if seen != owed or bool(status & ERROR) != err:
            fails += 1
            cocotb.log.error("ch%d: %d writes of %d owed, STATUS %x",
                             ch, len(seen), len(owed), status)
        await apb.xfer(1, ch * STRIDE + STATUS, DONE | ERROR)
    return fails


@cocotb.test()
async def directed(dut):
    apb, mem = await setup(dut)
    for i in range(8):
        mem.mem[0x1000 + 4 * i] = 0xDEAD0000 + i
        mem.mem[0x2000 + 4 * i] = 0xBEEF0000 + i
    fails = await run_channels(apb, mem, [(0, 0x1000, 0x8000, 8),
                                          (1, 0x2000, 0x9000, 8)])
    cocotb.log.info("directed: both channels at once, %d writes seen, "
                    "%d failures", len(mem.writes), fails)
    assert fails == 0


@cocotb.test()
async def registers(dut):
    apb, mem = await setup(dut)
    rules = []
    await apb.xfer(1, SRC, 0x1003)
    rules.append(("SRC low bits read as zero",
                  (await apb.xfer(0, SRC))[0] == 0x1000))
    rules.append(("unmapped offset gives PSLVERR",
                  (await apb.xfer(1, 0x14, 0))[1] == 1))
    await apb.xfer(1, LEN, 64)
    await apb.xfer(1, DST, 0x8000)
    await apb.xfer(1, CTRL, START)
    rules.append(("write while busy gives PSLVERR",
                  (await apb.xfer(1, DST, 0x9000))[1] == 1))
    rules.append(("refused write changes nothing",
                  (await apb.xfer(0, DST))[0] == 0x8000))
    for name, ok in rules:
        cocotb.log.info("%-32s %s", name, "ok" if ok else "VIOLATED")
    assert all(ok for _, ok in rules)


@cocotb.test()
async def random_rounds(dut):
    apb, mem = await setup(dut)
    random.seed(1)
    fails = 0
    for k in range(30):
        mem.style = random.choice(["wait_valid", "ready_first"])
        mem.rd_err.clear()
        mem.wr_err.clear()
        jobs, outs = [], []
        for ch in range(2):
            n = random.choice([0, 1, random.randint(2, 15),
                               random.randint(16, 40)])
            src = 0x10000 + ch * 0x100000 + k * 0x400
            dst = 0x80000 + ch * 0x100000 + k * 0x400
            for i in range(n):
                mem.mem[src + 4 * i] = random.getrandbits(32)
            out = random.choice(["ok", "ok", "rd_err", "wr_err"]) if n \
                else "ok"
            if out != "ok":
                at = random.randrange(n)
                (mem.rd_err if out == "rd_err" else mem.wr_err).add(
                    (src if out == "rd_err" else dst) + 4 * at)
            jobs.append((ch, src, dst, n))
            outs.append((n, out))
        fails += await run_channels(apb, mem, jobs)
        for n, out in outs:
            sample(n, out, mem.style)
    coverage_db.report_coverage(          # object addresses removed
        lambda s: cocotb.log.info(re.sub(r"<[^>]*>, ", "", s).rstrip()))
    hit = {k: v for k, v in coverage_db["dma.len_x_outcome"]
           .detailed_coverage.items()}
    holes = [f"{a}x{b}" for (a, b), v in hit.items() if v == 0]
    cocotb.log.info("len x outcome holes: %s", ", ".join(holes) or "none")
    cocotb.log.info("verdict: 30 rounds, %d channel failures", fails)
    assert fails == 0
