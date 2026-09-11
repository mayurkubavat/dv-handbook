#!/usr/bin/env bash
# run.sh -- one delay finer than its module's declared precision, under two
# simulators.
#
# The design declares nothing about what should happen to `#1.4` in a
# module whose precision is 1 ns. Each tool decides, they decide
# differently, and the difference is visible in the order two prints come
# out -- on identical source, with no race in it.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build

echo "=== event-driven simulator"
iverilog -g2012 -o build/ts.vvp coarse.sv fine.sv tb_timescale.sv
vvp build/ts.vvp | grep -E '^(coarse|fine)'

echo "=== statically scheduled simulator"
verilator --binary --timing -Wno-DECLFILENAME -Wno-STMTDLY \
    --top-module tb_timescale -Mdir build/v \
    coarse.sv fine.sv tb_timescale.sv >/dev/null
./build/v/Vtb_timescale | grep -E '^(coarse|fine)'
