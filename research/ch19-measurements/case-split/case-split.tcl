# case-split.tcl -- a product checked two ways (a miter), whole and
# in four cases on the two top bits of a. A: whole, W = 8; B: the four
# cases, W = 8, and the completeness check; C: the bug that lives in
# case 3, with a case list that forgot it; D: W = 10, whole and split.
set here [file dirname [info script]]
source $here/../common.tcl
proc mul {w bug} {
  clear -all
  analyze -sv12 $::here/mul.sv
  elaborate -top mul_miter -parameter W $w -parameter BUG $bug
  clock clk
  reset -none
}
# cases W BUG LIST LIMIT -- one proof per case, the case assumed.
proc cases {w bug list limit} {
  set hi [expr {$w - 1}]; set lo [expr {$w - 2}]
  foreach c $list {
    mul $w $bug
    assume -name M_case "a\[$hi:$lo\] == 2'd$c"
    assert -name A_eq {p_ref == p_arr}
    puts "--- case a\[$hi:$lo\] == $c"
    one informal-kind $limit -all
  }
}
puts "=== A: whole, W = 8"
mul 8 0
assert -name A_eq {p_ref == p_arr}
one informal-kind 60s -all
expect proven A_eq
puts "=== B: four cases, W = 8"
cases 8 0 {0 1 2 3} 60s
puts "--- completeness: the four case conditions cover every value"
mul 8 0
assert -name A_cover4 {a[7:6] == 2'd0 || a[7:6] == 2'd1 ||
                       a[7:6] == 2'd2 || a[7:6] == 2'd3}
one informal-kind 10s -all
expect proven A_cover4
puts "=== C: the bug in case 3; a case list that forgot case 3"
cases 8 1 {0 1 2 3} 60s
mul 8 1
assert -name A_cover3 {a[7:6] == 2'd0 || a[7:6] == 2'd1 ||
                       a[7:6] == 2'd2}
one informal-kind 10s -all
expect cex A_cover3
puts "=== D: W = 10, whole and in four cases"
mul 10 0
assert -name A_eq {p_ref == p_arr}
one informal-kind 60s -all
cases 10 0 {0 1 2 3} 60s
finish
