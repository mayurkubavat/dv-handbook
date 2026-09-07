# ======================================================================
#  examples/mk/sv.mk  --  SystemVerilog and UVM recipes
# ======================================================================
#  Select the simulator with SIM on the command line or in the environment:
#
#      make run SIM=verilator      (default; free; used for this book)
#      make run SIM=questa         (Siemens Questa / ModelSim: vlog + vsim)
#      make run SIM=vcs            (Synopsys VCS: vcs + simv)
#      make run SIM=xcelium        (Cadence Xcelium: xrun)
#
#  UVM examples set UVM=1 in their Makefile.  The UVM library is located via
#  UVM_HOME (the directory that contains src/uvm_pkg.sv).  Questa, VCS and
#  Xcelium all ship a precompiled UVM; the recipes below use the simulator's
#  bundled copy when UVM_HOME is not set, and the source copy when it is.
# ======================================================================
SIM       ?= verilator
TIMESCALE ?= 1ns/1ps
UVM_HOME  ?=

# ---- UVM compile arguments, shared by every simulator ------------
ifeq ($(UVM),1)
  UVM_DEFINES := +define+UVM_NO_DPI
  ifneq ($(UVM_HOME),)
    UVM_INCDIR  := +incdir+$(UVM_HOME)/src
    UVM_SOURCE  := $(UVM_HOME)/src/uvm_pkg.sv
  endif
  UVM_RUNARGS := +UVM_TESTNAME=$(UVM_TEST) +UVM_VERBOSITY=UVM_MEDIUM
endif

# ======================================================================
#  Verilator
# ======================================================================
ifeq ($(SIM),verilator)

VERILATOR      ?= verilator
VERILATOR_BIN  := $(BUILD_DIR)/V$(TOP)
# --timing lets Verilator run testbench code with # delays and event control.
# The -Wno-* switches keep UVM's own source from failing lint; drop them for
# plain SystemVerilog examples if you want the strictest checking.
VERILATOR_FLAGS ?= --timing --timescale $(TIMESCALE) -Wall \
                   -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL
ifeq ($(UVM),1)
  VERILATOR_FLAGS += -Wno-lint -Wno-style -Wno-fatal --error-limit 0
endif

lint:
ifeq ($(UVM)$(UVM_HOME),1)
	@echo "skipped: UVM example needs UVM_HOME to lint with Verilator"
else
	$(VERILATOR) --lint-only $(VERILATOR_FLAGS) \
	    $(UVM_DEFINES) $(UVM_INCDIR) $(UVM_SOURCE) $(SOURCES) \
	    --top-module $(TOP)
	@echo "verilator --lint-only -Wall: no warnings"
endif

# An example that is only a static check has no binary to build or run.
ifeq ($(LINT_ONLY),1)
run: lint
else
# A failing test ends with $fatal, which Verilator turns into an abort
# signal; the `|| exit 1` turns that into an ordinary non-zero exit.
run: $(VERILATOR_BIN)
	$(VERILATOR_BIN) $(UVM_RUNARGS) $(PLUSARGS) || exit 1
endif

$(VERILATOR_BIN): $(SOURCES) $(UVM_SOURCE)
	$(VERILATOR) --binary $(VERILATOR_FLAGS) \
	    $(UVM_DEFINES) $(UVM_INCDIR) --Mdir $(BUILD_DIR) \
	    --top-module $(TOP) $(UVM_SOURCE) $(SOURCES)

endif

# ======================================================================
#  Questa / ModelSim
# ======================================================================
ifeq ($(SIM),questa)

VLOG_FLAGS ?= -sv -timescale $(TIMESCALE) -work $(BUILD_DIR)/work
VSIM_FLAGS ?= -c -work $(BUILD_DIR)/work -voptargs=+acc
ifeq ($(UVM)$(UVM_HOME),1)
  # No UVM_HOME: use the UVM library that ships with Questa.
  VSIM_FLAGS += -L mtiUvm
endif

lint: $(BUILD_DIR)/work
	vlog $(VLOG_FLAGS) -lint $(UVM_DEFINES) $(UVM_INCDIR) \
	    $(UVM_SOURCE) $(SOURCES)

run: $(BUILD_DIR)/work
	vlog $(VLOG_FLAGS) $(UVM_DEFINES) $(UVM_INCDIR) \
	    $(UVM_SOURCE) $(SOURCES)
	vsim $(VSIM_FLAGS) $(TOP) $(UVM_RUNARGS) $(PLUSARGS) \
	    -do "run -all; quit -f"

$(BUILD_DIR)/work:
	vlib $(BUILD_DIR)/work

endif

# ======================================================================
#  Synopsys VCS
# ======================================================================
ifeq ($(SIM),vcs)

VCS_FLAGS ?= -full64 -sverilog -timescale=$(TIMESCALE) \
             -Mdir=$(BUILD_DIR)/csrc -o $(BUILD_DIR)/simv \
             -debug_access+all
ifeq ($(UVM)$(UVM_HOME),1)
  # No UVM_HOME: use the UVM library that ships with VCS.
  VCS_FLAGS += -ntb_opts uvm-1.2
endif

lint:
	vlogan -full64 -sverilog -timescale=$(TIMESCALE) \
	    $(UVM_DEFINES) $(UVM_INCDIR) $(UVM_SOURCE) $(SOURCES)

run:
	mkdir -p $(BUILD_DIR)
	vcs $(VCS_FLAGS) $(UVM_DEFINES) $(UVM_INCDIR) \
	    $(UVM_SOURCE) $(SOURCES) -top $(TOP)
	$(BUILD_DIR)/simv $(UVM_RUNARGS) $(PLUSARGS)

endif

# ======================================================================
#  Cadence Xcelium
# ======================================================================
ifeq ($(SIM),xcelium)

XRUN_FLAGS ?= -64bit -sv -timescale $(TIMESCALE) \
              -xmlibdirname $(BUILD_DIR)/xcelium.d \
              -access +rwc -top $(TOP)
ifeq ($(UVM)$(UVM_HOME),1)
  # No UVM_HOME: use the UVM library that ships with Xcelium.
  XRUN_FLAGS += -uvm
endif

lint:
	xrun $(XRUN_FLAGS) -compile $(UVM_DEFINES) $(UVM_INCDIR) \
	    $(UVM_SOURCE) $(SOURCES)

run:
	xrun $(XRUN_FLAGS) $(UVM_DEFINES) $(UVM_INCDIR) $(UVM_SOURCE) $(SOURCES) \
	    $(UVM_RUNARGS) $(PLUSARGS)

endif

# ---- extra clean-up the simulators leave behind --------------------
clean::
	rm -rf obj_dir csrc simv* ucli.key xcelium.d xrun.* \
	       transcript vsim.wlf work *.log
