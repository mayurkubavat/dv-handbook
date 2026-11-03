#!/usr/bin/env bash
# run_rate.sh -- the performance number section 11.3 sets a target
# against: one 64-word copy, cycles per word, on each version and each
# slave ready style it survives. Version 1 hangs on READY_FIRST, so it
# is measured with the slave its own testbench used.
set -euo pipefail
cd "$(dirname "$0")"
. ../tb/common.sh
mkdir -p build/v1 build/v2
verilator $VFLAGS --top-module tb_v1 -Mdir build/v1 $V1_SRC >/dev/null
verilator $VFLAGS --top-module tb_v2 -Mdir build/v2 $V2_SRC >/dev/null
per_word() {
  awk -v v="$1" '/^rate:/ { printf "%s, %s slave: %d cycles, %.2f per word\n",
    v, $9, $5, $5 / $2 }'
}
./build/v1/Vtb_v1 +test=rate | per_word "version 1"
./build/v2/Vtb_v2 +test=rate | per_word "version 2"
./build/v2/Vtb_v2 +test=rate +ready_first | per_word "version 2"
# The plan's target (DMA-008): at most 4.5 cycles per word, WAIT_VALID.
./build/v2/Vtb_v2 +test=rate | awk '/^rate:/ { r = $5 / $2;
  printf "verdict: version 2 at %.2f cycles per word %s the 4.5 target\n",
  r, (r <= 4.5 ? "meets" : "misses"); exit (r <= 4.5 ? 0 : 1) }'
