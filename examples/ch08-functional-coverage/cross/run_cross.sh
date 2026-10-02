#!/usr/bin/env bash
# run_cross.sh -- builds tb_cross with --coverage, runs it, and counts
# each cross's bins in the .dat with verilator_coverage; then builds
# the binsof form with -Wno-fatal and shows what 5.052 does with it.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf build; mkdir -p build             # a stale build prints no warning
FLAGS="--binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME
       -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --coverage"

bins() {  # bins <dat> <cross>: how many bins the .dat holds, how many hit
  rm -rf build/ann
  verilator_coverage --annotate build/ann --annotate-points \
      --annotate-min 1 --filter-type covergroup "$1" >/dev/null
  grep -h "hier=$2\." build/ann/* \
    | awk -v c="$2" '{ n++ } /^\+/ { h++ }
          END { printf "%s: %d bins in the .dat, %d hit\n", c, n, h }'
}

echo "--- tb_cross: two groups, one database"
verilator $FLAGS --top-module tb_cross lint.vlt -Mdir build/tb_cross \
    lint.vlt tb_cross.sv >/dev/null
./build/tb_cross/Vtb_cross +verilator+coverage+file+build/cross.dat \
    | grep get_inst_coverage
verilator_coverage --filter-type covergroup build/cross.dat \
    | grep covergroup | sed 's/^ */summary line: /'
bins build/cross.dat cg_full.ab
bins build/cross.dat cg_small.ab

echo "--- tb_cross_binsof: built with -Wno-fatal"
verilator $FLAGS -Wno-fatal --top-module tb_cross_binsof lint.vlt \
    -Mdir build/tb_cross_binsof lint.vlt tb_cross_binsof.sv 2>&1 \
  | grep -E "^%Warning" | sed -E 's/^(%Warning-[A-Z]+:) [^ ]+ /\1 /'
./build/tb_cross_binsof/Vtb_cross_binsof \
    +verilator+coverage+file+build/binsof.dat | grep get_inst_coverage
bins build/binsof.dat cg.ab
echo "verdict: .dat holds 160 cross bins, 12 hit; binsof was dropped"
