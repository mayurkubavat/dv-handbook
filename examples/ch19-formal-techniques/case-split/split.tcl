# split.tcl -- a product checked two ways (a miter), W = 8: whole, and
# in four cases on the two top bits of a, with the check that the
# four cases cover every value. Then a bug that lives in case 3, and
# a case list that forgot case 3.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
# mul BUG EQ -- a new session on the miter (no reset: it has no
# state), with the miter's assertion A_eq when EQ is 1.
proc mul {bug {eq 1}} {
  clear -all
  analyze -sv12 $::here/mul.sv
  elaborate -top mul_miter -parameter W 8 -parameter BUG $bug
  clock clk
  reset -none
  if {$eq} {assert -name A_eq {p_ref == p_arr}}
}
# cases BUG LIST -- one session per case, the case assumed.
proc cases {bug list} {
  foreach c $list {
    puts "--- case a\[7:6\] == $c"
    mul $bug
    assume -name M_case "a\[7:6\] == 2'd$c"
    one informal-kind 30s -all
  }
}

puts "=== A: whole"
mul 0
one informal-kind 40s -all
expect proven A_eq
puts "=== B: four cases"
foreach c {0 1 2 3} {
  cases 0 $c
  expect proven A_eq
}
puts "--- completeness: the four case conditions cover every value"
mul 0 0
assert -name A_cover4 {a[7:6] == 2'd0 || a[7:6] == 2'd1 ||
                       a[7:6] == 2'd2 || a[7:6] == 2'd3}
one informal-kind 5s -all
expect proven A_cover4
puts "=== C: the bug in case 3, and a case list that forgot case 3"
cases 1 3
expect cex     A_eq
expect_depth 0 A_eq
mul 1 0
assert -name A_cover3 {a[7:6] == 2'd0 || a[7:6] == 2'd1 ||
                       a[7:6] == 2'd2}
one informal-kind 5s -all
expect cex     A_cover3
expect_depth 0 A_cover3
puts "verdict: four cases and their completeness proven; the case list\
 that forgot case 3 fails its completeness check"
finish
