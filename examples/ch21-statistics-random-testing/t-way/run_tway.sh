#!/usr/bin/env bash
# run_tway.sh -- t-way coverage in Python (constructions, a greedy array
# and random selection on the architecture chapter's DMA transfer
# space), then that chapter's own version-2 random test under 50 seeds
# of 10 rounds, read back from one coverage database per seed and set
# against the Python model of its generator. The testbench and RTL are
# read by path from that chapter. About 35 seconds: the build is 25.
set -euo pipefail
cd "$(dirname "$0")"
C11=../../ch11-architecture-to-verification
SRC="$C11/tb/lint.vlt $C11/rtl/dma_regs_pkg.sv $C11/tb/dma_ifs.sv \
  $C11/tb/dma_tb_pkg.sv $C11/rtl/dma_v2.sv $C11/tb/tb_v2.sv"
SEEDS=50
ROUNDS=10
mkdir -p build
# The flags of that chapter's tb/common.sh (the book's, from sv.mk),
# plus --coverage.
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --coverage --top-module tb_v2 \
    -Mdir build $SRC >/dev/null
for s in $(seq 1 $SEEDS); do
  ./build/Vtb_v2 +test=random +n=$ROUNDS +verilator+seed+$s \
      +verilator+coverage+file+build/r_$s.dat | grep -q '^result: PASS'
done
python3 -I -B tway.py "$(verilator --version | cut -d' ' -f1-2)" \
    $SEEDS $ROUNDS
