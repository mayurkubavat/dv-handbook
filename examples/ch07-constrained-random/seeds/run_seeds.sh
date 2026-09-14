#!/usr/bin/env bash
# run_seeds.sh -- one binary, four runs: the testbench's own comparisons,
# then the simulator's seed changed from the command line and set back.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --top-module tb_seeds -Mdir build tb_seeds.sv >/dev/null
echo "--- default seed"
./build/Vtb_seeds | grep -E "twice|first draw"
for s in 1 2 1; do
  echo "--- +verilator+seed+$s"
  ./build/Vtb_seeds +verilator+seed+$s | grep -E "first draw"
done
echo "verdict: the run's seed reproduces the run; srandom replays a thread"
