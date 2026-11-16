// sanity.sv -- a free-running counter, a mode chosen by an input in
// the first cycle after reset, and a cycle count t that stops at 63.
// The script's assumptions end some or all traces early.
module sanity (
  input  logic       clk, rst_n, x,
  output logic [3:0] cnt
);
  logic       mode, chosen;
  logic [5:0] t;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      cnt <= '0; mode <= 1'b0; chosen <= 1'b0; t <= '0;
    end else begin
      cnt <= cnt + 4'd1;
      if (t != 6'd63) t <= t + 6'd1;
      if (!chosen) begin mode <= x; chosen <= 1'b1; end
    end
endmodule
