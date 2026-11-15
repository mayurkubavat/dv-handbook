// axil_master_sva.sv -- the two AXI rules a master must keep on each
// channel it drives, bound to the DMA.
//
//   held    once VALID is high it stays high until READY is seen
//   stable  the payload does not change while VALID waits
//
// The DMA drives three channels: read address, write address and
// write data. Each gets both rules and a cover of the waiting that
// makes the rules matter; a run in which VALID never waited has
// checked nothing here. Clocked immediate assertions with $past only.
module axil_master_sva (
  input logic        clk,
  input logic        rst_n,
  input logic        arvalid, arready,
  input logic [31:0] araddr,
  input logic        awvalid, awready,
  input logic [31:0] awaddr,
  input logic        wvalid, wready,
  input logic [31:0] wdata
);
  // One register per channel: VALID was waiting on the tick before.
  logic ar_w, aw_w, w_w;
  always @(posedge clk or negedge rst_n)
    if (!rst_n) {ar_w, aw_w, w_w} <= '0;
    else begin
      ar_w <= arvalid && !arready;
      aw_w <= awvalid && !awready;
      w_w  <= wvalid  && !wready;
    end

  always @(posedge clk) if (rst_n) begin
    if (ar_w) ArHeld_A:   assert (arvalid);
    if (ar_w) ArStable_A: assert (araddr == $past(araddr));
    if (aw_w) AwHeld_A:   assert (awvalid);
    if (aw_w) AwStable_A: assert (awaddr == $past(awaddr));
    if (w_w)  WHeld_A:    assert (wvalid);
    if (w_w)  WStable_A:  assert (wdata == $past(wdata));
    ArWait_C: cover (ar_w);
    AwWait_C: cover (aw_w);
    WWait_C:  cover (w_w);
  end
endmodule
