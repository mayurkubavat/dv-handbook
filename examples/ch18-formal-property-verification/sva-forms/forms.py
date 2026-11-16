"""forms.py -- the table of property forms, from one run of forms.tcl.

    python3 forms.py

forms.tcl tries every probe of forms.list on the tool and prints one
line for each. This script checks the lines, prints them as text and
writes tbl-sva.md, which the chapter includes. A form counts as
accepted only when the tool gave the right verdict twice: on a
property that holds and on one that does not. A wrong verdict on an
accepted form fails the run, and so does a change in how many forms
are accepted, turned away or dropped, because the chapter's prose
states those counts. The last check compares this table with the one
the temporal-properties chapter generates, for the forms both list.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import tables  # noqa: E402

WANT = {"assert": ("proven", "cex"), "live": ("proven", "cex"),
        "rtl": ("proven", "cex"), "assume": ("proven", "cex"),
        "fair": ("proven", "cex"), "cover": ("covered", "unreachable")}
COUNTS = {"yes": 50, "refused": 6, "error": 5, "dropped": 4}
# This table's probe -> the row of the other chapter's table that
# tests the same construct.
CH09 = {
    "immcomb": "immediate `assert (e)` in `always_comb`",
    "imm": "immediate `assert (e)` in `always @(posedge clk)`",
    "deferred": "deferred `assert #0 (e)`",
    "final": "deferred `assert final (e)`",
    "clock": "`assert property (@(posedge clk) e)`",
    "disable": "`disable iff (!rst_n)` on a clocked boolean",
    "defaults": "`default clocking` and an unclocked `assert property (e)`",
    "overlap": "overlapped implication `a |-> b`",
    "range": "ranged delay `a |-> ##[1:3] b`",
    "unbounded": "unbounded delay `a |-> ##[1:$] b` (weak)",
    "rep": "consecutive repetition `a[*3]`",
    "reprange": "ranged repetition `a[*1:3] ##1 b`",
    "goto": "goto repetition `b[->2]`",
    "noncons": "nonconsecutive repetition `b[=2] ##1 c`",
    "throughout": "`en throughout (a ##2 b)`",
    "seqand": "sequence `and`, sequence `or`",
    "first": "`first_match(a ##[1:3] b) |-> c`",
    "not": "`not (a ##1 b)`",
    "past": "`$past(x)`",
    "stable": "`$stable`, `$changed`",
    "event": "`assert property (s_eventually e)`, a liveness property",
    "until": "`until`, `s_until`, `until_with`",
    "nexttime": "`nexttime a`",
    "if": "property `if (m) p else q`",
    "followed": "followed-by `a #=# b`, `a #-# c`",
    "assume": "`assume` constraining a free input",
    "coverseq": "`cover property (a ##1 b)`",
    "bind": "`bind` to a module, named port connections",
    "underif": "concurrent assertion inside `always_ff` under `if`",
}
MATRIX = (HERE.parent.parent / "ch09-temporal-properties"
          / "support-matrix" / "matrix.md")

tables.need("informal")
rc, report = tables.shell("forms.tcl", "build/informal")
if rc:
    print(report[-2000:])
    print(f"FAILED: forms.tcl exit status {rc}")
    sys.exit(1)

rows, klass, failed = [], {}, 0
tally = dict.fromkeys(COUNTS, 0)
print(f"tool: informal {tables.version('informal')}; 3 s for each "
      f"property; informal-kind, and informal-ic3 on the liveness rows")
for line in report.splitlines():
    part = line.split("\t")
    if part[0] == "group":
        print(f"== {part[1]}")
        rows.append([f"**{part[1]}**", "", "", "", ""])
        continue
    if part[0] != "row":
        continue
    _, key, kind, label, accepted, message, good, bad, depth = part
    note = ""
    if kind in WANT:
        if (good, bad) != WANT[kind]:
            print(f"FAILED: {key}: verdicts {good} and {bad}, expected "
                  f"{' and '.join(WANT[kind])}")
            failed += 1
        klass[key] = "yes"
        where = "" if depth == "-1" else f", depth {depth}"
        cells = ["yes", good, bad + where]
        if kind in ("live", "fair"):
            note = "liveness; `informal-ic3`"
        elif kind == "assume":
            note = "second verdict: without the assumption"
        if kind == "fair":
            note = "without the assumption; " + note
    elif kind == "dropped":
        klass[key] = "dropped" if accepted == "none" else accepted
        cells = ["no: not in the report, and no message", "—", "—"]
        note = "the one assertion in the file is false"
        if accepted != "none":
            cells[0] = "yes"
            note = f"now read: {accepted}"
    else:                               # a form expected to be refused
        klass[key] = accepted if accepted in ("refused", "error") \
            else "yes"
        how = {"refused": "no: refused at the command",
               "error": "no: error at `prove`"}.get(accepted, "yes")
        cells = [how, "—", "—"]
        note = message if how != "yes" else f"now accepted: {accepted}"
    tally[klass[key]] = tally.get(klass[key], 0) + 1
    plain = re.sub(r"`", "", label)
    print(f"  {plain:48s} {cells[0].replace('`', ''):38s} "
          f"{cells[1]:8s} {cells[2]}")
    if note and kind not in WANT:
        print(f"      {note}")
    rows.append([tables.cell(label)] + [tables.cell(c) for c in cells]
                + [tables.cell(note)])

print("forms: " + ", ".join(f"{n} {k}" for k, n in tally.items()))
if tally != COUNTS:
    print(f"FAILED: the counts were {COUNTS} when the chapter was "
          f"written")
    failed += 1

# The other chapter's table, last column: runs / no build / wrong.
theirs = {}
for cells in tables.read(MATRIX):
    word = cells[-1].split(" — ")[0]
    theirs[cells[0]] = {"runs": "yes", "no build": "refused",
                        "wrong": "dropped"}.get(word, word)
differ = 0
for key, label in CH09.items():
    mine = "refused" if klass[key] == "error" else klass[key]
    if theirs.get(label) != mine:
        print(f"FAILED: {key} is {mine} here and "
              f"{theirs.get(label)} in {MATRIX.name}: {label}")
        differ += 1
print(f"compared with the temporal-properties chapter's table: "
      f"{len(CH09)} forms in both, {differ} differences")
if failed or differ:
    sys.exit(1)

tables.write(
    HERE / "tbl-sva.md",
    ["Form", "Accepted", "Where it holds", "Where it does not", "Note"],
    rows,
    f"Property forms and InFormal {tables.version('informal')} (commit "
    f"`{tables.PIN}`), generated by the example `sva-forms`: one probe "
    "for each form, as a property that holds on the probe design and "
    "one that does not, each in a session of its own with three "
    "seconds and one engine. *Accepted* is *yes* only when both "
    "verdicts are right. A depth counts the reset cycle as 0. "
    "{#tbl-ch18-sva}", grid=True)
print("wrote tbl-sva.md")
