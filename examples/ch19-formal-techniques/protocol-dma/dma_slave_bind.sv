// dma_slave_bind.sv -- hs_rules bound twice into the DMA of the
// architecture case study, as the receiver on the AXI channels it
// receives (R, B): their rules, rules on the slave, are assumed.
// ANSWER = 0, since AXI lets ready come first.
bind dma_v2 hs_rules #(.W(34), .ROLE(hs_role_pkg::RECEIVER), .ANSWER(0))
  u_r (.clk(PCLK), .rst_n(PRESETn), .valid(RVALID),
       .ready(RREADY), .data({RRESP, RDATA}));
bind dma_v2 hs_rules #(.W(2), .ROLE(hs_role_pkg::RECEIVER), .ANSWER(0))
  u_b (.clk(PCLK), .rst_n(PRESETn), .valid(BVALID),
       .ready(BREADY), .data(BRESP));
