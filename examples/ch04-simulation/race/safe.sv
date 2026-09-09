// safe.sv -- the same design with the race removed.
//
// The only change is the assignment operator. A non-blocking assignment
// evaluates its right side when the statement runs and updates the variable
// later, in a region of its own, so neither process can see the other's
// update within this timestep. Both simulators now agree, and they agree on
// the answer the hardware would give.
module safe (
  input  logic       clk,
  input  logic       rst_n,
  output logic [7:0] count,
  output logic [7:0] observed
);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) count <= 8'h00;
    else        count <= count + 8'd1;

  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) observed <= 8'h00;
    else        observed <= count;
endmodule
