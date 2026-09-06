# ======================================================================
#  examples/mk/cocotb.mk  --  cocotb and pyuvm recipes
# ======================================================================
#  cocotb ships its own build system (Makefile.sim).  This file translates the
#  book's variables into cocotb's, then includes Makefile.sim so that every
#  simulator cocotb supports works unchanged:
#
#      make run                       (default SIM=icarus)
#      make run SIM=verilator
#      make run SIM=questa | vcs | xcelium
#
#  The Python test module lives next to the Makefile.  pyuvm examples are
#  ordinary cocotb tests whose test module instantiates a uvm_test, so they
#  need nothing extra here beyond `pip install pyuvm`.
# ======================================================================
SIM            ?= icarus
TOPLEVEL_LANG  ?= verilog
TEST_MODULE    ?= test_$(TOP)

# cocotb 2.x names (the 1.x names TOPLEVEL / MODULE still work but warn).
COCOTB_TOPLEVEL     := $(TOP)
COCOTB_TEST_MODULES := $(TEST_MODULE)
VERILOG_SOURCES     := $(abspath $(SOURCES))
SIM_BUILD           := $(BUILD_DIR)

# Icarus needs generate-block and SystemVerilog support switched on.
ifeq ($(SIM),icarus)
  COMPILE_ARGS += -g2012
endif
# Verilator: keep the same lint waivers the SV examples use.
ifeq ($(SIM),verilator)
  EXTRA_ARGS += --timing -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL
endif

# Make the test module importable no matter where make was invoked from.
export PYTHONPATH := $(CURDIR):$(PYTHONPATH)

# Where cocotb's makefiles live (from the active Python environment).
COCOTB_MAKEFILES := $(shell cocotb-config --makefiles 2>/dev/null)
ifeq ($(COCOTB_MAKEFILES),)
  $(error cocotb-config not found: activate the Python env that has cocotb)
endif

# The book's targets, expressed in cocotb's terms.
.PHONY: lint run
lint:
	verilator --lint-only -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
	    $(VERILOG_SOURCES) --top-module $(TOP)

run: sim

include $(COCOTB_MAKEFILES)/Makefile.sim

clean::
	rm -rf __pycache__ results.xml
