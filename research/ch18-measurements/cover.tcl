# cover.tcl -- a cover is a reachability question: reachable is a
# trace, unreachable is a proof. The repaired FIFO and the original.
source [file dirname [info script]]/common.tcl
foreach {name rtl} [list original $book/examples/ch01-what-is-dv/rtl/fifo.sv \
                         repaired $ch09/rtl/fifo_fixed.sv] {
  clear -all
  analyze -sv12 $rtl $ch09/fifo-checker/fifo_sva.sv \
      $ch09/fifo-checker/fifo_bind.sv
  elaborate -top fifo
  clock clk
  reset -expression {!rst_n}
  puts "=== $name FIFO, the cover of sixteen entries"
  each_engine [concat informal-bmc $provers] 20s -property fifo.u_sva.FullReached_C
}
