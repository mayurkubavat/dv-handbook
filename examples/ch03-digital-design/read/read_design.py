#!/usr/bin/env python3
"""read_design.py -- read the two-clock design with the book's tools.

Runs the clock tree, reset tree, crossing report and connection graph on
../rtl/top.sv, prints the human report, writes the block diagram, and exits
non-zero if any crossing has no synchronizer. That exit status is what lets
the same tool gate a commit.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE / ".." / ".." / ".." / "tools"))
from dvh.cli import main  # noqa: E402

RTL = HERE / ".." / "rtl"
SOURCES = ("regblock.sv", "sync2.sv", "datapath.sv", "top.sv")
FILES = [str(RTL / f) for f in SOURCES]
SVG = str(HERE / "top-connections.svg")
sys.exit(main(["read", "top", *FILES, "--svg", SVG]))
