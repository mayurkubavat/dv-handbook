# fifo.tcl -- the chapter's FIFO checker, bound to the first chapter's
# FIFO and handed to InFormal. The checker and the bind file are the
# ones the simulation used; nothing in them was changed for this run.
set here [file dirname [info script]]
analyze -sv12 $here/../../ch01-what-is-dv/rtl/fifo.sv \
    $here/../fifo-checker/fifo_sva.sv $here/../fifo-checker/fifo_bind.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}

# One engine and a time limit, so that two runs print the same report.
informal::set_engines informal-kind
set_prove_time_limit 60s
prove -all

puts "--- the counterexample to FullBackward_A, one row per cycle"
puts [exec python3 $here/../common/vcdtable.py [trace FullBackward_A] \
    rst_n wr_en rd_en count u_sva.occ full]

expect proven      NoOverflow_A FullForward_A EmptyExact_A PushFull_A \
                   PopEmpty_A Sync_A
expect cex         FullBackward_A
expect unreachable FullReached_C
expect covered     PushFull_C PopEmpty_C Drained_C
puts "verdict: one direction refuted, the other proved of a state\
 that cannot be reached"
finish
