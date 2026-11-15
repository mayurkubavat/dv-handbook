#!/usr/bin/env bash
# run_checker.sh -- one checker file, bound to two FIFOs: random
# traffic on the repaired FIFO and on the original.
set -euo pipefail
cd "$(dirname "$0")"
. ../common/sim.sh
FIXED=../rtl/fifo_fixed.sv
ORIG=../../ch01-what-is-dv/rtl/fifo.sv
# SYNCASYNCNET: the checker reads the asynchronous reset at the clock
# edge, which is what a reset guard is for.
SIMFLAGS="$VFLAGS -Wno-SYNCASYNCNET --coverage"
build() {
  mkdir -p "build/$1"
  verilator $SIMFLAGS --top-module tb_fifo_sva -Mdir "build/$1" "$2" \
      fifo_sva.sv fifo_bind.sv tb_fifo_sva.sv >/dev/null
}
build fixed $FIXED
build orig  $ORIG

echo "=== simulation: the repaired FIFO, 400 random cycles"
./build/fixed/Vtb_fifo_sva +verilator+seed+1 \
    +verilator+coverage+file+build/fixed.dat | grep PASS
c=$(covers build/fixed.dat); echo "$c"
for k in FullReached PushFull PopEmpty Drained; do
  need "$c" "${k}_C=[1-9]" "${k}_C read zero on the repaired FIFO"
done
echo "=== simulation: the original FIFO, same test, same seed"
f=$(./build/orig/Vtb_fifo_sva +verilator+seed+1 2>&1 | failures || true)
echo "$f"
need "$f" '^ *tick +[0-9]+: FullBackward_A failed $' \
    "the original did not stop on FullBackward_A alone"
echo "the same run allowed to continue past its failures:"
f=$(./build/orig/Vtb_fifo_sva +verilator+seed+1 +verilator+error+limit+1000 \
    +verilator+coverage+file+build/orig.dat 2>&1 \
    | failures | awk '{ print $3 }' | sort | uniq -c \
    | awk '{ print "  " $2 " failed " $1 " times" }')
echo "$f"
need "$f" '^  FullBackward_A failed [0-9]+ times $' \
    "the original failed some other rule as well"
c=$(covers build/orig.dat); echo "$c"
need "$c" 'FullReached_C=0 ' "the original reached sixteen entries"
echo "verdict: the repaired FIFO passes with every cover hit;" \
     "the original fails FullBackward_A"
