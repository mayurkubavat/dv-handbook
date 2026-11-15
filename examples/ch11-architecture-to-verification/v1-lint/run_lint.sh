#!/usr/bin/env bash
# run_lint.sh -- both versions through the book's lint flags. Version 1
# is expected to warn and version 2 to be clean; each warning is
# printed as rule, line and the variable it names.
set -uo pipefail
cd "$(dirname "$0")"
FLAGS="--lint-only -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL"
echo "--- version 1: verilator $FLAGS"
verilator $FLAGS --top-module dma_engine ../rtl/dma_v1.v 2>&1 \
  | grep -E '^%Warning' \
  | sed -E 's/^%Warning-([A-Z]+): [^:]*:([0-9]+):[0-9]+: /\1 line \2: /'
echo "--- version 2: verilator $FLAGS"
if verilator $FLAGS --top-module dma_v2 ../rtl/dma_regs_pkg.sv \
     ../rtl/dma_v2.sv >/dev/null 2>&1; then
  echo "no warnings"
else
  echo "warnings"; exit 1
fi
n=$(verilator $FLAGS --top-module dma_engine ../rtl/dma_v1.v 2>&1 \
    | grep -c '^%Warning-MULTIDRIVENPROC')
echo "verdict: version 1 has $n registers written by two always blocks;" \
     "version 2 has none"
