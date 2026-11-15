// live_small.sv -- a request, two cycles of work, a grant.
//
// n is 0 when idle, 1 and 2 while working, 3 in the cycle of the
// grant. The stall input holds the design in state 2 for as long as
// it is high.
module live_small (
  input  logic clk,
  input  logic rst,
  input  logic req,
  input  logic stall,
  output logic gnt
);
  logic [1:0] n;
  assign gnt = (n == 2'd3);
  always_ff @(posedge clk)
    if (rst) n <= 2'd0;
    else if (n == 2'd0) begin
      if (req) n <= 2'd1;
    end else if (!(stall && n == 2'd2)) n <= n + 2'd1;
endmodule
