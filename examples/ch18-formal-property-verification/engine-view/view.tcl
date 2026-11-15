# view.tcl -- the pointer property through the tool at two and at four
# entries, by induction and by IC3. DEPTHS in the environment narrows
# the run to some sizes and ENGINES to some engines; view.sh uses that
# to look at one proof at a time.
set here [file dirname [info script]]
source $here/../common/proof.tcl
set depths  [expr {[info exists ::env(DEPTHS)]  ? $::env(DEPTHS)  : {2 4}}]
set engines [expr {[info exists ::env(ENGINES)] ? $::env(ENGINES) \
                   : {informal-kind informal-ic3}}]
foreach depth $depths {
  clear -all
  analyze -sv12 $ch09/rtl/fifo_fixed.sv
  elaborate -top fifo -parameter DEPTH $depth -parameter WIDTH 1
  clock clk
  reset -expression {!rst_n}
  assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
  puts "=== $depth entries"
  foreach engine $engines {
    one $engine 3s -all
    # Induction at four entries is the one row with no verdict here.
    if {$depth == 4 && $engine eq "informal-kind"} {
      expect undetermined EmptyPtrs_A
    } else {
      expect proven EmptyPtrs_A
    }
  }
}
finish
