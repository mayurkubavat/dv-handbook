// fifo_if.sv -- the FIFO's ports as one bundle, with the testbench's
// clocking block inside it.
//
// The design side sees plain wires through `dut`. The testbench side
// reaches `cb` through the whole interface, so every read is of a settled
// value and every write lands after the edge. Putting the clocking block
// in the interface is what lets a class drive the design without ever
// touching the edge.
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
  // No modport carries the clocking block: the testbench holds the whole
  // interface and reaches `cb` through it, because a `modport (clocking)`
  // is one of the constructs the chapter's support table says the default
  // simulator refuses.
endinterface
