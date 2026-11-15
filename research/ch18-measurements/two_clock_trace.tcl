source [file dirname [info script]]/common.tcl
set r $book/examples/ch03-digital-design/rtl
analyze -sv12 $r/top.sv $r/datapath.sv $r/sync2.sv $r/regblock.sv
elaborate -top top
clock bclk
clock cclk -factor 3
reset -expression {!brst_n && !crst_n}
assert -name a_never3  {count != 8'd3}
informal::set_engines informal-bmc
set_prove_time_limit 10s
prove -all
puts [exec python3 $ch09/common/vcdtable.py [file join $::env(WORK) two_clock_trace a_never3.vcd] bclk cclk brst_n crst_n count]
