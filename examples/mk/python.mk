# =============================================================================
#  examples/mk/python.mk  --  recipes for examples that are plain Python tools
# =============================================================================
#  Used by examples that are not simulations: plan reports, coverage
#  post-processing, generators. TOP is the script to run; SOURCES lists
#  every file that must compile. Extra arguments go in PLUSARGS.
#
#      make lint      byte-compile every source (catches syntax errors)
#      make run       python3 $(TOP) $(PLUSARGS)
# =============================================================================

PYTHON ?= python3

ifeq ($(strip $(LINT_CMD)),)
lint:
	$(PYTHON) -m py_compile $(SOURCES)
else
lint:
	$(LINT_CMD)
endif

run:
	$(PYTHON) $(TOP) $(PLUSARGS)

clean::
	rm -rf __pycache__
