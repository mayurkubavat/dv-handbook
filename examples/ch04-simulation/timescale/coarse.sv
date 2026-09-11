// coarse.sv -- a module that declares nanosecond precision.
//
// `#1.4` is finer than the precision this module declares, so what happens
// to it is the question. The standard says delays are scaled to the
// smallest precision used anywhere in the design; it does not say, in any
// openly readable form, what a module does with a delay finer than its own
// declared precision.
`timescale 1ns/1ns
module coarse;
  initial begin
    #1.4 $display("coarse: after #1.4, $time=%0t $realtime=%0f",
                  $time, $realtime);
    #1.6 $display("coarse: after #1.6, $time=%0t $realtime=%0f",
                  $time, $realtime);
  end
endmodule
