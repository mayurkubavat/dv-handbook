# cut.tcl -- three cuts of the same logic on the previous chapter's
# handshake (a request, a 200-cycle timer, a grant): the timer
# black-boxed, its `expired` output made a cut point, and the cut
# with a gap assumption that is then proved on the real timer. Then
# a gap assumption that spans many cycles and so binds too late, and
# the bounded response that only the real timer can prove.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set hs  $ch18/over-constraint/handshake.sv
set chk $here/timer_chk.sv

# bare ARGS -- a new session on the handshake alone, with its reset
# `rst` (active high, synchronous). ARGS go to `elaborate`.
proc bare {args} {
  clear -all
  analyze -sv12 $::hs
  elaborate -top handshake {*}$args
  clock clk
  reset -expression {rst}
}

# handshake ARGS -- the same with the timer's own assertion bound in,
# and the three properties and the cover of the previous chapter's
# cut-point run.
proc handshake {args} {
  clear -all
  analyze -sv12 $::hs $::chk
  elaborate -top handshake {*}$args
  clock clk
  reset -expression {rst}
  assert -name a_hold_q   {busy |=> $stable(q)}
  assert -name a_gnt_once {gnt |=> !gnt}
  assert -name a_no_early {$rose(busy) |=> !gnt}
  cover  -name c_gnt      {gnt}
}
set props {a_hold_q a_gnt_once a_no_early}

puts "=== A: the whole design"
handshake
one informal-kind 10s -all
expect proven  {*}$props *Range_A
expect covered c_gnt
expect_depth 202 c_gnt

puts "=== B: the timer black-boxed"
handshake -bbox_m {timer}
one informal-kind 10s -all
expect proven  a_hold_q a_gnt_once
expect cex     a_no_early
expect covered c_gnt
expect_depth 3 a_no_early c_gnt
# The assertion written in the timer stays in the table, as an error.
expect error   Range_A
puts "--- a name inside the box: accepted by assert, refused at prove"
handshake -bbox_m {timer}
assert -name a_inside {u_timer.t <= 16'd200}
puts "assert -name a_inside: accepted"
one informal-kind 10s -property a_inside
expect error   a_inside

puts "=== C: u_timer.expired as a cut point"
handshake
stopat u_timer.expired
puts "stopat -list: [stopat -list]"
one informal-kind 10s -all
expect proven  a_hold_q a_gnt_once *Range_A
expect cex     a_no_early
expect covered c_gnt
expect_depth 3 a_no_early c_gnt

puts "=== D: the cut, with the gap the property needs assumed"
# The gap, typed once: assumed here, proved on the real timer in E.
set gap {$rose(busy) |-> !u_timer.expired}
handshake
stopat u_timer.expired
assume -name m_gap $gap
one informal-kind 10s -all
expect proven  {*}$props *Range_A
expect covered c_gnt

puts "=== E: the gap, proved on the real timer (no cut)"
bare
assert -name a_gap $gap
one informal-kind 10s -all
expect proven  a_gap

puts "=== F: a gap over 199 cycles, assumed under the cut"
# True of the real timer, and stronger than D's, yet the depth-3
# trace survives it: the assumption's window runs past the end of
# that trace, and it constrains only traces that contain the whole
# window.
bare
stopat u_timer.expired
assume -name m_gap199 {req && !busy |=> !u_timer.expired [*199]}
assert -name a_no_early {$rose(busy) |=> !gnt}
one informal-kind 10s -all
expect cex     a_no_early
expect_depth 3 a_no_early
puts [exec python3 $ex/ch09-temporal-properties/common/vcdtable.py \
    [trace a_no_early] rst req busy u_timer.expired gnt]

puts "=== G: the delay itself, with the real timer and under the cut"
foreach cut {0 1} {
  bare
  if {$cut} {stopat u_timer.expired}
  assert -name a_201 {req && !busy |-> ##[1:201] gnt}
  if {!$cut} {assert -name a_200 {req && !busy |-> ##[1:200] gnt}}
  one informal-kind 10s -all
  if {$cut} {
    expect cex a_201
  } else {
    expect proven a_201
    expect cex    a_200
    expect_depth 201 a_200
  }
}
puts "verdict: each cut keeps the proofs; its counterexamples and\
 covers needed the gap, which the real timer proves"
finish
