# The two measured waveforms, written as WaveJSON for the two waveform figures.
EXAMPLE_LANG  := python
TOP           := run_waves.sh
SOURCES       := run_waves.sh
PYTHON        := bash
LINT_CMD      := bash -n run_waves.sh \&\& python3 -m py_compile vcd2wave.py
EXPECT_OUTPUT := -> v2_abort.json
include ../../common.mk
