// fifo_fwrap.sv -- for formal runs on a Yosys netlist mutant: the
// module `fifo` that Chapter 9's bind and Chapter 19's tracked-word
// harness expect, around the mutant netlist `fifo_m` (one mutation
// applied, no select). The bind reads count and DEPTH inside a fifo;
// the harness reads do_write, do_read, count, wr_ptr and rd_ptr.
module fifo #(
  parameter int WIDTH = 8,
  parameter int DEPTH = 16
) (
  input  logic             clk,
  input  logic             rst_n,
  input  logic             wr_en,
  input  logic [WIDTH-1:0] wr_data,
  input  logic             rd_en,
  output logic [WIDTH-1:0] rd_data,
  output logic             full,
  output logic             empty
);
  fifo_m u (.clk, .rst_n, .wr_en, .wr_data, .rd_en, .rd_data, .full,
            .empty);
  wire [4:0] count    = u.count;
  wire       do_write = u.do_write;
  wire       do_read  = u.do_read;
  wire [3:0] wr_ptr   = u.wr_ptr;
  wire [3:0] rd_ptr   = u.rd_ptr;
endmodule
