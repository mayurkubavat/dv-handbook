# engines_book.tcl -- every engine alone on the book's two real
# designs: the FIFO checker of the temporal-properties chapter on the
# repaired FIFO, and the six AXI rules on the DMA engine.
source [file dirname [info script]]/common.tcl
set all [concat informal-bmc $provers]

clear -all
analyze -sv12 $ch09/rtl/fifo_fixed.sv $ch09/fifo-checker/fifo_sva.sv \
    $ch09/fifo-checker/fifo_bind.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}
puts "=== repaired FIFO, 16 x 8, seven assertions and four covers"
each_engine $all 20s -all

clear -all
analyze -sv12 $ch11/rtl/dma_regs_pkg.sv $ch11/rtl/dma_v2.sv \
    $ch09/axi-rules/axil_master_sva.sv $ch09/axi-rules/dma_bind.sv
elaborate -top dma_v2
clock PCLK
reset -expression {!PRESETn}
puts "=== DMA version 2, six AXI rules and six covers"
each_engine $all 20s -all
