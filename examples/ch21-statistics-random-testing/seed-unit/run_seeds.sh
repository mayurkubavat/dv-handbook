#!/usr/bin/env bash
# run_seeds.sh -- the coverage chapter's FIFO testbench under 1000 seeds
# of one generator (+bias=even +n=200), one coverage database per seed,
# then seed_unit.py reads the bins back. About 25 seconds: the build is
# 13 of them.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/fifo_cov.sh
build_fifo_cov build
run_fifo_cov build even 200 1 1000 even200
python3 -I -B seed_unit.py "$(verilator --version | cut -d' ' -f1-2)"
