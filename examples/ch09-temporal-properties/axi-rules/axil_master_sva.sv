// axil_master_sva.sv -- the two AXI rules a master must keep on each
// channel it drives, bound to the DMA.
//
//   held    once VALID is high it stays high until READY is seen
//   stable  the payload does not change while VALID waits
//
// The DMA drives three channels: read address, write address and
// write data. Each gets both rules and a cover of the waiting that
// makes the rules matter, up to the tick on which the rules are
// judged; a run in which VALID never waited has checked nothing here.
//
// The rules are written "waiting now implies ... on the next tick".
// The other spelling, "was waiting on the tick before implies ... now"
// with $past on the left, reads the tick before the first one, and a
// tool is free to disagree about what was there.
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
  ArHeld_A:   assert property (@(posedge clk) disable iff (!rst_n)
                arvalid && !arready |=> arvalid);
  ArStable_A: assert property (@(posedge clk) disable iff (!rst_n)
                arvalid && !arready |=> $stable(araddr));
  AwHeld_A:   assert property (@(posedge clk) disable iff (!rst_n)
                awvalid && !awready |=> awvalid);
  AwStable_A: assert property (@(posedge clk) disable iff (!rst_n)
                awvalid && !awready |=> $stable(awaddr));
  WHeld_A:    assert property (@(posedge clk) disable iff (!rst_n)
                wvalid && !wready |=> wvalid);
  WStable_A:  assert property (@(posedge clk) disable iff (!rst_n)
                wvalid && !wready |=> $stable(wdata));

  ArWait_C:   cover property (@(posedge clk) disable iff (!rst_n)
                arvalid && !arready ##1 1'b1);
  AwWait_C:   cover property (@(posedge clk) disable iff (!rst_n)
                awvalid && !awready ##1 1'b1);
  WWait_C:    cover property (@(posedge clk) disable iff (!rst_n)
                wvalid && !wready ##1 1'b1);

  // The third rule, "a master must not wait for READY before it raises
  // VALID", says that a trace exists. Its witness: VALID high on a
  // channel whose READY has not been high since reset.
  logic ar_r, aw_r, w_r;           // READY has been seen since reset
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) {ar_r, aw_r, w_r} <= '0;
    else begin
      ar_r <= ar_r || arready;
      aw_r <= aw_r || awready;
      w_r  <= w_r  || wready;
    end
  ArFirst_C:  cover property (@(posedge clk) disable iff (!rst_n)
                arvalid && !arready && !ar_r);
  AwFirst_C:  cover property (@(posedge clk) disable iff (!rst_n)
                awvalid && !awready && !aw_r);
  WFirst_C:   cover property (@(posedge clk) disable iff (!rst_n)
                wvalid && !wready && !w_r);
endmodule
