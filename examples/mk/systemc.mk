# ======================================================================
#  examples/mk/systemc.mk  --  SystemC and UVM-SystemC recipes
# ======================================================================
#  SystemC examples are ordinary C++ programs linked against libsystemc.
#
#      SYSTEMC_HOME       install prefix containing include/systemc.h and lib/
#                         (defaults to the Homebrew prefix on macOS)
#      UVM_SYSTEMC_HOME   set this for UVM-SystemC examples; the recipe then
#                         adds the include path and links libuvm-systemc
#
#  Targets:  make lint (syntax-check only) | make run (build + execute)
# ======================================================================
CXX          ?= c++
CXXSTD       ?= -std=c++17
SYSTEMC_HOME ?= $(shell brew --prefix systemc 2>/dev/null \
                        || echo /usr/local/systemc)
UVM_SYSTEMC_HOME ?=

# Accellera's own installer puts libraries in lib-<arch>; Homebrew uses lib.
SYSTEMC_LIBDIR := $(firstword \
    $(wildcard $(SYSTEMC_HOME)/lib $(SYSTEMC_HOME)/lib-*))

CPPFLAGS += -I$(SYSTEMC_HOME)/include
LDFLAGS  += -L$(SYSTEMC_LIBDIR) -Wl,-rpath,$(SYSTEMC_LIBDIR)
LDLIBS   += -lsystemc -lm

ifneq ($(UVM_SYSTEMC_HOME),)
  UVM_SYSTEMC_LIBDIR := $(firstword \
      $(wildcard $(UVM_SYSTEMC_HOME)/lib $(UVM_SYSTEMC_HOME)/lib-*))
  CPPFLAGS += -I$(UVM_SYSTEMC_HOME)/include
  LDFLAGS  += -L$(UVM_SYSTEMC_LIBDIR) -Wl,-rpath,$(UVM_SYSTEMC_LIBDIR)
  LDLIBS   += -luvm-systemc
endif

EXE := $(BUILD_DIR)/$(TOP)

# A UVM-SystemC example cannot even be syntax-checked without the library.
ifeq ($(REQUIRES)$(UVM_SYSTEMC_HOME),uvm-systemc)
lint:
	@echo "skipped: UVM-SystemC example needs UVM_SYSTEMC_HOME"
else
lint:
	$(CXX) $(CXXSTD) $(CPPFLAGS) -fsyntax-only $(SOURCES)
endif

run: $(EXE)
	$(EXE) $(PLUSARGS)

$(EXE): $(SOURCES)
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXSTD) $(CPPFLAGS) $(SOURCES) -o $@ \
	    $(LDFLAGS) $(LDLIBS)
