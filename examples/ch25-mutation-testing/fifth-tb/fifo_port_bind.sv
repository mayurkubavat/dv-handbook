// fifo_port_bind.sv -- the temporal-properties chapter's checker bound
// as fifo_bind.sv binds it, except that its count input is the
// checker's own occupancy counter instead of the design's register.
// Sync_A (occ == count) then holds by construction, and every other
// property judges the FIFO at its ports only. The fifth testbench
// built with this bind instead of fifo_bind.sv counts the kills made
// at the ports, apart from the white-box Sync_A. fifo_sva.sv is read
// by path and not edited.
bind fifo fifo_sva #(.DEPTH(DEPTH)) u_sva (
  .clk, .rst_n, .wr_en, .rd_en, .full, .empty,
  .count (u_sva.occ)
);
