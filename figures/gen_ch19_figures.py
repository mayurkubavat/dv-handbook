#!/usr/bin/env python3
"""Generate the figures of the formal-techniques chapter (ch19-*.svg).

ch19-map.svg       the catalog: six families, what each entry preserves,
                   the design of its example
ch19-preserve.svg  over-approximation, under-approximation, exact
ch19-memabs.svg    one symbolic slot in place of a 256-word array, with
                   the verdicts of the mem-abs example
ch19-track.svg     one tracked word, two tracked words, and the slots
                   the flag form would need a fact about
ch19-prophecy.svg  the prophecy trap: a trace that ends before the check
ch19-ag.svg        the safety ring and the liveness ring of the ag example
ch19-decomp.svg    the DMA's end-to-end property, its lemmas, verdicts
ch19-pipe.svg      the worked example's structure and step verdicts

Every verdict drawn is read from an example's run.out, and each figure
fails if the run.out no longer says what it draws. The map is drawn
from ch19_catalog.csv, the chapter's own classification, and fails if
an entry heading of the chapter is missing from the file or the file
names an entry the chapter does not have.

    python3 figures/gen_ch19_figures.py [name ...]
"""
import csv
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hw import (AMBER, AMBER_T, BLUE, DEEP, DIM, GREEN, GREEN_T,  # noqa
                GROUND, HW, INK, MONO, RULE, TRACE, VIOLET, VIOLET_T)

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
EX = ROOT / "examples" / "ch19-formal-techniques"
QMD = ROOT / "chapters" / "ch19-formal-techniques.qmd"
RED = "#B03A2E"


def out(example):
    return (EX / example / "run.out").read_text()


def row(text, name):
    """(status, detail) of the report row for property NAME in TEXT;
    exactly one such row must exist."""
    got = re.findall(rf"^\S*{re.escape(name)}\s+\w+\s+(\S+)\s*(.*)$",
                     text, re.M)
    assert len(got) == 1, (name, got)
    status, rest = got[0]
    m = re.search(r"depth (\d+)", rest)
    return status, int(m.group(1)) if m else None


def block(text, start, end=None):
    """The part of TEXT from the line holding START to the next END."""
    part = text.split(start, 1)[1]
    return part.split(end, 1)[0] if end else part


def cell(d, x, y, w, h, status, depth=None, label=None, size=12.5):
    """A verdict cell: green for proven or covered, amber for a
    counterexample, hatched for no verdict, white for unreachable."""
    fill, edge, word = {
        "proven": (GREEN_T, GREEN, "proven"),
        "covered": (GREEN_T, GREEN, "covered"),
        "cex": (AMBER_T, AMBER, "cex"),
        "undetermined": ("url(#hatch)", RULE, "no verdict"),
        "unreachable": ("white", INK, "unreachable"),
    }[status]
    d.rect(x, y, w, h, fill, edge, 1.5, 5)
    if depth is not None:
        word += f", depth {depth}"
    if label:
        d.text(x + w / 2, y + h / 2 - 4, label, size - 1, INK, "600",
               "middle", MONO)
        d.text(x + w / 2, y + h / 2 + 13, word, size - 1, INK, "400",
               "middle")
    else:
        d.text(x + w / 2, y + h / 2 + 4, word, size, INK, "600", "middle")


def arrow(d, x1, y1, x2, y2, col=DIM, sw=1.6, dash=None):
    mk = {DIM: "ah", BLUE: "ahd", AMBER: "ahc", INK: "ahg"}.get(col, "ah")
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    d.raw(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" fill="none" '
          f'stroke="{col}" stroke-width="{sw}"{dd} '
          f'marker-end="url(#{mk})"/>')


def cross(d, x, y, r=9):
    d.line(x - r, y - r, x + r, y + r, RED, 3)
    d.line(x - r, y + r, x + r, y - r, RED, 3)


