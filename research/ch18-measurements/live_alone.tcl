# live_alone.tcl -- one liveness property in the session, so that no
# other property's monitor changes the lasso; prints the first lines
# of the trace file, where the tool names the loop.
source [file dirname [info script]]/common.tcl
clear -all
analyze -sv12 $here/live_small.sv
elaborate -top live_small
clock clk
reset -expression {rst}
set_prove_time_limit 30s
informal::set_engines informal-bmc
assert -name a_live {req && n == 2'd0 |-> s_eventually gnt}
prove -all
set vcd [file join $::env(WORK) live_alone a_live.vcd]
set f [open $vcd]; set n 0
while {[gets $f line] >= 0 && $n < 4} {puts "vcd: $line"; incr n}
close $f
puts [exec python3 $ch09/common/vcdtable.py $vcd rst req stall n gnt]
