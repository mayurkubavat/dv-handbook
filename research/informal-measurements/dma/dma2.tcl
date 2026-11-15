clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch11-architecture-to-verification/rtl/dma_regs_pkg.sv /home/user/dv-handbook/examples/ch11-architecture-to-verification/rtl/dma_v2.sv [file dirname [info script]]/axi_props2.sv
elaborate -top dma_v2
clock PCLK
reset -expression {!PRESETn}
set_prove_time_limit 120s
set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
