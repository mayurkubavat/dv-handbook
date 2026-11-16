// mul.sv -- a product computed two ways, for a miter.
// p_ref is the operator; p_arr adds one shifted copy of b for each
// set bit of a, the other operand order from the one a synthesis
// tool would use for p_ref. BUG = 1 drops the copy for bit 0 when
// the two top bits of a are both set, so only one case in four can
// show it.
module mul_miter #(parameter int W = 8, parameter bit BUG = 0) (
  input  logic           clk,
  input  logic [W-1:0]   a, b,
  output logic [2*W-1:0] p_ref, p_arr
);
  assign p_ref = a * b;
  always_comb begin
    p_arr = '0;
    for (int i = 0; i < W; i++)
      if (a[i] && !(BUG && i == 0 && a[W-1:W-2] == 2'b11))
        p_arr = p_arr + ((2*W)'(b) << i);
  end
endmodule
