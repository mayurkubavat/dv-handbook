foreach aw {8 12 13 16} {
  puts "=== AW=$aw"
  clear -all
  analyze -sv12 [file dirname [info script]]/bigmem.sv
  elaborate -top bigmem -parameter AW $aw
  clock clk
  set_prove_time_limit 30s
  assert -name a_rw {we && wa == ra ##1 !we && $stable(ra) |=> rd == $past(wd, 2)}
  assert -name a_bad {we ##1 1'b1 |=> rd == $past(wd, 2)}
  set t [clock milliseconds]; catch {prove -all} msg; puts "$msg wall [expr {[clock milliseconds]-$t}] ms"
}
