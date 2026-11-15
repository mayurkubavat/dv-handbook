# common.tcl -- shared by the measurement scripts.
set ::here [file dirname [info script]]
set ::book $::env(BOOK)
set ::ch09 $::book/examples/ch09-temporal-properties
set ::ch11 $::book/examples/ch11-architecture-to-verification

# One engine per prove, so that the engine column says who answered.
proc each_engine {engines limit args} {
  set_prove_time_limit $limit
  foreach e $engines {
    puts "--- engine $e, limit $limit"
    informal::set_engines $e
    set t [clock milliseconds]
    prove {*}$args
    puts "wall [expr {[clock milliseconds] - $t}] ms"
  }
}
set ::provers {informal-kind informal-ic3 informal-ic3-cadical
               informal-kind-ic3 informal-ic3-mt ric3-ic3}
set ::hunters {informal-bmc informal-bmc-10 informal-bmc-65 ric3-bmc}
