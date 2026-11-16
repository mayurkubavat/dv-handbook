# pipe.tcl -- the worked example: two control properties of a pipe of
# two 256-entry FIFOs (common/hier.sv), proved by induction through
# black boxes, the children's contracts and one parent helper.
# P1: the pipe is empty when its count G is 0; P2: when it is full, G
# is at least 256. Eight steps, then the record.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set fifo  $rtl09/fifo_fixed.sv
set hier  $here/../common/hier.sv
set d 256
set wrap [mutant fifo_wrap $fifo \
    {s/2'b10:   count <= count + 1'b1;/2'b10:   count <= (count ==\
 (PTR_W+1)'(DEPTH-2)) ? '0 : count + 1'b1;/}]
# Every property and assumption, typed once.
set P1 {G == '0 |-> empty}
set P2 "full |-> G >= $d"
set CE {empty == (g == '0)}
set CF "full == (g == $d)"
set H  {g == u.count}
set HP "G == 10'(u0.g) + 10'(u1.g) && u0.g <= $d && u1.g <= $d"
set summary {}

# note STEP NAME ... -- a line of the record for each property, with
# the engine and limit of the last `one`.
proc note {step args} {
  foreach name $args {
    set dp [depth $name]
    lappend ::summary [format "  %-2s %-13s %-4s %-9s %s" $step \
        $::one_engine $::one_limit $name \
        "[get_status $name][expr {$dp < 0 ? "" : ", depth $dp"}]"]
  }
}
# child FILE -- a new session on one FIFO and its ghost count.
proc child {file} {
  design [list $file $::hier] fifo_ctr -parameter DEPTH $::d
}
# parent -- a new session on the pipe, both FIFOs boxed, each
# child's contract assumed.
proc parent {} {
  design [list $::fifo $::hier] pipe2 -parameter DEPTH $::d \
      -bbox_m {fifo}
  foreach u {u0 u1} {
    assume -name ${u}_CE "$u.empty == ($u.g == '0)"
    assume -name ${u}_CF "$u.full == ($u.g == $::d)"
  }
}
# covers DEEP -- the shallow witnesses of P1 (the pipe drains after
# holding a word) and of the helper's terms (a word in each child),
# and with DEEP = 1 the second child full, 258 cycles from reset.
proc covers {deep} {
  cover -name Drain_C  {G == 10'd1 ##1 G == '0}
  cover -name Both1_C  {u0.g == 9'd1 && u1.g == 9'd1}
  if {$deep} {cover -name U1Full_C {u1.full}}
}

puts "=== step 1: witness covers, on the boxed pipe"
# P2's antecedent, the pipe full, is 513 cycles from reset and takes
# most of a minute; it is run once, under the final assumptions.
parent
covers 1
one informal-bmc 30s -all
expect covered      Drain_C Both1_C U1Full_C
expect_depth 258    U1Full_C
note 1 Drain_C Both1_C U1Full_C

puts "=== step 2: the child's contract, with its ghost helper"
child $fifo
assert -name H_A $H
one informal-kind 5s -all
expect proven H_A
note 2 H_A
child $fifo
assume -name H_M $H
assert -name CE_A $CE
assert -name CF_A $CF
one informal-kind 5s -all
expect proven CE_A CF_A
note 2 CE_A CF_A

puts "=== steps 3 and 4: both children boxed, induction on the parent"
parent
assert -name P1_A $P1
assert -name P2_A $P2
one informal-kind 5s -all
expect undetermined P1_A P2_A
note 4 P1_A P2_A

puts "=== step 5: the parent helper"
parent
assert -name HP_A $HP
one informal-kind 5s -all
expect proven HP_A
note 5 HP_A

puts "=== step 6: P1 and P2 with the parent helper assumed"
parent
assume -name HP_M $HP
assert -name P1_A $P1
assert -name P2_A $P2
covers 0
one informal-kind 5s -all
expect proven  P1_A P2_A
expect covered Drain_C Both1_C
note 6 P1_A P2_A Drain_C Both1_C
puts "--- P2's own antecedent, the pipe full, by bounded search"
parent
assume -name HP_M $HP
cover  -name Full_C {full}
one informal-bmc 120s -all
expect covered   Full_C
expect_depth 513 Full_C
note 6 Full_C

puts "=== step 7: the mutant child (count wraps one push short of full)"
child $wrap
assert -name H_A $H
one informal-bmc 20s -all
expect cex       H_A
expect_depth 256 H_A
note 7 H_A

puts "=== step 8: the record: step, engine, limit, property, answer"
puts [join $summary "\n"]
puts "  assumed: u0_CE u0_CF u1_CE u1_CF, proven as CE_A CF_A (step 2)"
puts "  assumed: HP_M, proven as HP_A (step 5)"
puts "verdict: P1 and P2 proven at 256 entries by induction, on two\
 contracts and one helper, each proven"
finish
