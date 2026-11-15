# VC Formal-style FPV setup for the counter (runs unchanged under informal).
set_fml_appmode FPV
set_fml_var fml_max_time 60s
read_file -top counter -format sverilog -sva -vcs "[file join [file dirname [info script]] counter.sv]"
create_clock clk -period 100
create_reset rst_n -sense low
sim_run -stable
sim_save_reset

fvassert a_max    -expr {q <= 4'd9}
fvassert a_step   -expr {@(posedge clk) disable iff (!rst_n) en && !done |-> ##1 q == $past(q) + 4'd1}
fvassert a_never9 -expr {q != 4'd9}
fvcover  c_done   -expr {$rose(done)}
fvcover  c_10     -expr {q == 4'd10}

check_fv -block
report_fv -list
puts "FALSIFIED [get_props -type assert -status falsified]"
