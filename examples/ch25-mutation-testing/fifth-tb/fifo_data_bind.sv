// fifo_data_bind.sv -- attaches the data check to every instance of
// fifo, beside the temporal-properties chapter's own bind, which is
// read by path and not edited.
bind fifo fifo_data_sva #(.WIDTH(WIDTH)) u_data (
  .clk, .rst_n, .wr_en, .rd_en, .full, .empty, .wr_data, .rd_data
);
