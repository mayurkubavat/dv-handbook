# Asynchronous reset re-asserted in mid-run (no reset command, so rst_n is a free input)
clear -all
analyze -sv12 [file dirname [info script]]/rst.sv
elaborate -top rst
clock clk
set_prove_time_limit 10s
informal::set_engines informal-kind
assert -name a_async_midrun {$past(rst_n) && !rst_n |-> a == 4'd0}
assert -name a_sync_view    {$past(!rst_n) |-> a == 4'd0}
prove -all
