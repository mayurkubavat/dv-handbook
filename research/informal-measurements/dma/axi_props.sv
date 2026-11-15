// The Chapter 9 AXI rules as concurrent assertions (clocked booleans with $past).
module axi_props (
  input logic        clk, rst_n,
  input logic        arvalid, arready, input logic [31:0] araddr,
  input logic        awvalid, awready, input logic [31:0] awaddr,
  input logic        wvalid, wready,   input logic [31:0] wdata);
  default clocking @(posedge clk); endclocking
  default disable iff (!rst_n);
  ArHeld_A:   assert property ($past(arvalid && !arready) |-> arvalid);
  ArStable_A: assert property ($past(arvalid && !arready) |-> araddr == $past(araddr));
  AwHeld_A:   assert property ($past(awvalid && !awready) |-> awvalid);
  AwStable_A: assert property ($past(awvalid && !awready) |-> awaddr == $past(awaddr));
  WHeld_A:    assert property ($past(wvalid && !wready) |-> wvalid);
  WStable_A:  assert property ($past(wvalid && !wready) |-> wdata == $past(wdata));
  ArWait_C:   cover property ($past(arvalid && !arready));
  AwWait_C:   cover property ($past(awvalid && !awready));
  WWait_C:    cover property ($past(wvalid && !wready));
endmodule
bind dma_v2 axi_props u_axi (
  .clk (PCLK), .rst_n (PRESETn),
  .arvalid (ARVALID), .arready (ARREADY), .araddr (ARADDR),
  .awvalid (AWVALID), .awready (AWREADY), .awaddr (AWADDR),
  .wvalid  (WVALID),  .wready  (WREADY),  .wdata  (WDATA));
