// dma_bind.sv -- attaches the AXI checker to the DMA by port name.
bind dma_v2 axil_master_sva u_axi_sva (
  .clk (PCLK), .rst_n (PRESETn),
  .arvalid (ARVALID), .arready (ARREADY), .araddr (ARADDR),
  .awvalid (AWVALID), .awready (AWREADY), .awaddr (AWADDR),
  .wvalid  (WVALID),  .wready  (WREADY),  .wdata  (WDATA)
);
