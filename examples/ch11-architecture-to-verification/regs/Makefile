# The register description and its generator. `make run` checks that the
# generated package and table match the YAML; `python3 gen_regs.py`
# rewrites them after an edit.
EXAMPLE_LANG  := python
TOP           := gen_regs.py
SOURCES       := gen_regs.py
PLUSARGS      := --check
EXPECT_OUTPUT := generated files match dma_regs.yaml
include ../../common.mk
