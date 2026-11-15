#!/usr/bin/env python3
"""Generate the figures of the formal-property-verification chapter
(ch18-*.svg).

ch18-map.svg     one question, three methods, what each hands back
ch18-sets.svg    the two-entry FIFO's sixteen states: reachable, bad,
                 and the helper's set between them
ch18-cti.svg     two counterexamples to induction at k = 3
ch18-frames.svg  IC3's lemmas by level, frontier by frontier
ch18-lasso.svg   a liveness counterexample: a stem and a loop
ch18-scale.svg   verdicts by engine and FIFO size, with and without
                 the helper

Every number drawn is read from an example's run.out or computed by
running the example's own code, and each figure checks itself against
the run.out where both state the same thing.

    python3 figures/gen_ch18_figures.py [name ...]
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import (AMBER, AMBER_T, BLUE, DIM, GREEN, GREEN_T,  # noqa
                GROUND, HW, INK, MONO, RULE, TRACE)

EX = (pathlib.Path(__file__).resolve().parent.parent / "examples" /
      "ch18-formal-property-verification")
sys.path.insert(0, str(EX / "common"))


def out(example):
    return (EX / example / "run.out").read_text()


def arrow(d, x1, y1, x2, y2, col=DIM, sw=1.6, dash=None):
    mk = {DIM: "ah", BLUE: "ahd", AMBER: "ahc", INK: "ahg"}.get(col, "ah")
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    d.raw(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" fill="none" '
          f'stroke="{col}" stroke-width="{sw}"{dd} '
          f'marker-end="url(#{mk})"/>')


# ---- F1: the chapter in one picture -----------------------------------
def fig_map():
    d = HW(1000, 470, "One question, three ways to answer it",
           "Does the property hold in every reachable state? What each "
           "method asks a solver, and what it hands back.",
           "Three rows. Bounded model checking unrolls k steps from "
           "reset and returns a trace or nothing up to depth k. "
           "k-induction adds a step case and returns a proof, a trace "
           "or a counterexample to induction. IC3 builds an inductive "
           "invariant one clause at a time and returns a proof with "
           "its invariant or a trace")
    rows = [
        ("Bounded model checking",
         "k steps from reset, then a bad state",
         ["a trace, k steps long", "or: no bug up to depth k"],
         "finds bugs; proves nothing beyond k"),
        ("k-induction",
         "also: k good steps, then a bad one",
         ["a proof, when the step case is unsatisfiable",
          "or: a counterexample to induction"],
         "proves what k steps show; may need a helper"),
        ("IC3",
         "one step, relative to what is known",
         ["a proof, with an inductive invariant",
          "or: a trace from reset"],
         "builds the helper itself, clause by clause"),
    ]
    for i, (name, query, back, note) in enumerate(rows):
        y = 100 + i * 118
        a = d.unit(30, y, 220, 84, name)
        b = d.unit(290, y, 330, 84, "asks a SAT solver about", query,
                   fill="white")
        d.wire([(a.r, a.cy), (b.l, b.cy)])
        d.wire([(b.r, b.cy), (660, b.cy)])
        for j, line in enumerate(back):
            d.text(672, y + 30 + j * 20, line, 13.5, INK,
                   "600" if j == 0 else "400")
        d.text(672, y + 76, note, 13, AMBER, "500")
    d.text(30, 452, "Every query is one of the previous chapter's: a "
           "circuit copied per cycle, turned into clauses, given to a "
           "solver.", 13, DIM)
    d.save("ch18-map.svg")


# ---- F2: the state space of the two-entry FIFO ------------------------
def fifo_states():
    """Classify the 16 states after reset by running the example's
    own model code: {(wr, rd, count): (first step or None, bad)}."""
    from ts import Aig, evaluate, explicit, fields, names, unpack
    model = EX / "common" / "fifo_ptrs2.aag"
    aig, name = Aig(model), names(model)
    n = len(aig.latches)
    reach, _ = explicit(aig)
    table = {}
    for s in range(1 << n):
        r = fields(unpack(s, n), name)
        if not r["started"]:
            continue
        bad = any(ok and b for _, ok, b in
                  (evaluate(aig, s, x)
                   for x in range(1 << len(aig.inputs))))
        table[r["wr_ptr"], r["rd_ptr"], r["count"]] = (reach.get(s), bad)
    return table


def fig_sets():
    table = fifo_states()
    text = out("reach")
    live = [k for k, (step, _) in table.items() if step is not None]
    bad = [k for k, (_, b) in table.items() if b]
    helper = [k for k in table if k[2] & 1 == k[0] ^ k[1]]
    assert f"{len(live)} reachable, {len(bad)} bad" in text
    assert f"count[0] == wr_ptr ^ rd_ptr): {len(helper)} states" in text
    assert set(live) <= set(helper) and not set(helper) & set(bad)
    d = HW(1000, 520, "Sixteen states, six of them reachable",
           "The two-entry FIFO after reset. The property rules out "
           "two states; the design never enters ten.",
           "A grid of sixteen states, four pointer pairs by four "
           "counts. Six are green and carry the step that first "
           "reaches them, two are amber and marked bad, and a blue "
           "outline marks the eight states of the helper's set, which "
           "contains all six green ones and neither amber one")
    x0, y0, cw, ch = 230, 130, 150, 76
    for c in range(4):
        d.text(x0 + c * cw + cw / 2, y0 - 14, f"count = {c}", 14, INK,
               "600", "middle", MONO)
    pairs = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for r, (wr, rd) in enumerate(pairs):
        d.text(x0 - 16, y0 + r * ch + ch / 2 + 5,
               f"wr_ptr={wr} rd_ptr={rd}", 14, INK, "600", "end", MONO)
        for c in range(4):
            step, is_bad = table[wr, rd, c]
            x, y = x0 + c * cw, y0 + r * ch
            fill = (GREEN_T if step is not None else AMBER_T if is_bad
                    else "white")
            edge = (GREEN if step is not None else AMBER if is_bad
                    else RULE)
            d.rect(x + 8, y + 8, cw - 16, ch - 16, fill, edge, 1.6, 6)
            if step is not None:
                d.text(x + cw / 2, y + ch / 2 + 5, f"step {step}", 14,
                       INK, "600", "middle")
            elif is_bad:
                d.text(x + cw / 2, y + ch / 2 + 5, "bad", 14, AMBER,
                       "700", "middle")
            if (wr, rd, c) in helper:
                d.rect(x + 3, y + 3, cw - 6, ch - 6, "none", BLUE, 2.4,
                       9, )
    ly = y0 + 4 * ch + 34
    items = [(GREEN_T, GREEN, f"reachable: {len(live)}, with the step "
              "that first reaches each (reset is step 0)"),
             (AMBER_T, AMBER, f"bad: {len(bad)}, empty with the "
              "pointers apart"),
             ("white", RULE, f"allowed by the property and never "
              f"reached: {16 - len(live) - len(bad)}")]
    for i, (fill, edge, label) in enumerate(items):
        d.rect(x0, ly + i * 24 - 13, 26, 16, fill, edge, 1.6, 3)
        d.text(x0 + 38, ly + i * 24, label, 13.5, INK)
    d.rect(x0, ly + 3 * 24 - 13, 26, 16, "none", BLUE, 2.4, 4)
    d.text(x0 + 38, ly + 3 * 24, f"the helper's set, count[0] == wr_ptr "
           f"^ rd_ptr: {len(helper)} states", 13.5, INK)
    d.save("ch18-sets.svg")


# ---- F3: counterexamples to induction ---------------------------------
def fig_cti():
    text = out("kind")
    plain = text.split("=== the step case at k = 3, decoded")[1] \
        .split("===")[0]
    simple = text.split("=== the step case at k = 3 with different "
                        "states, decoded")[1].split("===")[0]
    table = fifo_states()

    def path(part):
        got = re.findall(r"state \d\s+wr_ptr=(\d) rd_ptr=(\d) count=(\d)"
                         r"\s+(not reachable|reachable)(.*)", part)
        assert len(got) == 4
        return [(int(a), int(b), int(c), "BAD" in e) for a, b, c, _, e
                in got]

    d = HW(1000, 470, "Two counterexamples to induction at k = 3",
           "Three states that satisfy the property, then one that "
           "does not. No state on either path is reachable.",
           "Two rows of four state boxes joined by arrows. In the "
           "first row the first and third states are the same state. "
           "In the second row all four differ. The last state of each "
           "row is amber and marked bad")
    for r, (title, part) in enumerate(
            [("plain induction: the solver may revisit a state", plain),
             ("with unique states: every state on the path differs",
              simple)]):
        y = 130 + r * 160
        states = path(part)
        d.text(30, y - 16, title, 15, BLUE, "700")
        for i, (wr, rd, cnt, is_bad) in enumerate(states):
            assert table[wr, rd, cnt] == (None, is_bad)
            x = 30 + i * 245
            twin = r == 0 and i in (0, 2)
            d.rect(x, y, 190, 84, AMBER_T if is_bad else "white",
                   AMBER if is_bad else BLUE, 2.6 if twin else 1.8, 8,
                   )
            d.text(x + 95, y + 26, f"state {i}", 13, DIM, "400",
                   "middle")
            d.text(x + 95, y + 48, f"wr={wr} rd={rd} count={cnt}", 14,
                   INK, "600", "middle", MONO)
            d.text(x + 95, y + 70, "bad" if is_bad else
                   "good, not reachable", 13, AMBER if is_bad else DIM,
                   "700" if is_bad else "400", "middle")
            if i < 3:
                arrow(d, x + 194, y + 42, x + 241, y + 42, INK, 1.8)
        if r == 0:
            assert "repeated states: 0 and 2" in part
            d.text(30 + 245, y + 104, "states 0 and 2 are one state: "
                   "the path walks a cycle among unreachable states",
                   13, AMBER, "500")
        else:
            assert "repeated states: none" in part
    k = re.search(r"proven at k = (\d+), (\d+) queries", text)
    d.text(30, 440, "Plain induction finds such a path at every k "
           f"tried. With unique states the paths run out: proven at "
           f"k = {k.group(1)}.", 13.5, INK)
    d.save("ch18-cti.svg")


# ---- F4: IC3's lemmas by level ----------------------------------------
def fig_frames():
    text = out("ic3").split("=== the invariant")[0]
    before = re.findall(r"frontier (\d) is clear\.\s+lemmas by level: "
                        r"(.*)", text)
    after = re.findall(r"after propagation:\s+(.*)", text)
    assert len(before) == len(after) == 5
    fixed = re.search(r"level (\d) is empty: F(\d) = F(\d)", text)
    lemmas = int(re.search(r"invariant of (\d+) lemmas", text).group(1))

    def counts(s):
        return {int(a): int(b) for a, b in re.findall(r"(\d):(\d+)", s)}

    d = HW(1000, 500, "Lemmas move outward until one level is empty",
           "IC3 on the two-entry FIFO. Each row is the state of the "
           "engine after one frontier is cleared and its lemmas are "
           "propagated.",
           "A table with five rows, frontier 1 to 5, and six columns, "
           "level 1 to 6. Each cell holds the number of lemmas stored "
           "at that level. In the last row level 4 holds zero lemmas "
           "and level 5 holds six; the zero is circled as the fixed "
           "point")
    x0, y0, cw, ch = 250, 132, 110, 56
    for lv in range(1, 7):
        d.text(x0 + (lv - 1) * cw + cw / 2, y0 - 14, f"level {lv}", 14,
               INK, "600", "middle", MONO)
    for r, ((k, b), a) in enumerate(zip(before, after)):
        k, b, a = int(k), counts(b), counts(a)
        y = y0 + r * ch
        d.text(x0 - 16, y + ch / 2 + 5, f"frontier {k} cleared", 14, INK,
               "600", "end")
        for lv in range(1, 7):
            x = x0 + (lv - 1) * cw
            if lv not in a:
                continue
            hit = fixed and r == 4 and lv == int(fixed.group(1))
            d.rect(x + 6, y + 6, cw - 12, ch - 12,
                   AMBER_T if hit else GREEN_T if a[lv] else "white",
                   AMBER if hit else GREEN if a[lv] else RULE,
                   2.4 if hit else 1.4, 6)
            d.text(x + cw / 2, y + ch / 2 + 6, str(a[lv]), 17, INK,
                   "700", "middle", MONO)
            if b.get(lv) != a[lv]:
                d.text(x + cw - 14, y + 22, f"was {b[lv]}", 10.5, DIM,
                       "400", "end", MONO)
    end = counts(after[-1])
    assert end[int(fixed.group(1))] == 0
    assert sum(n for lv, n in end.items()
               if lv > int(fixed.group(1))) == lemmas
    ly = y0 + 5 * ch + 30
    d.text(30, ly, f"A lemma stored at level i holds in frames 1 to i. "
           f"Level {fixed.group(1)} is empty after the last "
           f"propagation, so F{fixed.group(2)} = F{fixed.group(3)}:",
           13.5, INK)
    d.text(30, ly + 22, f"the {lemmas} lemmas at level "
           f"{fixed.group(3)} are closed under a step, and they are "
           f"the invariant. \"was n\": the count before propagation.",
           13.5, INK)
    d.save("ch18-frames.svg")


# ---- F5: a lasso ------------------------------------------------------
def fig_lasso():
    text = out("lasso").split("=== the same property")[0]
    m = re.search(r"frame (\d+) has the state of frame (\d+) again", text)
    last, back = int(m.group(1)), int(m.group(2))
    head = re.search(r"^cycle +(.*)", text, re.M).group(1).split()
    rows = [[int(v) for v in line.split()] for line in text.splitlines()
            if re.match(r"\s+\d+(\s+\d+)+$", line)]
    assert len(rows) == last + 1 and all(r[-1] == 0 for r in rows)
    reg = head.index("n") + 1
    assert rows[last][reg] == rows[back][reg]
    d = HW(1000, 480, "A liveness counterexample is a stem and a loop",
           "The trace the tool printed for a grant that never comes: "
           "five cycles, the last back in the state of the one before.",
           "A table of five cycles, 0 to 4, with rows rst, req, stall, "
           "n and gnt. gnt is 0 in every cycle. Cycles 0 to 2 are "
           "marked stem. An arrow leads from cycle 4 back to cycle 3 "
           "and is marked loop")
    x0, y0, cw, ch = 210, 150, 130, 40
    for c, row in enumerate(rows):
        x = x0 + c * cw
        d.text(x + cw / 2, y0 - 14, f"cycle {row[0]}", 14, INK, "600",
               "middle", MONO)
        loop = c >= back
        for r, name in enumerate(head):
            y = y0 + r * ch
            if c == 0:
                d.text(x0 - 16, y + ch / 2 + 5, name, 14, INK, "600",
                       "end", MONO)
            d.rect(x + 4, y + 4, cw - 8, ch - 8,
                   AMBER_T if loop and name in ("n", "gnt") else "white",
                   AMBER if loop and name in ("n", "gnt") else RULE,
                   1.4, 5)
            d.text(x + cw / 2, y + ch / 2 + 5, str(row[r + 1]), 15, INK,
                   "600", "middle", MONO)
    by = y0 + len(head) * ch + 18
    d.line(x0 + 6, by, x0 + back * cw - 6, by, BLUE, 2.2)
    d.text(x0 + back * cw / 2, by + 20, f"stem: cycles 0 to {back - 1}",
           13.5, BLUE, "600", "middle")
    xa, xb = x0 + last * cw + cw / 2, x0 + back * cw + cw / 2
    d.raw(f'<path d="M{xa:.0f},{by} L{xa:.0f},{by + 30} L{xb:.0f},'
          f'{by + 30} L{xb:.0f},{by + 4}" fill="none" stroke="{AMBER}" '
          f'stroke-width="2.2" marker-end="url(#ahc)"/>')
    d.text((xa + xb) / 2, by + 50, f"loop: the register n in cycle "
           f"{last} equals n in cycle {back}", 13.5, AMBER, "600",
           "middle")
    d.text(30, 462, "From the loop on, the inputs can repeat for ever "
           "and gnt stays 0. A finite trace with a loop stands for an "
           "infinite one.", 13.5, INK)
    d.save("ch18-lasso.svg")


# ---- F6: verdicts by size ---------------------------------------------
def fig_scale():
    text = out("scaling").split("=== verdicts by number of entries")[1]
    limits = re.search(r"limits: (.*);", text).group(1)
    grid = re.findall(r"^(.*?)\s+(informal-kind|informal-ic3|ric3-ic3)"
                      r"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$", text, re.M)
    assert len(grid) == 9
    d = HW(1000, 580, "The helper removes the dependence on size",
           "Two true properties of the repaired FIFO at four sizes, "
           "one engine to a run, and the first again with the second "
           "assumed.",
           "A grid of verdicts: three groups of three engines against "
           "FIFO sizes 2, 4, 8 and 64. Without the helper, induction "
           "proves the pointer property only at size 2 and the "
           "in-house IC3 up to size 8. With the helper assumed every "
           "cell is proven")
    x0, y0, cw, ch = 470, 124, 120, 40
    for c, size in enumerate((2, 4, 8, 64)):
        d.text(x0 + c * cw + cw / 2, y0 - 12, f"{size} entries", 13.5,
               INK, "600", "middle", MONO)
    y = y0
    for i, (label, engine, *cells) in enumerate(grid):
        if i % 3 == 0:
            if i:
                y += 14
            d.text(30, y + ch / 2 + 5, label.strip(), 14, BLUE, "700",
                   font=MONO)
        d.text(x0 - 16, y + ch / 2 + 5, engine, 13.5, INK, "500", "end",
               MONO)
        for c, v in enumerate(cells):
            ok = v == "proven"
            assert ok or v == "-"
            d.rect(x0 + c * cw + 5, y + 4, cw - 10, ch - 8,
                   GREEN_T if ok else "url(#hatch)",
                   GREEN if ok else RULE, 1.4, 5)
            d.text(x0 + c * cw + cw / 2, y + ch / 2 + 5,
                   "proven" if ok else "no verdict", 13, INK,
                   "600" if ok else "400", "middle")
        y += ch
    d.text(30, y + 26, f"Time allowed for each property: {limits}.",
           13, DIM)
    d.text(30, y + 46, "\"No verdict\" says the limit was reached, and "
           "nothing about what a longer run would do.", 13, DIM)
    d.save("ch18-scale.svg")


FIGS = [fig_map, fig_sets, fig_cti, fig_frames, fig_lasso, fig_scale]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
