# vacuity.tcl -- the broken responder and its checker under InFormal:
# with free inputs, with an environment that is too quiet, and with
# assumptions that contradict each other.
set here [file dirname [info script]]
analyze -sv12 $here/../vacuity/ack_check.sv $here/../vacuity/responder.sv
elaborate -top responder
clock clk
reset -none
informal::set_engines informal-kind
set_prove_time_limit 60s

puts "=== inputs free"
prove -all
expect cex     Ack_A
expect covered Req_C

puts "=== assumed: the environment never requests"
assume -name Quiet_M {!req}
prove -all
expect proven      Ack_A
expect unreachable Req_C

puts "=== assumed as well: it requests on every tick"
assume -name Busy_M {req}
prove -all
expect proven      Ack_A
expect unreachable Req_C

puts "=== a contradiction that takes a tick to bite"
assume -remove Quiet_M
assume -name Pulse_M {req |=> !req}
cover  -name ReqNext_C {req ##1 1'b1}
prove -all
expect proven      Ack_A
expect covered     Req_C
expect unreachable ReqNext_C
puts "verdict: an assertion proved under assumptions is worth what\
 its cover says"
finish
