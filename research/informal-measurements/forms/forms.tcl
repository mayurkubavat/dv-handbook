clear -all
analyze -sv12 [file join [file dirname [info script]] probe.sv]
elaborate -top probe
clock clk
reset -expression {rst}
set_prove_time_limit 20s
set n 0
proc try {kind text} {
  global n; incr n
  if {[catch {$kind -name p$n $text} msg]} { puts "REJECT p$n $kind {$text}: $msg" } else { puts "ACCEPT p$n $kind {$text}" }
}
try assert {q <= 4'd9}
try assert {en && !done |=> q == $past(q) + 4'd1}
try assert {!en |=> $stable(q)}
try assert {$rose(done) |-> $past(en)}
try assert {$fell(done) |-> 1'b0}
try assert {$changed(q) |-> $past(en)}
try assert {$past(q,2) <= q}
try assert {@(posedge clk) disable iff (rst) q <= 4'd9}
try assert {@(negedge clk) q <= 4'd9}
try assert {a ##1 b |-> ##2 y}
try assert {a ##[1:3] b |-> q <= 4'd9}
try assert {a [*3] |=> y}
try assert {a [*1:3] ##1 b |-> q <= 4'd9}
try assert {(a ##1 b) and (b ##1 a) |-> q <= 4'd9}
try assert {(a ##1 b) or (b ##1 a) |-> q <= 4'd9}
try assert {(a ##1 b) intersect (b ##1 a) |-> q <= 4'd9}
try assert {a within (b ##2 b) |-> q <= 4'd9}
try assert {en throughout (a ##2 b) |-> q <= 4'd9}
try assert {first_match(a ##[1:3] b) |-> q <= 4'd9}
try assert {a |-> (y until b)}
try assert {a |=> (y until_with !a)}
try assert {a |-> (a s_until b)}
try assert {a |-> s_eventually y}
try assert {en |-> s_eventually done}
try assert {nexttime [2] (q <= 4'd9)}
try assert {a |-> nexttime y}
try assert {s_eventually [1:3] a}
try assert {always [0:2] (q <= 4'd9)}
try assert {a |-> ##[1:$] b}
try assert {a [->2] |-> b}
try assert {a [=2] |-> b}
try assert {not (a ##1 b)}
try assert {accept_on (b) a |=> y}
try assert {a #-# b}
try assert {a #=# b}
try assert {a |-> always b}
try assert {a iff b}
try assert {a implies b}
try assert {if (a) b else !b}
try assert {$onehot0({a,b})}
try assert {$countones(q) <= 4}
try assert {$isunknown(q) == 0}
try assert {u_leaf.hid |=> y || rst}
try assert {probe.u_leaf.hid == y}
try assert {nosuch == 1'b0}
try assert {q <= LIM}
try assert {$bits(q) == W}
try assert {q inside {[0:9]}}
try assert {a |-> strong(##[1:3] b)}
try assert {a ##0 b |-> q <= 4'd9}
try assert {$past(q) <= q || $past(rst)}
try cover {q == 4'd9}
try cover {a ##1 b ##1 a}
try cover {q == 4'd10}
try assume {a |=> !a}
prove -all
puts "SUMMARY [get_property_list -include {status error}]"
