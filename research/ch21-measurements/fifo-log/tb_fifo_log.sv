// tb_fifo_log.sv -- one run of the Chapter 1 FIFO under random push and
// pop, summarized on one line for the statistics experiments.
//
// The driver and monitor are those of the Chapter 8 coverage example
// (examples/ch08-functional-coverage/fifo-coverage/tb_fifo_cov.sv), with
// the covergroup replaced by plain counters so that the per-bin counts
// can be printed for Python to read. Plusargs: +n=<cycles>,
// +pw=<push percent>, +pr=<pop percent>.
//
// Output, one line:
//   RUN pw=<pw> pr=<pr> n=<n> exposed=<0|1> first=<cycle|-1> grid=<68>
// where grid is the hit count of each (occupancy 0..16, op) pair, op =
// {rd_en, wr_en}, in occupancy-major order, and exposed says whether a
// push was requested while the DUT showed full: the dropped push that
// the Chapter 1 scoreboard reports as a failure.
`timescale 1ns/1ps

module tb_fifo_log;
  logic       clk = 0;
  logic       rst_n;
  logic       wr_en, rd_en;
  logic [7:0] wr_data, rd_data;
  logic       full, empty;
  int         n, pw, pr, cyc, first;
  int         grid[17][4];
  bit [4:0]   occ;
  bit         done;

  fifo dut (.clk, .rst_n, .wr_en, .wr_data, .rd_en, .rd_data, .full,
            .empty);

  always #5 clk <= ~clk;

  task automatic drive(int cycles);
    repeat (cycles) begin
      @(negedge clk);
      wr_en   <= ($urandom_range(99) < pw);
      rd_en   <= ($urandom_range(99) < pr);
      wr_data <= 8'($urandom);
    end
  endtask

  task automatic monitor();
    forever begin
      @(posedge clk);
      if (rst_n && !done) begin
        grid[occ][{rd_en, wr_en}]++;
        if (wr_en && full && first < 0) first = cyc;
        if (wr_en && !full) occ++;
        if (rd_en && !empty) occ--;
        cyc++;
      end
    end
  endtask

  initial begin
    string s;
    if (!$value$plusargs("n=%d", n)) n = 200;
    if (!$value$plusargs("pw=%d", pw)) pw = 50;
    if (!$value$plusargs("pr=%d", pr)) pr = 50;
    first = -1; cyc = 0; occ = 0;
    rst_n = 0; wr_en = 0; rd_en = 0; wr_data = 0;
    fork monitor(); join_none
    repeat (2) @(posedge clk);
    rst_n <= 1;
    drive(n);
    @(negedge clk);
    wr_en <= 0; rd_en <= 0; done = 1;
    @(posedge clk);
    s = "";
    for (int o = 0; o < 17; o++)
      for (int k = 0; k < 4; k++)
        s = {s, $sformatf("%0d%s", grid[o][k],
                          (o == 16 && k == 3) ? "" : ",")};
    $display("RUN pw=%0d pr=%0d n=%0d exposed=%0d first=%0d grid=%s",
             pw, pr, n, first >= 0, first, s);
    $finish;
  end
endmodule
