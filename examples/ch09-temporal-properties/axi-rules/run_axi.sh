#!/usr/bin/env bash
# run_axi.sh -- the AXI master rules on the DMA of the case study: in
# its own random test, then in the same test against two one-line
# mutants of the design that each break one rule.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/sim.sh
C11=../../ch11-architecture-to-verification
RTL=$C11/rtl/dma_v2.sv
# SYNCASYNCNET: the checker reads the asynchronous reset at the clock
# edge, which is what a reset guard is for.
build() {
  mkdir -p "build/$1"
  verilator $VFLAGS -Wno-SYNCASYNCNET --coverage --top-module tb_v2 \
      -Mdir "build/$1" $C11/tb/lint.vlt $C11/rtl/dma_regs_pkg.sv \
      $C11/tb/dma_ifs.sv $C11/tb/dma_tb_pkg.sv "$2" axil_master_sva.sv \
      dma_bind.sv $C11/tb/tb_v2.sv >/dev/null
}
# A mutant is the design with one line changed; the change is printed.
mutant() {
  sed "$2" $RTL > "build/dma_$1.sv"
  diff $RTL "build/dma_$1.sv" | grep '^[<>]' | sed -E 's/ +\/\/.*//' || true
  build "$1" "build/dma_$1.sv"
  "./build/$1/Vtb_v2" +test=random +n=300 +verilator+seed+1 \
      >"build/$1.log" 2>&1 || true
  failures <"build/$1.log" | head -1 | sed 's/  tick *[0-9]*:/  first:/'
  grep -q 'Assertion failed' "build/$1.log" || exit 1
}

echo "=== the design as it is: the case study's random test"
build asis $RTL
./build/asis/Vtb_v2 +test=random +n=300 +verilator+seed+1 \
    +verilator+coverage+file+build/asis.dat | grep -E '^result'
covers build/asis.dat
OLD='R_ADDR: if (ARREADY) begin  '
echo "=== mutant drop: leave the address state after one tick"
mutant drop   "s/$OLD/R_ADDR: begin                /"
echo "=== mutant wander: step the address while it waits"
mutant wander "s/$OLD/R_ADDR: if (!ARREADY) ARADDR <= ARADDR + 4; else begin/"
echo "verdict: no rule failed on the design; each mutant failed" \
     "the rule it breaks"
