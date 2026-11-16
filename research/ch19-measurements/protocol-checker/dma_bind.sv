// dma_bind.sv -- the same checker on the DMA: assertions on the three
// AXI channels it drives, assumptions on the two it receives.
module dma_vr;
endmodule
bind dma_v2 vr_rules #(.W(32), .ASSUME(0)) u_ar (.clk(PCLK),
  .rst_n(PRESETn), .valid(ARVALID), .ready(ARREADY), .data(ARADDR));
bind dma_v2 vr_rules #(.W(32), .ASSUME(0)) u_aw (.clk(PCLK),
  .rst_n(PRESETn), .valid(AWVALID), .ready(AWREADY), .data(AWADDR));
bind dma_v2 vr_rules #(.W(32), .ASSUME(0)) u_w (.clk(PCLK),
  .rst_n(PRESETn), .valid(WVALID), .ready(WREADY), .data(WDATA));
bind dma_v2 vr_rules #(.W(34), .ASSUME(1)) u_r (.clk(PCLK),
  .rst_n(PRESETn), .valid(RVALID), .ready(RREADY), .data({RRESP, RDATA}));
bind dma_v2 vr_rules #(.W(2), .ASSUME(1)) u_b (.clk(PCLK),
  .rst_n(PRESETn), .valid(BVALID), .ready(BREADY), .data(BRESP));
