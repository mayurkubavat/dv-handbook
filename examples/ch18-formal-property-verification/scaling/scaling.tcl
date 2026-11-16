# scaling.tcl -- two true properties of the repaired FIFO at four
# sizes under three engines, and the first of them again with the
# second assumed. The in-house engines get five seconds a property;
# the external one gets twenty, and is expected to need none of it.
set here [file dirname [info script]]
source $here/../common/proof.tcl
set engines {informal-kind informal-ic3 ric3-ic3}
array set limit {informal-kind 5s informal-ic3 5s ric3-ic3 20s}
# The helper, typed once: asserted, then assumed.
set helper {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}

# The verdicts expected, by size: one letter for each engine in the
# order above, P for proven and - for no verdict within the limit.
array set want_empty {2 PPP 4 -PP 8 -PP 64 --P}
array set want_count {2 PPP 4 PPP 8 PPP 64 P-P}
set word(P) proven
set word(-) undetermined

foreach depth {2 4 8 64} {
  clear -all
  analyze -sv12 $ch09/rtl/fifo_fixed.sv
  elaborate -top fifo -parameter DEPTH $depth -parameter WIDTH 1
  clock clk
  reset -expression {!rst_n}
  assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
  assert -name CountPtrs_A $helper
  puts "=== $depth entries"
  set i 0
  foreach engine $engines {
    one $engine $limit($engine) -all
    foreach {name want} [list EmptyPtrs_A $want_empty($depth) \
                              CountPtrs_A $want_count($depth)] {
      expect $word([string index $want $i]) $name
      set grid($name,$engine,$depth) [get_status $name]
    }
    incr i
  }
  puts "=== $depth entries, CountPtrs_A assumed"
  assert -disable CountPtrs_A
  assume -name CountPtrs_M $helper
  foreach engine $engines {
    one $engine $limit($engine) -all
    expect proven EmptyPtrs_A
    set grid(helped,$engine,$depth) [get_status EmptyPtrs_A]
  }
}

puts "=== verdicts by number of entries"
puts "limits: informal-kind 5 s, informal-ic3 5 s, ric3-ic3 20 s;\
 `-` is no verdict within it"
puts [format "%-28s %-13s %7s %7s %7s %7s" property engine 2 4 8 64]
foreach {key label} {EmptyPtrs_A EmptyPtrs_A CountPtrs_A CountPtrs_A
                     helped "EmptyPtrs_A, helper assumed"} {
  foreach engine $engines {
    set row [format "%-28s %-13s" $label $engine]
    foreach depth {2 4 8 64} {
      set v $grid($key,$engine,$depth)
      append row [format " %7s" [expr {$v eq "undetermined" ? "-" : $v}]]
    }
    puts $row
  }
}
puts "verdict: with the helper assumed, every engine proves the\
 property at every size"
finish
