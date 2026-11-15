// tb_handshake.sv -- four offers and one stray ready, from a tick
// counter, under the checker.
//
//   tick    2..4   offer A, ready at 4            keeps the rule
//           6..8   offer B, data changes at 7     payload changed
//          10      offer C, withdrawn at 11       valid dropped
//          13      offer D, reset at 14           abandoned by reset
//          16      ready with nothing on offer    answer to no one
`timescale 1ns/1ps
module tb_handshake;
  logic       clk = 0;
  logic [4:0] t = 0;                       // the tick counter
  always #5 clk <= ~clk;
  always_ff @(posedge clk) t <= t + 5'd1;

  wire       rst_n = (t != 14);
  wire       valid = (t >= 2 && t <= 4) || (t >= 6 && t <= 8) ||
                     (t == 10) || (t == 13);
  wire       ready = (t == 4) || (t == 8) || (t == 16);
  wire [7:0] data  = (t <= 4) ? 8'hA0 : (t == 6) ? 8'hB0 : 8'hC0;

  hs_check chk (.*);

  initial begin
    repeat (18) @(posedge clk);
    $finish;
  end
endmodule
