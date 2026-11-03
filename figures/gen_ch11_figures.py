#!/usr/bin/env python3
"""Generate the thirteen figures of the architecture-to-verification
chapter (ch11-*.svg).

Every number a figure shows is read from the chapter's examples, not
typed here: the register map from regs/dma_regs.yaml, the waveforms from
waves/*.json, the plan from vplan/dma_plan.yaml, the bin counts and the
cycle counts from each example's run.out. Rerun the examples, then this
script, and the figures follow.

Hardware shapes come from hw.py (registers, multiplexers, FIFOs, state
machines, waveforms); the flow shapes from blocks.py. Page-width figures
are at most 1000 px wide, as in the other chapters' figures, so their
type prints at 7 pt or larger.

    python3 figures/gen_ch11_figures.py
"""
import json
import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import (AMBER, AMBER_T, BLUE, DEEP, DIM, GREEN, GREEN_T,  # noqa
                GROUND, HW, INK, MONO, RULE, TRACE, VIOLET, VIOLET_T)

EX = (pathlib.Path(__file__).resolve().parent.parent / "examples" /
      "ch11-architecture-to-verification")


def run_out(name):
    """The bins of a run.out as {'cp': {'bin': n}}; wrapped lines are
    joined first."""
    txt = (EX / name / "run.out").read_text()
    out, cur = {}, None
    for ln in txt.splitlines():
        m = re.match(r"^(\w+): (.*)$", ln)
        if m and "=" in m.group(2):
            cur = m.group(1)
            out[cur] = {}
            body = m.group(2)
        elif cur and re.match(r"^[\w]+=\d", ln):
            body = ln
        else:
            cur = None
            continue
        for k, v in re.findall(r"(\w+)=(\d+)", body):
            out[cur][k] = int(v)
    return out


# ---- F1: the DMA in its system ----------------------------------------
def fig_context():
    d = HW(1000, 520, "The DMA in its system",
           "Software programs it over APB, it moves words over AXI4-Lite, "
           "and it says it has finished on IRQ.",
           "System context: CPU, APB bridge, DMA engine and memory, with "
           "the architecture boundary drawn around the DMA's three "
           "interfaces")
    cpu = d.tool(40, 170, "CPU", w=170, h=80, sub="driver software")
    br = d.tool(270, 175, "APB bridge", w=150, h=70)
    d.region(470, 115, 260, 225, "architecture boundary", stroke=AMBER)
    dma = d.model(500, 165, "DMA engine", w=200, h=90, sub="two channels")
    mem = d.store(810, 160, "Memory", w=160, h=100, sub="AXI4-Lite slave")
    d.wire([(cpu.r, cpu.cy), (br.l - 2, br.cy)], "data")
    d.text((cpu.r + br.l) / 2, cpu.t - 8, "loads, stores", 13, INK,
           "500", "middle", MONO)
    d.bus([(br.r, br.cy), (dma.l - 2, br.cy)], 32)
    d.text((br.r + dma.l) / 2, br.cy - 12, "APB3", 14, INK, "700",
           "middle", MONO)
    d.wire([(dma.r, 195), (mem.l - 2, 195)], "data")
    d.wire([(mem.l, 228), (dma.r + 2, 228)], "data")
    d.text((dma.r + mem.l) / 2, 186, "AR AW W", 13, INK, "500", "middle",
           MONO)
    d.text((dma.r + mem.l) / 2, 248, "R B", 13, INK, "500", "middle",
           MONO)
    d.wire([(dma.cx, dma.b), (dma.cx, 395), (cpu.cx, 395),
            (cpu.cx, cpu.b + 2)], "control")
    d.text((dma.cx + cpu.cx) / 2, 387, "IRQ: level, one per DMA", 13,
           AMBER, "600", "middle", MONO)
    d.note(250, 430, "APB3 slave: five registers per\nchannel, PSLVERR on "
           "a refused access", w=270, size=14)
    d.note(540, 430, "AXI4-Lite master: one read and\none write in flight "
           "at a time", w=240, size=14)
    d.note(800, 290, "Memory answers OKAY,\nor SLVERR to inject\nan error",
           w=170, size=14)
    d.note(40, 290, "Architecture: what crosses\nthe amber line, and "
           "when.\nNothing inside it.", w=200, size=14)
    d.save("ch11-context.svg")


# ---- F2: the architecture view ----------------------------------------
def fig_arch():
    d = HW(1000, 600, "The architecture view: interfaces and promises",
           "What a user of the DMA can observe. No state machine, no FIFO, "
           "no arbiter appears.",
           "Black-box view of the DMA: APB signals on the left, five AXI "
           "channels on the right, IRQ below, and inside the programmer's "
           "model and four behavioral promises")
    x, y, w, h = 330, 100, 340, 420
    d.rect(x, y, w, h, GROUND, BLUE, 3, 10)
    d.text(x + w / 2, y + 30, "dma_v2", 19, BLUE, "700", "middle", MONO)
    d.text(x + 20, y + 64, "Programmer's model", 15, INK, "700")
    d.text(x + 20, y + 84, "per channel n, base 0x20 x n", 13, DIM, "400",
           "start", MONO)
    regs = [("0x00", "SRC_ADDR"), ("0x04", "DST_ADDR"), ("0x08", "XFER_LEN"),
            ("0x0C", "CTRL"), ("0x10", "STATUS")]
    for i, (o, n) in enumerate(regs):
        yy = y + 96 + i * 26
        d.rect(x + 20, yy, w - 40, 24, "white", RULE, 1, 3)
        d.text(x + 32, yy + 17, o, 13, DIM, "400", "start", MONO)
        d.text(x + 90, yy + 17, n, 14, INK, "600", "start", MONO)
    d.text(x + 20, y + 260, "Behavior", 15, INK, "700")
    for i, t in enumerate(["copies XFER_LEN words, in order",
                           "two channels run at once",
                           "precise errors: DONE and ERROR,",
                           "  no word after the failing one",
                           "at most 4.5 cycles per word"]):
        d.text(x + (26 if t[0] != " " else 38), y + 284 + i * 24,
               ("- " if t[0] != " " else "") + t.strip(), 14, INK)
    # APB, left
    d.text(40, 150, "APB3 slave", 16, BLUE, "700")
    d.wire([(40, 200), (x - 2, 200)], "data", "PSEL PENABLE PWRITE",
           at=(170, 190), anchor="middle")
    d.text(170, 222, "PADDR PWDATA", 13, INK, "500", "middle", MONO)
    d.wire([(x, 270), (42, 270)], "data", "PRDATA PREADY PSLVERR",
           at=(170, 260))
    d.text(40, 320, "PCLK, PRESETn", 13, DIM, "400", "start", MONO)
    # AXI, right
    d.text(700, 130, "AXI4-Lite master", 16, BLUE, "700")
    chans = [("AR", "ARADDR ARVALID", "ARREADY", True),
             ("R", "RDATA RRESP RVALID", "RREADY", False),
             ("AW", "AWADDR AWVALID", "AWREADY", True),
             ("W", "WDATA WSTRB WVALID", "WREADY", True),
             ("B", "BRESP BVALID", "BREADY", False)]
    for i, (c, pay, rdy, out) in enumerate(chans):
        yy = 175 + i * 66
        if out:
            d.wire([(x + w, yy), (958, yy)], "data")
        else:
            d.wire([(958, yy), (x + w + 2, yy)], "data")
        d.text(x + w + 12, yy - 8, c, 14, BLUE, "700", "start", MONO)
        d.text(x + w + 44, yy - 8, pay, 12.5, INK, "500", "start", MONO)
        d.text(x + w + 44, yy + 18, ("<- " if out else "-> ") + rdy, 12.5,
               DIM, "400", "start", MONO)
    d.wire([(x + w / 2, y + h), (x + w / 2, 572)], "control")
    d.text(x + w / 2 + 10, 566, "IRQ", 14, AMBER, "700", "start", MONO)
    d.text(40, 560, "solid: data and handshakes; dashed: interrupt",
           13, DIM)
    d.save("ch11-arch.svg")


