#!/usr/bin/env bash
# run_response.sh -- a rule that spans several ticks, checked by a
# monitor register and one assertion, in simulation on a
# responder that breaks the rule and on one that keeps it.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/sim.sh
run() {
  mkdir -p "build/$1"
  verilator $VFLAGS --coverage -GSLOW_BY_ONE="$2" --top-module \
      tb_responder -Mdir "build/$1" responder.sv resp_check.sv \
      resp_bind.sv tb_responder.sv >/dev/null
  "./build/$1/Vtb_responder" +verilator+seed+1 +verilator+error+limit+100 \
      "+verilator+coverage+file+build/$1.dat" >"build/$1.log" 2>&1 || true
  failures <"build/$1.log"
  echo "  Window_A failed $(failures <"build/$1.log" | wc -l) times"
  covers "build/$1.dat"
}
echo "=== the slow-by-one responder, 40 random ticks, seed 1"
run slow 1
[ "$(failures <build/slow.log | wc -l)" -gt 0 ] || exit 1
echo "=== the correct responder, same test, same seed"
run good 0
[ "$(failures <build/good.log | wc -l)" -eq 0 ] || exit 1
echo "verdict: the monitor register caught the late grant"
