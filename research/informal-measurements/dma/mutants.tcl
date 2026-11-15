# The two Chapter 9 mutants (made by sed into dma/mutants/, see FINDINGS)
foreach m {drop wander} {
  puts "=== mutant $m"
  clear -all
  analyze -sv12 /home/user/dv-handbook/examples/ch11-architecture-to-verification/rtl/dma_regs_pkg.sv [file dirname [info script]]/mutants/dma_$m.sv [file dirname [info script]]/axi_props2.sv
  elaborate -top dma_v2
  clock PCLK
  reset -expression {!PRESETn}
  set_prove_time_limit 120s
  prove -all
}
