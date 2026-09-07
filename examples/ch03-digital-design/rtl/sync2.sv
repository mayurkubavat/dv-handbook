// sync2.sv -- a two-flop synchronizer. The first flop may go metastable;
// the second gives it a clock period to settle. Correct for single bits
// and for multi-bit values only when they change one bit at a time.
module sync2 #(
  parameter int WIDTH = 1
) (
  input  logic             clk,
  input  logic             rst_n,
  input  logic [WIDTH-1:0] d,
  output logic [WIDTH-1:0] q
);
  logic [WIDTH-1:0] meta;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      meta <= '0;
      q    <= '0;
    end else begin
      meta <= d;
      q    <= meta;
    end
  end
endmodule
