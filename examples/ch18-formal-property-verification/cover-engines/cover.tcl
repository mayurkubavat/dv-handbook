# cover.tcl -- a cover is a reachability question with two kinds of
# answer. "The FIFO can hold sixteen entries" is asked of the first
# chapter's FIFO, which cannot, and of the repaired one, which can,
# under each of three engines.
set here [file dirname [info script]]
source $here/../common/proof.tcl
set name fifo.u_sva.FullReached_C
set summary {}

# note DESIGN -- one line of the summary printed last, naming the
# engine and the limit of the last `one`.
proc note {design} {
  set d [depth $::name]
  lappend ::summary [format "  %-14s %-14s %-6s %s" $design $::one_engine \
      $::one_limit "[get_status $::name][expr {$d < 0 ? "" : ", depth $d"}]"]
}

# load RTL -- the FIFO with the temporal-properties chapter's checker.
proc load {rtl} {
  clear -all
  analyze -sv12 $rtl $::ch09/fifo-checker/fifo_sva.sv \
      $::ch09/fifo-checker/fifo_bind.sv
  elaborate -top fifo
  clock clk
  reset -expression {!rst_n}
}

puts "=== the first chapter's FIFO: full is raised at fifteen"
load $here/../../ch01-what-is-dv/rtl/fifo.sv
one informal-bmc 3s -property $name
expect undetermined $name
note "first chapter"
foreach engine {informal-kind informal-ic3} {
  one $engine 20s -property $name
  expect unreachable $name
  note "first chapter"
}

puts "=== the repaired FIFO"
load $ch09/rtl/fifo_fixed.sv
foreach engine {informal-bmc informal-kind informal-ic3} {
  one $engine 20s -property $name
  expect covered $name
  expect_depth 17 $name
  note repaired
}
puts "=== FullReached_C: the FIFO, the engine, its limit, the answer"
puts [join $summary "\n"]
puts "verdict: covered is a trace and every engine finds it;\
 unreachable is a proof and bounded search cannot give one"
finish
