clear -all
set d [file dirname [info script]]
analyze -sv12 $d/dut.sv
elaborate -top cnt -parameter LIM 5
clock clk
reset -expression {rst}
assert -name t_five {q <= 4'd5}
cover -name c_six {q == 4'd6}
prove -all
