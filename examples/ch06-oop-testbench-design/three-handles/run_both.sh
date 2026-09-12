#!/usr/bin/env bash
# run_both.sh -- the same file under both simulators.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
echo "--- event-driven simulator"
iverilog -g2012 -o build/th.vvp tb_three_handles.sv \
  && vvp build/th.vvp | grep -E "^sides"
echo "--- statically scheduled simulator"
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --top-module tb_three_handles -Mdir build/v tb_three_handles.sv \
    >/dev/null && ./build/v/Vtb_three_handles | grep -E "^sides"
echo "verdict: the simulators disagree on one virtual call"
