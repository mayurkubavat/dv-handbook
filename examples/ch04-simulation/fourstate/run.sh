#!/usr/bin/env bash
# run.sh -- the same unreset design under three initialization models.
#
# Four-state shows the missing reset directly, as an unknown. Two-state
# with a fixed initial value hides it: the design looks like it works.
# Two-state with randomized initialization shows it a different way, as a
# result that changes from seed to seed, which is the signal a two-state
# flow actually gives you.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build

echo "=== four-state, event-driven"
iverilog -g2012 -o build/fs.vvp dut_unreset.sv tb_fourstate.sv
vvp build/fs.vvp | grep -E '^out'

echo "=== two-state, every register starts at zero"
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --x-initial 0 --top-module tb_fourstate -Mdir build/v0 \
    dut_unreset.sv tb_fourstate.sv >/dev/null
./build/v0/Vtb_fourstate | grep -E '^out'

echo "=== two-state, randomized, three seeds"
verilator --binary --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
    --x-initial unique --top-module tb_fourstate -Mdir build/vu \
    dut_unreset.sv tb_fourstate.sv >/dev/null
vals=""
for s in 1 7 99; do
  printf 'seed %-3s ' $s
  v=$(./build/vu/Vtb_fourstate +verilator+rand+reset+2 +verilator+seed+$s \
      | grep -E '^out')
  echo "$v"
  vals="$vals$v|"
done
if [ "$(tr '|' '\n' <<<"$vals" | grep -c .)" -gt 1 ] \
   && [ "$(tr '|' '\n' <<<"$vals" | sort -u | grep -c .)" -gt 1 ]; then
  echo "the result changes with the seed: the missing reset is visible here too"
else
  echo "the result did not change with the seed"
fi
