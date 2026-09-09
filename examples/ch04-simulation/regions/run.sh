#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
iverilog -g2012 -o build/regions.vvp tb_regions.sv
vvp build/regions.vvp | grep -vE '^\s*$'
