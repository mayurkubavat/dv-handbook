#!/usr/bin/env bash
# run_waves.sh -- the two waveforms of the timing section, measured: version
# 1's directed test (APB programming, then the first word's read and
# write), and version 2 meeting a read error on word 2 of 4. Each VCD
# is cut to a window and written as WaveJSON for the figure generator.
set -euo pipefail
cd "$(dirname "$0")"
. ../tb/common.sh
mkdir -p build/v1 build/v2
verilator $VFLAGS --trace --top-module tb_v1 -Mdir build/v1 $V1_SRC >/dev/null
verilator $VFLAGS --trace --top-module tb_v2 -Mdir build/v2 $V2_SRC >/dev/null
./build/v1/Vtb_v1 +test=directed +vcd=build/v1/v1.vcd | grep result
./build/v2/Vtb_v2 +test=abort +vcd=build/v2/v2.vcd | grep -E '^  |result'
D=tb_v1.dut
python3 vcd2wave.py build/v1/v1.vcd v1_word.json tb_v1.clk \
  first:$D.PSEL first:$D.PSEL+24 $D.PSEL $D.PENABLE $D.PADDR \
  $D.ARVALID $D.ARREADY $D.RVALID $D.RREADY $D.AWVALID $D.AWREADY \
  $D.WVALID $D.WREADY $D.BVALID $D.BREADY $D.state
D=tb_v2.dut
python3 vcd2wave.py build/v2/v2.vcd v2_abort.json tb_v2.clk \
  first:$D.ARVALID-1 first:$D.ARVALID+16 $D.ARVALID $D.ARREADY $D.ARADDR \
  $D.RVALID $D.RRESP $D.f_cnt $D.AWVALID $D.AWADDR $D.BVALID $D.abort \
  $D.busy $D.err
