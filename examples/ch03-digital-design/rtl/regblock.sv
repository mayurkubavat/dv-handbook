// regblock.sv -- two registers on the bus clock, written through a
// one-bit address: 0 = enable, 1 = configuration value.
module regblock (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       wr_en,
  input  logic       wr_addr,
  input  logic [7:0] wr_data,
  output logic       en,
  output logic [7:0] cfg
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      en  <= 1'b0;
      cfg <= 8'h00;
    end else if (wr_en) begin
      if (wr_addr == 1'b0) en  <= wr_data[0];
      else                 cfg <= wr_data;
    end
  end
endmodule
