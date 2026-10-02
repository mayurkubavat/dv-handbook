#!/usr/bin/env bash
# run_codecov.sh -- Verilator's own coverage on the counter, end to end:
# build with --coverage, run twice, read each .dat back, annotate the
# source at two thresholds, merge, rank, and export to lcov.
set -euo pipefail
cd "$(dirname "$0")"
RTL=../../appF-counter/rtl/counter.sv
mkdir -p build
# The book's flags from examples/mk/sv.mk, plus --coverage.
verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
    -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --coverage \
    --top-module tb_counter_cov -Mdir build $RTL tb_counter_cov.sv \
    >/dev/null

# Records per type in a .dat: each line is C '<key>' <count>, the key a
# sequence of \001<tag>\002<value> fields; tag t is the point type.
records() {
  awk -F'\001' '/^C /{for(i=2;i<=NF;i++) if(substr($i,1,2)=="t\002")
    n[substr($i,3)]++} END{printf "records: line=%d toggle=%d branch=%d",
    n["line"],n["toggle"],n["branch"];
    printf " expr=%d user=%d\n", n["expr"], n["user"]}' "$1"
}
# The summary on one line, without the two FSM rows the counter has none of.
summary() {
  verilator_coverage "$@" | grep -E 'line|toggle|branch|expr|user' \
    | sed -E 's/^ +//; s/ +: +/ /; s/\( */(/; s/\/ +/\//' | paste -sd' ' -
}
# The count of one cover property in a .dat, by the tail of its hierarchy.
user_count() {
  awk -F'\001' -v want="$2" '/^C /{split($NF,a,"\047 "); h=substr(a[1],3);
    if (h ~ want"$") print a[2]}' "$1"
}

# Three annotated lines: % marks a line with a point below the threshold,
# ~ a line where only some attached points reached it, a space all did.
taste() {
  grep -E 'rst_n,|else if \(en\)' "$1"/counter.sv
  grep -E 'cov_wrap' "$1"/tb_counter_cov.sv
}

for run in A B; do
  if [ $run = A ]; then n=10; else n=300; fi
  echo "--- run $run: +n=$n"
  ./build/Vtb_counter_cov +n=$n +verilator+coverage+file+build/run$run.dat \
    | grep count=
  records build/run$run.dat
  echo "summary: $(summary build/run$run.dat)"
done

echo "--- annotate run A at the default threshold (--annotate-min 10)"
rm -rf build/ann10 build/ann1
verilator_coverage --annotate build/ann10 --annotate-all build/runA.dat \
  | grep -E 'attached points' | sed -E 's/^ +//; s/ +/ /g'
taste build/ann10
echo "--- annotate run A with --annotate-min 1"
verilator_coverage --annotate build/ann1 --annotate-all --annotate-min 1 \
  build/runA.dat | grep -E 'attached points' | sed -E 's/^ +//; s/ +/ /g'
taste build/ann1

echo "--- merge: verilator_coverage --write merged.dat runA.dat runB.dat"
verilator_coverage --write build/merged.dat build/runA.dat build/runB.dat
echo "cov_counting: A=$(user_count build/runA.dat cov_counting)" \
     "B=$(user_count build/runB.dat cov_counting)" \
     "merged=$(user_count build/merged.dat cov_counting)"
echo "summary: $(summary build/merged.dat)"

echo "--- rank: verilator_coverage --rank runA.dat runB.dat"
verilator_coverage --rank build/runA.dat build/runB.dat | sed 's/build\///'

echo "--- lcov: verilator_coverage --write-info merged.info (first lines)"
verilator_coverage --write-info build/merged.info build/merged.dat
head -6 build/merged.info
echo "verdict: a merge adds counts; the annotation threshold decides" \
     "which lines count as covered"
