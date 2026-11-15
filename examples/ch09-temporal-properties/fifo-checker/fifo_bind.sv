// fifo_bind.sv -- attaches the checker to every instance of fifo. The
// port connections are resolved inside the fifo, which is how count,
// a register the design does not export, reaches the checker.
bind fifo fifo_sva #(.DEPTH(DEPTH)) u_sva (
  .clk, .rst_n, .wr_en, .rd_en, .full, .empty,
  .count (5'(count))
);
