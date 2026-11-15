# response.tcl -- "a grant within three ticks", proved on the correct
# responder and refuted on the one whose slow path takes four.
set here [file dirname [info script]]
set src  $here/../bounded-response

proc load {slow_by_one} {
  clear -all
  analyze -sv12 $::src/responder.sv $::src/resp_check.sv \
      $::src/resp_bind.sv
  elaborate -top responder -parameter SLOW_BY_ONE $slow_by_one
  clock clk
  reset -expression {!rst_n}
  informal::set_engines informal-kind
  set_prove_time_limit 60s
}

puts "=== the correct responder"
load 0
prove -all
expect proven  Window_A
expect covered Waited_C

puts "=== the slow-by-one responder"
load 1
prove -all
expect cex     Window_A
expect covered Waited_C
puts [exec python3 $here/../common/vcdtable.py [trace Window_A] \
    rst_n req slow gnt chk.waiting]
puts "verdict: proved on one responder, refuted on the other in the\
 fewest ticks a late grant takes"
finish
