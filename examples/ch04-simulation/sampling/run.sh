#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
iverilog -g2012 -o build/sampling.vvp tb_sampling.sv
vvp build/sampling.vvp | grep -vE '^\s*$'
