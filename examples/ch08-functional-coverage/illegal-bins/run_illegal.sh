#!/usr/bin/env bash
# run_illegal.sh -- builds both testbenches and runs each twice, with
# sampling on and off (+cov=0); prints the lines that stopped or failed
# each run and its exit code. The coverage gate is a plusarg because
# stop() is parsed and dropped on Verilator 5.052: an illegal bin still
# fires after g.stop() (measured; the chapter's support matrix). On this
# simulator $error stops the run, so the check's failure is its message
# and a non-zero exit, like the illegal bin's.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
FLAGS="--binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME
       -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT"
for t in tb_illegal tb_ignore_assert; do
  verilator $FLAGS --top-module $t -Mdir build/$t lint.vlt $t.sv \
      >/dev/null || exit 1
done

run() {  # run <top> [plusargs]: the lines that matter, then the exit code
  echo "--- $*"
  ./build/$1/V$1 "${@:2}" > build/$1.log 2>&1
  rc=$?
  grep -E "^drove|Illegal bin|check failed|^end of test" build/$1.log \
    | sed -E 's/^\[[0-9]+\] /    /' \
    | while IFS= read -r l; do           # wrap the simulator's message
        printf '%s\n' "$l" | fold -sw 74 | sed -E '2,$ s/^/      /; s/ +$//'
      done
  echo "exit code: $rc"
  return $rc
}
check() {  # check <exit> <pattern> <top> [plusargs]: run, count a match
  local want=$1 pat=$2; shift 2
  run "$@"
  if [[ $? -eq $want ]] && grep -q "$pat" "build/$1.log"; then ((ok++)); fi
}
ok=0
check 1 "Illegal bin"  tb_illegal
check 0 "end of test"  tb_illegal +cov=0
check 1 "check failed" tb_ignore_assert
check 1 "check failed" tb_ignore_assert +cov=0
if [[ $ok -eq 4 ]]; then
  echo "verdict: the illegal bin needs sampling; the assertion does not"
else
  echo "verdict: unexpected behaviour ($ok of 4 runs as described)"; exit 1
fi
