# assume.tcl -- one sink, properties in three places, proved twice:
# with its inputs free, and with the source's rules assumed.
set here [file dirname [info script]]
analyze -sv12 $here/hs_sink.sv $here/../handshake/hs_check.sv \
    $here/hs_bind.sv
elaborate -top hs_sink
clock clk
reset -expression {!rst_n}
informal::set_engines informal-kind
set_prove_time_limit 60s

puts "=== inputs free: the source may do anything"
prove -all
expect cex     Taken_A Answer_A Held_A Stable_A
expect covered Waited_C

puts "=== the source's two rules assumed"
assume -name Held_M   {valid && !ready |=> valid}
assume -name Stable_M {valid && !ready |=> $stable(data)}
prove -all
expect proven  Taken_A Answer_A Held_A Stable_A
expect covered Waited_C
puts "verdict: the sink is correct against a source that keeps the\
 rules, and only against that one"
finish
