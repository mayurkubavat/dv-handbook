// fifo_ptrs.sv -- the repaired FIFO, small, with its reset cycle
// written as hardware and one property of its own registers.
//
// Three macros choose the model:
//   DEPTH   the number of entries (default 2)
//   COUNT   assert the helper CountPtrs_A instead of EmptyPtrs_A
//   HELPER  assume the helper while asserting EmptyPtrs_A
`ifndef DEPTH
  `define DEPTH 2
`endif
module fifo_ptrs (
  input logic clk,
  input logic rst_n,
  input logic wr_en,
  input logic rd_en
);
  localparam int PW = $clog2(`DEPTH);
  logic full, empty, rd_data;
  fifo #(.WIDTH(1), .DEPTH(`DEPTH)) dut (.wr_data(1'b0), .*);

  logic started = 1'b0;             // 0 in the first cycle only
  always_ff @(posedge clk) started <= 1'b1;

  // The helper: the low bits of the occupancy are the distance
  // between the pointers.
  wire helper = dut.count[PW-1:0] == dut.wr_ptr - dut.rd_ptr;

  always_comb begin
    // Reset is held for the first cycle and released for good.
    Reset_M:     assume (rst_n == started);
`ifdef COUNT
    CountPtrs_A: assert (!rst_n || helper);
`else
    EmptyPtrs_A: assert (!rst_n || !empty || dut.wr_ptr == dut.rd_ptr);
`endif
`ifdef HELPER
    CountPtrs_M: assume (!rst_n || helper);
`endif
  end
endmodule
