# two_clock.tcl -- the two-clock design of the digital-design chapter:
# is it tractable at all, and with which engines. Two resets, so the
# reset expression names both, joined with && (with || the tool may
# hold only one of them low, and the other domain is never reset). Properties: a cover that the enable
# crosses, an assertion that count moves only when the synchronized
# enable is up (true), and one that it never reaches 3 (false).
source [file dirname [info script]]/common.tcl
set r $book/examples/ch03-digital-design/rtl
clear -all
analyze -sv12 $r/top.sv $r/datapath.sv $r/sync2.sv $r/regblock.sv
elaborate -top top
clock bclk
clock cclk -factor 3
reset -expression {!brst_n && !crst_n}
cover  -name c_crossed {en_c}
assert -name a_gated   {@(posedge cclk) !en_c |=> $stable(count)}
assert -name a_never3  {count != 8'd3}
each_engine [concat informal-bmc $provers] 20s -all
