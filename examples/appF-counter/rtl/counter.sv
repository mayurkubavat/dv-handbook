// counter.sv -- the design under test shared by every language in the
// build appendix: an 8-bit counter with an active-low asynchronous reset
// and a count enable.
module counter #(
  parameter int WIDTH = 8
) (
  input  logic             clk,
  input  logic             rst_n,   // active-low, asynchronous
  input  logic             en,      // count when high
  output logic [WIDTH-1:0] count
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)   count <= '0;
    else if (en)  count <= count + 1'b1;
  end
endmodule
