# bmc_depth.tcl -- a bug at increasing depth, every engine alone.
source [file dirname [info script]]/common.tcl
foreach bug {16 64 256 1024 4096} {
  clear -all
  analyze -sv12 $here/deep.sv
  elaborate -top deep -parameter BUG $bug
  clock clk
  reset -expression {rst}
  assert -name a_never "cnt != 16'd$bug"
  puts "=== BUG=$bug"
  each_engine [concat $hunters $provers] 20s -all
}
