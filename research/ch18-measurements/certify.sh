#!/bin/sh
# certify.sh -- what can be seen of certificate checking, counter-
# example replay and the depth an engine reached. Uses two switches
# the tool's engine document lists as experimental (INFORMAL_IC3_STATS,
# INFORMAL_IC3_TRACE) and the engine child of --isolate.
export PATH=/opt/dvtools/venv/bin:/opt/dvtools/bin:$PATH
M=$(cd "$(dirname "$0")" && pwd)
BOOK=${BOOK:-$(cd "$M/../.." && pwd)}; export BOOK
W=$(mktemp -d); export WORK=$W
cd "$M"
for d in 2 4; do
  echo "=== DEPTH=$d: the shell's model of EmptyPtrs_A"
  DEPTH=$d INFORMAL_IC3_STATS=1 INFORMAL_IC3_TRACE=$W/trace$d.jsonl \
    informal shell --engines engines.toml --workdir $W/p$d ptr_one.tcl 2>&1 |
    sed -E "s#$W#WORK#g; s/in [0-9.]+ s/in T s/; s/ [0-9.]+ s\$/ T s/"
  echo "trace events: $(wc -l < $W/trace$d.jsonl)"
  cut -c1-12 $W/trace$d.jsonl | sort | uniq -c | sort -rn | head -6
  for e in informal-kind informal-bmc; do
    for run in 1 2 3; do
      informal engine $e $W/p$d/prop_0.btor2 --timeout-ms 3000 2>&1 |
        tail -2 | tr '\n' ' '; echo " <- $e run $run"
    done
  done
done
echo "=== files the shell leaves for a refuted property"
informal shell --engines engines.toml --workdir $W/cex cex_one.tcl 2>&1 |
  sed -E 's/in [0-9.]+ s/in T s/'
ls $W/cex
head -c 600 $W/cex/prop_0.trace.btor2; echo
