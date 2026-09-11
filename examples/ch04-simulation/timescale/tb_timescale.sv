// tb_timescale.sv -- both modules in one design. Nothing here depends on
// the order in which the two prints appear, which is the point: the order
// is not stated by the source, and the two simulators do not agree on it.
`timescale 1ns/1ps
module tb_timescale;
  coarse u_coarse ();
  fine   u_fine ();
  initial #20 $finish;
endmodule
