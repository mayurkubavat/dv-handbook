#!/usr/bin/env bash
# lint.sh -- lint the three testbenches with the design under -Wall.
set -euo pipefail
cd "$(dirname "$0")"
for tb in tb_bit tb_logic tb_fixed; do
  verilator --lint-only --timing --timescale 1ns/1ps -Wall \
      -Wno-DECLFILENAME -Wno-INITIALDLY --top-module $tb dut_reg.sv $tb.sv
done
echo "verilator --lint-only -Wall: no warnings on three testbenches"
