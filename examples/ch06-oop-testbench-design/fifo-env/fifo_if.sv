// fifo_if.sv -- the FIFO's ports as one bundle, with the testbench's
// clocking block beside them (the Chapter 5 interface, reused).
interface fifo_if #(parameter int WIDTH = 8) (input logic clk);
  logic             rst_n;
  logic             wr_en, rd_en;
  logic [WIDTH-1:0] wr_data, rd_data;
  logic             full, empty;
  clocking cb @(posedge clk);
    default input #1step output #0;
    output rst_n, wr_en, rd_en, wr_data;
    input  rd_data, full, empty;
  endclocking
  modport dut (input clk, rst_n, wr_en, rd_en, wr_data,
               output rd_data, full, empty);
endinterface
