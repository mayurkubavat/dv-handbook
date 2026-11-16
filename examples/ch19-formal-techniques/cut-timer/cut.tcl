# cut.tcl -- three cuts of the same logic on the previous chapter's
# handshake (a request, a 200-cycle timer, a grant): the timer
# black-boxed, its `expired` output made a cut point, and the cut
# with a gap assumption that is then proved on the real timer. Then
# a gap over a window of several cycles, which this tool judges, in
# an assumption as in a cover, only once the whole window lies inside
# a trace; and the bounded response only the real timer can prove.
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
# the three properties and the cover of the previous chapter's
# cut-point run, and a witness that runs one cycle past the grant.
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
  cover  -name c_gnt1     {gnt ##1 1}
}
set props {a_hold_q a_gnt_once a_no_early}

puts "=== A: the whole design"
handshake
one informal-kind 10s -all
expect proven  {*}$props *Range_A
expect covered c_gnt c_gnt1
expect_depth 202 c_gnt

puts "=== B: the timer black-boxed"
handshake -bbox_m {timer}
one informal-kind 10s -all
expect proven  a_hold_q a_gnt_once
expect cex     a_no_early
expect covered c_gnt c_gnt1
expect_depth 3 a_no_early c_gnt
# The assertion written in the timer stays in the table, as an error.
expect error   Range_A
puts "--- a name inside the box: accepted by assert, an error at prove"
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
expect covered c_gnt c_gnt1
expect_depth 3 a_no_early c_gnt

puts "=== D: the cut, with the gap the property needs assumed"
# The gap, typed once: assumed here, proved on the real timer in E.
set gap {$rose(busy) |-> !u_timer.expired}
handshake
stopat u_timer.expired
assume -name m_gap $gap
one informal-kind 10s -all
expect proven  {*}$props *Range_A
expect covered c_gnt c_gnt1

puts "=== E: the gap, proved on the real timer (no cut)"
bare
assert -name a_gap $gap
cover  -name c_rose {$rose(busy)}
one informal-kind 10s -all
expect proven  a_gap
expect covered c_rose

puts "=== F: a gap over a window of N cycles, assumed under the cut"
# Both windows are stronger than D's gap, and both are first proved
# on the real timer. The depth-3 trace raises expired in cycle 2,
# inside both windows. InFormal judges a multi-cycle implication only
# once its whole window lies inside the trace: the window of 2 does,
# and removes the trace; the window of 199 does not, and the trace
# survives it. The same holds for a cover, so the witness cover runs
# to the end of the window: `req && !busy ##N 1`.
set win {req && !busy |=> !u_timer.expired [*%d]}
puts "--- both windows, on the real timer (no cut)"
bare
foreach n {2 199} {
  assert -name a_gap$n [format $win $n]
  cover  -name c_win$n [format {req && !busy ##%d 1} $n]
}
one informal-kind 20s -all
expect proven  a_gap2 a_gap199
expect covered c_win2 c_win199
foreach n {2 199} {
  puts "--- window $n, under the cut"
  bare
  stopat u_timer.expired
  assume -name m_gap$n [format $win $n]
  assert -name a_no_early {$rose(busy) |=> !gnt}
  cover  -name c_win [format {req && !busy ##%d 1} $n]
  one informal-kind 10s -all
  expect covered c_win
  expect_depth [expr {$n + 1}] c_win
  if {$n == 2} {
    expect proven  a_no_early
  } else {
    expect cex     a_no_early
    expect_depth 3 a_no_early
    puts [exec python3 $ex/ch09-temporal-properties/common/vcdtable.py \
        [trace a_no_early] rst req busy u_timer.expired gnt]
  }
}
puts "--- a window no request can satisfy, under the cut"
# The window ends in 1'b0, so it excludes every trace that runs two
# cycles past a request, and no shorter one: a false response
# assertion is proven, a cover of the request alone is still reached,
# and only the cover that runs to the window's end is unreachable.
bare
stopat u_timer.expired
assume -name m_never {req && !busy |=> !u_timer.expired ##1 1'b0}
assert -name a_resp  {req && !busy |-> ##[1:3] gnt}
cover  -name c_rose  {$rose(busy)}
cover  -name c_win   {req && !busy ##2 1}
one informal-kind 10s -all
expect proven      a_resp
expect covered     c_rose
expect unreachable c_win

puts "=== G: the delay itself, with the real timer and under the cut"
foreach cut {0 1} {
  bare
  if {$cut} {stopat u_timer.expired}
  assert -name a_201 {req && !busy |-> ##[1:201] gnt}
  if {!$cut} {assert -name a_200 {req && !busy |-> ##[1:200] gnt}}
  if {!$cut} {cover  -name c_gnt {gnt}}
  one informal-kind [expr {$cut ? "10s" : "20s"}] -all
  if {$cut} {
    expect cex a_201
  } else {
    expect proven  a_201
    expect cex     a_200
    expect covered c_gnt
    expect_depth 201 a_200
  }
}
puts "verdict: each cut keeps the proofs; its counterexamples and\
 covers needed the gap, which the real timer proves"
finish
