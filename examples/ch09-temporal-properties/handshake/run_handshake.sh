#!/usr/bin/env bash
# run_handshake.sh -- the handshake checker in simulation: once as the
# simulator runs it by default, once allowed to go on after a failure.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/sim.sh
mkdir -p build
verilator $VFLAGS --coverage --top-module tb_handshake -Mdir build \
    hs_check.sv tb_handshake.sv >/dev/null

echo "--- default: the first failure ends the run"
rc=0; ./build/Vtb_handshake >build/default.log 2>&1 || rc=$?
failures <build/default.log
echo "  exit status $rc"
echo "--- +verilator+error+limit+100: every failure, to the end"
rc=0
./build/Vtb_handshake +verilator+error+limit+100 \
    +verilator+coverage+file+build/hs.dat >build/all.log 2>&1 || rc=$?
failures <build/all.log
echo "  exit status $rc"
covers build/hs.dat
n=$(failures <build/all.log | wc -l)
[ "$n" -eq 5 ] || { echo "unexpected: $n failures, wanted 5"; exit 1; }
echo "verdict: three rules failed once each;" \
     "only the rule with no reset term failed at the reset"
