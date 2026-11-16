// tb_async_reset.sv -- a reset that never meets a clock edge.
//
// Every testbench of the book holds rst_n low across a rising edge of
// clk, so a reset that the design sees only at the edge and a reset it
// sees at once look the same to them. This one pushes three words,
// then drops rst_n for 2 ns between two edges and raises it again
// before the next one, and reads empty while the clock is still low.
// An asynchronous reset has emptied the FIFO by then; a synchronous
// one never saw the pulse. The design is module fifo; +mut=K selects
// a mutant when the design is the chapter's source schema.
`timescale 1ns/1ps
module tb_async_reset;
  logic       clk = 0, rst_n = 0, wr_en = 0, rd_en = 0;
  logic [7:0] wr_data = '0, rd_data;
  logic       full, empty;
  always #5 clk <= ~clk;

  fifo dut (.*);

  initial begin
    repeat (2) @(negedge clk);
    rst_n = 1;
    for (int i = 0; i < 3; i++) begin
      @(negedge clk);
      wr_en   = 1;
      wr_data = 8'(i + 1);
    end
    @(negedge clk);
    wr_en = 0;
    #1 rst_n = 0;                  // 1 ns after the falling edge
    #2 rst_n = 1;                  // released 2 ns before the next rise
    #1;
    $display("after a reset pulse between edges: empty=%0b", empty);
    if (empty !== 1'b1) $fatal(1, "FAIL: the pulse did not empty it");
    $display("PASS: the reset acted between clock edges");
    $finish;
  end
endmodule
