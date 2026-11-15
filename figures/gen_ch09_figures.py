#!/usr/bin/env python3
"""Generate the two figures of the temporal-properties chapter
(ch09-*.svg).

ch09-automaton.svg  "a grant within three ticks of every request" as
                    an automaton, beside the monitor register of the
                    bounded-response example
ch09-attempts.svg   the waveform of the handshake example with one
                    mark per tick for the check Held_A

The second figure's waveform is computed from the same expressions the
testbench uses, and the ticks it marks as failures are checked against
the example's run.out, so the figure cannot show an outcome the
simulator did not print.

    python3 figures/gen_ch09_figures.py
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import (AMBER, AMBER_T, BLUE, DIM, GREEN, GREEN_T,  # noqa
                GROUND, HW, INK, MONO, RULE, TRACE)

EX = (pathlib.Path(__file__).resolve().parent.parent / "examples" /
      "ch09-temporal-properties")


# ---- F1: a sequence is an automaton, and an automaton is registers ----
def fig_automaton():
    d = HW(1000, 520, "One rule, as an automaton and as registers",
           "Every request is granted one, two or three ticks later; in "
           "sequence notation, req |-> ##[1:3] gnt.",
           "State diagram with states idle, age 1, age 2, age 3 and "
           "fail, and below it a three-bit shift register named "
           "waiting whose bits are the three age states")
    y = 210
    idle = d.fsm_state(140, y, "idle", initial=True)
    a1 = d.fsm_state(345, y, "age 1", "waiting[0]")
    a2 = d.fsm_state(550, y, "age 2", "waiting[1]")
    a3 = d.fsm_state(755, y, "age 3", "waiting[2]")
    bad = d.fsm_state(925, y, "fail", r=38, stroke=AMBER, fill=AMBER_T)
    d.fsm_arc(idle, a1, "req", ldy=-10)
    d.fsm_arc(a1, a2, "!gnt", ldy=-10)
    d.fsm_arc(a2, a3, "!gnt", ldy=-10)
    d.fsm_arc(a3, bad, "!gnt", ldy=-10, col=AMBER, sw=3)
    d.fsm_arc(a1, idle, "gnt", bend=-70, ldy=18, col=GREEN)
    d.fsm_arc(a2, idle, "gnt", bend=-110, ldy=18, col=GREEN, lpos=0.4)
    d.fsm_arc(a3, idle, "gnt", bend=-150, ldy=18, col=GREEN, lpos=0.35)
    d.text(140, 108, "a request can start", 13, DIM, "400", "middle")
    d.text(140, 124, "at every tick", 13, DIM, "400", "middle")
    # the registers
    ry = 420
    d.text(30, ry - 22, "The same three states as a shift register: "
           "several can be set at once, one per request still waiting.",
           14, INK)
    xs = [345, 550, 755]
    regs = [d.reg(x - 60, ry, f"waiting[{i}]", w=120, h=44)
            for i, x in enumerate(xs)]
    d.wire([(170, ry + 22), (regs[0].l, ry + 22)], "data", label="req",
           at=(225, ry + 14))
    d.wire([(regs[0].r, ry + 22), (regs[1].l, ry + 22)], "data")
    d.wire([(regs[1].r, ry + 22), (regs[2].l, ry + 22)], "data")
    d.wire([(regs[2].r, ry + 22), (905, ry + 22)], "control",
           label="&& !gnt", at=(860, ry + 14))
    d.rect(905, ry + 4, 80, 36, AMBER_T, AMBER, 2, 4)
    d.text(945, ry + 27, "assert", 14, INK, "600", "middle", MONO)
    d.text(550, ry + 70, "a grant clears every bit", 13, GREEN, "600",
           "middle")
    d.save("ch09-automaton.svg")


# ---- F2: attempts of one assertion over one waveform ------------------
N = 18


def stimulus():
    """The handshake example's wires, tick by tick."""
    rows = []
    for t in range(N):
        valid = 2 <= t <= 4 or 6 <= t <= 8 or t in (10, 13)
        rows.append(dict(
            rst=t == 14, valid=valid, ready=t in (4, 8, 16),
            data="A0" if t <= 4 else "B0" if t == 6 else "C0"))
    return rows


def bits(rows, key):
    out, prev = "", None
    for r in rows:
        c = "1" if r[key] else "0"
        out += "." if c == prev else c
        prev = c
    return out


def fig_attempts():
    rows = stimulus()
    out = (EX / "handshake" / "run.out").read_text()
    printed = sorted(set(int(m) for m in
                         re.findall(r"tick +(\d+): Held_A ", out)))
    data_w, data_v, prev = "", [], None
    for r in rows:
        if r["data"] == prev:
            data_w += "."
        else:
            data_w += "="
            data_v.append(r["data"])
        prev = r["data"]
    wj = {"signal": [
        {"name": "clk", "wave": "p" + "." * (N - 1)},
        {"name": "rst", "wave": bits(rows, "rst")},
        {"name": "valid", "wave": bits(rows, "valid")},
        {"name": "ready", "wave": bits(rows, "ready")},
        {"name": "data", "wave": data_w, "data": data_v}]}
    cw, nw, rh = 46, 110, 30
    d = HW(1000, 470, "One check, tick by tick",
           "Held_A: if an offer was pending on the tick before, valid "
           "is still high. Reset switches the check off.",
           "Waveform of rst, valid, ready and data over eighteen ticks, "
           "with a row of bars below: gray for ticks at which the guard "
           "was false, green for checks that passed, amber for the one "
           "that failed and a hatched bar for the one reset switched "
           "off")
    y0 = 120
    d.wave(30, y0, wj, cw=cw, rh=rh, namew=nw, first=0)
    x0 = 30 + nw
    ya = y0 + rh * 5 + 26
    d.text(x0 - 10, ya + 15, "Held_A", 13, INK, "600", "end", MONO)
    fails = []
    for s in range(N - 1):
        r, nx = rows[s], rows[s + 1]
        x = x0 + s * cw
        if r["rst"]:
            d.rect(x + 3, ya, cw - 6, 22, "url(#hatch)", DIM, 1, 3)
            continue
        if not (r["valid"] and not r["ready"]):
            d.rect(x + 3, ya, cw - 6, 22, GROUND, RULE, 1, 3)
            continue
        lane = ya + 34 + (s % 2) * 28
        if nx["rst"]:
            fill, stroke, word = "url(#hatch)", DIM, "reset"
        elif nx["valid"]:
            fill, stroke, word = GREEN_T, GREEN, "pass"
        else:
            fill, stroke, word = AMBER_T, AMBER, "fail"
            fails.append(s + 1)
        d.rect(x + 3, lane, 2 * cw - 6, 22, fill, stroke, 2, 3)
        d.text(x + cw, lane + 16, word, 12, INK, "600", "middle", MONO)
    if fails != printed:
        sys.exit(f"ch09-attempts: figure says {fails}, run.out {printed}")
    d.text(x0, ya + 112, "gray: no offer was pending here, so the tick "
           "after it checks nothing", 13, DIM)
    d.text(x0, ya + 130, "a two-tick bar: an offer was pending on its "
           "first tick, and the assertion ran on its second", 13, DIM)
    d.save("ch09-attempts.svg")


FIGS = [fig_automaton, fig_attempts]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
