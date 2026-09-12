// tb_fifo_env.sv -- build the environment once, then run the three tests.
//
// Each test is a few lines of construction: which maker, which driver,
// which callback. The environment's own classes are never touched.
module tb_fifo_env;
  localparam int N = 6;
  logic clk = 0;
  always #5 clk <= ~clk;
  fifo_if #(.WIDTH(8)) bus (.clk);
  fifo #(.WIDTH(8), .DEPTH(4)) dut (
    .clk, .rst_n(bus.rst_n), .wr_en(bus.wr_en), .wr_data(bus.wr_data),
    .rd_en(bus.rd_en), .rd_data(bus.rd_data), .full(bus.full),
    .empty(bus.empty));

  driver     drv;
  scoreboard sb;

  task reset();
    bus.cb.rst_n <= 0; bus.cb.wr_en <= 0; bus.cb.rd_en <= 0;
    bus.cb.wr_data <= 0;
    repeat (2) @(bus.cb);
    bus.cb.rst_n <= 1;
  endtask

  task run_test(string name);
    sb = new; sb.vif = bus;
    drv.vif = bus;
    if (drv.maker == null) drv.maker = new;
    reset();
    fork
      drv.run(N);
      sb.run(N, drv.sent);
    join
    $display("%-9s %0d packets, %0d errors, last sent: %s", name, sb.seen,
             sb.errors, drv.sent.size() != 0 ? "leftover" : "all checked");
  endtask

  initial begin
    // test 1: factory -- a derived packet, substituted by the maker
    begin
      even_maker m = new;
      drv = new; drv.maker = m;
      run_test("factory");
    end
    // test 2: strategy -- a derived driver, one hook overridden
    begin
      inverting_driver d = new;
      drv = d;
      run_test("strategy");
    end
    // test 3: callback -- a hook object the driver only calls
    begin
      counting_cb c = new;
      drv = new; drv.cb = c;
      run_test("callback");
      $display("          callback counted kinds: %p", c.by_kind);
    end
    $finish;
  end
endmodule
