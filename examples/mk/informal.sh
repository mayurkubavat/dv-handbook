#!/usr/bin/env bash
# informal.sh -- run one InFormal script the way the book's examples
# do, and print a report that is the same on every run.
#
#   informal.sh SCRIPT.tcl [WORKDIR]
#
# The engine list is the file beside this one, so the script runs from
# any directory. The wall-clock time at the end of each report row is
# removed: it is the one column that differs between two runs once a
# script selects a single engine for each `prove`. The exit status is
# the script's own.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
script="$1"
work="${2:-build/informal}"
if ! command -v informal >/dev/null 2>&1; then
  echo "skipped: informal is not on the PATH"
  exit 0
fi
mkdir -p "$work"
informal shell --engines "$here/informal-engines.toml" \
    --workdir "$work" -c "set ::workdir $work" \
    -c "source $here/informal.tcl" "$script" \
    >"$work/report.txt" 2>&1
rc=$?
sed -E 's/ in [0-9]+\.[0-9]+ s$//; s/ +[0-9]+\.[0-9]+ s$//; s/ +$//' \
    "$work/report.txt"
exit $rc
