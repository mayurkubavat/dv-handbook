// coarse.sv -- a module that declares nanosecond precision.
//
// `#1.4` is finer than the precision this module declares, so what happens
// to it is the question. Delays are scaled to the smallest precision used
// anywhere in the design; what a module does with a delay finer than its
// own declared precision is not stated in any openly readable source, and
// the two simulators below answer it differently.
//
// Both times print as plain numbers in this module's own unit, nanoseconds,
// so the two readings can be compared without a decoder: `%t` would print
// picoseconds, the design-wide precision, and hide the disagreement.
`timescale 1ns/1ns
module coarse;
  initial begin
    #1.4 $display("coarse: after #1.4, $time=%0d $realtime=%0.1f",
                  $time, $realtime);
    #1.6 $display("coarse: after #1.6, $time=%0d $realtime=%0.1f",
                  $time, $realtime);
  end
endmodule
