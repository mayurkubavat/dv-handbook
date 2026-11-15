source [file dirname [info script]]/common.tcl
proc trial {lim bad} {
  puts "=== LIMIT=$lim BAD=$bad"
  setup wrap.sv wrap -parameter LIMIT $lim -parameter BAD $bad
  assert -name a_notbad "cnt != 32'd$bad"
  foreach e {informal-kind informal-ic3 informal-ic3-cadical informal-ic3-mt informal-kind-ic3 ric3-ic3 ric3} {
    informal::set_engines $e; set_prove_time_limit 20s
    set t [clock milliseconds]
    prove -all
    puts "wall [expr {[clock milliseconds]-$t}] ms"
  }
}
trial 1048576 3145728
trial 1000 5000
trial 1000 1400
