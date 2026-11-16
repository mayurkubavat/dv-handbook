#!/usr/bin/env bash
# run.sh NAME -- run NAME/NAME.tcl through the book's InFormal wrapper
# (examples/mk/informal.sh: time column stripped, `expect`/`finish`
# available) and keep two files beside the script:
#   NAME/run.out     the report as an example's run.out would hold it
#   NAME/timed.out   the same run with the per-property seconds kept,
#                    followed by the wall-clock time of the whole run
# The work directory is build/NAME under this directory; delete
# build/ when done.
set -uo pipefail
export PATH=/opt/dvtools/venv/bin:/opt/dvtools/bin:$PATH
here="$(cd "$(dirname "$0")" && pwd)"
name="$1"
wrap="$here/../../examples/mk/informal.sh"
work="$here/build/$name"
rm -rf "$work"
start=$(date +%s.%N)
"$wrap" "$here/$name/$name.tcl" "$work" >"$here/$name/run.out"
rc=$?
end=$(date +%s.%N)
cp "$work/report.txt" "$here/$name/timed.out"
printf 'wall: %.1f s; exit status %d\n' "$(echo "$end - $start" | bc)" \
    "$rc" >>"$here/$name/timed.out"
tail -1 "$here/$name/timed.out"
