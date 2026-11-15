// deep.sv -- a counter whose forbidden value is BUG enabled steps
// from reset. One free input, so a search has a choice at every step.
module deep #(parameter int BUG = 16, parameter int W = 16)
  (input logic clk, input logic rst, input logic en,
   output logic [W-1:0] cnt);
  always_ff @(posedge clk)
    if (rst)     cnt <= '0;
    else if (en) cnt <= cnt + W'(1);
endmodule
