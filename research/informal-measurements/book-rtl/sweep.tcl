# Elaborate every synthesizable design file the book ships; print the first error or the instance count.
set E /home/user/dv-handbook/examples
foreach {top files} {
  fifo        {ch01-what-is-dv/rtl/fifo.sv}
  fifo        {ch09-temporal-properties/rtl/fifo_fixed.sv}
  top         {ch03-digital-design/rtl/top.sv ch03-digital-design/rtl/datapath.sv ch03-digital-design/rtl/sync2.sv ch03-digital-design/rtl/regblock.sv}
  dma_v1      {ch11-architecture-to-verification/rtl/dma_v1.v}
  dma_v2      {ch11-architecture-to-verification/rtl/dma_regs_pkg.sv ch11-architecture-to-verification/rtl/dma_v2.sv}
  counter     {appF-counter/rtl/counter.sv}
  responder   {ch09-temporal-properties/vacuity/responder.sv ch09-temporal-properties/vacuity/ack_check.sv}
  responder   {ch09-temporal-properties/bounded-response/responder.sv ch09-temporal-properties/bounded-response/resp_check.sv}
  {}          {ch09-temporal-properties/handshake/hs_check.sv}
  {}          {ch04-simulation/race/safe.sv}
  {}          {ch04-simulation/fourstate/dut_unreset.sv}
} {
  clear -all
  set fs {}; foreach f $files {lappend fs $E/$f}
  puts "=== $files"
  if {[catch {
    analyze -sv12 {*}$fs
    if {$top eq ""} {elaborate} else {elaborate -top $top}
    set_prove_time_limit 20s
    puts "elaborated; prove -all (no clock/reset given): [prove -all]"
  } msg]} {puts "ERROR: [string range $msg 0 600]"}
}
