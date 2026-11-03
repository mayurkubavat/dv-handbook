// dma_tb_pkg.sv -- the testbench the chapter draws, one class per box.
//
//   apb_master   programs the DMA as software would, APB3 timing
//   axil_slave   memory on the AXI4-Lite side, with three ready styles
//                and per-address error injection
//   axil_monitor watches the AXI pins, checks the handshake rules, and
//                hands every completed read and write to its subscribers
//   dma_model    the reference model: what the *specification* says a
//                transfer must do, predicted before it runs
//   dma_scoreboard  compares what the monitor saw with what the model
//                predicted, word by word and channel by channel
//   dma_coverage the plan's cover points for one finished transfer
//   dma_env      builds and connects the rest; tests talk to it
package dma_tb_pkg;
  import dma_regs_pkg::*;

  typedef enum {WAIT_VALID, READY_FIRST, RANDOM, W_FIRST} ready_style_e;
  typedef enum {OUT_OK, OUT_RD_ERR, OUT_WR_ERR} outcome_e;
  localparam int RESP_SLVERR = 2;        // what the memory answers on error

  int unsigned errors;                   // every failed check adds one
  function automatic void fail(string msg);
    errors++;
    $display("  FAIL: %s", msg);
  endfunction

  // ==================================================================
  class apb_master;
    virtual apb_if vif;
    function new(virtual apb_if v);
      vif = v;
    endfunction
    task reset();
      vif.psel <= 0; vif.penable <= 0; vif.pwrite <= 0;
      vif.paddr <= 0; vif.pwdata <= 0;
    endtask
    // One transfer: a setup cycle, then access cycles until PREADY.
    // PRDATA and PSLVERR are taken at the edge that ends the access,
    // which is where APB3 says a master samples them.
    task automatic xfer(bit wr, bit [31:0] addr, bit [31:0] wdata,
                        output bit [31:0] rdata, output bit slverr);
      vif.psel <= 1; vif.penable <= 0; vif.pwrite <= wr;
      vif.paddr <= addr; vif.pwdata <= wdata;
      @(vif.cb) vif.penable <= 1;
      do @(vif.cb); while (!vif.cb.pready);
      rdata = vif.cb.prdata;
      slverr = vif.cb.pslverr;
      vif.psel <= 0; vif.penable <= 0;
    endtask
    task automatic write(bit [31:0] addr, bit [31:0] data,
                         output bit slverr);
      bit [31:0] unused;
      xfer(1, addr, data, unused, slverr);
    endtask
    task automatic read(bit [31:0] addr, output bit [31:0] data);
      bit slverr;
      xfer(0, addr, 0, data, slverr);
    endtask
  endclass

  // ==================================================================
  class axil_slave;
    virtual axil_if vif;
    ready_style_e style = WAIT_VALID;
    int unsigned  resp_delay = 0;        // up to this many idle cycles
    int unsigned  ready_pct  = 50;       // RANDOM: chance of READY high
    bit [31:0]    mem    [bit [31:0]];
    bit           rd_err [bit [31:0]];   // addresses answered SLVERR
    bit           wr_err [bit [31:0]];

    function new(virtual axil_if v);
      vif = v;
    endfunction
    function bit [31:0] peek(bit [31:0] a);
      return mem.exists(a) ? mem[a] : 32'h0;
    endfunction
    // WAIT_VALID raises READY the cycle after it sees VALID; READY_FIRST
    // holds READY high before any VALID, which AXI allows; RANDOM picks;
    // W_FIRST is WAIT_VALID, except that AWREADY waits for the W
    // handshake, so the two land on different edges, as AXI allows.
    function bit ready(bit valid);
      case (style)
        WAIT_VALID, W_FIRST: return valid;
        READY_FIRST: return 1;
        default:     return $urandom_range(99) < ready_pct;
      endcase
    endfunction
    task run();
      vif.arready <= 0; vif.rvalid <= 0; vif.rdata <= 0; vif.rresp <= 0;
      vif.awready <= 0; vif.wready <= 0; vif.bvalid <= 0; vif.bresp <= 0;
      fork
        read_side();
        write_side();
      join_none
    endtask

    task read_side();
      int st = 0, n = 0;
      bit [31:0] a;
      forever begin
        @(vif.cb);
        case (st)
          0: if (vif.cb.arvalid && vif.cb.arready) begin
               a = vif.cb.araddr; vif.arready <= 0;
               n = $urandom_range(resp_delay); st = 1;
             end else vif.arready <= ready(vif.cb.arvalid);
          2: if (vif.cb.rready) begin
               vif.rvalid <= 0; vif.arready <= ready(0); st = 0;
             end
          default: ;
        endcase
        if (st == 1) begin
          if (n == 0) begin
            vif.rdata <= peek(a);
            vif.rresp <= rd_err.exists(a) ? RESP_SLVERR : RESP_OKAY;
            vif.rvalid <= 1; st = 2;
          end else n--;
        end
      end
    endtask

    // The address and data handshakes are taken independently, as AXI
    // allows: either may complete first.
    task write_side();
      int st = 0, n = 0;
      bit got_a = 0, got_w = 0;
      bit [31:0] a, d;
      forever begin
        @(vif.cb);
        case (st)
          0: begin
            if (!got_a && vif.cb.awvalid && vif.cb.awready) begin
              got_a = 1; a = vif.cb.awaddr;
            end
            if (!got_w && vif.cb.wvalid && vif.cb.wready) begin
              got_w = 1; d = vif.cb.wdata;
            end
            if (got_a && got_w) begin
              vif.awready <= 0; vif.wready <= 0;
              if (!wr_err.exists(a)) mem[a] = d;
              n = $urandom_range(resp_delay); st = 1;
              got_a = 0; got_w = 0;
            end else begin
              vif.awready <= !got_a && ready(vif.cb.awvalid) &&
                             (style != W_FIRST || got_w);
              vif.wready  <= !got_w && ready(vif.cb.wvalid);
            end
          end
          2: if (vif.cb.bready) begin
               vif.bvalid <= 0; st = 0;
               vif.awready <= ready(0); vif.wready <= ready(0);
             end
          default: ;
        endcase
        if (st == 1) begin
          if (n == 0) begin
            vif.bresp <= wr_err.exists(a) ? RESP_SLVERR : RESP_OKAY;
            vif.bvalid <= 1; st = 2;
          end else n--;
        end
      end
    endtask
  endclass

  // ==================================================================
  class axil_txn;
    bit          wr = 0;
    bit [31:0]   addr = 0, data = 0;
    bit          ok;                     // response was OKAY
    longint      cycle;                  // edge of the R or B handshake
    longint      acycle;                 // first edge address VALID seen
    function string str();
      return $sformatf("%s %08h %s %08h", wr ? "W" : "R", addr,
                       wr ? "<-" : "->", data);
    endfunction
  endclass

  // Anything that wants to see completed transactions implements this.
  virtual class axil_subscriber;
    pure virtual function void observe(axil_txn t);
  endclass

  class axil_monitor;
    virtual axil_if vif;
    axil_subscriber subs [$];
    longint      cycle;
    int unsigned n_ar, n_aw, n_w, n_r, n_b, idle_cycles;
    int unsigned arvalid_cycles;         // cycles ARVALID was high
    longint      first_ar = 0, last_b = 0;  // span of the bus traffic
    bit          verbose = 0;
    bit [31:0]   ar_q [$], aw_q [$], w_q [$];
    longint      ar_c [$], aw_c [$];

    function new(virtual axil_if v);
      vif = v;
    endfunction

    // A VALID that was waiting must still be high, with the same
    // payload, on the next edge: the source may not take it back.
    function void stable(string ch, bit was, bit [31:0] then_v,
                         bit valid, bit [31:0] now_v);
      if (was && !valid)
        fail($sformatf("cycle %0d: %s dropped VALID before READY",
                       cycle, ch));
      else if (was && then_v != now_v)
        fail($sformatf("cycle %0d: %s payload changed while waiting",
                       cycle, ch));
    endfunction

    task run();
      bit ar_w = 0, aw_w = 0, w_w = 0;
      bit [31:0] ar_v, aw_v, w_v;
      longint ar_0, aw_0;                // edge each VALID was first seen
      axil_txn t;
      forever begin
        @(vif.cb);
        cycle++;
        stable("AR", ar_w, ar_v, vif.cb.arvalid, vif.cb.araddr);
        stable("AW", aw_w, aw_v, vif.cb.awvalid, vif.cb.awaddr);
        stable("W",  w_w,  w_v,  vif.cb.wvalid,  vif.cb.wdata);
        if (vif.cb.arvalid && !ar_w) ar_0 = cycle;
        if (vif.cb.arvalid && first_ar == 0) first_ar = cycle;
        if (vif.cb.awvalid && !aw_w) aw_0 = cycle;
        ar_w = vif.cb.arvalid && !vif.cb.arready; ar_v = vif.cb.araddr;
        aw_w = vif.cb.awvalid && !vif.cb.awready; aw_v = vif.cb.awaddr;
        w_w  = vif.cb.wvalid  && !vif.cb.wready;  w_v  = vif.cb.wdata;
        idle_cycles++;
        if (vif.cb.arvalid) arvalid_cycles++;
        if (vif.cb.arvalid && vif.cb.arready) begin
          n_ar++; ar_q.push_back(vif.cb.araddr); ar_c.push_back(ar_0);
          idle_cycles = 0;
        end
        if (vif.cb.awvalid && vif.cb.awready) begin
          n_aw++; aw_q.push_back(vif.cb.awaddr); aw_c.push_back(aw_0);
          idle_cycles = 0;
        end
        if (vif.cb.wvalid && vif.cb.wready) begin
          n_w++; w_q.push_back(vif.cb.wdata); idle_cycles = 0;
        end
        if (vif.cb.rvalid && vif.cb.rready) begin
          n_r++; idle_cycles = 0;
          t = new; t.wr = 0; t.cycle = cycle; t.data = vif.cb.rdata;
          t.ok = vif.cb.rresp == RESP_OKAY;
          if (ar_q.size() == 0) fail("R handshake with no AR before it");
          else begin
            t.addr = ar_q.pop_front(); t.acycle = ar_c.pop_front();
            publish(t);
          end
        end
        if (vif.cb.bvalid && vif.cb.bready) begin
          n_b++; idle_cycles = 0; last_b = cycle;
          t = new; t.wr = 1; t.cycle = cycle;
          t.ok = vif.cb.bresp == RESP_OKAY;
          if (aw_q.size() == 0 || w_q.size() == 0)
            fail("B handshake with no AW and W before it");
          else begin
            t.addr = aw_q.pop_front(); t.data = w_q.pop_front();
            t.acycle = aw_c.pop_front();
            publish(t);
          end
        end
      end
    endtask
    function void publish(axil_txn t);
      if (verbose) $display("  cycle %0d: %s", t.cycle, t.str());
      foreach (subs[i]) subs[i].observe(t);
    endfunction
  endclass

  // ==================================================================
  // The reference model reads the transfer's parameters as software
  // programmed them and the memory's contents before the transfer, and
  // predicts every read and write the specification requires.
  class dma_model;
    int unsigned nch;
    bit [31:0] exp_rd [][$];
    bit [31:0] exp_wa [][$], exp_wd [][$];
    int unsigned need_rd [];             // reads that must happen
    bit        exp_err [];
    function new(int unsigned n);
      nch = n;
      exp_rd = new[nch]; exp_wa = new[nch]; exp_wd = new[nch];
      need_rd = new[nch]; exp_err = new[nch];
    endfunction
    function void predict(int ch, bit [31:0] src, bit [31:0] dst,
                          longint unsigned len, axil_slave mem);
      bit [31:0] ra, wa;
      exp_rd[ch].delete(); exp_wa[ch].delete(); exp_wd[ch].delete();
      exp_err[ch] = 0; need_rd[ch] = 0;
      for (longint unsigned i = 0; i < len; i++) begin
        ra = src + 32'(4 * i); wa = dst + 32'(4 * i);
        exp_rd[ch].push_back(ra);
        if (!exp_err[ch]) need_rd[ch]++;
        if (exp_err[ch]) continue;       // later reads allowed, not owed
        if (mem.rd_err.exists(ra)) begin exp_err[ch] = 1; continue; end
        exp_wa[ch].push_back(wa); exp_wd[ch].push_back(mem.peek(ra));
        if (mem.wr_err.exists(wa)) exp_err[ch] = 1;
      end
    endfunction
  endclass

  class dma_scoreboard extends axil_subscriber;
    dma_model  m;
    int unsigned n_rd [], n_wr [];
    function new(dma_model model);
      m = model;
      n_rd = new[m.nch]; n_wr = new[m.nch];
    endfunction
    function void start(int ch);
      n_rd[ch] = 0; n_wr[ch] = 0;
    endfunction
    virtual function void observe(axil_txn t);
      for (int c = 0; c < int'(m.nch); c++) begin
        if (!t.wr && m.exp_rd[c].size() != 0 && m.exp_rd[c][0] == t.addr) begin
          void'(m.exp_rd[c].pop_front()); n_rd[c]++; return;
        end
        if (t.wr && m.exp_wa[c].size() != 0 && m.exp_wa[c][0] == t.addr)
          begin
          void'(m.exp_wa[c].pop_front());
          if (m.exp_wd[c].pop_front() != t.data)
            fail($sformatf("ch%0d: wrong data, %s", c, t.str()));
          n_wr[c]++; return;
        end
      end
      fail($sformatf("cycle %0d: unexpected %s", t.cycle, t.str()));
    endfunction
    // At the end of a transfer: every write owed was seen, enough reads
    // were seen, and STATUS says error exactly when the model does.
    function bit check_end(int ch, bit [31:0] status);
      int unsigned n0 = errors;
      if (m.exp_wa[ch].size() != 0)
        fail($sformatf("ch%0d: %0d writes never seen, next %08h", ch,
                       m.exp_wa[ch].size(), m.exp_wa[ch][0]));
      if (n_rd[ch] < m.need_rd[ch])
        fail($sformatf("ch%0d: %0d reads seen, %0d owed", ch, n_rd[ch],
                       m.need_rd[ch]));
      if (((status & STATUS_ERROR) != 0) != m.exp_err[ch])
        fail($sformatf("ch%0d: STATUS %0h, model says error=%0d", ch,
                       status, m.exp_err[ch]));
      return errors == n0;
    endfunction
  endclass

  // ==================================================================
  class dma_coverage;
    covergroup xfer_cg with function sample(int unsigned words,
                                            outcome_e out, int at,
                                            ready_style_e how);
      len_cp: coverpoint words {
        bins zero = {0};
        bins one  = {1};
        bins few  = {[2:15]};
        bins many = {[16:65535]};
        bins over = {[65536:$]};
      }
      out_cp: coverpoint out {
        bins ok = {OUT_OK}; bins rd_err = {OUT_RD_ERR};
        bins wr_err = {OUT_WR_ERR};
      }
      pos_cp: coverpoint at iff (out != OUT_OK) {
        bins first = {0}; bins middle = {1}; bins last = {2};
      }
      style_cp: coverpoint how {
        bins wait_valid = {WAIT_VALID}; bins ready_first = {READY_FIRST};
        bins random = {RANDOM}; bins w_first = {W_FIRST};
      }
      len_x_out: cross len_cp, out_cp;
    endgroup
    function new();
      xfer_cg = new;
    endfunction
  endclass

  // ==================================================================
  class dma_env;
    apb_master     apb;
    axil_slave     mem;
    axil_monitor   mon;
    dma_model      model;
    dma_scoreboard sb;
    dma_coverage   cov;
    int unsigned   nch, stride, timeout = 2000;

    function new(virtual apb_if a, virtual axil_if x, int unsigned n,
                 int unsigned s);
      nch = n; stride = s;
      apb = new(a); mem = new(x); mon = new(x);
      model = new(nch); sb = new(model); cov = new;
      mon.subs.push_back(sb);
    endfunction
    task run();
      apb.reset();
      mem.run();
      fork mon.run(); join_none
    endtask

    function bit [31:0] reg_addr(int ch, int off);
      return 32'(ch * stride + off);
    endfunction
    task automatic wr(int ch, int off, bit [31:0] v, output bit slverr);
      apb.write(reg_addr(ch, off), v, slverr);
    endtask
    task automatic rd(int ch, int off, output bit [31:0] v);
      apb.read(reg_addr(ch, off), v);
    endtask

    // Program one channel, tell the model, and start it.
    task automatic start(int ch, bit [31:0] src, bit [31:0] dst,
                         longint unsigned len, bit irq_en = 1);
      bit e;
      model.predict(ch, src, dst, len, mem);
      sb.start(ch);
      wr(ch, SRC_ADDR, src, e);
      wr(ch, DST_ADDR, dst, e);
      wr(ch, XFER_LEN, 32'(len), e);
      wr(ch, CTRL, CTRL_START | (irq_en ? CTRL_IRQ_EN : 0), e);
    endtask

    // Wait for the AXI side to go quiet with no handshake for `quiet`
    // cycles, or for the timeout: the watchdog every test needs.
    task automatic wait_quiet(int unsigned quiet, output bit timed_out);
      int unsigned n = 0;
      timed_out = 0;
      while (mon.idle_cycles < quiet) begin
        @(apb.vif.cb);
        if (++n > timeout) begin timed_out = 1; return; end
      end
    endtask

    // Poll STATUS until BUSY clears, then return the last value read.
    task automatic wait_idle(int ch, output bit [31:0] status,
                             output bit timed_out);
      int unsigned n = 0;
      timed_out = 0;
      do begin
        rd(ch, STATUS, status);
        if (++n > timeout) begin timed_out = 1; return; end
      end while ((status & STATUS_BUSY) != 0);
    endtask
  endclass
endpackage
