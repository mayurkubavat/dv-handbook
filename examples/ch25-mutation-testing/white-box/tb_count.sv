// tb_count.sv -- the FIFO's internal count beside its two flags, one
// line for each clock edge: three pushes, one pop, then idle. The
// design is the chapter's source schema; +mut=K selects a mutant (0,
// the default, is the repaired FIFO). The count is read through the
// hierarchy, as the temporal-properties chapter's bind reads it.
`timescale 1ns/1ps
module tb_count;
  logic       clk = 0, rst_n = 0, wr_en = 0, rd_en = 0;
  logic [7:0] wr_data = '0, rd_data;
  logic       full, empty;
  always #5 clk <= ~clk;

  fifo dut (.*);

  task automatic step(input logic w, input logic r, input string what);
    @(negedge clk);
    wr_en = w;
    rd_en = r;
    @(posedge clk);
    #1 $display("  %-6s count=%0d full=%0b empty=%0b", what, dut.count,
                full, empty);
  endtask

  initial begin
    repeat (2) @(negedge clk);
    rst_n = 1;
    #1 $display("  reset  count=%0d full=%0b empty=%0b", dut.count, full,
                empty);
    step(1, 0, "push");
    step(1, 0, "push");
    step(1, 0, "push");
    step(0, 1, "pop");
    step(0, 0, "idle");
    $display("PASS: trace done");
    $finish;
  end
endmodule
