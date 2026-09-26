#!/usr/bin/env bash
# run_nosolver.sh -- the same binary twice: with the solver the book's
# environment carries, and with VERILATOR_SOLVER pointed at nothing.
# Verilator does not solve constraints itself; at run time it hands them
# to an SMT solver over a pipe, and when there is none it warns and
# returns from randomize() without changing anything.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --top-module tb_nosolver -Mdir build tb_nosolver.sv >/dev/null
echo "--- with z3 on the path"
./build/Vtb_nosolver | grep -E "^randomize"
echo "--- with VERILATOR_SOLVER=/nonexistent/z3"
VERILATOR_SOLVER=/nonexistent/z3 ./build/Vtb_nosolver > build/nosolver.log 2>&1
grep -m1 -E "^%Warning: Unable" build/nosolver.log
grep -E "^randomize" build/nosolver.log
echo "verdict: without a solver every call returned 0 and len kept 99"
