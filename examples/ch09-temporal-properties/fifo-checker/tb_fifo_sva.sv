// tb_fifo_sva.sv -- random traffic and nothing else. The testbench has
// no checker of its own: every check is in the bound module, and a
// failing assertion stops the run.
`timescale 1ns/1ps
module tb_fifo_sva;
  logic       clk = 0, rst_n = 0, wr_en = 0, rd_en = 0;
  logic [7:0] wr_data = '0, rd_data;
  logic       full, empty;
  always #5 clk <= ~clk;

  fifo dut (.*);

  initial begin
    repeat (2) @(negedge clk);
    rst_n = 1;
    for (int cycle = 0; cycle < 400; cycle++) begin
      @(negedge clk);
      // Fill early, drain late, so both ends are visited.
      wr_en   = ($urandom_range(0, 99) < (cycle < 200 ? 80 : 30));
      rd_en   = ($urandom_range(0, 99) < (cycle < 200 ? 30 : 80));
      wr_data = 8'($urandom);
    end
    @(negedge clk);
    $display("PASS: 400 cycles, no assertion failed");
    $finish;
  end
endmodule
