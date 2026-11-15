# The table of property forms the formal tool accepts, generated: one
# probe a form, each as a property that holds and one that does not,
# written as tbl-sva.md (kept under version control like a run.out,
# so `make clean` leaves it). Needs informal. About five seconds.
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := forms.py
SOURCES       := forms.py ../common/tables.py
LINT_CMD      := verilator --lint-only -Wall -Wno-DECLFILENAME \
                     -Wno-UNUSEDSIGNAL -Wno-MULTITOP -Wno-UNUSEDPARAM \
                     --top-module probe probe.sv \
                 && verilator --lint-only -Wall -Wno-DECLFILENAME \
                     -Wno-UNUSEDSIGNAL -Wno-MULTITOP \
                     --top-module in_module_t where.sv \
                 && python3 -m py_compile $(SOURCES) \
                 && echo "lint: no warnings"
EXPECT_OUTPUT := wrote tbl-sva.md
include ../../common.mk
