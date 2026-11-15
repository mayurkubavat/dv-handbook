# modes.tcl -- what set_engine_mode and set_prove_time_limit do.
source [file dirname [info script]]/common.tcl
clear -all
analyze -sv12 $here/deep.sv
elaborate -top deep -parameter BUG 16
clock clk
reset -expression {rst}
assert -name a_never {cnt != 16'd16}
assert -name a_true  {cnt != 16'd16 || 1'b1}
cover  -name c_no    {cnt == 16'd3 && cnt == 16'd4}
foreach mode {Ht Hp B N {Ht B} Tri K I AM} {
  puts "--- set_engine_mode {$mode}"
  if {[catch {set_engine_mode $mode} msg]} {puts "ERROR: $msg"; continue}
  set_prove_time_limit 3s
  prove -all
}
informal::set_engines informal-bmc
foreach lim {5 5s 0.5s 2m 1h 500ms 0 -1 abc} {
  puts "--- set_prove_time_limit $lim"
  if {[catch {set_prove_time_limit $lim} msg]} {puts "ERROR: $msg"; continue}
  if {$lim in {5 0.5s 0}} {
    set t [clock milliseconds]
    prove -property a_true
    puts "wall [expr {[clock milliseconds] - $t}] ms"
  }
}
puts "--- default limit (fresh session value)"
puts [catch {get_prove_time_limit} msg]; puts $msg
