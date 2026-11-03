#!/usr/bin/env bash
# run_findings.sh -- five questions the version 1 spec leaves open,
# asked of the RTL in simulation. Each run prints what the design did
# and which checks, written from the spec, it failed.
set -euo pipefail
cd "$(dirname "$0")"
. ../tb/common.sh
mkdir -p build
verilator $VFLAGS --top-module tb_v1 -Mdir build $V1_SRC >/dev/null
fails=0
for t in len64k busy_write apb_read ready_first split_aw_w; do
  out=$(./build/Vtb_v1 +test=$t +report_only +verilator+seed+1)
  echo "$out" | grep -E '^(---|  |finding|result)'
  if echo "$out" | grep -q 'result: FAIL'; then fails=$((fails + 1)); fi
done
echo "verdict: $fails of 5 questions fail a check written from the spec"