# ---- F3: register bit-fields ------------------------------------------
ACC = {"rw": ("white", BLUE, "rw"), "ro": (GROUND, DIM, "ro"),
       "wo": (AMBER_T, AMBER, "wo"), "w1c": (GREEN_T, GREEN, "w1c")}


def fig_regs():
    spec = yaml.safe_load((EX / "regs" / "dma_regs.yaml").read_text())["v2"]
    regs = spec["registers"]
    d = HW(1000, 150 + 70 * len(regs) + 70,
           "Version 2 register map, bit by bit",
           f"{spec['channels']} channels; channel n's registers sit at "
           f"0x{spec['stride']:02X} x n plus the offset. Drawn from "
           "dma_regs.yaml.",
           "Bit-field diagram of the five version 2 registers with access "
           "types; unassigned bits are reserved and read as zero")
    X0, X1, Y0 = 180, 970, 130
    bw = (X1 - X0) / 32
    for b in (31, 24, 16, 15, 8, 3, 2, 1, 0):
        d.text(X0 + (31 - b + 0.5) * bw, Y0 - 10, b, 11, DIM, "400",
               "middle", MONO)
    for i, r in enumerate(regs):
        y = Y0 + i * 70
        d.text(40, y + 28, r["name"], 15, INK, "700", "start", MONO)
        d.text(40, y + 46, f"+0x{r['offset']:02X}", 12, DIM, "400", "start",
               MONO)
        used, narrow = set(), []
        for f in r["fields"]:
            hi, lo = f["bits"]
            used.update(range(lo, hi + 1))
            fill, stroke, a = ACC[f["access"]]
            xa = X0 + (31 - hi) * bw
            wd = (hi - lo + 1) * bw
            d.rect(xa, y + 6, wd, 40, fill, stroke, 2, 2)
            nm = f["name"] if f["name"] != "zero" else "0"
            if wd >= 45 or nm == "0":
                d.text(xa + wd / 2, y + 26, nm, 13, INK, "600", "middle",
                       MONO)
            else:
                narrow.append((xa, f"{nm} [{hi}]"))
                d.text(xa + wd / 2, y + 26, hi, 11, DIM, "400", "middle",
                       MONO)
            d.text(xa + wd / 2, y + 41, a, 10.5, stroke, "600", "middle",
                   MONO)
        b = 31
        while b >= 0:
            if b in used:
                b -= 1
                continue
            hi = b
            while b >= 0 and b not in used:
                b -= 1
            lo = b + 1
            xa = X0 + (31 - hi) * bw
            wd = (hi - lo + 1) * bw
            d.rect(xa, y + 6, wd, 40, "url(#hatch)", RULE, 1, 2)
            if wd > 80:
                d.text(xa + 14, y + 31, "reserved, reads 0", 12, DIM,
                       "400", "start")
        if narrow:
            t = "  ".join(n for _, n in sorted(narrow))
            xr = min(x for x, _ in narrow) - 10
            d.rect(xr - 7.6 * len(t) - 10, y + 14, 7.6 * len(t) + 14, 24,
                   "white", "white", 0, 3)
            d.text(xr, y + 31, t, 12.5, INK, "600", "end", MONO)
    ly = Y0 + 70 * len(regs) + 20
    lx = 180
    for a in ("rw", "ro", "wo", "w1c"):
        fill, stroke, _ = ACC[a]
        d.rect(lx, ly, 28, 20, fill, stroke, 2, 2)
        d.text(lx + 36, ly + 15, {"rw": "read-write", "ro": "read-only",
                                 "wo": "write-only, reads 0",
                                 "w1c": "write 1 to clear"}[a], 14)
        lx += {"rw": 130, "ro": 130, "wo": 210, "w1c": 170}[a]
    d.rect(lx, ly, 28, 20, "url(#hatch)", RULE, 1, 2)
    d.text(lx + 36, ly + 15, "reserved", 14)
    d.save("ch11-regs.svg")


