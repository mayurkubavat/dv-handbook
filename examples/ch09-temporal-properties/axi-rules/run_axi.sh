#!/usr/bin/env bash
# run_axi.sh -- the AXI master rules on the DMA engine: in
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
# It must fail the rule named for it, and that must be the first
# assertion of the checker to fail.
mutant() {
  sed "$3" $RTL > "build/dma_$1.sv"
  diff $RTL "build/dma_$1.sv" | grep '^[<>]' | sed -E 's/ +\/\/.*//' || true
  build "$1" "build/dma_$1.sv"
  "./build/$1/Vtb_v2" +test=random +n=300 +verilator+seed+1 \
      >"build/$1.log" 2>&1 || true
  f=$(failures <"build/$1.log" | head -1)
  echo "$f" | sed 's/  tick *[0-9]*:/  first:/'
  need "$f" " $2 failed \$" "mutant $1 did not fail $2"
}

echo "=== the design as it is: its random test"
build asis $RTL
./build/asis/Vtb_v2 +test=random +n=300 +verilator+seed+1 \
    +verilator+coverage+file+build/asis.dat | grep -E '^result: PASS'
c=$(covers build/asis.dat); echo "$c"
for k in Ar Aw W; do
  need "$c" "${k}Wait_C=[1-9].*${k}First_C=[1-9]" "a $k cover read zero"
done
OLD='R_ADDR: if (ARREADY) begin  '
echo "=== mutant drop: leave the address state after one tick"
mutant drop ArHeld_A "s/$OLD/R_ADDR: begin                /"
echo "=== mutant wander: step the address while it waits"
mutant wander ArStable_A \
    "s/$OLD/R_ADDR: if (!ARREADY) ARADDR <= ARADDR + 4; else begin/"
echo "verdict: no rule failed on the design; each mutant failed" \
     "the rule it breaks"
