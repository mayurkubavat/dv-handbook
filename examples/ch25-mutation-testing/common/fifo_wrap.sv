// fifo_wrap.sv -- the module `fifo` the book's testbenches instantiate,
// around Yosys's mutated netlist `fifo_mut` (every mutation of the
// repaired FIFO behind one 14-bit select, as MCY's `mutate -ctrl`
// builds it). +mut=N picks mutation N; 0, the default, is the design
// unchanged. The names the temporal-properties chapter's bind reads
// inside a fifo (count) and this chapter's data check reads (do_write,
// do_read) are passed through from the netlist, whose own wires keep
// those names. Simulation only: the select is read from a plusarg.
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
  logic [13:0] mutsel;
  initial if (!$value$plusargs("mut=%d", mutsel)) mutsel = '0;
  fifo_mut u (.clk, .rst_n, .wr_en, .wr_data, .rd_en, .rd_data, .full,
              .empty, .mutsel);
  wire [4:0] count    = u.count;
  wire       do_write = u.do_write;
  wire       do_read  = u.do_read;
endmodule
