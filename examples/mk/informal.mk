# ======================================================================
#  examples/mk/informal.mk  --  recipes for formal examples on InFormal
# ======================================================================
#  TOP is the Tcl script `informal shell` runs. SOURCES lists the
#  script and the SystemVerilog files it reads; the .sv files among
#  them are what `make lint` hands to Verilator, with LINT_TOP as the
#  top module.
#
#      make lint      verilator --lint-only on the .sv files of SOURCES
#      make run       examples/mk/informal.sh $(TOP)
#
#  InFormal is an optional tool. An example sets REQUIRES := informal,
#  and when the program is not on the PATH `make run` prints one line
#  beginning "skipped" and succeeds, so a machine without it records a
#  skip and not a failure.
#
#  The script chooses the verdicts it expects and its own exit status
#  (see informal.tcl): the tool itself exits with status 0 whatever it
#  found.
# ======================================================================
INFORMAL_RUN  := $(EXAMPLES_ROOT)mk/informal.sh
LINT_TOP      ?=
LINT_FLAGS    ?= -Wall --timing --timescale 1ns/1ps -Wno-DECLFILENAME \
                 -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT

ifeq ($(strip $(LINT_CMD)),)
lint:
	verilator --lint-only $(LINT_FLAGS) --top-module $(LINT_TOP) \
	    $(filter %.sv,$(SOURCES))
	@echo "lint: no warnings"
else
lint:
	$(LINT_CMD)
endif

run:
	@$(INFORMAL_RUN) $(TOP) $(BUILD_DIR)/informal
