// fine.sv -- a module in the same design that declares picosecond
// precision, and whose one delay falls between the two readings the
// coarse module can produce for its own.
`timescale 1ns/1ps
module fine;
  initial #1.2 $display("fine:   after #1.2, $realtime=%0t", $realtime);
endmodule
