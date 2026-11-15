# Data through the memory: Chapter 9 fixed FIFO
clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch09-temporal-properties/rtl/fifo_fixed.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}
set_prove_time_limit 30s
assert -name a_first_word {wr_en && empty |=> rd_data == $past(wr_data)}
assert -name a_mem0       {wr_en && !full && wr_ptr == 4'd0 |=> mem[0] == $past(wr_data)}
assert -name a_wrong      {wr_en && !empty && !full |=> rd_data == $past(wr_data)}
set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
