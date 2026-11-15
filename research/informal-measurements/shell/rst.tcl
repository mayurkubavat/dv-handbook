proc go {label cmds} {
  puts "=== $label"
  clear -all
  analyze -sv12 [file dirname [info script]]/rst.sv
  elaborate -top rst
  set_prove_time_limit 10s
  informal::set_engines informal-kind
  foreach c $cmds { if {[catch $c msg]} {puts "ERROR in {$c}: $msg"} }
  assert -name a_async_in_reset {!rst_n |-> a == 4'd0}
  assert -name a_after_reset    {$rose(rst_n) |-> a == 4'd0}
  assert -name a_iv             {iv == 4'd5}
  assert -name a_nr_zero        {nr == 4'd0}
  assert -name a_rst_stays_high {$past(rst_n) |-> rst_n}
  cover  -name c_rst_low_later  {rst_n ##1 !rst_n}
  cover  -name c_a3             {a == 4'd3}
  if {[catch {prove -all} msg]} {puts "ERROR in prove: $msg"}
}
go "clock + reset"           {{clock clk} {reset -expression {!rst_n}}}
go "clock, no reset command" {{clock clk}}
go "reset -none"             {{clock clk} {reset -none}}
go "no clock command"        {{reset -expression {!rst_n}}}
go "reset on a name that is not there" {{clock clk} {reset -expression {!rstn}}}
go "clock on a name that is not there" {{clock ck} {reset -expression {!rst_n}}}
