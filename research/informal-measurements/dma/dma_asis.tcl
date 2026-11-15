# Chapter 9's axi-rules checker as shipped
clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch11-architecture-to-verification/rtl/dma_regs_pkg.sv /home/user/dv-handbook/examples/ch11-architecture-to-verification/rtl/dma_v2.sv /home/user/dv-handbook/examples/ch09-temporal-properties/axi-rules/axil_master_sva.sv /home/user/dv-handbook/examples/ch09-temporal-properties/axi-rules/dma_bind.sv
elaborate -top dma_v2
clock PCLK
reset -expression {!PRESETn}
puts "prove returned: [prove -all]"
