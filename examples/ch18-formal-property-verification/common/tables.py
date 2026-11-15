"""tables.py -- shared by the three scripts that write the chapter's
reference tables as Markdown.

A generated table is a file the chapter includes, so its cells must
survive two readers: Markdown, where a pipe ends a cell even inside a
code span, and LaTeX by way of pandoc, where a bare dollar sign opens
inline math and takes the text up to the next one with it.
"""
import pathlib
import shutil
import subprocess
import sys

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
    """One table cell. A pipe is escaped everywhere, because it ends
    a cell even inside a code span. A dollar sign is escaped outside
    code spans only: inside one it is already literal, and a
    backslash there would be printed."""
    parts = str(text).replace("|", "\\|").split("`")
    for i in range(0, len(parts), 2):       # the parts outside spans
        parts[i] = parts[i].replace("$", "\\$")
    return "`".join(parts)


def write(path, header, rows, caption, align=None):
    """Write a pipe table with a caption and its label below it."""
    align = align or ["---"] * len(header)
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join(align) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    pathlib.Path(path).write_text("\n".join(lines) + f"\n\n: {caption}\n")


def shell(script, work, env=None):
    """Run a Tcl script the way every formal example does, through the
    book's wrapper; returns (exit status, report text)."""
    done = subprocess.run([str(MK / "informal.sh"), script, work],
                          capture_output=True, text=True, env=env)
    return done.returncode, done.stdout
