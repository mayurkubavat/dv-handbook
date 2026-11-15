clear -all
set d [file dirname [info script]]
analyze -sv12 $d/dut.sv
elaborate -top top
clock clk
reset -expression {rst}
assert -name t_tcl {u_cnt.q <= 4'd9}
set r [prove -all]
puts "prove returned: $r"
puts "status a: [get_status t_tcl]"
