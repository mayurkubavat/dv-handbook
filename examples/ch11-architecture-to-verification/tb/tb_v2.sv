// tb_v2.sv -- version 2, two channels, in the same testbench.
//
//   +test=directed   eight words on channel 0, then on channel 1
//   +test=regs       the register rules of the version 2 spec
//   +test=random     +n rounds: both channels at once, random lengths,
//                    errors, response delays and slave ready styles
//   +test=rate       one 64-word transfer, cycles per word printed
//   +test=abort      a read error on word 2 of 4, for the waveform
//   +test=maxlen     one 65535-word copy, the longest XFER_LEN allows
//   +report_only     print failed checks but exit 0
//   -GPRECISE=0      build the draft that dropped words on a read error
module tb_v2 #(parameter bit PRECISE = 1);
  import dma_regs_pkg::*;
  import dma_tb_pkg::*;

  logic clk = 0, rst_n = 0;
  always #5 clk = ~clk;

  apb_if  apb (clk);
  axil_if axi (clk);

  dma_v2 #(.PRECISE(PRECISE)) dut (
    .PCLK(clk), .PRESETn(rst_n),
    .PSEL(apb.psel), .PENABLE(apb.penable), .PWRITE(apb.pwrite),
    .PADDR(apb.paddr), .PWDATA(apb.pwdata), .PRDATA(apb.prdata),
    .PREADY(apb.pready), .PSLVERR(apb.pslverr),
    .ARADDR(axi.araddr), .ARVALID(axi.arvalid), .ARREADY(axi.arready),
    .RDATA(axi.rdata), .RRESP(axi.rresp[1:0]), .RVALID(axi.rvalid),
    .RREADY(axi.rready), .AWADDR(axi.awaddr), .AWVALID(axi.awvalid),
    .AWREADY(axi.awready), .WDATA(axi.wdata), .WSTRB(axi.wstrb[3:0]),
    .WVALID(axi.wvalid), .WREADY(axi.wready), .BRESP(axi.bresp[1:0]),
    .BVALID(axi.bvalid), .BREADY(axi.bready), .IRQ(apb.irq));
  assign axi.wstrb[31:4] = '0;

  // White-box coverage from the microarchitecture (the block diagram):
  // FIFO occupancy while both channels run, and the case precise errors
  // exist for: a read error that finds words of its own channel still
  // in the FIFO. rd_bad is a one-cycle pulse, so each bin counts events.
  covergroup uarch_cg @(posedge clk);
    fifo_cp: coverpoint dut.f_cnt iff (rst_n) {
      bins empty = {0}; bins one = {1}; bins full = {2};
    }
    both_cp: coverpoint (dut.busy == 2'b11) iff (rst_n) {
      bins one_ch = {0}; bins both = {1};
    }
    fifo_x_both: cross fifo_cp, both_cp;
    rd_err_cp: coverpoint {dut.rd_bad[1] && dut.in_fifo[1] != 0,
                           dut.rd_bad[0] && dut.in_fifo[0] != 0}
               iff (rst_n) {
      bins queued = {2'b01, 2'b10};
    }
  endgroup
  uarch_cg uarch_cov = new;

  // Arbitration check: a read whose address was granted while both
  // channels were running and owed reads must not be the second in a
  // row for its channel. The grant is the edge before ARVALID is first
  // seen; a channel runs from the edge after its start write.
  // Channels are told apart by address window.
  class arb_checker extends axil_subscriber;
    int     left [2];
    longint since [2] = '{0, 0};
    int     last = -1, runs = 0, repeats = 0, grants [2];
    virtual function void observe(axil_txn t);
      int c;
      bit both;
      if (t.wr || !t.ok) return;
      c = t.addr[20] ? 1 : 0;              // ch1's source is 0x10_0000 up
      both = left[0] > 0 && left[1] > 0 && t.acycle > since[0] + 1 &&
             t.acycle > since[1] + 1;
      if (both && c == last) begin
        repeats++;
        fail($sformatf("arbiter: ch%0d read twice in a row at %08h", c,
                       t.addr));
      end
      if (both) begin
        runs++; grants[c]++;
      end
      if (left[c] > 0) left[c]--;
      last = c;
    endfunction
  endclass

  dma_env     env;

  // No read may be issued while the FIFO is full (plan item DMA-102).
  // Sampled on the falling edge: ARVALID as the last rising edge left
  // it, and the FIFO count the read engine saw at that edge.
  bit arv_q = 0;
  int fcnt_q = 0, full_reads = 0;
  initial forever begin
    @(negedge clk);
    if (rst_n && dut.ARVALID && !arv_q && fcnt_q >= 2) begin
      full_reads++;
      fail("read issued while the FIFO was full");
    end
    arv_q = dut.ARVALID; fcnt_q = int'(dut.f_cnt);
  end

  // +vcd=<file> dumps a waveform (the binary must be built with --trace).
  string vcd;
  initial if ($value$plusargs("vcd=%s", vcd)) begin
    $dumpfile(vcd);
    $dumpvars(0, tb_v2);
  end
  arb_checker arb;
  string      test;

  task automatic expect_reg(int ch, int off, bit [31:0] want, string what);
    bit [31:0] v;
    env.rd(ch, off, v);
    if (v != want)
      fail($sformatf("%s: read %08h, spec says %08h", what, v, want));
  endtask

  task automatic expect_err(int ch, int off, bit [31:0] v, bit want,
                            string what);
    bit e;
    env.wr(ch, off, v, e);
    if (e != want)
      fail($sformatf("%s: PSLVERR=%0d, spec says %0d", what, e, want));
  endtask

  // Wait for a channel, check it against the model, clear its status.
  task automatic finish(int ch, output bit [31:0] s);
    bit to, e;
    env.wait_idle(ch, s, to);
    if (to) fail($sformatf("watchdog: ch%0d still busy", ch));
    void'(env.sb.check_end(ch, s));
    env.wr(ch, STATUS, STATUS_DONE | STATUS_ERROR, e);
  endtask

  task automatic fill(bit [31:0] src, int unsigned len);
    for (int i = 0; i < int'(len); i++) env.mem.mem[src + 4 * i] = $urandom;
  endtask

  task automatic t_directed();
    bit [31:0] s;
    for (int ch = 0; ch < 2; ch++) begin
      fill(32'h1000 + 32'(ch) * 32'h10_0000, 8);
      env.start(ch, 32'h1000 + 32'(ch) * 32'h10_0000, 32'h8000 + 32'(ch) *
                32'h10_0000, 8);
      finish(ch, s);
      $display("  ch%0d: 8 words, STATUS %0h, %0d writes", ch, s,
               env.sb.n_wr[ch]);
    end
  endtask

  task automatic t_regs();
    bit [31:0] s;
    expect_reg(0, XFER_LEN, 0, "LEN after reset");
    expect_err(0, SRC_ADDR, 32'h0000_1003, 0, "SRC write while idle");
    expect_reg(0, SRC_ADDR, 32'h0000_1000, "SRC low bits read as zero");
    expect_err(0, XFER_LEN, 32'hABCD_0010, 0, "LEN write while idle");
    expect_reg(0, XFER_LEN, 32'h0000_0010, "LEN upper bits read as zero");
    expect_err(0, 32'h14, 0, 1, "unmapped offset 0x14");
    expect_err(2, SRC_ADDR, 0, 1, "channel 2 does not exist");
    fill(32'h1000, 16);
    env.mem.resp_delay = 2;
    env.start(0, 32'h1000, 32'h8000, 16);
    repeat (6) @(apb.cb);
    expect_reg(0, STATUS, STATUS_BUSY, "STATUS while running");
    expect_err(0, DST_ADDR, 32'h9000, 1, "DST write while busy");
    expect_err(0, CTRL, CTRL_START, 1, "start while busy");
    expect_err(1, DST_ADDR, 32'h9000, 0, "ch1 write while ch0 busy");
    expect_reg(0, DST_ADDR, 32'h8000, "DST unchanged by refused write");
    expect_reg(0, CTRL, CTRL_IRQ_EN, "CTRL start reads as zero");
    finish(0, s);
    expect_reg(0, STATUS, 0, "STATUS after write-one-to-clear");
    if (apb.irq) fail("IRQ still high after STATUS was cleared");
    $display("  %0d register rules checked", 15);
  endtask

  task automatic t_random();
    int unsigned n = 30;
    void'($value$plusargs("n=%d", n));
    for (int k = 0; k < int'(n); k++) begin
      bit [31:0] src [2], dst [2], s;
      int unsigned len [2], at;
      outcome_e out [2];
      int pos [2];
      env.mem.style = ready_style_e'($urandom_range(3));  // all four
      env.mem.resp_delay = $urandom_range(2);
      env.mem.rd_err.delete(); env.mem.wr_err.delete();
      for (int c = 0; c < 2; c++) begin
        randcase
          1: len[c] = 0;
          2: len[c] = 1;
          4: len[c] = $urandom_range(2, 15);
          3: len[c] = $urandom_range(16, 48);
        endcase
        src[c] = 32'h0001_0000 + 32'(c) * 32'h10_0000 + 32'(k) * 32'h400;
        dst[c] = 32'h0008_0000 + 32'(c) * 32'h10_0000 + 32'(k) * 32'h400;
        fill(src[c], len[c]);
        out[c] = OUT_OK; pos[c] = 0;
        if (len[c] > 0)
          randcase
            6: out[c] = OUT_OK;
            2: out[c] = OUT_RD_ERR;
            2: out[c] = OUT_WR_ERR;
          endcase
        if (out[c] != OUT_OK) begin
          randcase
            1: at = 0;
            1: at = len[c] - 1;
            1: at = $urandom_range(len[c] - 1);
          endcase
          pos[c] = (at == 0) ? 0 : (at == len[c] - 1) ? 2 : 1;
          if (out[c] == OUT_RD_ERR) env.mem.rd_err[src[c] + 4 * at] = 1;
          else                      env.mem.wr_err[dst[c] + 4 * at] = 1;
        end
      end
      arb.left = '{0, 0};
      arb.last = -1;
      for (int c = 0; c < 2; c++) begin
        env.start(c, src[c], dst[c], 64'(len[c]));
        // Counted from the start, so a channel competes once it runs.
        arb.left[c] = out[c] == OUT_OK ? int'(len[c]) : 0;
        arb.since[c] = env.mon.cycle;
      end
      for (int c = 0; c < 2; c++) begin
        finish(c, s);
        env.cov.xfer_cg.sample(len[c], out[c], pos[c], env.mem.style);
      end
    end
    $display("  %0d rounds, both channels each round; %0d reads while %s",
             n, arb.runs, $sformatf("both owed: ch0 %0d, ch1 %0d",
             arb.grants[0], arb.grants[1]));
    $display("  same channel twice in a row: %0d; reads at a full FIFO: %0d",
             arb.repeats, full_reads);
  endtask

  // A read error on the third of four words: the two before it must
  // reach the destination and nothing after it may (precise errors).
  task automatic t_abort();
    bit [31:0] s;
    fill(32'h1000, 4);
    env.mem.resp_delay = 0;
    env.mem.rd_err[32'h1008] = 1;
    env.start(0, 32'h1000, 32'h8000, 4);
    finish(0, s);
    $display("  read error at word 2 of 4: STATUS %0h, %0d writes", s,
             env.sb.n_wr[0]);
  endtask

  // The longest transfer the register allows (plan item DMA-009).
  task automatic t_maxlen();
    bit [31:0] s;
    fill(32'h0010_0000, 65535);
    env.mem.resp_delay = 0;
    env.timeout = 600000;
    env.start(0, 32'h0010_0000, 32'h0080_0000, 65535);
    finish(0, s);
    env.cov.xfer_cg.sample(65535, OUT_OK, 0, env.mem.style);
    $display("  65535 words: STATUS %0h, %0d writes", s, env.sb.n_wr[0]);
  endtask

  task automatic t_rate();
    bit [31:0] s;
    fill(32'h1000, 64);
    env.start(0, 32'h1000, 32'h8000, 64, 0);
    finish(0, s);
    // From the first ARVALID to the last write response.
    $display("rate: 64 words in %0d cycles with a %s slave",
             env.mon.last_b - env.mon.first_ar + 1, env.mem.style.name());
  endtask

  initial begin
    if (!$value$plusargs("test=%s", test)) test = "directed";
    env = new(apb, axi, 2, CH_STRIDE);
    arb = new;
    env.mon.subs.push_back(arb);
    env.mon.verbose = $test$plusargs("verbose");
    if ($test$plusargs("ready_first")) env.mem.style = READY_FIRST;
    env.run();
    repeat (3) @(posedge clk);
    rst_n <= 1;
    repeat (2) @(apb.cb);
    $display("--- test %s", test);
    case (test)
      "directed": t_directed();
      "regs":     t_regs();
      "random":   t_random();
      "rate":     t_rate();
      "abort":    t_abort();
      "maxlen":   t_maxlen();
      default:    $fatal(1, "unknown +test=%s", test);
    endcase
    $display("AXI handshakes: AR %0d, R %0d, AW %0d, W %0d, B %0d",
             env.mon.n_ar, env.mon.n_r, env.mon.n_aw, env.mon.n_w,
             env.mon.n_b);
    if (errors == 0) $display("result: PASS");
    else             $display("result: FAIL, %0d checks failed", errors);
    if (errors != 0 && !$test$plusargs("report_only")) $fatal(1);
    $finish;
  end
endmodule
