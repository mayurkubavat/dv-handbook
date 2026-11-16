# Memory abstraction on a 256-word RAM with forwarding: induction
# without a verdict on the whole design, a proof with the storage
# black-boxed under a contract at one symbolic address, the spurious
# trace without the contract, the contract proved on the storage with
# a helper, and a forwarding bug found boxed and whole. In-house
# engines only. About thirty-five seconds, ten of them two limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := mem.tcl
SOURCES       := mem.tcl ../common/ch19.tcl mem_abs.sv
LINT_TOP      := mem_top
EXPECT_OUTPUT := verdict: 256 words proven through one slot
include ../../common.mk
