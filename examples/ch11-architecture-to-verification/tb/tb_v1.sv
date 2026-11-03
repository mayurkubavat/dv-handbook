// tb_v1.sv -- version 1 of the DMA in the testbench of Figure F11.
//
//   +test=directed   the 8-word copy the original testbench runs
//   +test=random     +n transfers: random lengths, addresses, response
//                    delays and injected errors, with coverage
//   +test=rate       one 64-word transfer, cycles per word printed
//   +test=<finding>  one spec question, asked of the RTL (see the
//                    findings example): len64k, busy_write, apb_read,
//                    ready_first (the slave holds READY before VALID),
//                    split_aw_w (AW and W accepted on different edges)
//   +report_only     print failed checks but exit 0
module tb_v1;
  import dma_regs_pkg::*;
  import dma_tb_pkg::*;

  logic clk = 0, rst_n = 0;
  always #5 clk = ~clk;

  apb_if  apb (clk);
  axil_if axi (clk);

  dma_engine dut (
    .PCLK(clk), .PRESETn(rst_n),
    .PSEL(apb.psel), .PENABLE(apb.penable), .PWRITE(apb.pwrite),
    .PADDR(apb.paddr), .PWDATA(apb.pwdata), .PRDATA(apb.prdata),
    .PREADY(apb.pready), .PSLVERR(apb.pslverr),
    .AWADDR(axi.awaddr), .AWVALID(axi.awvalid), .AWREADY(axi.awready),
    .WDATA(axi.wdata), .WSTRB(axi.wstrb), .WVALID(axi.wvalid),
    .WREADY(axi.wready), .BRESP(axi.bresp), .BVALID(axi.bvalid),
    .BREADY(axi.bready), .ARADDR(axi.araddr), .ARVALID(axi.arvalid),
    .ARREADY(axi.arready), .RDATA(axi.rdata), .RRESP(axi.rresp),
    .RVALID(axi.rvalid), .RREADY(axi.rready), .IRQ(apb.irq));

  // White-box coverage: the FSM's arcs, read from the microarchitecture
  // (Figure F6). Transition bins count consecutive states.
  covergroup fsm_cg @(posedge clk);
    st_cp: coverpoint dut.state iff (rst_n) {
      bins start      = (0 => 1);
      bins idle       = (0 => 0);      // also how a zero length ends
      bins ar_wait    = (1 => 1);
      bins ar_done    = (1 => 2);
      bins r_wait     = (2 => 2);
      bins r_ok       = (2 => 3);
      bins r_err      = (2 => 0);
      bins aw_wait    = (3 => 3);
      bins aw_done    = (3 => 4);
      bins b_wait     = (4 => 4);
      bins next_word  = (4 => 1);
      bins last_or_err = (4 => 0);
    }
  endgroup
  fsm_cg fsm_cov = new;

  dma_env env;

  // +vcd=<file> dumps a waveform (the binary must be built with --trace).
  string vcd;
  initial if ($value$plusargs("vcd=%s", vcd)) begin
    $dumpfile(vcd);
    $dumpvars(0, tb_v1);
  end
  string  test;

  // Version 1's PRDATA arrives one access late (the apb_read finding),
  // so the testbench reads STATUS twice and keeps the second answer.
  task automatic status_v1(output bit [31:0] s);
    env.rd(0, STATUS, s);
    env.rd(0, STATUS, s);
  endtask

  task automatic wait_irq(output bit timed_out);
    int unsigned n = 0;
    timed_out = 0;
    repeat (2) @(apb.cb);                // the old IRQ clears first
    while (!apb.cb.irq) begin
      @(apb.cb);
      if (++n > env.timeout) begin timed_out = 1; return; end
    end
  endtask

  // One transfer end to end: program, wait, check, sample coverage.
  task automatic transfer(bit [31:0] src, bit [31:0] dst,
                          longint unsigned len, outcome_e out, int pos);
    bit to;
    bit [31:0] s;
    longint t0;
    t0 = env.mon.cycle;
    env.start(0, src, dst, len);
    wait_irq(to);
    if (to) begin
      fail($sformatf("watchdog: no IRQ %0d cycles after start, %0d AR %s",
                     env.timeout, env.mon.n_ar, "handshakes so far"));
      return;
    end
    env.wait_quiet(4, to);
    status_v1(s);
    void'(env.sb.check_end(0, s));
    env.cov.xfer_cg.sample(32'(len), out, pos, env.mem.style);
    $display("  %0d words %08h -> %08h: STATUS %0h, %0d writes, %0d cycles",
             len, src, dst, s, env.sb.n_wr[0], env.mon.cycle - t0);
  endtask

  task automatic t_directed();
    for (int i = 0; i < 8; i++)
      env.mem.mem[32'h1000 + 4 * i] = 32'hDEAD0000 + i;
    transfer(32'h1000, 32'h2000, 8, OUT_OK, 0);
  endtask

  task automatic t_random();
    int unsigned n = 40;
    void'($value$plusargs("n=%d", n));
    env.mem.resp_delay = 3;
    for (int k = 0; k < int'(n); k++) begin
      bit [31:0] src, dst;
      int unsigned len, at;
      outcome_e out;
      int pos;
      randcase
        1: len = 0;
        2: len = 1;
        4: len = $urandom_range(2, 15);
        3: len = $urandom_range(16, 64);
      endcase
      src = 32'h0001_0000 + 32'(k) * 32'h400;
      dst = 32'h0010_0000 + 32'(k) * 32'h400;
      for (int i = 0; i < int'(len); i++)
        env.mem.mem[src + 4 * i] = $urandom;
      env.mem.rd_err.delete(); env.mem.wr_err.delete();
      out = OUT_OK; pos = 0;
      if (len > 0)
        randcase
          6: out = OUT_OK;
          2: out = OUT_RD_ERR;
          2: out = OUT_WR_ERR;
        endcase
      if (out != OUT_OK) begin
        randcase
          1: at = 0;
          1: at = len - 1;
          1: at = $urandom_range(len - 1);
        endcase
        pos = (at == 0) ? 0 : (at == len - 1) ? 2 : 1;
        if (out == OUT_RD_ERR) env.mem.rd_err[src + 4 * at] = 1;
        else                   env.mem.wr_err[dst + 4 * at] = 1;
      end
      transfer(src, dst, 64'(len), out, pos);
    end
  endtask

  task automatic t_rate();
    bit to;
    for (int i = 0; i < 64; i++) env.mem.mem[32'h1000 + 4 * i] = $urandom;
    env.start(0, 32'h1000, 32'h8000, 64);
    wait_irq(to);
    if (to) fail("watchdog: no IRQ");
    // From the first ARVALID to the last write response.
    $display("rate: 64 words in %0d cycles with a %s slave",
             env.mon.last_b - env.mon.first_ar + 1, env.mem.style.name());
  endtask

  // ---- The findings: each asks version 1 one question the spec ----
  // ---- left open, and prints what the RTL answers.             ----
  task automatic f_len64k();
    for (int i = 0; i < 4; i++) env.mem.mem[32'h1000 + 4 * i] = i + 1;
    transfer(32'h1000, 32'h2000, 65536, OUT_OK, 0);
    $display("finding len64k: XFER_LEN=65536 moved %0d words",
             env.sb.n_wr[0]);
  endtask

  task automatic f_busy_write();
    bit e;
    bit [31:0] v, s;
    bit to;
    env.mem.resp_delay = 2;
    env.start(0, 32'h1000, 32'h2000, 16);
    repeat (20) @(apb.cb);
    env.wr(0, DST_ADDR, 32'h9000, e);
    wait_irq(to);
    env.wait_quiet(4, to);
    status_v1(s);
    void'(env.sb.check_end(0, s));
    env.rd(0, DST_ADDR, v);
    env.rd(0, DST_ADDR, v);
    $display("finding busy_write: write while busy gave PSLVERR=%0d, %s",
             e, $sformatf("DST_ADDR reads %08h afterwards", v));
  endtask

  task automatic f_apb_read();
    bit e;
    bit [31:0] v;
    env.wr(0, SRC_ADDR, 32'h1111_1111, e);
    env.wr(0, DST_ADDR, 32'h2222_2222, e);
    env.rd(0, SRC_ADDR, v);
    $display("  read SRC_ADDR (holds 11111111): PRDATA %08h", v);
    if (v != 32'h1111_1111) fail("SRC_ADDR read back wrong");
    env.rd(0, DST_ADDR, v);
    $display("  read DST_ADDR (holds 22222222): PRDATA %08h", v);
    if (v != 32'h2222_2222) fail("DST_ADDR read back wrong");
    env.rd(0, XFER_LEN, v);
    $display("  read XFER_LEN (holds 00000000): PRDATA %08h", v);
    $display("finding apb_read: each read returns the previous one's data");
  endtask

  task automatic f_handshake();
    env.mem.mem[32'h1000] = 32'hCAFE_0001;
    transfer(32'h1000, 32'h2000, 1, OUT_OK, 0);
    $display("finding %s: ARVALID high for %0d cycles, %0d AR, %0d AW, %s",
             test, env.mon.arvalid_cycles, env.mon.n_ar, env.mon.n_aw,
             $sformatf("%0d W, %0d B handshakes", env.mon.n_w,
                       env.mon.n_b));
  endtask

  initial begin
    if (!$value$plusargs("test=%s", test)) test = "directed";
    env = new(apb, axi, 1, 0);
    env.mon.verbose = $test$plusargs("verbose");
    if (test == "ready_first") env.mem.style = READY_FIRST;
    if (test == "split_aw_w")  env.mem.style = W_FIRST;
    if (test == "len64k")      env.timeout = 600000;
    env.run();
    repeat (3) @(posedge clk);
    rst_n <= 1;
    repeat (2) @(apb.cb);
    $display("--- test %s, slave %s", test, env.mem.style.name());
    case (test)
      "directed": t_directed();
      "random":   t_random();
      "rate":     t_rate();
      "len64k":   f_len64k();
      "busy_write": f_busy_write();
      "apb_read": f_apb_read();
      "ready_first", "split_aw_w": f_handshake();
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
