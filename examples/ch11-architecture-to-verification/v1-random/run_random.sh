#!/usr/bin/env bash
# run_random.sh -- version 1 under forty random transfers with the
# coverage of Figure F13: the transfer covergroup the plan asks for and
# the FSM arcs read from the microarchitecture. Bins are read from the
# coverage database, not from a percentage.
set -euo pipefail
cd "$(dirname "$0")"
. ../tb/common.sh
mkdir -p build
verilator $VFLAGS --coverage --top-module tb_v1 -Mdir build $V1_SRC \
  >/dev/null
./build/Vtb_v1 +test=random +n=40 +verilator+seed+1 \
  +verilator+coverage+file+build/v1.dat | grep -E '^(---|AXI|result)'
bins build/v1.dat
zero_bins build/v1.dat