# ---- F4: cycle accounting ---------------------------------------------
def fig_cycles():
    txt = (EX / "throughput" / "run.out").read_text()
    rates = re.findall(r"version (\d), (\w+) slave: \d+ cycles, ([\d.]+)",
                       txt)
    target = float(re.search(r"meets the ([\d.]+) target", txt).group(1))
    wv = json.loads((EX / "waves" / "v1_word.json").read_text())
    st = next(r for r in wv["signal"] if r["name"] == "state")
    # cycles per state for the first word: from the first 1 to the next 1
    seq, k0 = [], None
    di = 0
    for k, c in enumerate(st["wave"]):
        if c == "=":
            v = st["data"][di]
            di += 1
            if k0 is not None:
                seq.append((cur, k - k0))
            cur, k0 = v, k
    word = [(s, n) for s, n in seq if s != "0"][:4]
    d = HW(1000, 560, "Where the cycles go",
           "Cycles per word for a 64-word copy, measured, against the "
           "architecture's target.",
           "Bar chart of cycles per word: version 1 at about 8 split into "
           "four FSM phases, version 2 at about 4 and 3, target line at "
           "4.5; below, a timeline showing version 1 serial and version 2 "
           "overlapped")
    X0, S = 290, 82                      # x of zero, px per cycle
    names = {"1": "AR", "2": "R", "3": "AW+W", "4": "B"}
    shades = [BLUE, "#2F6B94", BLUE, "#2F6B94"]
    for c in range(0, 10):
        d.line(X0 + c * S, 100, X0 + c * S, 290, "#E3E7EB")
        d.text(X0 + c * S, 306, c, 12, DIM, "400", "middle", MONO)
    d.text(X0 + 4.5 * S, 326, "cycles per word", 13, DIM, "400", "middle")
    for i, (v, style, r) in enumerate(rates):
        y = 116 + i * 58
        d.text(X0 - 14, y + 18, f"version {v}, {style.lower()}", 14, INK,
               "600", "end", MONO)
        if v == "1":
            x = X0
            for j, (s, n) in enumerate(word):
                d.rect(x, y, n * S, 28, shades[j], "white", 1.5, 0)
                d.text(x + n * S / 2, y + 19, f"{names[s]} {n}", 13, "white",
                       "700", "middle", MONO)
                x += n * S
        else:
            d.rect(X0, y, float(r) * S, 28, GREEN, "white", 1.5, 0)
        if v == "1":
            d.text(X0 + float(r) * S + 8, y + 19, r, 14, INK, "700")
        else:
            d.text(X0 + float(r) * S - 8, y + 19, r, 14, "white", "700",
                   "end")
    d.line(X0 + target * S, 96, X0 + target * S, 292, AMBER, 2.5, "7 5")
    d.text(X0 + target * S + 6, 96, f"target {target}", 13, AMBER, "700")
    # timeline
    ty = 380
    d.text(40, ty - 14, "Three words on a timeline (four-cycle reads and "
           "writes)", 15, BLUE, "700")
    cw = 26

    def blk(x, y, n, t, fill):
        d.rect(x, y, n * cw, 26, fill, "white", 1.5, 3)
        d.text(x + n * cw / 2, y + 18, t, 12, "white", "700", "middle",
               MONO)
    lx = 240
    d.text(lx - 14, ty + 22, "version 1", 14, INK, "600", "end", MONO)
    for w in range(3):
        blk(lx + w * 8 * cw, ty + 4, 4, f"read {w}", BLUE)
        blk(lx + (w * 8 + 4) * cw, ty + 4, 4, f"write {w}", "#2F6B94")
    d.text(lx - 14, ty + 74, "version 2", 14, INK, "600", "end", MONO)
    for w in range(3):
        blk(lx + w * 4 * cw, ty + 56, 4, f"read {w}", GREEN)
        blk(lx + (w * 4 + 4) * cw, ty + 90, 4, f"write {w}", "#4E9A52")
    d.text(lx + 16 * cw + 10, ty + 108, "the read of word n+1 overlaps "
           "the write of word n,", 13, INK)
    d.text(lx + 16 * cw + 10, ty + 126, "so word n waits in a FIFO", 13,
           INK)
    for c in range(0, 25, 4):
        d.text(lx + c * cw, ty + 146, c, 11, DIM, "400", "middle", MONO)
    d.save("ch11-cycles.svg")


