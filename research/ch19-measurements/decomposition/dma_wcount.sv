// dma_wcount.sv -- ghost state for an end-to-end property of channel
// 0 of the DMA: the length captured when the channel is started, and
// the number of write responses accepted since. Bound into dma_v2.
module dma_wcount (
  input  logic        clk, rst_n, start0, wgood0,
  input  logic [15:0] len_now,
  output logic [15:0] len0, wcnt0
);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      len0 <= '0; wcnt0 <= '0;
    end else if (start0) begin
      len0 <= len_now; wcnt0 <= '0;
    end else if (wgood0) begin
      wcnt0 <= wcnt0 + 16'd1;
    end
endmodule

// The start condition is the DMA's own: an accepted APB write of
// CTRL for channel 0 with the START bit set.
bind dma_v2 dma_wcount u_wc (
  .clk(PCLK), .rst_n(PRESETn),
  .start0(wr_ok && a_ch == 1'b0 && a_off == 5'(CTRL) && PWDATA[0]),
  .wgood0(wr_good[0]), .len_now(len[0]), .len0(), .wcnt0());
