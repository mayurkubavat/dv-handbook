#!/usr/bin/env bash
# run.sh -- draw from six Chapter 7 constraint shapes on Verilator 5.052
# with z3 on the path, then test the draws (uniform.py). One long run
# (10000 draws per class, seed 1) and twenty short ones (500 draws,
# seeds 1..20) for the distribution of p-values across seeds, and
# 50000 draws of the 16-bit range alone (seed 2).
set -euo pipefail
cd "$(dirname "$0")"
export PATH=/opt/dvtools/bin:/opt/dvtools/venv/bin:$PATH
mkdir -p build out
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --top-module tb_uniform \
    -Mdir build tb_uniform.sv > /dev/null
./build/Vtb_uniform +n=10000 +verilator+seed+1 | grep -E '^(D|ERR)' \
    | gzip -9 > out/long.txt.gz
for s in $(seq 1 20); do
  ./build/Vtb_uniform +n=500 +verilator+seed+$s | grep -E '^(D|ERR)' \
      | gzip -9 > out/short_$s.txt.gz
done
# A longer run of the 16-bit range alone, 50000 draws, seed 2.
./build/Vtb_uniform +n=50000 +only_ranged +verilator+seed+2 \
    | grep -E '^(D|ERR)' | gzip -9 > out/ranged50k.txt.gz
rm -rf build
python3 uniform.py > run.out
