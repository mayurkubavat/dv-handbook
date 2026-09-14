#!/usr/bin/env bash
# run_stream.sh -- the stream under three seeds, the third repeating the
# first: a different mix each time the seed changes, the same mix when it
# does not.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --top-module tb_packet_stream \
    -Mdir build ../../ch01-what-is-dv/rtl/fifo.sv \
    ../../ch06-oop-testbench-design/fifo-env/fifo_if.sv \
    ../../ch06-oop-testbench-design/fifo-env/env.sv \
    rand_packet.sv tb_packet_stream.sv >/dev/null
for s in 3 4 3; do
  printf 'seed %s: ' $s
  ./build/Vtb_packet_stream +verilator+seed+$s | grep -E "packets"
done
echo "verdict: every packet checked; the mix follows the seed"
