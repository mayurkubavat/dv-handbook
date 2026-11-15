// ack_check.sv -- "every request is acknowledged on the next tick",
// and the cover that says whether the rule was ever exercised. The
// responder has no reset, so neither property names one.
module ack_check (
  input logic clk,
  input logic req,
  input logic ack
);
  Ack_A: assert property (@(posedge clk) req |=> ack);
  Req_C: cover property (@(posedge clk) req);
endmodule
