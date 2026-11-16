#!/usr/bin/env bash
# gen.sh -- MCY's fault model on the repaired FIFO without MCY: Yosys's
# own `mutate` pass (the pass MCY drives) lists every mutation of the
# netlist after `prep`, and the list is applied in one Yosys run with
# each mutation behind its own value of a 14-bit select `mutsel`.
#
#   gen.sh OUTDIR   writes OUTDIR/list.txt (one `mutate` command per
#                   mutation, number 0 the unmutated design) and
#                   OUTDIR/fifo_mut.v (the netlist, module fifo_mut).
#
# mutants.txt.gz beside this script is the saved list. Paths are
# relative to the repository root.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="$(mkdir -p "$1" && cd "$1" && pwd)"
cd "$here/../../.."
rtl=examples/ch09-temporal-properties/rtl/fifo_fixed.sv
start=$(date +%s)
yosys -q -p "read_verilog -sv $rtl; prep -top fifo; \
  mutate -list 100000 -seed 1 -none -ctrl mutsel 14 0 \
  -o $out/list.txt" 2>&1 | grep -v 'Replacing memory' || true
{
  echo "read_verilog -sv $rtl"
  echo "prep -top fifo"
  echo "rename fifo fifo_mut"
  grep -v 'mode none' "$out/list.txt" \
    | sed 's/-module fifo /-module fifo_mut /'
  echo "opt_clean"
  echo "write_verilog -noattr $out/fifo_mut.v"
} > "$out/all.ys"
yosys -q -s "$out/all.ys" 2>&1 | grep -v 'Replacing memory' || true
gzip -9c "$out/list.txt" > "$here/mutants.txt.gz"
echo "mutations: $(grep -vc 'mode none' "$out/list.txt")," \
     "netlist: $(wc -l < "$out/fifo_mut.v") lines," \
     "$(( $(date +%s) - start )) s"
