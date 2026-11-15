#!/bin/sh
# usage: ./run.sh script.tcl
# Runs one measurement script on InFormal with the engine list beside
# this file (it adds rIC3 to the in-house engines). BOOK is the root
# of the book's repository; the work directory is a fresh temporary
# one unless WORK is set. Output goes to stdout: the kept copies are
# in out/.
export PATH=/opt/dvtools/venv/bin:/opt/dvtools/bin:$PATH
M=$(cd "$(dirname "$0")" && pwd)
BOOK=${BOOK:-$(cd "$M/../.." && pwd)}
WORK=${WORK:-$(mktemp -d)}
export BOOK WORK
s=$1; shift
exec informal shell --engines "$M/engines.toml" \
    --workdir "$WORK/$(basename "$s" .tcl)" "$s" "$@" 2>&1
