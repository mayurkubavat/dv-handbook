#!/usr/bin/env bash
# run_both.sh -- one static task, two concurrent callers, two simulators.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
echo "--- event-driven simulator"
iverilog -g2012 -o build/lt.vvp tb_lifetime.sv \
  && vvp build/lt.vvp | grep -E "task"
echo "--- statically scheduled simulator"
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --top-module tb_lifetime -Mdir build/v tb_lifetime.sv >/dev/null \
  && ./build/v/Vtb_lifetime | grep -E "task"
echo "verdict: the static task's answer depends on the simulator"
