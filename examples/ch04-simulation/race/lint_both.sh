#!/usr/bin/env bash
# lint_both.sh -- lint each design and report what lint had to say.
#
# The race-free design passes the strictest lint in silence. The racing one
# earns BLKSEQ, "blocking assignment in sequential logic", which is off by
# default and is the one warning that would have caught this bug.
#
# Note the capture-then-search: with `pipefail` set, piping the linter
# straight into grep would report the linter's own non-zero exit rather than
# whether the warning was found, and a warning is a non-zero exit here.
set -uo pipefail
cd "$(dirname "$0")"
FLAGS="--lint-only -Wall --timing --timescale 1ns/1ps -Wno-DECLFILENAME"

verilator $FLAGS -DDUT_SAFE --top-module tb_race safe.sv tb_race.sv \
  && echo "safe: no warnings under -Wall"

racy_out=$(verilator $FLAGS -Wwarn-BLKSEQ -DDUT_RACY --top-module tb_race \
             racy.sv tb_race.sv 2>&1)
if grep -q BLKSEQ <<<"$racy_out"; then
  echo "racy: BLKSEQ, blocking assignment in sequential logic"
else
  echo "racy: lint said nothing, which this example does not expect"
  exit 1
fi
