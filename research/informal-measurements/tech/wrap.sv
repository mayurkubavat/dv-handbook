// A counter that wraps at LIMIT-1. BAD is a value it never reaches, but the
// unreachable states LIMIT..BAD-1 walk straight into it, one step at a time.
module wrap #(parameter int LIMIT = 1_000_000, parameter int BAD = 3_000_000)
  (input logic clk, input logic rst, input logic en, output logic [31:0] cnt);
  always_ff @(posedge clk)
    if (rst) cnt <= '0;
    else if (en) cnt <= (cnt == LIMIT - 1) ? '0 : cnt + 32'd1;
endmodule
