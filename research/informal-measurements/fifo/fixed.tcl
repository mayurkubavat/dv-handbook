# Fixed FIFO: occ <= DEPTH, engine by engine, without and with the helper
proc go {defs} {
  clear -all
  analyze -sv12 {*}$defs /home/user/dv-handbook/examples/ch09-temporal-properties/rtl/fifo_fixed.sv [file dirname [info script]]/fifo_props.sv
  elaborate -top fifo
  clock clk
  reset -expression {!rst_n}
  set_prove_time_limit 30s
  foreach e {informal-bmc informal-kind informal-ic3 informal-ic3-cadical informal-ic3-mt informal-kind-ic3 ric3-ic3 ric3 {}} {
    puts "--- defs {$defs} engines: {$e}"
    informal::set_engines {*}$e
    set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
  }
}
go {}
go +define+HELPER
