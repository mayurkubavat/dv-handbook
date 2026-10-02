#!/usr/bin/env bash
# run_silent.sh -- build and run tb_silent_group, keeping the simulator's
# own last words: the run ends when a covergroup that new() never built
# is asked for its figure.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
verilator --binary --timing --timescale 1ns/1ps -Wall \
    -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
    --top-module tb_silent_group -Mdir build lint.vlt tb_silent_group.sv \
    >/dev/null
set +e
./build/Vtb_silent_group 2>&1 | grep -v '^- ' \
    | sed 's/^%/  %/; s/^Aborting/  Aborting/'
rc=${PIPESTATUS[0]}
set -e
echo "simulator exit status : $rc"
echo "verdict: one group said nothing;" \
     "the unbuilt one stopped the run when asked"
