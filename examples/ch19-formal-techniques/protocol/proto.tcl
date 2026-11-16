# proto.tcl -- one checker, hs_rules, asserted on the side the block
# under proof drives and assumed on the side its neighbor drives.
# A: the wire stage with a free input; B: the same stage with the
# checker on its input as well; C: the register stage with a free
# input; D: the output's checker bound with the neighbor's role.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f [list $here/hs_rules.sv $here/vr.sv]

puts "=== A: wire stage, input free"
design $f vr_top -parameter PASS 1
one informal-kind 5s -all
expect cex     Held_A Stable_A
expect covered Wait_C
puts "=== B: wire stage, the input's rules assumed"
design $f vr_top -parameter PASS 1 -parameter ENV 1
cover  -name c_ready {i_ready}
one informal-kind 5s -all
expect proven  Held_A Stable_A Answer_A
expect covered Wait_C c_ready
puts "=== C: register stage, input free"
design $f vr_top -parameter PASS 0
one informal-kind 5s -all
expect proven  Held_A Stable_A
expect covered Wait_C
puts "=== D: wire stage, the output's checker in the receiver's role"
design $f vr_top -parameter PASS 1 -parameter WRONG 1
assert -name a_in_held {i_valid && !i_ready |=> i_valid}
cover  -name c_in_wait {i_valid && !i_ready}
cover  -name c_in_drop {i_valid && !i_ready ##1 !i_valid}
one informal-kind 5s -all
expect cex         Answer_A
expect proven      a_in_held
expect covered     c_in_wait
expect unreachable c_in_drop
puts "verdict: the role decides which rules bind; the wrong role\
 proves a rule about the input that nothing enforces"
finish
