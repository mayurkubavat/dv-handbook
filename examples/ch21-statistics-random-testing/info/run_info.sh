#!/usr/bin/env bash
# run_info.sh -- the coverage chapter's FIFO testbench under its own two
# knobs, +bias in {even, push} and +n in {50, 100, 200, 400}: eight
# generators, 250 seeds each, one coverage database per seed. Then
# info.py measures each generator's spread, reach and trigger rate and
# which knob moves which bin. About 40 seconds: the build is 13.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/fifo_cov.sh
build_fifo_cov build
for b in even push; do
  for n in 50 100 200 400; do
    run_fifo_cov build $b $n 1 250 ${b}_$n
  done
done
python3 -I -B info.py "$(verilator --version | cut -d' ' -f1-2)"
