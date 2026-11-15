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
  echo "  Ack_A failed $(failures <build/sim.log | wc -l) times"
  covers build/sim.dat
}
echo "=== simulation: no requests driven"
sim
echo "=== simulation: requests driven (+traffic)"
sim +traffic
echo "verdict: a pass with the cover at zero proved nothing"
