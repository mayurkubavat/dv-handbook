#!/bin/sh
# usage: ./run.sh dir/script.tcl [extra informal shell args]
# Runs InFormal from this directory so every script sees the same engines.toml.
export PATH=/opt/dvtools/bin:$PATH
M=$(cd "$(dirname "$0")" && pwd)
s=$1; shift
exec informal shell --engines "$M/config/engines.toml" --workdir "$M/build/$(basename "$s" .tcl)" "$s" "$@"
