// racy.sv -- one variable, two processes, one clock edge.
//
// `count` is written by one process and read by another on the same edge of
// the same clock. Nothing here says which runs first, so what the reader
// sees is whichever value the simulator's ordering happens to produce.
//
// This is the design the chapter runs under two simulators. It is not a
// trick: it is the shape of a monitor sampling a signal a driver updates.
module racy (
  input  logic       clk,
  input  logic       rst_n,
  output logic [7:0] count,
  output logic [7:0] observed
);
  // Blocking assignment in a clocked block: the update is visible to
  // anything scheduled after it in the same region, which is the bug.
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) count = 8'h00;
    else        count = count + 8'd1;

  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) observed = 8'h00;
    else        observed = count;
endmodule
