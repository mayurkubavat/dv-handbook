// Two modules that each declare an array called `mem`. Ordinary RTL, and
// the shape that defeated the first version of the location fix: the two
// arrays were one ambiguous key, the location was dropped rather than
// guessed at, and the registers fell through to the *top* module's
// declaration -- a location in a different module from the array it named,
// well formed enough to pass every check in the suite.
module two_arrays_a (
    input  logic clk,
    input  logic [3:0] a,
    output logic [7:0] q
);
  logic [7:0] mem [16];
  always_ff @(posedge clk) mem[a] <= 8'hAA;
  always_ff @(posedge clk) q <= mem[a];
endmodule

module two_arrays_b (
    input  logic clk,
    input  logic [3:0] a,
    output logic [7:0] q
);
  logic [7:0] mem [16];
  always_ff @(posedge clk) mem[a] <= 8'hBB;
  always_ff @(posedge clk) q <= mem[a];
endmodule

module two_arrays_one_name (
    input  logic clk,
    input  logic [3:0] a,
    output logic [7:0] q1,
    output logic [7:0] q2
);
  two_arrays_a u_a (.clk(clk), .a(a), .q(q1));
  two_arrays_b u_b (.clk(clk), .a(a), .q(q2));
endmodule
