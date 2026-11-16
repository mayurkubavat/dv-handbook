# common.tcl -- shared by the ch19 measurement scripts. Loads the
# previous chapter's procedures (`one`, `depth`, `expect_depth`,
# `full`) on top of the book's `expect` and `finish`.
set ::m19 [file dirname [info script]]
source $::m19/../../examples/ch18-formal-property-verification/common/proof.tcl
set ::rtl09 $::m19/../../examples/ch09-temporal-properties/rtl
set ::rtl11 $::m19/../../examples/ch11-architecture-to-verification/rtl

# design FILES TOP ARGS -- clear, read, elaborate, clock clk, reset
# on !rst_n. ARGS go to `elaborate` (parameters, -bbox_m).
proc design {files top args} {
  clear -all
  analyze -sv12 {*}$files
  elaborate -top $top {*}$args
  clock clk
  reset -expression {!rst_n}
}
