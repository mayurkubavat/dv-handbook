# axi.tcl -- the AXI master rules proved on the DMA of the case study.
# The checker and its bind file are the ones the simulation used. No
# slave is modelled: every input of the design is free.
set here [file dirname [info script]]
set c11  $here/../../ch11-architecture-to-verification
set sva  [list $here/../axi-rules/axil_master_sva.sv \
               $here/../axi-rules/dma_bind.sv]

proc load {args} {
  clear -all
  analyze -sv12 $::c11/rtl/dma_regs_pkg.sv {*}$args
  elaborate -top dma_v2
  clock PCLK
  reset -expression {!PRESETn}
  informal::set_engines informal-ic3
  set_prove_time_limit 120s
}

puts "=== the design: six rules, six covers"
load $c11/rtl/dma_v2.sv {*}$sva
prove -all
expect proven  ArHeld_A ArStable_A AwHeld_A AwStable_A WHeld_A WStable_A
expect covered ArWait_C AwWait_C WWait_C ArFirst_C AwFirst_C WFirst_C

# A mutant is the design with one line changed, as in the simulation.
proc mutant {name edit} {
  set file [file join $::workdir dma_$name.sv]
  exec sed $edit $::c11/rtl/dma_v2.sv > $file
  load $file {*}$::sva
  prove -all
}
set old {R_ADDR: if (ARREADY) begin  }
puts "=== mutant drop: leave the address state after one tick"
mutant drop "s/$old/R_ADDR: begin                /"
expect cex    ArHeld_A
expect proven ArStable_A AwHeld_A AwStable_A WHeld_A WStable_A
puts "=== mutant wander: step the address while it waits"
mutant wander \
    "s/$old/R_ADDR: if (!ARREADY) ARADDR <= ARADDR + 4; else begin/"
expect cex    ArStable_A
expect proven ArHeld_A AwHeld_A AwStable_A WHeld_A WStable_A
puts "=== mutant wait: raise ARVALID only once ARREADY has been seen"
mutant wait {s/R_IDLE: if (r_any/R_IDLE: if (ARREADY \&\& r_any/}
expect proven      ArHeld_A ArStable_A
expect unreachable ArFirst_C
expect covered     ArWait_C

puts "=== one rule, two spellings, as Tcl properties on the design"
load $c11/rtl/dma_v2.sv
assert -name HeldNext_A {ARVALID && !ARREADY |=> ARVALID}
assert -name HeldPast_A {$past(ARVALID && !ARREADY) |-> ARVALID}
prove -all
puts [exec python3 $here/../common/vcdtable.py [trace HeldPast_A] \
    PRESETn ARVALID ARREADY]
expect proven HeldNext_A
expect cex    HeldPast_A
puts "verdict: six rules proved; each mutant caught, two by an\
 assertion and one by a cover"
finish
