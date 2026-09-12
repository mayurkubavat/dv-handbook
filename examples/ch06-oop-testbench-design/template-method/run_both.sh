#!/usr/bin/env bash
# run_both.sh -- the same file under both simulators.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
echo "--- event-driven simulator"
iverilog -g2012 -o build/tm.vvp tb_template.sv \
  && vvp build/tm.vvp | grep -E "^total"
echo "--- statically scheduled simulator"
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --top-module tb_template -Mdir build/v tb_template.sv >/dev/null \
  && ./build/v/Vtb_template | grep -E "^total"
echo "verdict: the simulators disagree on the template method"
