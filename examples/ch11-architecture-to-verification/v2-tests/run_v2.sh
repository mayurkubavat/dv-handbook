#!/usr/bin/env bash
# run_v2.sh -- version 2 against the plan: the directed copy on each
# channel, the register rules, and 300 random rounds with both channels
# at once under all four slave ready styles, then the coverage. Last,
# the first draft of the microarchitecture (PRECISE=0) under the same
# random test, to show what the test caught.
set -euo pipefail
cd "$(dirname "$0")"
. ../tb/common.sh
mkdir -p build/draft
verilator $VFLAGS --coverage --top-module tb_v2 -Mdir build $V2_SRC \
  >/dev/null
for t in directed regs; do
  ./build/Vtb_v2 +test=$t +verilator+coverage+file+build/$t.dat \
    | grep -E '^(---|  |result)'
done
./build/Vtb_v2 +test=random +n=300 +verilator+seed+1 \
  +verilator+coverage+file+build/random.dat | grep -E '^(---|  |result)'
verilator_coverage --write build/v2.dat build/directed.dat build/regs.dat \
  build/random.dat
bins build/v2.dat
zero_bins build/v2.dat
echo "--- the first draft, PRECISE=0, same test and seed"
verilator $VFLAGS -GPRECISE=0 --top-module tb_v2 -Mdir build/draft $V2_SRC \
  >/dev/null
out=$(./build/draft/Vtb_v2 +test=random +n=300 +verilator+seed+1 +report_only)
echo "$out" | grep -m 3 'FAIL'
echo "$out" | grep 'result'
n=$(echo "$out" | grep -c 'writes never seen' || true)
echo "verdict: version 2 passes; the draft lost a word in $n transfers"
