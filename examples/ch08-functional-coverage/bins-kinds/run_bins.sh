#!/usr/bin/env bash
# run_bins.sh -- build tb_bins_kinds with --coverage, run it, then read
# every bin of the covergroup back from the database the run wrote.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
verilator --binary --coverage --timing --timescale 1ns/1ps -Wall \
    -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
    --top-module tb_bins_kinds -Mdir build lint.vlt tb_bins_kinds.sv \
    >/dev/null
echo "--- the run"
./build/Vtb_bins_kinds +verilator+coverage+file+build/coverage.dat \
    | grep -v '^- '
echo "--- every bin, read back from build/coverage.dat"
# Keep only the covergroup records, then print each one's hierarchy
# name, hit count and bin type in source order.
verilator_coverage --filter-type covergroup --write build/cg.dat \
    build/coverage.dat
tr '\001\002' '|:' < build/cg.dat | awk -F'|' '
  /^C / { line = 0; kind = "normal"; hier = ""; cnt = 0
    for (i = 2; i <= NF; i++) {
      split($i, kv, ":")
      if (kv[1] == "l") line = kv[2] + 0
      if (kv[1] == "bin_type") kind = kv[2]
      if (kv[1] == "h") {
        split(kv[2], hc, "\047 "); hier = hc[1]; cnt = hc[2] + 0
      }
    }
    printf "%03d %-14s %d  %s\n", line, hier, cnt, kind }' | sort | cut -c5-
echo "--- verilator_coverage summary"
verilator_coverage --filter-type covergroup build/coverage.dat \
    | grep covergroup
echo "verdict: the standard says 100.00; the tool keeps b[2] in the count"
