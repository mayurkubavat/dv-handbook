// The crossing arrives on a synchronous reset, not on a data pin. Yosys
// folds the reset term into $sdff, so a walk that reads a fixed list of
// data ports never sees it.
module sync_reset_crossing (
    input  logic clk_a,
    input  logic clk_b,
    input  logic flag_in,
    input  logic [7:0] din,
    output logic [7:0] dout
);
  logic flag;

  always_ff @(posedge clk_a)
    flag <= flag_in;

  always_ff @(posedge clk_b)
    if (flag) dout <= 8'h00;   // clk_a's flag, sampled by clk_b
    else      dout <= din;
endmodule