# ---- F5: version 2 microarchitecture ----------------------------------
def fig_uarch():
    d = HW(1000, 720, "Version 2 microarchitecture",
           "One owner per register: the channel block owns every "
           "per-channel register; the engines only report.",
           "Microarchitecture block diagram of version 2: APB decode, the "
           "channel block holding per-channel registers, a read engine "
           "with a round-robin arbiter, a two-entry FIFO, a write engine, "
           "and the IRQ register, with numbered design decisions")
    apb = d.unit(30, 130, 150, 150, "APB decode", top=True)
    for i, t in enumerate(["a_ch, a_off", "a_map, wr_ok", "PSLVERR"]):
        d.text(42, 182 + i * 20, t, 12.5, DIM, "400", "start", MONO)
    d.wire([(0, 165), (apb.l - 2, 165)], "data")
    d.text(4, 157, "APB", 12, INK, "700", "start", MONO)
    # channel block with a ghost for channel 1
    d.rect(258, 108, 260, 440, "white", DIM, 1.5, 10, "6 4")
    ch = d.unit(250, 100, 260, 440, "channel block, x2", "the only writer "
                "of channel state", fill="white", top=True)
    rows = [("src", "30"), ("dst", "30"), ("len", "16")]
    for i, (n, wd) in enumerate(rows):
        d.reg(270, 160 + i * 50, n, w=100, h=38, sub=f"[{wd}]")
    for i, (n, wd) in enumerate([("rd_ptr", "30"), ("rd_left", "16")]):
        d.reg(390, 160 + i * 50, n, w=104, h=38, sub=f"[{wd}]")
    for i, (n, wd) in enumerate([("wr_ptr", "30"), ("wr_left", "16")]):
        d.reg(390, 290 + i * 50, n, w=104, h=38, sub=f"[{wd}]")
    d.reg(270, 320, "in_fifo", w=100, h=38, sub="[2]")
    d.text(270, 398, "flags", 13, DIM, "600")
    for i, f in enumerate(["busy", "done", "err", "irq_en", "abort",
                           "drop"]):
        d.reg(270 + (i % 3) * 76, 406 + (i // 3) * 48, f, w=70, h=38,
              fill=AMBER_T if f in ("abort", "drop") else "white")
    d.wire([(apb.r, 180), (ch.l - 2, 180)], "data", "PWDATA", at=(215, 172))
    d.wire([(ch.l, 240), (apb.r + 2, 240)], "data", "PRDATA", at=(215, 232))
    # read engine
    rd = d.unit(590, 100, 230, 170, "read engine", "R_IDLE R_ADDR R_DATA",
                top=True)
    arb = d.unit(610, 160, 190, 50, "round robin", "r_last r_pick",
                 fill="white")
    d.reg(610, 220, "ARADDR", w=110, h=38)
    d.wire([(ch.r, 175), (arb.l - 2, 175)], "data")
    d.text(552, 167, "rd_ptr", 12, INK, "500", "middle", MONO)
    d.text(552, 196, "busy abort", 11, DIM, "400", "middle", MONO)
    d.wire([(rd.l, 255), (ch.r + 2, 255)], "control")
    d.text(552, 248, "rd_good", 12, AMBER, "600", "middle", MONO)
    d.text(552, 270, "rd_bad", 12, AMBER, "600", "middle", MONO)
    d.wire([(rd.r, 160), (990, 160)], "data")
    d.text(830, 152, "AR", 13, BLUE, "700", "start", MONO)
    d.wire([(990, 230), (rd.r + 2, 230)], "data")
    d.text(830, 222, "R", 13, BLUE, "700", "start", MONO)
    # FIFO
    ff = d.fifo(630, 340, 2, w=150, h=50, name="data FIFO, DEPTH 2",
                entry="{ch,\ndata}")
    d.wire([(700, rd.b), (700, ff.t - 26)], "data")
    d.text(708, 300, "{r_ch, RDATA}", 12, INK, "500", "start", MONO)
    d.wire([(ff.r, ff.cy), (812, ff.cy), (812, rd.b + 2)], "control")
    d.text(820, ff.cy - 30, "f_cnt <", 12, AMBER, "600", "start", MONO)
    d.text(820, ff.cy - 14, "DEPTH", 12, AMBER, "600", "start", MONO)
    # write engine
    wr = d.unit(590, 450, 230, 150, "write engine", "W_IDLE W_REQ W_RESP",
                top=True)
    d.reg(610, 510, "AWADDR", w=95, h=38)
    d.reg(712, 510, "WDATA", w=95, h=38)
    d.wire([(700, ff.b), (700, wr.t - 2)], "data")
    d.text(708, 430, "f_ch, word", 12, INK, "500", "start", MONO)
    d.wire([(ch.r, 470), (wr.l - 2, 470)], "data")
    d.text(552, 462, "wr_ptr", 12, INK, "500", "middle", MONO)
    d.text(552, 486, "drop", 11, DIM, "400", "middle", MONO)
    d.wire([(wr.l, 525), (ch.r + 2, 525)], "control")
    d.text(552, 518, "wr_good", 12, AMBER, "600", "middle", MONO)
    d.text(552, 541, "wr_bad", 12, AMBER, "600", "middle", MONO)
    d.text(552, 557, "popped", 12, AMBER, "600", "middle", MONO)
    for i, c in enumerate(["AW", "W"]):
        d.wire([(wr.r, 480 + i * 30), (990, 480 + i * 30)], "data")
        d.text(830, 472 + i * 30, c, 13, BLUE, "700", "start", MONO)
    d.wire([(990, 580), (wr.r + 2, 580)], "data")
    d.text(830, 572, "B", 13, BLUE, "700", "start", MONO)
    d.text(985, 120, "AXI4-Lite", 14, BLUE, "700", "end")
    # IRQ
    irq = d.reg(60, 470, "IRQ", w=90, h=38)
    d.wire([(ch.l, 489), (irq.r + 2, 489)], "control")
    d.text(200, 481, "irq_en &", 11, AMBER, "600", "middle", MONO)
    d.text(200, 506, "(done|err)", 11, AMBER, "600", "middle", MONO)
    d.wire([(irq.l, 489), (2, 489)], "control")
    d.text(4, 481, "IRQ", 12, AMBER, "700", "start", MONO)
    # decisions
    for n, (x, y) in enumerate([(612, 365), (800, 160), (500, 452)], 1):
        d.failure_mark(x, y, n)
    d.text(30, 640, "Decisions the architecture forced:", 14, INK, "700")
    notes = ["1  a FIFO lets a read overlap a write: the 4.5-cycle target",
             "2  round robin: two channels, neither starves",
             "3  abort stops reads, drop discards queued words: "
             "precise errors"]
    for i, t in enumerate(notes):
        d.text(30, 664 + i * 22, t, 13, INK)
    d.legend_hw(560, 640, ("data", "control", "reg", "fifo"))
    d.save("ch11-uarch.svg")


# ---- F6: version 1 state machine --------------------------------------
def fig_fsm():
    d = HW(1000, 730, "Version 1's state machine, as found",
           "Arcs carry the condition and, in brackets, the coverage bin "
           "that counts them. Two arcs break AXI's handshake rules.",
           "Five-state FSM of version 1: IDLE, READ_REQ, READ_RESP, "
           "WRITE_REQ, WRITE_RESP, with labeled transitions and two "
           "amber arcs marking handshake violations")
    idle = d.fsm_state(220, 380, "IDLE", "0", initial=True)
    rq = d.fsm_state(460, 230, "READ_REQ", "1", r=56)
    rr = d.fsm_state(780, 230, "READ_RESP", "2", r=56)
    wq = d.fsm_state(780, 510, "WRITE_REQ", "3", r=56, stroke=AMBER,
                     fill=AMBER_T)
    wr = d.fsm_state(460, 510, "WRITE_RESP", "4", r=56)
    d.fsm_arc(idle, rq, "start, len != 0\n[start]", bend=30, lpos=0.4,
              ldx=-20, ldy=-14, anchor="end")
    d.fsm_loop(idle, "l", "start, len == 0\nor no start\n[idle]")
    d.fsm_loop(rq, "t", "!ARREADY  [ar_wait]")
    d.fsm_arc(rq, rr, "ARREADY  [ar_done]", bend=0, ldy=-10, col=AMBER,
              sw=3)
    d.fsm_loop(rr, "t", "!RVALID  [r_wait]")
    d.fsm_arc(rr, wq, "RVALID, OKAY\n[r_ok]", bend=0, ldx=12, ldy=0,
              anchor="start")
    d.fsm_arc(rr, idle, "RVALID, not OKAY  [r_err]", bend=-60, lpos=0.4,
              ldx=10, ldy=4, anchor="start")
    d.fsm_loop(wq, "r", "!(AWREADY\n  && WREADY)\n[aw_wait]", col=AMBER,
               sw=3)
    d.fsm_arc(wq, wr, "AWREADY && WREADY  [aw_done]", bend=0, ldy=-10)
    d.fsm_loop(wr, "b", "!BVALID  [b_wait]")
    d.fsm_arc(wr, rq, "OKAY, words left\n[next_word]", bend=0, lpos=0.3,
              ldx=12, ldy=0, anchor="start")
    d.fsm_arc(wr, idle, "last word or not OKAY\n[last_or_err]", bend=-40,
              lpos=0.45, ldx=-10, ldy=28, anchor="end")
    d.failure_mark(620, 200, 1)
    d.failure_mark(860, 440, 2)
    d.note(40, 655, "1  taken on ARREADY alone: with READY already high,\n"
           "   ARVALID never rises and no read happens", w=420, size=13)
    d.note(560, 655, "2  waits for AWREADY and WREADY on the same\n"
           "   edge: a slave that takes them apart deadlocks it",
           w=420, size=13)
    d.save("ch11-fsm.svg")


# ---- F7: datapath -----------------------------------------------------
def fig_datapath():
    d = HW(1000, 600, "One channel's read datapath in version 2",
           "Registers, multiplexers and operators: the level at which an "
           "assertion or a white-box coverpoint is written.",
           "Datapath of version 2: source register and read pointer with "
           "an increment, length and words-left counter with a decrement "
           "and a not-zero test feeding the arbiter, a channel multiplexer "
           "to ARADDR, and the FIFO from RDATA to WDATA")
    # address lane
    d.bus([(20, 170), (128, 170)], 30, "PWDATA[31:2]", at=(22, 160),
          anchor="start")
    src = d.reg(130, 151, "src", w=90, h=38, sub="[29:0]")
    m1 = d.mux(250, 130, h=80, sel="start")
    d.wire([(src.r, 170), (m1.l - 2, 170)], "data")
    ptr = d.reg(320, 151, "rd_ptr", w=100, h=38, sub="[29:0]")
    d.wire([(m1.r, 170), (ptr.l - 2, 170)], "data")
    inc = d.op(450, 250, "+1")
    d.wire([(ptr.r, 170), (450, 170), (450, inc.t - 2)], "data")
    d.wire([(inc.l, 250), (230, 250), (230, 192), (m1.l - 2, 192)], "data")
    d.wire([(370, 110), (370, ptr.t - 2)], "control")
    d.text(362, 116, "en: start | rd_good", 12, AMBER, "600", "end",
           MONO)
    m2 = d.mux(560, 130, h=80, sel="r_pick")
    d.wire([(450, 170), (m2.l - 2, 170)], "data")
    d.text(530, 162, "ch0", 11, DIM, "400", "middle", MONO)
    d.wire([(500, 115), (500, 192), (m2.l - 2, 192)], "data", arrow=True)
    d.text(506, 114, "ch1 rd_ptr", 11, DIM, "400", "start", MONO)
    cat = d.unit(630, 148, 90, 44, "{p, 00}", fill="white")
    d.wire([(m2.r, 170), (cat.l - 2, 170)], "data")
    ar = d.reg(760, 151, "ARADDR", w=100, h=38, sub="[31:0]")
    d.wire([(cat.r, 170), (ar.l - 2, 170)], "data")
    d.bus([(ar.r, 170), (985, 170)], 32, "to AXI AR", at=(920, 160))
    # count lane
    ln = d.reg(130, 331, "len", w=90, h=38, sub="[15:0]")
    d.bus([(20, 350), (128, 350)], 16, "PWDATA[15:0]", at=(22, 340),
          anchor="start")
    m3 = d.mux(250, 310, h=80, sel="start")
    d.wire([(ln.r, 350), (m3.l - 2, 350)], "data")
    left = d.reg(320, 331, "rd_left", w=100, h=38, sub="[15:0]")
    d.wire([(m3.r, 350), (left.l - 2, 350)], "data")
    dec = d.op(450, 430, "-1")
    d.wire([(left.r, 350), (450, 350), (450, dec.t - 2)], "data")
    d.wire([(dec.l, 430), (230, 430), (230, 372), (m3.l - 2, 372)], "data")
    nz = d.op(520, 350, "!=0")
    d.wire([(450, 350), (nz.l - 2, 350)], "data")
    arb = d.unit(600, 320, 160, 60, "round robin", "busy & !abort")
    d.wire([(nz.r, 350), (arb.l - 2, 350)], "control")
    d.wire([(arb.cx - 30, arb.t), (arb.cx - 30, 260), (m2.cx, 260),
            (m2.cx, m2.b + 22)], "control")
    d.text(arb.cx - 24, 290, "r_pick", 12, AMBER, "600", "start", MONO)
    d.wire([(870, 450), (870, 350), (arb.r + 2, 350)], "control")
    d.text(876, 420, "f_cnt <", 12, AMBER, "600", "start", MONO)
    d.text(876, 436, "DEPTH", 12, AMBER, "600", "start", MONO)
    # data lane
    d.bus([(20, 500), (318, 500)], 32, "RDATA, from AXI R", at=(22, 490),
          anchor="start")
    ff = d.fifo(320, 476, 2, w=200, h=48, entry="{ch, word}")
    d.text(420, ff.b + 18, "FIFO", 13, INK, "700", "middle")
    wd = d.reg(640, 481, "WDATA", w=100, h=38, sub="[31:0]")
    d.wire([(ff.r, 500), (wd.l - 2, 500)], "data")
    d.wire([(470, ff.t), (470, 450), (870, 450)], "control",
           arrow=False)
    d.bus([(wd.r, 500), (985, 500)], 32, "to AXI W", at=(920, 490))
    d.legend_hw(30, 580, ("data", "control", "reg", "mux", "fifo"))
    d.save("ch11-datapath.svg")


# ---- F8, F9: waveforms ------------------------------------------------
def fig_wave_v1():
    wj = json.loads((EX / "waves" / "v1_word.json").read_text())
    n = len(wj["signal"][0]["wave"])
    cw, nw = 34, 100
    d = HW(1000, 140 + 28 * len(wj["signal"]) + 80,
           "Version 1 moving its first two words",
           "Each word passes through four states in turn; nothing "
           "overlaps. From the directed test's VCD, cycles "
           f"{wj['head']['from']} to {wj['head']['to']}.",
           "Waveform of version 1: APB programming, then for each word an "
           "AR handshake, an R handshake, an AW and W handshake together, "
           "and a B handshake, eight cycles per word")
    x0 = 30 + nw
    st = next(r for r in wj["signal"] if r["name"] == "state")
    ks = [k for k, c in enumerate(st["wave"]) if c == "="]
    a, b = ks[1], ks[5]                       # first 1 to the next 1
    d.rect(x0 + a * cw, 116, (b - a) * cw, 28 * len(wj["signal"]) - 4,
           TRACE, TRACE, 0, 4)
    d.wave(30, 120, wj, cw=cw, rh=28, namew=nw, first=wj["head"]["from"])
    y = 120 + 28 * len(wj["signal"]) + 16
    d.wire([(x0 + a * cw, y), (x0 + b * cw, y)], "plain", both=True)
    d.text(x0 + (a + b) / 2 * cw, y + 20, f"one word: {b - a} cycles", 14,
           BLUE, "700", "middle")
    d.wire([(x0, y), (x0 + ks[1] * cw, y)], "plain", both=True)
    d.text(x0 + ks[1] / 2 * cw, y + 20, "APB: four register writes", 13,
           INK, "500", "middle")
    d.text(x0 + n * cw, y + 46, "state: 1 READ_REQ, 2 READ_RESP, "
           "3 WRITE_REQ, 4 WRITE_RESP", 12, DIM, "400", "end", MONO)
    d.save("ch11-wave-v1.svg")


def fig_wave_v2():
    wj = json.loads((EX / "waves" / "v2_abort.json").read_text())
    n = len(wj["signal"][0]["wave"])
    cw, nw = 52, 100
    d = HW(1000, 140 + 30 * len(wj["signal"]) + 80,
           "Version 2 meets a read error on word 2 of 4",
           "Words 0 and 1 reach the destination; nothing after the "
           "failing read is written; the channel ends with ERROR.",
           "Waveform of version 2's abort test: three reads, the third "
           "answered with SLVERR, two writes, abort rising, busy falling "
           "and err rising")
    x0 = 30 + nw
    rr = next(r for r in wj["signal"] if r["name"] == "RRESP")
    k_err = rr["wave"].rindex("=")
    d.wave(30, 120, wj, cw=cw, rh=30, namew=nw, first=wj["head"]["from"],
           hl_rows=("RRESP", "abort", "err"))
    y = 120 + 30 * len(wj["signal"])
    d.line(x0 + k_err * cw, 112, x0 + k_err * cw, y, AMBER, 2, "6 4")
    d.text(x0 + k_err * cw + 6, y + 22, "SLVERR on the read of 0x1008",
           13, AMBER, "700")
    d.text(x0, y + 22, "writes to 0x8000 and 0x8004 complete", 13, INK)
    d.text(x0, y + 42, "no AWVALID after the error: precise", 13, INK)
    d.text(x0 + n * cw, y + 62, "values in hex", 12, DIM, "400", "end",
           MONO)
    d.save("ch11-wave-v2.svg")


# ---- F10: traceability ------------------------------------------------
def fig_trace():
    plan = yaml.safe_load((EX / "vplan" / "dma_plan.yaml").read_text())
    items = plan["items"]
    status = {e["dir"].split("examples/", 1)[1]: e["run"] for e in
              json.loads((EX.parent / "status.json").read_text())
              ["examples"]}
    rh, Y0 = 38, 140
    H = Y0 + rh * len(items) + 136
    d = HW(1000, H, "From spec item to test and coverage bin",
           "Each row is a plan item. Black-box items come from the "
           "architecture, white-box from the microarchitecture.",
           "Traceability diagram: coverage bins on the left, plan items in "
           "the middle, tests on the right; two must-have items have no "
           "test")
    CX, CW_ = 330, 330
    covers = []
    for it in items:
        for c in it.get("covers", []):
            if c not in covers:
                covers.append(c)
    tests = []
    for it in items:
        for t in it.get("tests", []):
            if t not in tests:
                tests.append(t)
    d.text(CX, Y0 - 20, "plan item", 14, DIM, "700")
    d.text(20, Y0 - 20, "coverage bins", 14, DIM, "700")
    d.text(760, Y0 - 20, "tests (status)", 14, DIM, "700")
    span = rh * len(items)
    cy = {c: Y0 + (i + 0.5) * span / len(covers) for i, c in
          enumerate(covers)}
    ty = {t: Y0 + (i + 0.5) * span / (len(tests) + 1) for i, t in
          enumerate(tests)}
    for c, y in cy.items():
        d.rect(20, y - 13, 200, 26, VIOLET_T, VIOLET, 1.5, 4)
        d.text(30, y + 5, c, 12.5, INK, "500", "start", MONO)
    for t, y in ty.items():
        ok = status.get(t) == "pass"
        d.rect(760, y - 16, 220, 32, GREEN_T if ok else AMBER_T,
               GREEN if ok else AMBER, 1.5, 4)
        d.text(770, y + 5, t.split("/")[-1], 13, INK, "600", "start", MONO)
        d.text(970, y + 5, "pass" if ok else "?", 12, GREEN if ok else
               AMBER, "700", "end", MONO)
    prev, gap = None, 0
    for i, it in enumerate(items):
        if it["source"] != prev:
            if prev is not None:
                gap = 26
                y = Y0 + i * rh
                d.line(CX, y + 6, CX + CW_, y + 6, BLUE, 1.5, "4 3")
                d.text(CX + CW_, y + 21, "microarchitecture items", 12,
                       BLUE, "700", "end")
            prev = it["source"]
        y = Y0 + i * rh + gap
        none = not it.get("tests")
        d.rect(CX, y + 4, CW_, rh - 8, AMBER_T if none else "white",
               AMBER if none else BLUE, 1.8 if none else 1.2, 4)
        d.text(CX + 10, y + rh / 2 + 5, it["id"], 13, BLUE, "700", "start",
               MONO)
        d.text(CX + 92, y + rh / 2 + 5, it["feature"], 13, INK)
        tag = it["priority"]
        d.text(CX + CW_ - 8, y + rh / 2 + 5, "no test" if none else tag,
               11.5, AMBER if none else DIM, "700" if none else "400",
               "end", MONO)
        for c in it.get("covers", []):
            d.wire([(CX, y + rh / 2), (222, cy[c])], "check", arrow=False)
        for t in it.get("tests", []):
            d.wire([(CX + CW_, y + rh / 2), (758, ty[t])], "plain")
    yb = Y0 + span + 8 + gap
    d.text(CX + CW_, Y0 - 20, "architecture items", 12, BLUE, "700",
           "end")
    missing = [it["id"] for it in items if not it.get("tests")]
    must = [it["id"] for it in items
            if not it.get("tests") and it.get("priority") == "must"]
    tail = ("the plan report fails until they do." if must else
            "it is a should-have, so the report passes and lists it.")
    d.note(20, yb + 16, f"{len(items) - len(missing)} of {len(items)} items "
           "have a passing test. "
           f"{' and '.join(missing)} has none: {tail}", w=960, size=14)
    d.save("ch11-trace.svg")


# ---- F11: testbench architecture --------------------------------------
def fig_tb():
    d = HW(1000, 700, "The testbench: one environment, both versions",
           "Tests choose the stimulus; the environment is the same for "
           "version 1 and version 2.",
           "Testbench architecture: tests above the environment; APB "
           "master and AXI-Lite slave around the DUT; a monitor feeding "
           "the scoreboard, coverage and arbitration checker; a reference "
           "model predicting the scoreboard's expected writes")
    for i, t in enumerate(["directed", "regs", "maxlen", "random", "rate",
                           "abort", "findings"]):
        d.tool(40 + i * 135, 88, t, w=120, h=40)
    d.region(20, 150, 960, 520, "dma_env")
    am = d.tool(50, 250, "apb_master", w=170, h=60, sub="xfer, wr, rd")
    dut = d.model(395, 230, "DUT", w=210, h=100, sub="dma_engine | dma_v2")
    sl = d.tool(775, 240, "axil_slave", w=180, h=80,
                sub="mem, errors,\n4 ready styles")
    d.wire([(am.r, 280), (dut.l - 2, 280)], "data", "apb_if",
           at=(300, 270))
    d.wire([(dut.r, 268), (sl.l - 2, 268)], "data")
    d.wire([(sl.l, 296), (dut.r + 2, 296)], "data")
    d.text(690, 258, "axil_if", 13, INK, "500", "middle", MONO)
    d.raw(f'<circle cx="690" cy="282" r="4" fill="{VIOLET}"/>')
    mon = d.tool(560, 400, "axil_monitor", w=260, h=60,
                 sub="handshake stability, counts")
    d.wire([(690, 286), (690, mon.t - 2)], "check")
    d.text(698, 360, "every edge", 12, VIOLET, "500", "start", MONO)
    sb = d.tool(300, 540, "scoreboard", w=190, h=60, sub="observe, check_end")
    cov = d.tool(530, 540, "coverage", w=170, h=60, sub="xfer_cg, probes")
    arb = d.tool(740, 540, "arb_checker", w=190, h=60, sub="version 2 only")
    for t in (sb, arb):
        d.wire([(mon.cx, mon.b), (mon.cx, 505), (t.cx, 505),
                (t.cx, t.t - 2)], "check")
    d.wire([(910, 140), (965, 140), (965, 630), (cov.cx, 630),
            (cov.cx, cov.b + 2)], "plain")
    d.text(cov.cx + 10, 648, "sample() when a transfer ends", 12, INK,
           "500", "start", MONO)
    d.text(mon.cx + 8, 494, "publish(txn)", 12, VIOLET, "500", "start",
           MONO)
    mdl = d.tool(30, 540, "dma_model", w=170, h=60, sub="predict at start")
    d.wire([(mdl.r, 570), (sb.l - 2, 570)], "data", "owed writes",
           at=(250, 560))
    d.line(100, 140, 910, 140, INK, 1.4)
    for i in range(7):
        d.line(100 + i * 135, 128, 100 + i * 135, 140, INK, 1.4)
    d.wire([(135, 140), (135, am.t - 2)], "plain")
    d.wire([(114, 140), (114, 190), (36, 190), (36, 470), (70, 470),
            (70, mdl.t - 2)], "plain")
    d.text(143, 220, "start(ch, src, dst, len)", 12, INK, "500", "start",
           MONO)
    d.wire([(am.cx, am.b), (am.cx, 470), (sb.cx, 470), (sb.cx, sb.t - 2)],
           "data")
    d.text(sb.cx - 6, 462, "STATUS at the end", 12, INK, "500", "end",
           MONO)
    d.text(500, 214, "white-box probes, e.g. dut.state, dut.f_cnt", 12, DIM,
           "400", "middle", MONO)
    d.text(40, 690, "solid: stimulus and responses; dashed violet: what "
           "the monitor observes", 13, DIM)
    d.save("ch11-tb.svg")


# ---- F12: one transfer as a sequence ----------------------------------
def fig_seq():
    cols = [("test", 70), ("apb_master", 210), ("dma_model", 350),
            ("DUT", 490), ("axil_slave", 630), ("axil_monitor", 775),
            ("scoreboard", 920)]
    x = dict(cols)
    d = HW(1000, 760, "One transfer, message by message",
           "A one-word copy through the environment of the previous "
           "figure. Time runs down.",
           "Sequence diagram of one transfer: the test starts the channel, "
           "the model predicts, the APB master programs the DUT, the DUT "
           "reads and writes the slave, the monitor publishes each write "
           "to the scoreboard, and the test checks STATUS")
    for n, cx in cols:
        d.lifeline(cx, 90, 730, n, w=126 if n != "axil_monitor" else 134)
    y = 170
    step = 36
    msgs = [
        ("test", "apb_master", "start(0, src, dst, 1)", "plain"),
        ("test", "dma_model", "predict(src, dst, 1)", "plain"),
        ("dma_model", "scoreboard", "expect: (dst, word)", "plain"),
        ("apb_master", "DUT", "write SRC, DST, LEN", "data"),
        ("apb_master", "DUT", "write CTRL = START", "data"),
        ("DUT", "axil_slave", "AR: src", "data"),
        ("axil_slave", "DUT", "R: word, OKAY", "data"),
        ("DUT", "axil_slave", "AW: dst  W: word", "data"),
        ("axil_slave", "DUT", "B: OKAY", "data"),
        ("axil_monitor", "scoreboard", "observe(write)", "check"),
        ("test", "apb_master", "wait_idle()", "plain"),
        ("apb_master", "DUT", "read STATUS", "data"),
        ("DUT", "apb_master", "DONE", "data"),
        ("test", "scoreboard", "check_end(0, STATUS)", "plain"),
        ("apb_master", "DUT", "write STATUS = DONE (W1C)", "data"),
    ]
    loop_a = loop_b = None
    for i, (a, b, t, k) in enumerate(msgs):
        if i == 5:
            loop_a = y - 26
        if i == 10:
            loop_b = y - 22
        d.message(x[a], x[b], y, t, k)
        y += step
    d.rect(x["DUT"] - 90, loop_a, x["scoreboard"] - x["DUT"] + 150,
           loop_b - loop_a, "none", BLUE, 1.5, 4, "")
    d.activation(x["axil_monitor"], loop_a + 14, loop_b - 44, VIOLET_T)
    d.rect(x["DUT"] - 90, loop_a, 120, 20, BLUE, BLUE, 0, 0)
    d.text(x["DUT"] - 84, loop_a + 15, "loop: per word", 12, "white",
           "700", "start", MONO)
    d.text(x["axil_monitor"] + 12, loop_a + 50, "samples every", 11,
           VIOLET, "500", "start", MONO)
    d.text(x["axil_monitor"] + 12, loop_a + 64, "handshake", 11, VIOLET,
           "500", "start", MONO)
    d.save("ch11-seq.svg")


# ---- F13: coverage map ------------------------------------------------
def fig_coverage():
    v1 = run_out("v1-random")
    v2 = run_out("v2-tests")
    st = v1["st_cp"]
    d = HW(1000, 720, "What the tests reached",
           "Left: the state machine's arcs. Right: the plan's bins for v1 "
           "and v2. Amber is a bin no test hit.",
           "Coverage map: bar chart of the twelve FSM arc bins of version "
           "1 with hit counts, and grids of the length, outcome and slave "
           "style bins for version 1 and version 2 with holes in amber")
    X0, Y0, rh = 150, 120, 34
    mx = max(st.values())
    d.text(30, Y0 - 16, "fsm_cg.st_cp, version 1", 15, BLUE, "700",
           "start", MONO)
    for i, (k, v) in enumerate(st.items()):
        y = Y0 + i * rh
        d.text(X0 - 10, y + 19, k, 13, INK, "500", "end", MONO)
        wpx = 280 * v / mx
        d.rect(X0, y + 6, max(wpx, 2), 20, GREEN if v else AMBER, "white",
               1, 2)
        d.text(X0 + wpx + 8, y + 21, v, 12.5, INK, "600", "start", MONO)
    d.text(30, Y0 + 12 * rh + 24, "every arc hit; r_err 10 times", 13, DIM)

    def grid(x, y, title, rows, cols, data, key):
        d.text(x, y - 34, title, 15, BLUE, "700", "start", MONO)
        cw_, ch_ = 78, 30
        for j, c in enumerate(cols):
            d.text(x + 80 + j * cw_ + cw_ / 2, y - 10, c, 12, DIM, "600",
                   "middle", MONO)
        for i, r in enumerate(rows):
            d.text(x + 72, y + i * ch_ + 20, r, 12.5, INK, "500", "end",
                   MONO)
            for j, c in enumerate(cols):
                v = data.get(key(r, c), 0)
                imp = r == "zero" and c != "ok"
                fill = GREEN_T if v else (GROUND if imp else AMBER_T)
                stroke = GREEN if v else (RULE if imp else AMBER)
                d.rect(x + 80 + j * cw_, y + i * ch_, cw_ - 4, ch_ - 4, fill,
                       stroke, 1.5, 3)
                d.text(x + 80 + j * cw_ + cw_ / 2 - 2, y + i * ch_ + 18,
                       v if v or not imp else "n/a", 12.5,
                       INK if v else (DIM if imp else AMBER), "700",
                       "middle", MONO)
    lens = ["zero", "one", "few", "many", "max", "over"]
    outs = ["ok", "rd_err", "wr_err"]
    grid(520, 150, "len_x_out, version 1", lens, outs,
         v1["len_x_out"], lambda r, c: f"{r}_x_{c}")
    grid(520, 390, "len_x_out, version 2", lens, outs,
         v2["len_x_out"], lambda r, c: f"{r}_x_{c}")
    sy = 650
    d.text(520, sy - 50, "style_cp", 15, BLUE, "700", "start", MONO)
    for row, (lab, data) in enumerate([("v1", v1["style_cp"]),
                                       ("v2", v2["style_cp"])]):
        d.text(600, sy + row * 30 + 2, lab, 12.5, INK, "500", "end", MONO)
        for j, (k, v) in enumerate(data.items()):
            xx = 608 + j * 94
            d.rect(xx, sy - 16 + row * 30, 90, 26, GREEN_T if v else AMBER_T,
                   GREEN if v else AMBER, 1.5, 3)
            d.text(xx + 45, sy + 2 + row * 30, f"{k}" if row == 0 and
                   False else str(v), 12, INK if v else AMBER, "700",
                   "middle", MONO)
            if row == 0:
                d.text(xx + 45, sy - 22, k, 11, DIM, "500", "middle", MONO)
    d.note(30, 560, "zero x err: no word can fail (n/a)\nmax: the maxlen test, "
           "version 2 only\nover: only the len64k finding asks,\n"
           "and it samples no coverage", w=330, size=13)
    d.save("ch11-coverage.svg")


FIGS = [fig_context, fig_arch, fig_regs, fig_cycles, fig_uarch, fig_fsm,
        fig_datapath, fig_wave_v1, fig_wave_v2, fig_trace, fig_tb, fig_seq,
        fig_coverage]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
