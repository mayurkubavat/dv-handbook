# Chapter 1 FIFO; model and concurrent properties in a bound module
clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch01-what-is-dv/rtl/fifo.sv [file dirname [info script]]/fifo_props.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}
set_prove_time_limit 60s
prove -all
