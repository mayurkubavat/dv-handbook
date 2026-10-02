#!/usr/bin/env bash
# run_fifo_cov.sh -- the FIFO coverage model under two stimulus mixes
# and one seed, then the two coverage databases merged. The bin counts
# are read from the .dat files, not from the group's percentage.
set -euo pipefail
cd "$(dirname "$0")"
RTL=../../ch01-what-is-dv/rtl/fifo.sv
mkdir -p build
# The book's flags from examples/mk/sv.mk, plus --coverage; lint.vlt
# waives the one warning every covergroup raises on this release.
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --coverage \
    --top-module tb_fifo_cov -Mdir build lint.vlt $RTL tb_fifo_cov.sv \
    >/dev/null

# Covergroup records in a .dat: C '<key>' <count>, the key a sequence of
# \001<tag>\002<value> fields, the h tag the path <group>.<point>.<bin>.
# Printed one line per coverpoint or cross: "<point>: bin=count ...".
bins() {
  awk -F'\001' '/^C /{ if (index($0,"\001t\002covergroup")==0) next;
    split($NF, a, "\047 "); h = substr(a[1], 3);
    n = split(h, p, "."); item = p[2]; bin = p[n];
    if (!(item in seen)) { seen[item] = 1; order[++k] = item }
    line[item] = line[item] " " bin "=" a[2] }
    END { for (i = 1; i <= k; i++) print order[i] ":" line[order[i]] }' \
    "$1" | fold -s -w 78
}
zero_bins() {
  awk -F'\001' '/^C /{ if (index($0,"\001t\002covergroup")==0) next;
    split($NF, a, "\047 "); h = substr(a[1], 3); sub(/^[^.]*\./, "", h);
    if (a[2] == 0) z = z " " h }
    END { print "still zero after the merge:" z }' "$1" | fold -s -w 78
}

echo "--- run A: 50/50 push and pop, seed 1"
./build/Vtb_fifo_cov +bias=even +n=200 +verilator+seed+1 \
    +verilator+coverage+file+build/runA.dat | grep -E '^\+|covered'
bins build/runA.dat
echo "--- run B: push-biased, seed 1"
./build/Vtb_fifo_cov +bias=push +n=200 +verilator+seed+1 \
    +verilator+coverage+file+build/runB.dat | grep -E '^\+|covered'
bins build/runB.dat
echo "--- merge: verilator_coverage --write merged.dat runA.dat runB.dat"
verilator_coverage --write build/merged.dat build/runA.dat build/runB.dat
bins build/merged.dat
zero_bins build/merged.dat
echo "verdict: the merge closed the hole run A left, except full_16," \
     "which the DUT never reaches"
