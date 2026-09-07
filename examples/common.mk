# ======================================================================
#  examples/common.mk  --  the one entry point every example Makefile includes
# ======================================================================
#  Every example directory in this book has the same three targets:
#
#      make lint     compile / syntax-check only, no simulation
#      make run      build and simulate (or execute) the example
#      make clean    remove generated files
#      make help     print the variables this example was built with
#
#  An example Makefile only sets a handful of variables and then includes this
#  file.  The language-specific recipes live in examples/mk/<language>.mk so
#  that chapters can talk about verification, not build systems.
#
#  Required variables (set in the example's Makefile before the include):
#      EXAMPLE_LANG   sv | cocotb | systemc      which recipe file to load
#      TOP            top-level module name (HDL) or executable name (SystemC)
#      SOURCES        source files, relative to the example directory
#
#  Optional variables:
#      REQUIRES       commercial   -> CI runs `make lint` only;
#                                     `make run` needs a commercial tool
#      PLUSARGS       extra +args passed to the simulation (SV / UVM)
#      UVM            1 to compile the UVM library and pass +UVM_TESTNAME
#      UVM_TEST       name of the uvm_test to run (when UVM=1)
#      EXPECT         pass (default) or fail. A teaching example whose point
#                     is to find a bug sets EXPECT := fail; the checker then
#                     treats a non-zero `make run` as the correct outcome.
#      LINT_ONLY      1 for an example that has nothing to simulate, because
#                     the example *is* the static check (a lint or analysis
#                     demonstration, or RTL shown without a testbench).
#                     `make run` then runs the example's lint, so the checker
#                     records the lint verdict as the example's result
#                     instead of an empty simulation log.
#
#  Layout assumed by the paths below:
#      examples/common.mk            <- this file
#      examples/mk/sv.mk             <- SystemVerilog / UVM recipes
#      examples/mk/cocotb.mk         <- cocotb / pyuvm recipes
#      examples/mk/systemc.mk        <- SystemC / UVM-SystemC recipes
#      examples/<chapter>/<lang>/Makefile
# ======================================================================
# Directory that holds this file, regardless of where make was invoked from.
EXAMPLES_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Fail early with a readable message instead of a cryptic recipe error.
ifndef EXAMPLE_LANG
  $(error EXAMPLE_LANG is not set (expected sv, cocotb or systemc))
endif
ifndef TOP
  $(error TOP is not set (top-level module or executable name))
endif
ifndef SOURCES
  $(error SOURCES is not set (list of source files))
endif

# Defaults that every language may use.
REQUIRES ?=
EXPECT   ?= pass
LINT_ONLY ?= 0
PLUSARGS ?=
UVM      ?= 0
UVM_TEST ?=
BUILD_DIR ?= build

# The default target when someone just types `make`.
.DEFAULT_GOAL := run

# Load the recipes for this example's language.
include $(EXAMPLES_ROOT)mk/$(EXAMPLE_LANG).mk

# ----------------------------------------------------------------------
#  Shared targets.  `clean::` is a double-colon rule so that language files
#  (and cocotb's own Makefile.sim) can each add their own clean actions.
# ----------------------------------------------------------------------
.PHONY: help lint run clean
help:
	@echo "example language : $(EXAMPLE_LANG)"
	@echo "top              : $(TOP)"
	@echo "sources          : $(SOURCES)"
	@echo "requires         : $(if $(REQUIRES),$(REQUIRES),nothing special)"
	@echo "expected outcome : $(EXPECT)"
	@echo "targets          : lint | run | clean | help"

clean::
	rm -rf $(BUILD_DIR)
