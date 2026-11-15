# seconds.tcl -- the runs that seconds.py times: one property, one
# engine, ten seconds. Each run prints a line "run|KEY|ENGINE" and
# then the tool's one-row table, whose last column is the time; the
# book's wrapper removes that column from the report it prints and
# keeps it in the file seconds.py reads.
set here [file dirname [info script]]
source $here/../common/proof.tcl
set limit 10s

proc counter {bug} {
  clear -all
  analyze -sv12 $::here/../bmc-depth/deep.sv
  elaborate -top deep -parameter BUG $bug
  clock clk
  reset -expression {rst}
}

proc fifo {depth helper} {
  clear -all
  analyze -sv12 $::ch09/rtl/fifo_fixed.sv
  elaborate -top fifo -parameter DEPTH $depth -parameter WIDTH 1
  clock clk
  reset -expression {!rst_n}
  assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
  if {$helper} {
    assume -name CountPtrs_M \
        {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
  }
}

proc run {key engine name} {
  puts "run|$key|$engine"
  one $engine $::limit -property [full $name]
}

foreach bug {16 64 256 1024} {
  counter $bug
  run bug$bug informal-bmc a_never
  if {$bug == 1024} {run bug$bug ric3-ic3 a_never}
}
foreach depth {2 4 8 16 64} {
  fifo $depth 0
  foreach engine {informal-kind informal-ic3 ric3-ic3} {
    if {$engine eq "informal-kind" && $depth > 4} continue
    run fifo$depth $engine EmptyPtrs_A
  }
}
fifo 64 1
foreach engine {informal-kind informal-ic3 ric3-ic3} {
  run help64 $engine EmptyPtrs_A
}
finish
