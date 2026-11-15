clear -all
set d [file dirname [info script]]
analyze -sv12 +define+WITH_ACTION $d/dut.sv
elaborate -top top
clock clk
reset -expression {rst}
prove -all
