// One register, asynchronously loaded, with no reset at all. An
// asynchronous load forces another signal's value rather than a constant,
// so it is not a reset -- and the human report said the design had no
// unreset registers when its only register had none.
module async_load_only (
    input  logic clk,
    input  logic ld,
    input  logic [7:0] d,
    input  logic [7:0] v,
    output logic [7:0] q
);
  logic [7:0] r;

  always_ff @(posedge clk or posedge ld)
    if (ld) r <= v;
    else    r <= d;

  assign q = r;
endmodule
