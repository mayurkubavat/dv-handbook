#!/usr/bin/env bash
# run_both.sh -- run one design under both simulators and print both answers.
#
# The point of the example is the comparison, so the script runs each
# simulator in turn and labels the output rather than leaving the reader to
# run two commands and remember which was which. It ends with a verdict line
# saying whether the two agreed, which is what the chapter quotes.
set -uo pipefail
cd "$(dirname "$0")"
BUILD=build; mkdir -p $BUILD

run_one() {                 # $1 = racy|safe, $2 = the -D macro
  local name=$1 macro=$2
  iverilog -g2012 -D"$macro" -o $BUILD/$name.vvp $name.sv tb_race.sv
  vvp $BUILD/$name.vvp | grep -E '^(design|count)='  > $BUILD/$name.icarus
  verilator --binary --timing --timescale 1ns/1ps \
      -Wno-BLKSEQ -Wno-DECLFILENAME -D"$macro" \
      --top-module tb_race -Mdir $BUILD/v_$name $name.sv tb_race.sv >/dev/null
  ./$BUILD/v_$name/Vtb_race \
    | grep -E '^(design|count)=' > $BUILD/$name.static

  echo "=== $name"
  echo "--- event-driven simulator"
  sed 's/^/    /' $BUILD/$name.icarus
  echo "--- statically scheduled simulator"
  sed 's/^/    /' $BUILD/$name.static
  if diff -q $BUILD/$name.icarus $BUILD/$name.static >/dev/null; then
    echo "verdict: the two simulators agree on $name"
  else
    echo "verdict: the two simulators disagree on $name"
  fi
}

run_one racy DUT_RACY
echo
run_one safe DUT_SAFE
