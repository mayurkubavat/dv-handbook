# An equivalent mutant that a white-box assertion kills: m44, the
# counter's case labels exchanged. The miter proved by rIC3; the
# property set on m44, where only Sync_A fails; and the count beside the
# flags from a short simulation (tb_count.sv). Selects ric3-ic3, so it
# is skipped where rIC3 is not installed. About thirty seconds.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := whitebox.py
SOURCES       := whitebox.py
PYTHON        := python3 -I -B
LINT_CMD      := python3 -I -B -m py_compile whitebox.py && \
                 verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                 -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                 --top-module tb_count $(C09)/rtl/fifo_fixed.sv tb_count.sv && \
                 echo "lint: no warnings"
EXPECT_OUTPUT := verdict: m44 is equivalent at the ports and killed by Sync_A
include ../../common.mk
