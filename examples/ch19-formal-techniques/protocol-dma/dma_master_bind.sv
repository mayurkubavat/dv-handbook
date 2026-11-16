// dma_master_bind.sv -- hs_rules bound three times into the DMA of
// the architecture case study, as the sender on the AXI channels it
// drives (AR, AW, W): their rules are asserted. ANSWER = 0, since AXI
// lets ready come first.
bind dma_v2 hs_rules #(.W(32), .ROLE(hs_role_pkg::SENDER), .ANSWER(0))
  u_ar (.clk(PCLK), .rst_n(PRESETn), .valid(ARVALID),
        .ready(ARREADY), .data(ARADDR));
bind dma_v2 hs_rules #(.W(32), .ROLE(hs_role_pkg::SENDER), .ANSWER(0))
  u_aw (.clk(PCLK), .rst_n(PRESETn), .valid(AWVALID),
        .ready(AWREADY), .data(AWADDR));
bind dma_v2 hs_rules #(.W(32), .ROLE(hs_role_pkg::SENDER), .ANSWER(0))
  u_w (.clk(PCLK), .rst_n(PRESETn), .valid(WVALID),
       .ready(WREADY), .data(WDATA));
