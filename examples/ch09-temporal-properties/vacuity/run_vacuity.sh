#!/usr/bin/env bash
# run_vacuity.sh -- one assertion and one cover in two simulations: a
# test that drives no requests, and one that does.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/sim.sh
mkdir -p build/sim
verilator $VFLAGS --coverage --top-module tb_vacuity -Mdir build/sim \
    ack_check.sv responder.sv tb_vacuity.sv >/dev/null
sim() {
  ./build/sim/Vtb_vacuity "$@" +verilator+error+limit+100 \
      +verilator+coverage+file+build/sim.dat >build/sim.log 2>&1 || true
  grep '^test' build/sim.log
  n=$(failures <build/sim.log | grep -c ' Ack_A failed$' || true)
  echo "  Ack_A failed $n times"
  c=$(covers build/sim.dat); echo "$c"
}
echo "=== simulation: no requests driven"
sim
need "$n $c" '^0 covers: +Req_C=0 $' "the quiet run was not a vacuous pass"
echo "=== simulation: requests driven (+traffic)"
sim +traffic
need "$n $c" '^[1-9][0-9]* covers: +Req_C=[1-9]' "Ack_A did not fail"
echo "verdict: a pass with the cover at zero proved nothing"
