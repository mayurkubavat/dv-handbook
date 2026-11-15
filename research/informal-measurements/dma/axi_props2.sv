// The AXI rules in two spellings that do not look back into the reset cycle.
module axi_props2 (
  input logic        clk, rst_n,
  input logic        arvalid, arready, input logic [31:0] araddr,
  input logic        awvalid, awready, input logic [31:0] awaddr,
  input logic        wvalid, wready,   input logic [31:0] wdata);
  default clocking @(posedge clk); endclocking
  default disable iff (!rst_n);
  // (a) next-cycle implication
  ArHeld_A:   assert property (arvalid && !arready |=> arvalid);
  ArStable_A: assert property (arvalid && !arready |=> $stable(araddr));
  AwHeld_A:   assert property (awvalid && !awready |=> awvalid);
  AwStable_A: assert property (awvalid && !awready |=> $stable(awaddr));
  WHeld_A:    assert property (wvalid && !wready |=> wvalid);
  WStable_A:  assert property (wvalid && !wready |=> $stable(wdata));
  // (b) the book's waiting register, reset with the design
  logic ar_w;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) ar_w <= 1'b0; else ar_w <= arvalid && !arready;
  ArHeld_reg_A:   assert property (ar_w |-> arvalid);
  ArStable_reg_A: assert property (ar_w |-> araddr == $past(araddr));
  ArWait_C:   cover property (ar_w);
  AwWait_C:   cover property (awvalid && !awready ##1 1'b1);
  WWait_C:    cover property (wvalid && !wready ##1 1'b1);
endmodule
bind dma_v2 axi_props2 u_axi (
  .clk (PCLK), .rst_n (PRESETn),
  .arvalid (ARVALID), .arready (ARREADY), .araddr (ARADDR),
  .awvalid (AWVALID), .awready (AWREADY), .awaddr (AWADDR),
  .wvalid  (WVALID),  .wready  (WREADY),  .wdata  (WDATA));
