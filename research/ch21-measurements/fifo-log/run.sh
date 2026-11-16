#!/usr/bin/env bash
# run.sh -- build the FIFO logger once with Verilator 5.052 and run it
# under many seeds and push/pop mixes; every line of out/*.log is one
# run. Usage: ./run.sh  (writes out/even.log, out/sweep.log)
set -euo pipefail
cd "$(dirname "$0")"
export PATH=/opt/dvtools/bin:$PATH
RTL=../../../examples/ch01-what-is-dv/rtl/fifo.sv
mkdir -p build out
verilator --version > out/tool.txt
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --top-module tb_fifo_log \
    -Mdir build $RTL tb_fifo_log.sv > /dev/null
# 1000 seeds of the Chapter 8 "even" mix, 200 cycles each.
: > out/even.log
for s in $(seq 1 1000); do
  ./build/Vtb_fifo_log +pw=50 +pr=50 +n=200 +verilator+seed+$s \
      | grep '^RUN' | sed "s/^RUN/RUN seed=$s/" >> out/even.log
done
# A knob sweep for the information-theory experiment: push percent in
# {30,50,70,90}, pop 50, 250 seeds each, 200 cycles.
: > out/sweep.log
for pw in 30 50 70 90; do
  for s in $(seq 1 250); do
    ./build/Vtb_fifo_log +pw=$pw +pr=50 +n=200 +verilator+seed+$s \
        | grep '^RUN' | sed "s/^RUN/RUN seed=$s/" >> out/sweep.log
  done
done
# A long run for the cycle-level (abundance) view: 20000 cycles, seed 1.
./build/Vtb_fifo_log +pw=50 +pr=50 +n=20000 +verilator+seed+1 \
    | grep '^RUN' | sed "s/^RUN/RUN seed=1/" > out/long.log
rm -rf build
wc -l out/*.log
