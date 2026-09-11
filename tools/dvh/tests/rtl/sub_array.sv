// An array inside a submodule, so the registers it becomes carry the
// instance path as well as the array's name. The location those registers
// report has to survive flattening: it is recovered from a picture of the
// design taken before the memory passes ran, and the cell names in the
// flattened netlist are prefixed with `u_store.`.
module sub_array_store (
    input  logic clk,
    input  logic we,
    input  logic [3:0] a,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic [7:0] ram [16];
  always_ff @(posedge clk) if (we) ram[a] <= d;
  always_ff @(posedge clk) q <= ram[a];
endmodule

module sub_array (
    input  logic clk,
    input  logic we,
    input  logic [3:0] a,
    input  logic [7:0] d,
    output logic [7:0] q
);
  sub_array_store u_store (.clk(clk), .we(we), .a(a), .d(d), .q(q));
endmodule
