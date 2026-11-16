"""tables.py -- shared by the three scripts that write the chapter's
reference tables as Markdown.

A generated table is a file the chapter includes, so its cells must
survive two readers: Markdown, and LaTeX by way of pandoc, where a bare
dollar sign opens inline math and takes the text up to the next one
with it. A pipe ends a cell of a pipe table even inside a code span,
and the escape `\\|` is then printed with its backslash inside the
span (pandoc 3.1.3, HTML and LaTeX alike). A table whose cells hold an
operator such as `|->` is therefore written as a grid table, where
the cells are found by position and a pipe inside one is plain text.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import textwrap

PIN = "5114330"         # the commit of InFormal the book's text is pinned to
MK = pathlib.Path(__file__).resolve().parent.parent.parent / "mk"


def need(*programs):
    """Print the one line the checker reads as a skip, and stop, when
    a program this example needs is not installed."""
    for p in programs:
        if not shutil.which(p):
            print(f"skipped: {p} is not on the PATH")
            sys.exit(0)


def version(program):
    out = subprocess.run([program, "--version"], capture_output=True,
                         text=True).stdout.split()
    return out[-1] if out else "?"


def cell(text):
    """One table cell. A dollar sign is escaped outside code spans
    only: inside one it is already literal, and a backslash there
    would be printed. A pipe is left alone; `write` refuses a pipe
    table that has one and writes a grid table instead."""
    parts = str(text).split("`")
    for i in range(0, len(parts), 2):       # the parts outside spans
        parts[i] = parts[i].replace("$", "\\$")
    return "`".join(parts)


# A grid cell is a block, so text that opens a list, a heading, a
# quotation or a definition would be read as one.
BLOCK = re.compile(r"([-+*] |[0-9]+[.)] |#|>|: )")


def wrap(text, width):
    """The lines of a cell wrapped at spaces to width characters; a
    word longer than width keeps its own line. A code span broken at a
    space is joined again with a space, which is what it held."""
    return textwrap.wrap(text, width, break_long_words=False,
                         break_on_hyphens=False) or [""]


def write(path, header, rows, caption, align=None, grid=False,
          widths=None):
    """Write a pipe table, or with grid=True a grid table, with a
    caption and its label below it. Each cell is one line, except that
    a grid table given widths wraps its cells to them: the dashes of a
    grid table set the share of the page each column gets, and without
    widths one long cell would squeeze the other columns."""
    align = align or ["---"] * len(header)
    every = [header] + rows
    if not grid:
        assert not any("|" in c for r in every for c in r), \
            "a pipe in a pipe table's cell: write it with grid=True"
        lines = ["| " + " | ".join(header) + " |",
                 "|" + "|".join(align) + "|"]
        lines += ["| " + " | ".join(row) + " |" for row in rows]
    else:
        for c in (c for r in every for c in r):
            assert "\n" not in c and not BLOCK.match(c), repr(c)
        if widths:
            width = [max([w] + [len(x) for r in every for x in
                                wrap(r[i], w)])
                     for i, w in enumerate(widths)]
        else:
            width = [max(len(r[i]) for r in every)
                     for i in range(len(header))]
        rule = "+" + "+".join("-" * (w + 2) for w in width) + "+"
        head = "+" + "+".join(
            (":" if a.startswith(":") else "=") + "=" * w
            + (":" if a.endswith(":") else "=")
            for a, w in zip(align, width)) + "+"

        def line(r):
            cells = [wrap(c, w) if widths else [c]
                     for c, w in zip(r, width)]
            return ["| " + " | ".join(
                (c[k] if k < len(c) else "").ljust(w)
                for c, w in zip(cells, width)) + " |"
                for k in range(max(map(len, cells)))]
        lines = [rule] + line(header) + [head]
        for r in rows:
            lines += line(r) + [rule]
    pathlib.Path(path).write_text("\n".join(lines) + f"\n\n: {caption}\n")


def read(path):
    """The body rows of the grid tables in a Markdown file, each a
    list of stripped cells; rules and header rows are left out."""
    rows, cuts, header, inside = [], [], False, False
    for text in pathlib.Path(path).read_text().splitlines():
        if text.startswith("+"):
            cuts = [i for i, ch in enumerate(text) if ch == "+"]
            header = not inside or (header and "=" not in text)
            inside = True
        elif text.startswith("|") and inside:
            if not header:
                rows.append([text[a + 1:b].strip()
                             for a, b in zip(cuts, cuts[1:])])
        else:
            inside = False
    return rows


def shell(script, work, env=None):
    """Run a Tcl script the way every formal example does, through the
    book's wrapper; returns (exit status, report text)."""
    done = subprocess.run([str(MK / "informal.sh"), script, work],
                          capture_output=True, text=True, env=env)
    return done.returncode, done.stdout
