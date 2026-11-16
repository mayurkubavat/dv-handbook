#!/usr/bin/env bash
# run_clean.sh -- what N clean seeds prove: the bounds in Python, then
# the coverage chapter's FIFO testbench under 250 seeds of a short-test
# generator (+bias=even +n=30) that rarely fills the FIFO, beside the
# exact chain's probability for the same generator. About 25 seconds.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/fifo_cov.sh
build_fifo_cov build
run_fifo_cov build even 30 1 250 even30
python3 -I -B clean.py "$(verilator --version | cut -d' ' -f1-2)"
