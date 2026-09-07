// datapath.sv -- counts while enabled and accumulates the configuration
// value on the core clock. last_cfg deliberately has no reset: the
// specification says its value is don't-care until the first enable.
module datapath (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       en,
  input  logic [7:0] cfg,
  output logic [7:0] count,
  output logic [7:0] acc,
  output logic [7:0] last_cfg   // debug view; no reset by specification
);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      count <= 8'h00;
      acc   <= 8'h00;
    end else if (en) begin
      count <= count + 8'd1;
      acc   <= acc + cfg;
    end
  end

  always_ff @(posedge clk) begin
    if (en) last_cfg <= cfg;
  end
endmodule
