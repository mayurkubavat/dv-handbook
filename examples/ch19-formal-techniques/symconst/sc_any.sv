// sc_any.sv -- one symbolic slot address of the book's FIFO, written
// with $anyconst, a formal-tool extension this tool does not take.
// Its RTL assertion is the one sc_free.sv states: a push to the slot
// sa leaves the pushed word there. Not linted: Verilator does not
// take $anyconst either.
module sc_any #(parameter int DEPTH = 16) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  localparam int PW = $clog2(DEPTH);
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic [PW-1:0] sa;
  assign sa = $anyconst;
  Slot_A: assert property (@(posedge clk) disable iff (!rst_n)
            u.do_write && u.wr_ptr == sa |=> u.mem[sa] == $past(wr_data));
endmodule