# ---- F1: the catalog ---------------------------------------------------
PRESERVE = {
    "proofs": (TRACE, BLUE, "keeps proofs"),
    "counterexamples": (AMBER_T, AMBER, "keeps counterexamples"),
    "both": (GREEN_T, GREEN, "keeps both"),
    "neither": ("url(#hatch)", RULE, "neither, without an argument"),
    "n.a.": (VIOLET_T, VIOLET, "checks the setup (n.a.)"),
}


def catalog():
    rows = list(csv.DictReader((HERE / "ch19_catalog.csv").open()))
    text = QMD.read_text()
    # Entry headings: every level-3 heading from the first family to
    # the recipes.
    body = text.split("## Shrinking the problem", 1)[1] \
        .split("## Six recipes", 1)[0]
    heads = re.findall(r"^### .*\{#sec-ch19-([a-z]+)\}$", body, re.M)
    labels = [r["label"] for r in rows]
    assert heads == labels, (set(heads) ^ set(labels), heads, labels)
    assert len(rows) == 31
    for r in rows:
        assert r["preserves"] in PRESERVE, r
    return rows


def fig_map():
    rows = catalog()
    fams = []
    for r in rows:
        if not fams or fams[-1][0] != r["family"]:
            fams.append((r["family"], []))
        fams[-1][1].append(r)
    d = HW(1000, 640, "Thirty-one techniques in six families",
           "What each change to the problem preserves, and the design "
           "its example runs on.",
           "Six columns of cells, one per family, each cell an entry "
           "with a colored band for what it preserves and a tag for the "
           "design of its example")
    x0, cw, y0, ch = 24, 160, 104, 58
    for i, (fam, items) in enumerate(fams):
        x = x0 + i * (cw + 3)
        words = fam.split()
        half = (len(words) + 1) // 2
        for j, line in enumerate((" ".join(words[:half]),
                                  " ".join(words[half:]))):
            d.text(x + 6, y0 + j * 17, line, 13.5, BLUE, "700")
        for k, r in enumerate(items):
            y = y0 + 30 + k * ch
            fill, edge, _ = PRESERVE[r["preserves"]]
            d.rect(x, y, cw - 6, ch - 8, "white", RULE, 1.2, 5)
            d.rect(x, y, 9, ch - 8, fill, edge, 1.2, 2)
            d.text(x + 16, y + 20, r["short"], 13, INK, "600")
            tag = r["design"] if r["design"] != "none" else "-"
            eng = r["engine"]
            eng = eng.replace(" + ", "+")
            d.text(x + 16, y + 39, f"{tag} · {eng}", 10, DIM, "400",
                   font=MONO)
    ly = y0 + 30 + 7 * ch + 18
    for i, key in enumerate(PRESERVE):
        fill, edge, label = PRESERVE[key]
        x = 24 + (i % 3) * 320
        y = ly + (i // 3) * 26
        d.rect(x, y - 12, 18, 16, fill, edge, 1.2, 2)
        d.text(x + 26, y + 1, label, 13, INK)
    d.text(24, ly + 60, "Tag: the design of the example (other: a "
           "design built for the entry) and the engines it runs; "
           "- marks a compact entry with no example of its own.",
           12.5, DIM)
    d.save("ch19-map.svg")


# ---- F2: what a change preserves ---------------------------------------
def fig_preserve():
    d = HW(1000, 470, "Which answers survive a change to the problem",
           "Behaviors of the design, and of the changed problem.",
           "Three panels of nested ovals: an over-approximation with a "
           "spurious trace outside the design, an under-approximation "
           "with a missed bug outside the restriction, and an exact "
           "change where the two coincide")
    panels = [
        ("over-approximation", "keeps proofs",
         ["black box, cut point,", "timer, memory and",
          "initial-value abstraction"]),
        ("under-approximation", "keeps counterexamples",
         ["over-constraint for hunting,", "bounded proof,",
          "cover-guided search"]),
        ("exact for the property", "keeps both",
         ["symbolic constant, oracle,", "ghost state,",
          "history variable"]),
    ]
    for i, (name, keeps, ents) in enumerate(panels):
        cx, cy = 170 + i * 330, 230
        d.text(cx, 108, name, 16, BLUE, "700", "middle")
        d.text(cx, 128, keeps, 14, INK, "500", "middle")
        if i == 0:
            d.raw(f'<ellipse cx="{cx}" cy="{cy}" rx="140" ry="82" '
                  f'fill="{TRACE}" stroke="{BLUE}" stroke-width="2"/>')
            d.raw(f'<ellipse cx="{cx - 30}" cy="{cy + 8}" rx="80" '
                  f'ry="50" fill="white" stroke="{DEEP}" '
                  'stroke-width="2"/>')
            d.text(cx - 30, cy + 13, "design", 14, INK, "600", "middle")
            d.text(cx + 60, cy - 54, "changed problem", 12.5, BLUE,
                   "500", "middle")
            cross(d, cx + 96, cy + 10)
            d.text(cx + 96, cy + 38, "spurious", 12.5, RED, "600",
                   "middle")
        elif i == 1:
            d.raw(f'<ellipse cx="{cx}" cy="{cy}" rx="140" ry="82" '
                  f'fill="white" stroke="{DEEP}" stroke-width="2"/>')
            d.raw(f'<ellipse cx="{cx - 36}" cy="{cy + 6}" rx="74" '
                  f'ry="46" fill="{AMBER_T}" stroke="{AMBER}" '
                  'stroke-width="2"/>')
            d.text(cx - 36, cy + 11, "changed", 14, INK, "600", "middle")
            d.text(cx + 40, cy - 56, "design", 13, INK, "600", "middle")
            cross(d, cx + 90, cy + 10)
            d.text(cx + 90, cy + 38, "missed", 12.5, RED, "600",
                   "middle")
        else:
            d.raw(f'<ellipse cx="{cx}" cy="{cy}" rx="140" ry="82" '
                  f'fill="{GREEN_T}" stroke="{GREEN}" stroke-width="2"/>')
            d.raw(f'<ellipse cx="{cx}" cy="{cy}" rx="134" ry="76" '
                  f'fill="none" stroke="{DEEP}" stroke-width="2" '
                  'stroke-dasharray="6 4"/>')
            d.text(cx, cy + 5, "design = changed problem", 14, INK,
                   "600", "middle")
        for j, line in enumerate(ents):
            d.text(cx, 350 + j * 19, line, 13, DIM, "400", "middle")
    d.text(30, 440, "For a cover the rule runs the other way: a cover "
           "reached on an over-approximation may be unreachable in the "
           "design.", 13, DIM)
    d.save("ch19-preserve.svg")


# ---- F3: memory abstraction --------------------------------------------
def fig_memabs():
    t = out("mem-abs")
    verdicts = [
        ("whole design", row(block(t, "=== A", "==="), "a_read")),
        ("boxed, contract", row(block(t, "=== B", "==="), "a_read")),
        ("boxed, no contract", row(block(t, "=== C", "==="), "a_read")),
        ("contract alone",
         row(block(t, "=== D", "--- the helper"), "a_store")),
        ("helper", row(block(t, "--- the helper, alone", "--- the contract"),
                       "h_mem")),
        ("contract + helper",
         row(block(t, "--- the contract with", "==="), "a_store")),
        ("bug, boxed", row(block(t, "=== E", "--- the whole"), "a_read")),
        ("bug, 16 words whole",
         row(block(t, "--- the whole design, 16", "verdict"), "a_read")),
    ]
    expect = ["undetermined", "proven", "cex", "undetermined", "proven",
              "proven", "cex", "cex"]
    assert [v[1][0] for v in verdicts] == expect, verdicts
    d = HW(1000, 520, "One slot in place of 256 words",
           "The RAM with forwarding, whole and abstracted, and the "
           "verdicts of the mem-abs example.",
           "Left the RAM whole, right the storage boxed with one "
           "symbolic slot, its shadow and the contract, below a row of "
           "verdict cells")
    # left: the whole RAM
    d.text(40, 106, "the design", 15, BLUE, "700")
    d.unit(40, 120, 300, 200, "fwd_ram", top=True)
    for i in range(8):
        d.rect(70 + i * 30, 160, 26, 90, "white" if i != 5 else TRACE,
               DEEP, 1.2)
    d.text(190, 275, "m[0..255]: 2048 bits", 12.5, INK, "500", "middle",
           MONO)
    d.text(190, 300, "the property reads one word", 12.5, DIM, "400",
           "middle")
    arrow(d, 330, 205, 400, 205, INK)
    # right: the abstraction
    d.text(420, 106, "the abstraction", 15, BLUE, "700")
    d.unit(420, 120, 540, 200, "fwd_ram, storage boxed", top=True)
    d.rect(440, 150, 180, 120, "url(#hatch)", DIM, 2, 6)
    d.text(530, 200, "mem_store", 14, INK, "700", "middle", MONO)
    d.text(530, 220, "outputs free", 12.5, DIM, "400", "middle")
    d.reg(680, 150, "sa", w=110, sub="free, $stable")
    d.reg(680, 210, "sv, sv_ok", w=110, sub="shadow")
    d.text(820, 175, "the slot", 13, INK, "500")
    d.text(820, 235, "last word written", 13, INK, "500")
    d.text(820, 252, "to sa, and whether", 13, INK, "500")
    d.raw(f'<path d="M680,262 C640,300 600,300 600,272" fill="none" '
          f'stroke="{VIOLET}" stroke-width="2" stroke-dasharray="6 4" '
          'marker-end="url(#ahj)"/>')
    d.text(640, 308, "contract: read of sa returns sv", 12.5, VIOLET,
           "600", "middle", MONO)
    # verdicts
    y = 370
    d.text(40, y - 12, "mem-abs, 256 words unless noted:", 13.5, INK,
           "600")
    w = 112
    for i, (label, (status, depth)) in enumerate(verdicts):
        x = 40 + i * (w + 4)
        cell(d, x, y, w, 56, status, depth if status == "cex" else None)
        for j, part in enumerate(label.split(", ")):
            d.text(x + w / 2, y + 74 + j * 16, part, 11.5, DIM, "400",
                   "middle")
    d.save("ch19-memabs.svg")


# ---- F4: tracking one word and two -------------------------------------
def fig_track():
    t = out("track-word")
    assert row(block(t, "=== C", "==="), "a_integrity")[0] == "proven"
    t2 = out("two-word")
    c = block(t2, "=== C", "===")
    for p in ("p_head1", "p_head2", "p_ahead", "a_order"):
        assert row(c, p)[0] == "proven", p
    for p in ("a_once1", "a_once2"):
        assert row(c, p)[0] == "undetermined", p
    d = HW(1000, 470, "What each check needs to know about the memory",
           "One tracked word, and two; the slots a helper must "
           "describe.",
           "Two FIFO strips: one with a tracked word three slots past "
           "the read pointer, the other with two tracked words and "
           "every other slot shaded")
    x0, cw, h = 130, 72, 52

    def strip(y, marks, shade):
        for i in range(10):
            fill = AMBER_T if i in shade else "white"
            d.rect(x0 + i * cw, y, cw, h, fill, DEEP, 1.4)
            if i in marks:
                d.rect(x0 + i * cw + 3, y + 3, cw - 6, h - 6, "none",
                       BLUE, 2.6, 4)
                d.text(x0 + i * cw + cw / 2, y + h / 2 + 5, marks[i], 14,
                       INK, "700", "middle", MONO)
        d.text(x0 - 12, y + h / 2 + 5, "head", 13, DIM, "500", "end")
        arrow(d, x0 - 10, y + h + 18, x0 + cw / 2, y + h + 4, INK)
        d.text(x0 - 12, y + h + 30, "rd_ptr", 12, DIM, "400", "end",
               MONO)

    d.text(30, 108, "one word: proved with the slot helper", 15, BLUE,
           "700")
    strip(140, {3: "sd"}, set())
    d.line(x0 + 4, 130, x0 + 3 * cw - 4, 130, BLUE, 2)
    d.text(x0 + 1.5 * cw, 124, "ahead = 3", 13, BLUE, "600", "middle",
           MONO)
    for j, line in enumerate(["helper:", "mem[rd_ptr+ahead]", "== sd"]):
        d.text(x0 + 10 * cw + 12, 152 + j * 17, line, 11.5, INK, "500",
               font=MONO)
    d.text(30, 278, "two words: position form proved; flag form's "
           "once-only checks not", 15, BLUE, "700")
    strip(310, {2: "d1", 6: "d2"}, {0, 1, 3, 4, 5, 7, 8, 9})
    d.text(x0 + 10 * cw + 16, 330, "position: a fact", 12.5, INK, "500")
    d.text(x0 + 10 * cw + 16, 348, "about each blue slot", 12.5, INK,
           "500")
    d.text(x0 + 10 * cw + 16, 372, "flag form: \"no other", 12.5, AMBER,
           "600")
    d.text(x0 + 10 * cw + 16, 390, "occupied slot holds", 12.5,
           AMBER, "600")
    d.text(x0 + 10 * cw + 16, 408, "d1\", about every", 12.5, AMBER,
           "600")
    d.text(x0 + 10 * cw + 16, 426, "shaded slot", 12.5, AMBER, "600")
    d.text(30, 455, "Verdicts from the track-word example (16 entries) "
           "and the two-word example (4 entries), helpers assumed.",
           12.5, DIM)
    d.save("ch19-track.svg")


# ---- F5: the prophecy trap ---------------------------------------------
def fig_prophecy():
    t = out("history")
    part = block(t, "--- the prophecy", "verdict")
    status, depth = row(part, "a_proph")
    assert (status, depth) == ("cex", 1)
    trace = re.findall(r"^\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)$", part,
                       re.M)
    assert len(trace) == depth + 1
    push = [int(c) for c, _, _, p, _ in trace if p == "1"]
    assert push == [1] and all(q == "0" for *_, q in trace)
    d = HW(1000, 400, "A check that comes after the trace has ended",
           "The prophecy pv is read at push k and checked at pop k; "
           "the counterexample ends in between.",
           "A timeline of cycles. Push k at cycle 1 with the assertion "
           "reading pv, pop k far to the right with the assumption "
           "checking pv, and a bracket over cycles 0 and 1 marking the "
           "counterexample")
    x0, cw, y = 70, 70, 190
    for c in range(12):
        x = x0 + c * cw
        inside = c <= depth
        d.rect(x + 3, y, cw - 6, 44, TRACE if inside else "white",
               DEEP if inside else RULE, 1.4, 4)
        # The gap to pop k is schematic: cell 11 stands for a later
        # cycle, not for cycle 11.
        label = {10: "...", 11: "later"}.get(c, str(c))
        d.text(x + cw / 2, y + 27, label, 13,
               INK if inside else DIM, "600", "middle", MONO)
    d.text(x0 - 10, y + 27, "cycle", 13, DIM, "500", "end")
    px = x0 + push[0] * cw + cw / 2
    arrow(d, px, 140, px, y - 4, AMBER)
    d.text(px, 118, "push k: the assertion", 13, AMBER, "600", "middle")
    d.text(px, 134, "reads pv here", 13, AMBER, "600", "middle")
    qx = x0 + 11 * cw + cw / 2
    arrow(d, qx, 140, qx, y - 4, VIOLET)
    d.text(qx - 40, 118, "pop k: the assumption", 13, VIOLET, "600",
           "middle")
    d.text(qx - 40, 134, "checks pv here", 13, VIOLET, "600", "middle")
    by = y + 64
    d.line(x0 + 6, by, x0 + (depth + 1) * cw - 6, by, BLUE, 2.4)
    d.text(x0 + (depth + 1) * cw / 2, by + 22,
           f"the counterexample, depth {depth}", 13.5, BLUE, "700",
           "middle")
    d.rect(x0 + (depth + 1) * cw + 3, by - 8, (10 - depth) * cw - 6, 16,
           "url(#hatch)", RULE, 1, 3)
    d.text(x0 + (depth + 1) * cw + (10 - depth) * cw / 2, by + 30,
           "never reached: the assumption constrains nothing here",
           13, DIM, "500", "middle")
    d.text(30, 370, "Read from the history example: the prophecy "
           "asserted at the push fails on a correct FIFO.", 12.5, DIM)
    d.save("ch19-prophecy.svg")


# ---- F6: the two rings -------------------------------------------------
def fig_ag():
    t = out("ag")
    a = block(t, "--- RST1 = 0", "--- RST1 = 1")
    b = block(t, "=== B", "===")
    c = block(t, "=== C", "===")
    dd = block(t, "=== D", "verdict")
    assert row(a, "G_out")[0] == "proven"
    assert row(b, "G_x")[0] == row(b, "G_y")[0] == "proven"
    assert row(c, "G_out")[0] == "proven"
    live = row(dd, "G_x")
    assert live[0] == "cex"
    d = HW(1000, 480, "The same circle, sound for safety, not for "
           "liveness",
           "Two blocks that pass each other's output on, one cycle "
           "later: the ag example.",
           "Two rings of two blocks each. Left: safety, each block "
           "proven under the other's guarantee and the ring proven "
           "flat. Right: liveness, each block proven and the ring "
           "refuted by a lasso")

    def ring(x, title, assume, guar, ring_status, depth):
        d.text(x, 108, title, 16, BLUE, "700")
        ua = d.reg(x + 40, 150, "ua", w=110)
        ub = d.reg(x + 260, 150, "ub", w=110)
        d.wire([(ua.r, ua.cy), (ub.l, ub.cy)], label="x")
        d.wire([(ub.r, ub.cy), (ub.r + 30, ub.cy), (ub.r + 30, 240),
                (ua.l - 30, 240), (ua.l - 30, ua.cy), (ua.l, ua.cy)],
               label="y", at=(x + 205, 258))
        d.text(x, 300, f"assume: {assume}", 13, INK, "500", font=MONO)
        d.text(x, 320, f"guarantee: {guar}", 13, INK, "500", font=MONO)
        cell(d, x, 340, 190, 50, "proven", label="each block")
        cell(d, x + 205, 340, 190, 50, ring_status,
             depth if ring_status == "cex" else None, label="the ring")

    ring(40, "safety", "in == 0", "out == 0", "proven", None)
    ring(540, "liveness", "s_eventually in", "s_eventually out",
         live[0], live[1])
    d.text(40, 420, "The register in each block means a guarantee at "
           "cycle t + 1 needs the other's only up to cycle t.", 13, DIM)
    d.text(40, 442, "Lasso: x and y reset to 0 and pass 0 to each "
           "other for ever.", 13, DIM)
    d.save("ch19-ag.svg")


# ---- F7: the DMA decomposition -----------------------------------------
def fig_decomp():
    t = out("decomp")
    a = block(t, "=== A", "=== B")
    for eng in ("informal-bmc", "informal-kind", "informal-ic3"):
        part = block(a, f"--- {eng}", "---")
        for p in ("E2E_A", "L1_A", "L2_A"):
            assert row(part, p)[0] == "undetermined", (eng, p)
    limit = re.search(r"limit (\d+s)", a).group(1)
    b = block(t, "=== B", "verdict")
    assert row(b, "E2E_A")[0] == "proven"
    cov = row(b, "Done3_C")
    assert cov[0] == "covered"
    d = HW(1000, 470, "The chain is sound; the first links are the work",
           "An end-to-end property of the DMA's channel 0, its two "
           "lemmas, and the verdicts of the decomp example.",
           "A tree: E2E_A proven with L1 and L2 assumed; L1 and L2 with "
           "no verdict from any engine; below them a dashed box of DMA "
           "invariants not written")
    cell(d, 380, 100, 240, 60, "proven", label="E2E_A, L1 and L2 assumed")
    cell(d, 690, 100, 240, 60, "covered", cov[1], label="Done3_C")
    d.text(690, 180, "the witness cover", 12.5, DIM)
    for i, (name, what) in enumerate((("L1_A", "responses + left = len"),
                                      ("L2_A", "done, no error: left = 0"))):
        x = 200 + i * 360
        cell(d, x, 240, 240, 60, "undetermined", label=name)
        d.text(x + 120, 318, what, 12.5, INK, "500", "middle", MONO)
        d.text(x + 120, 336, f"bmc, kind, ic3: no verdict in {limit}",
               12, DIM, "400", "middle")
        arrow(d, x + 120, 240, 500, 162, INK)
        arrow(d, 500, 410, x + 120, 342, DIM, dash="5 4")
    d.rect(330, 370, 340, 70, "white", DIM, 1.6, 8, dash="6 5")
    d.text(500, 398, "invariants of the DMA", 14, INK, "700", "middle")
    d.text(500, 420, "e.g. a write in flight implies busy: not written",
           12.5, DIM, "400", "middle")
    d.save("ch19-decomp.svg")


# ---- F8: the worked example --------------------------------------------
def fig_pipe():
    t = out("pipe-256")
    rec = block(t, "=== step 8", "  assumed")
    lines = re.findall(r"^\s+(\d)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\w+)"
                       r"(?:, depth (\d+))?$", rec, re.M)
    assert len(lines) == 15, lines
    d = HW(1000, 560, "Two 256-entry FIFOs, proved one level at a time",
           "Each child boxed under its contract; one helper at the "
           "parent; the verdicts of the pipe-256 example.",
           "Two boxed FIFOs with ghost counts and contracts, the "
           "parent's count with its helper, and a strip of verdict "
           "cells for the steps")
    for i, name in enumerate(("u0", "u1")):
        x = 160 + i * 380
        d.rect(x, 190, 220, 90, "url(#hatch)", DIM, 2, 8)
        d.text(x + 110, 230, f"fifo in {name}", 14, INK, "700", "middle",
               MONO)
        d.text(x + 110, 250, "boxed", 12.5, DIM, "400", "middle")
        d.reg(x + 230, 252, f"{name}.g", w=96)
        d.text(x + 110, 304, "contract: empty iff g == 0,", 12, VIOLET,
               "600", "middle", MONO)
        d.text(x + 110, 320, "full iff g == 256", 12, VIOLET, "600",
               "middle", MONO)
    d.wire([(60, 235), (160, 235)], label="push")
    d.wire([(380, 235), (540, 235)], label="move")
    d.wire([(760, 235), (900, 235)], label="pop")
    d.reg(430, 110, "G", w=100)
    d.text(560, 124, "helper: G == u0.g + u1.g,", 12.5, BLUE, "600",
           font=MONO)
    d.text(560, 142, "each at most 256", 12.5, BLUE, "600", font=MONO)
    y, w = 370, 60
    d.text(30, y - 14, "step, property: verdict", 13.5, INK, "600")
    for i, (step, eng, lim, prop, status, depth) in enumerate(lines):
        x = 30 + i * (w + 2)
        cell(d, x, y, w, 52, status, None, size=10)
        d.text(x + w / 2, y + 68, step, 12, INK, "700", "middle")
        d.text(x + w / 2, y + 84, prop.replace("_A", "").replace("_C", ""),
               10.5, DIM, "400", "middle", MONO)
        if depth:
            d.text(x + w / 2, y + 100, depth, 10.5, DIM, "400", "middle",
                   MONO)
    d.text(30, y + 130, "Depths in the last row; a hatched cell is a "
           "limit that ended without a verdict.", 12.5, DIM)
    d.save("ch19-pipe.svg")


FIGS = [fig_map, fig_preserve, fig_memabs, fig_track, fig_prophecy,
        fig_ag, fig_decomp, fig_pipe]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGS:
        if not want or f.__name__[4:] in want:
            f()
