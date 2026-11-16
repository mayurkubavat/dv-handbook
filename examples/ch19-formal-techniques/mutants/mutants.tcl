# mutants.tcl -- the chapter's FIFO property set against three
# mutants of the repaired FIFO. The set: Chapter 9's checker, bound
# as it ships; the previous chapter's pointer property; and the
# tracked-word check of track-word/. Each mutant is one line of
# fifo_fixed.sv changed by sed when the script runs. A bounded search
# of two seconds for each property: a property with no
# counterexample in that time has not killed the mutant.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set fifo $rtl09/fifo_fixed.sv
set sva  [list $chk09/fifo_sva.sv $chk09/fifo_bind.sv]
set m(dup)  [mutant fifo_dup $fifo \
    {s/      if (do_read) begin/      if (do_read \&\& !do_write) begin/}]
set m(wrap) [mutant fifo_wrap $fifo \
    {s/2'b10:   count <= count + 1'b1;/2'b10:   count <= (count ==\
 (PTR_W+1)'(DEPTH-2)) ? '0 : count + 1'b1;/}]
set m(skip) [mutant fifo_skip $fifo \
    {s/rd_ptr <= rd_ptr + 1'b1;/rd_ptr <= rd_ptr + 2'd2;/}]
# What each mutant does, and the properties expected to kill it.
set what(dup)  "the read pointer stays put when a push and a pop meet"
set what(wrap) "the count wraps to 0 one push short of full"
set what(skip) "the read pointer steps by two"
set kill(dup)  {a_integrity EmptyPtrs_A}
set kill(wrap) {NoOverflow_A FullForward_A EmptyExact_A Sync_A
                EmptyPtrs_A}
set kill(skip) {a_integrity EmptyPtrs_A}
set summary {}

foreach k {dup wrap skip} {
  puts "=== mutant $k: $what($k)"
  design [list $m($k) {*}$sva $here/../track-word/track.sv] track
  cover -disable *_C
  assume -name m_sd {$stable(sd)}
  assert -name a_integrity {in_q && ahead == '0 |-> rd_data == sd}
  assert -name EmptyPtrs_A {empty |-> u.wr_ptr == u.rd_ptr}
  one informal-bmc 2s -all
  set alive 0
  foreach p [get_property_list -include {type assert}] {
    set short [lindex [split $p .] end]
    if {$short in $kill($k)} {
      expect cex $p
      lappend summary [format "  %-5s %-14s depth %d" $k $short \
          [depth $p]]
    } else {
      expect undetermined $p
      incr alive
    }
  }
  lappend summary [format "  %-5s %d other properties: no\
 counterexample in 2 s" $k $alive]
}
puts "=== summary: mutant, property that killed it, depth"
puts [join $summary "\n"]
puts "verdict: every mutant killed; Chapter 9's checker kills only the\
 one that breaks the count"
finish
