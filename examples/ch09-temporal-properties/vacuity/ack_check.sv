// ack_check.sv -- "every request is acknowledged on the next tick",
// and the cover that says whether the rule was ever exercised.
module ack_check (
  input logic clk,
  input logic req,
  input logic ack
);
  logic started = 1'b0;                 // $past is meaningful from tick 1
  always @(posedge clk) started <= 1'b1;

  always @(posedge clk) begin
    if (started && $past(req)) Ack_A: assert (ack);
    Req_C: cover (started && $past(req));
  end
endmodule
