// sby needs the reset applied by hand: assume PRESETn low in step 0, high after.
module wrap_reset(input logic clk, input logic rst_n);
  logic init = 1'b1;
  always @(posedge clk) init <= 1'b0;
  always @(posedge clk) begin
    if (init) assume (!rst_n); else assume (rst_n);
  end
endmodule
bind dma_v2 wrap_reset u_wr(.clk(PCLK), .rst_n(PRESETn));
