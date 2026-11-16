# Closing the gap: the temporal-properties chapter's traffic and checker,
# read by path and unchanged, plus a data check (fifo_data_sva.sv and its
# bind). Control on the repaired and the original FIFO; the 44 source
# mutants at default and randomized initial values; the 1,000-mutation
# netlist sample; the kills at the ports, with the white-box Sync_A made
# vacuous by fifo_port_bind.sv; the before-and-after table
# tbl-ch25-report.md. Yosys and Verilator; about a minute.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := fifth.py
SOURCES       := fifth.py
PYTHON        := python3 -I -B
LINT_CMD      := python3 -I -B -m py_compile fifth.py && \
                 verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                 -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                 -Wno-SYNCASYNCNET --top-module tb_fifo_sva \
                 $(C09)/rtl/fifo_fixed.sv \
                 $(C09)/fifo-checker/fifo_sva.sv \
                 $(C09)/fifo-checker/fifo_bind.sv fifo_data_sva.sv \
                 fifo_data_bind.sv $(C09)/fifo-checker/tb_fifo_sva.sv && \
                 verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                 -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                 -Wno-SYNCASYNCNET --top-module tb_fifo_sva \
                 $(C09)/rtl/fifo_fixed.sv \
                 $(C09)/fifo-checker/fifo_sva.sv \
                 fifo_port_bind.sv fifo_data_sva.sv \
                 fifo_data_bind.sv $(C09)/fifo-checker/tb_fifo_sva.sv && \
                 echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the data check raises the source kills from 22 to 37
include ../../common.mk
