clear -all
set d [file dirname [info script]]
analyze -sv12 $d/dut.sv $d/bind.sv
elaborate -top top
clock clk
reset -expression {rst}
prove -all
