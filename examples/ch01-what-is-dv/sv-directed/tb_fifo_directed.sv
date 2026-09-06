// tb_fifo_directed.sv -- the test that passed.
// Writes eight values, reads eight values, compares. Everything it checks
// is correct. Read Chapter 1 before deciding what that proves.
`timescale 1ns/1ps
module tb_fifo_directed;
  logic       clk = 0;
  logic       rst_n;
  logic       wr_en, rd_en;
  logic [7:0] wr_data, rd_data;
  logic       full, empty;

  fifo dut (.*);

  always #5 clk <= ~clk;

  int errors = 0;

  initial begin
    rst_n = 0; wr_en = 0; rd_en = 0; wr_data = '0;
    repeat (2) @(posedge clk);
    rst_n = 1;

    // Push eight values.
    for (int i = 0; i < 8; i++) begin
      @(negedge clk);
      wr_en   = 1;
      wr_data = 8'(8'hA0 + i);
    end
    @(negedge clk);
    wr_en = 0;

    // Pop eight values and compare in order.
    for (int i = 0; i < 8; i++) begin
      @(negedge clk);
      rd_en = 1;
      if (rd_data !== 8'(8'hA0 + i)) begin
        errors++;
        $display("MISMATCH entry %0d: got %02h expected %02h",
                 i, rd_data, 8'(8'hA0 + i));
      end
    end
    @(negedge clk);
    rd_en = 0;

    if (!empty) begin errors++; $display("FIFO not empty at end"); end

    if (errors == 0) $display("PASS: 8 entries written and read back");
    else begin
      $display("FAIL: %0d errors", errors);
      $fatal(1, "test failed");           // non-zero exit for make
    end
    $finish;
  end
endmodule
