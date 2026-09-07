// gated_clock.sv -- a clock gate, which must not become a second domain.
//
// q_gated runs on clk with an enable in its clock path. A walk that treats
// the gate's enable as a clock source puts q_gated in a domain of its own
// and then reports the ordinary synchronous path into it as a crossing.
module gated_clock (
  input  logic clk,
  input  logic rst_n,
  input  logic en,
  input  logic d,
  output logic q_free,
  output logic q_gated
);
  logic gclk;
  assign gclk = clk & en;

  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) q_free <= 1'b0;
    else        q_free <= d;

  always_ff @(posedge gclk or negedge rst_n)
    if (!rst_n) q_gated <= 1'b0;
    else        q_gated <= q_free;
endmodule
