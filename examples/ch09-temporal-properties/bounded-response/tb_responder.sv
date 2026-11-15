// tb_responder.sv -- random requests against the responder, with the
// checker bound in. By default the responder is the one whose slow
// path is one tick too long.
`timescale 1ns/1ps
module tb_responder #(parameter bit SLOW_BY_ONE = 1);
  logic clk = 0, rst_n = 0, req = 0, slow = 0, gnt;
  always #5 clk <= ~clk;

  responder #(.SLOW_BY_ONE(SLOW_BY_ONE)) dut (.*);
  bind responder resp_check chk (.*);

  initial begin
    repeat (2) @(negedge clk);
    rst_n = 1;
    for (int i = 0; i < 40; i++) begin
      @(negedge clk);
      req  = ($urandom_range(0, 9) < 2);
      slow = ($urandom_range(0, 9) < 5);
    end
    req = 0;
    repeat (5) @(negedge clk);
    $finish;
  end
endmodule
