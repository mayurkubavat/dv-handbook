# protocol-checker.tcl -- one checker, asserted on outputs and assumed
# on inputs. A: the wire stage with a free input; B: the same stage
# with the checker assumed on its input; C: the register stage with a
# free input; D: the wrong direction, the output's rules assumed;
# E: the DMA with the checker bound five times, by induction and by
# rIC3.
set here [file dirname [info script]]
source $here/../common.tcl
set f $here/vr.sv
puts "=== A: wire stage, input free"
design $f vr_top -parameter PASS 1 -parameter ENV 0
one informal-bmc 30s -all
expect cex Held_A Stable_A
puts "=== B: wire stage, input rules assumed"
design $f vr_top -parameter PASS 1 -parameter ENV 1
one informal-kind 30s -all
expect proven Held_A Stable_A
expect covered Wait_C
puts "=== C: register stage, input free"
design $f vr_top -parameter PASS 0 -parameter ENV 0
one informal-kind 30s -all
expect proven Held_A Stable_A
expect covered Wait_C
puts "=== D: wire stage, the output's rules assumed by mistake"
design $f vr_top -parameter PASS 1 -parameter ENV 0 -parameter OUT_ASSUME 1
assert -name a_in_held {i_valid && !i_ready |=> i_valid}
cover  -name c_in_drop {i_valid && !i_ready ##1 !i_valid}
one informal-kind 30s -all
expect proven a_in_held
expect unreachable c_in_drop
puts "=== E: DMA version 2, outputs asserted, inputs assumed"
clear -all
analyze -sv12 $f $::rtl11/dma_regs_pkg.sv $::rtl11/dma_v2.sv \
    $here/dma_bind.sv
elaborate -top dma_v2
clock PCLK
reset -expression {!PRESETn}
one informal-kind 60s -all
one ric3-ic3 60s -all
finish
