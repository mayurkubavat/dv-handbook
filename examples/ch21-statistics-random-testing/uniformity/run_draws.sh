#!/usr/bin/env bash
# run_draws.sh -- tests a constraint's histogram against the law it
# asks for: first on the constrained-random chapter's own printed
# counts (ch07_counts.py), then on 2000 fresh draws from each of six of
# its classes under seed 1, one process per class so the six run in
# parallel (uniform.py). Needs z3 on the PATH, as that chapter does.
# About 40 seconds: the build is 14 of them, the draws about 22.
set -euo pipefail
cd "$(dirname "$0")"
C7=../../ch07-constrained-random
C6=../../ch06-oop-testbench-design/fifo-env
python3 -I -B ch07_counts.py
mkdir -p build
# forms.sv draws a foreach index and a `unique` array that 5.052 calls
# undriven, which is why that chapter's own Makefile adds -Wno-UNDRIVEN;
# rand_packet.sv extends the packet class of env.sv, which needs fifo_if.
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT -Wno-UNDRIVEN --top-module tb_draws \
    -Mdir build $C6/fifo_if.sv $C6/env.sv $C7/packet-stream/rand_packet.sv \
    $C7/constraint-forms/forms.sv tb_draws.sv >/dev/null
pids=()
for c in range16 dist_assign dist_divide implication solve_before kind; do
  ./build/Vtb_draws +n=2000 +cls=$c +verilator+seed+1 \
      | grep -E '^(D |randomize)' > build/$c.txt &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
python3 -I -B uniform.py "$(verilator --version | cut -d' ' -f1-2)" \
    "$(z3 --version | cut -d' ' -f1-3)"
