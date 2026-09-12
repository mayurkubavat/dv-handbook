#!/usr/bin/env bash
# run_both.sh -- three testbenches, two simulators, one missed reset.
#
# The four-state simulator sees X -> 0 as an edge and `tb_logic` resets;
# the two-state one starts `logic` at zero too, so only `tb_fixed`, which
# manufactures the edge, resets on both.
# -e: a simulator that fails to build or run ends the script here, so a
# verdict is never printed about a comparison that did not happen.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
for tb in tb_bit tb_logic tb_fixed; do
  echo "=== $tb"
  echo "--- event-driven, four-state simulator"
  iverilog -g2012 -o build/$tb.vvp dut_reg.sv $tb.sv
  vvp build/$tb.vvp | grep -E "^tb_[a-z]+: "
  echo "--- statically scheduled, two-state simulator"
  verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
      -Wno-INITIALDLY --top-module $tb -Mdir build/v_$tb \
      dut_reg.sv $tb.sv >/dev/null
  ./build/v_$tb/V$tb | grep -E "^tb_[a-z]+: "
done
echo "verdict: only the manufactured edge resets on both simulators"
