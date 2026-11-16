#!/usr/bin/env bash
# run_worked.sh -- sizing and signing off the FIFO regression, in the
# order an engineer runs it: a 200-seed pilot of the coverage chapter's
# testbench, the union bound from its per-seed rates, a fresh run of
# that many seeds merged with verilator_coverage, the unseen-bin and
# stimulus checks on it; then the temporal-properties chapter's checking
# testbench (random traffic, its assertions bound to the design) under
# 1000 seeds on the repaired FIFO and on the original. Every file is
# read by path from its chapter. About 50 seconds: three builds.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/fifo_cov.sh
C09=../../ch09-temporal-properties
build_fifo_cov build
# 1. the pilot: seeds 5001..5200
run_fifo_cov build even 200 5001 5200 pilot
# 2. the union bound from the pilot sets the size of the fresh run
n=$(python3 -I -B worked.py size)
# 3. the fresh run: seeds 6001.., n of them, merged into one database
run_fifo_cov build even 200 6001 $((6000 + n)) fresh
verilator_coverage --write build/merged.dat \
    $(for s in $(seq 6001 $((6000 + n))); do echo build/fresh_$s.dat; done)
# 6. the checking testbench, on both FIFOs, 1000 seeds each
for rtl in fixed orig; do
  src=$C09/rtl/fifo_fixed.sv
  [[ $rtl == orig ]] && src=$FIFO_RTL
  mkdir -p build/$rtl
  # SYNCASYNCNET: that chapter's checker reads the asynchronous reset at
  # the clock edge, and its own runner waives the warning for that.
  verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
      -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT -Wno-SYNCASYNCNET \
      --top-module tb_fifo_sva -Mdir build/$rtl $src \
      $C09/fifo-checker/fifo_sva.sv $C09/fifo-checker/fifo_bind.sv \
      $C09/fifo-checker/tb_fifo_sva.sv >/dev/null
  : > build/$rtl.pass
  for s in $(seq 1 1000); do
    p=$(./build/$rtl/Vtb_fifo_sva +verilator+seed+$s 2>&1 \
        | grep -c '^PASS: 400 cycles' || true)
    echo "$s $p" >> build/$rtl.pass
  done
done
python3 -I -B worked.py report "$(verilator --version | cut -d' ' -f1-2)" \
    "$n"
