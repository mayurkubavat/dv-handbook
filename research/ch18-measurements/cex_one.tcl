# cex_one.tcl -- one refuted property: used by certify.sh.
source [file dirname [info script]]/common.tcl
analyze -sv12 $here/deep.sv
elaborate -top deep -parameter BUG 3
clock clk
reset -expression {rst}
assert -name a_never {cnt != 16'd3}
informal::set_engines informal-bmc
prove -all
