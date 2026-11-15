# Chapter 9's checker exactly as the book ships it (clocked immediate assertions, bound)
clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch01-what-is-dv/rtl/fifo.sv /home/user/dv-handbook/examples/ch09-temporal-properties/fifo-checker/fifo_sva.sv /home/user/dv-handbook/examples/ch09-temporal-properties/fifo-checker/fifo_bind.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}
set_prove_time_limit 60s
puts "prove returned: [prove -all]"
