// tb_packet_stream.sv -- 64 constrained packets through the FIFO, checked
// by the scoreboard, counted by the callback, replayable by seed.
module tb_packet_stream;
  localparam int N = 64;
  logic clk = 0;
  always #5 clk <= ~clk;
  fifo_if #(.WIDTH(8)) bus (.clk);
  fifo #(.WIDTH(8), .DEPTH(4)) dut (
    .clk, .rst_n(bus.rst_n), .wr_en(bus.wr_en), .wr_data(bus.wr_data),
    .rd_en(bus.rd_en), .rd_data(bus.rd_data), .full(bus.full),
    .empty(bus.empty));

  driver       drv;
  scoreboard   sb;
  random_maker maker;
  histogram_cb hist;

  initial begin
    bus.cb.rst_n <= 0; bus.cb.wr_en <= 0; bus.cb.rd_en <= 0;
    bus.cb.wr_data <= 0;
    repeat (2) @(bus.cb);
    bus.cb.rst_n <= 1;

    drv = new; sb = new; maker = new; hist = new;
    drv.vif = bus; sb.vif = bus; drv.maker = maker; drv.cb = hist;
    fork
      drv.run(N);
      sb.run(N, drv.sent);
    join
    $display("%0d packets, %0d errors; kinds 0:%0d 1:%0d 2:%0d 3:%0d",
             sb.seen, sb.errors, hist.by_kind[0], hist.by_kind[1],
             hist.by_kind[2], hist.by_kind[3]);
    $finish;
  end
endmodule
