// Request, three cycles of work, grant. `stall` can hold the work for ever.
module live_small (input logic clk, input logic rst, input logic req, input logic stall,
                   output logic gnt);
  logic [1:0] n;      // 0 idle, 1 and 2 working, 3 granting
  assign gnt = n == 2'd3;
  always_ff @(posedge clk)
    if (rst) n <= 2'd0;
    else if (n == 2'd0) begin if (req) n <= 2'd1; end
    else if (!(stall && n == 2'd2)) n <= n + 2'd1;
endmodule
