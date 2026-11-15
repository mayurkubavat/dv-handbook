// dma_v2.sv -- the two-channel DMA the chapter's microarchitecture
// describes. APB3 slave for registers, AXI4-Lite master for data.
//
//   channel block  per-channel registers and counters; the only writer
//                  of every channel bit, so no register has two drivers
//   read engine    round-robin over channels with work and FIFO room,
//                  one read outstanding, pushes {channel, data}
//   data FIFO      DEPTH entries, so a read can be issued while the
//                  previous word is still being written
//   write engine   pops the FIFO, one write outstanding, address and
//                  data handshakes completed independently
//
// Errors are precise: every word before the failing one reaches the
// destination and no word after it does. A read error stops the
// channel's reads and lets its words already in the FIFO be written; a
// write error also drops those, since they come after it. The channel
// ends with done and error set once nothing of it is in flight.
// PRECISE = 0 builds the first draft, which dropped the queued words on
// a read error too; the random test is what caught it.
module dma_v2
  import dma_regs_pkg::*;
#(parameter int DEPTH = 2, parameter bit PRECISE = 1)
(
  input  logic        PCLK,
  input  logic        PRESETn,
  // APB3 slave
  input  logic        PSEL, PENABLE, PWRITE,
  input  logic [31:0] PADDR, PWDATA,
  output logic [31:0] PRDATA,
  output logic        PREADY, PSLVERR,
  // AXI4-Lite master
  output logic [31:0] ARADDR,
  output logic        ARVALID,
  input  logic        ARREADY,
  input  logic [31:0] RDATA,
  input  logic [1:0]  RRESP,
  input  logic        RVALID,
  output logic        RREADY,
  output logic [31:0] AWADDR,
  output logic        AWVALID,
  input  logic        AWREADY,
  output logic [31:0] WDATA,
  output logic [3:0]  WSTRB,
  output logic        WVALID,
  input  logic        WREADY,
  input  logic [1:0]  BRESP,
  input  logic        BVALID,
  output logic        BREADY,
  output logic        IRQ
);
  localparam int CW = (NCH > 1) ? $clog2(NCH) : 1;
  localparam int PW = (DEPTH > 1) ? $clog2(DEPTH) : 1;
  localparam int SB = $clog2(CH_STRIDE);        // offset bits in a channel

  // ---- Per-channel state (written only by the channel block) ------
  logic [29:0] src [NCH], dst [NCH], rd_ptr [NCH], wr_ptr [NCH];
  logic [15:0] len [NCH], rd_left [NCH], wr_left [NCH];
  logic [NCH-1:0] irq_en, busy, done, err, abort, drop;
  logic [$clog2(DEPTH+1)-1:0] in_fifo [NCH];

  // ---- APB decode: valid in the access phase, as APB3 requires -----
  logic [CW-1:0] a_ch;
  logic [SB-1:0] a_off;
  logic          a_map, a_cfg, acc, wr_ok;
  assign a_ch  = CW'(PADDR[31:SB]);
  assign a_off = PADDR[SB-1:0];
  // Written out rather than with `inside`, which Icarus 13 refuses.
  assign a_map = (32'(PADDR[31:SB]) < NCH) &&
                 (a_off == SB'(SRC_ADDR) || a_off == SB'(DST_ADDR) ||
                  a_off == SB'(XFER_LEN) || a_off == SB'(CTRL) ||
                  a_off == SB'(STATUS));
  assign a_cfg = a_off != SB'(STATUS);
  assign acc   = PSEL && PENABLE;
  assign PREADY  = 1'b1;
  assign PSLVERR = acc && (!a_map || (PWRITE && a_cfg && busy[a_ch]));
  assign wr_ok   = acc && PWRITE && !PSLVERR;

  always_comb begin
    PRDATA = '0;
    if (acc && !PWRITE && a_map)
      case (a_off)
        SB'(SRC_ADDR): PRDATA = {src[a_ch], 2'b00};
        SB'(DST_ADDR): PRDATA = {dst[a_ch], 2'b00};
        SB'(XFER_LEN): PRDATA = {16'h0, len[a_ch]};
        SB'(CTRL):     PRDATA = irq_en[a_ch] ? CTRL_IRQ_EN : 0;
        default:       PRDATA = (busy[a_ch] ? STATUS_BUSY  : 0) |
                                (done[a_ch] ? STATUS_DONE  : 0) |
                                (err[a_ch]  ? STATUS_ERROR : 0);
      endcase
  end

  // ---- Engine events, one-cycle pulses per channel -----------------
  logic [NCH-1:0] rd_good, rd_bad, wr_good, wr_bad, popped;
  logic [NCH-1:0] rd_fly, wr_fly;

  // ---- Channel block -----------------------------------------------
  always_ff @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
      for (int c = 0; c < NCH; c++) begin
        src[c] <= '0; dst[c] <= '0; len[c] <= '0;
        rd_ptr[c] <= '0; wr_ptr[c] <= '0;
        rd_left[c] <= '0; wr_left[c] <= '0; in_fifo[c] <= '0;
      end
      irq_en <= '0; busy <= '0; done <= '0; err <= '0; abort <= '0;
      drop <= '0;
    end else begin
      for (int c = 0; c < NCH; c++) begin
        // Software side
        if (wr_ok && a_ch == CW'(c))
          case (a_off)
            SB'(SRC_ADDR): src[c] <= PWDATA[31:2];
            SB'(DST_ADDR): dst[c] <= PWDATA[31:2];
            SB'(XFER_LEN): len[c] <= PWDATA[15:0];
            SB'(CTRL): begin
              irq_en[c] <= |(PWDATA & CTRL_IRQ_EN);
              if (|(PWDATA & CTRL_START)) begin
                rd_ptr[c] <= src[c];  wr_ptr[c] <= dst[c];
                rd_left[c] <= len[c]; wr_left[c] <= len[c];
                busy[c] <= len[c] != 0;
                done[c] <= len[c] == 0;
                err[c] <= 1'b0; abort[c] <= 1'b0; drop[c] <= 1'b0;
              end
            end
            default: begin                         // STATUS: W1C
              if (|(PWDATA & STATUS_DONE))  done[c] <= 1'b0;
              if (|(PWDATA & STATUS_ERROR)) err[c]  <= 1'b0;
            end
          endcase
        // Hardware side
        if (rd_good[c]) begin
          rd_ptr[c] <= rd_ptr[c] + 1; rd_left[c] <= rd_left[c] - 1;
        end
        if (rd_bad[c] || wr_bad[c]) abort[c] <= 1'b1;   // no more reads
        if (wr_bad[c] || (rd_bad[c] && !PRECISE)) drop[c] <= 1'b1;
        in_fifo[c] <= in_fifo[c] + rd_good[c] - popped[c];
        if (wr_good[c]) begin
          wr_ptr[c] <= wr_ptr[c] + 1; wr_left[c] <= wr_left[c] - 1;
          if (wr_left[c] == 1) begin busy[c] <= 1'b0; done[c] <= 1'b1; end
        end
        if (busy[c] && abort[c] && !rd_fly[c] && !wr_fly[c] &&
            in_fifo[c] == 0) begin
          busy[c] <= 1'b0; done[c] <= 1'b1; err[c] <= 1'b1;
          abort[c] <= 1'b0; drop[c] <= 1'b0;
        end
      end
    end
  end

  always_ff @(posedge PCLK or negedge PRESETn)
    if (!PRESETn) IRQ <= 1'b0;
    else          IRQ <= |(irq_en & (done | err));

  // ---- Data FIFO: {channel, word} ----------------------------------
  logic [CW+31:0] fifo [DEPTH];
  logic [PW-1:0] f_wp, f_rp;
  logic [$clog2(DEPTH+1)-1:0] f_cnt;
  logic f_push, f_pop;
  logic [CW-1:0] f_ch;
  assign f_ch = fifo[f_rp][CW+31:32];

  // ---- Read engine -------------------------------------------------
  typedef enum logic [1:0] {R_IDLE, R_ADDR, R_DATA} rstate_e;
  rstate_e rs;
  logic [CW-1:0] r_ch, r_last, r_pick;
  logic          r_any;

  // Round robin: the first eligible channel after the last one granted.
  always_comb begin
    int c;
    r_any = 1'b0; r_pick = r_last;
    for (int k = 1; k <= NCH; k++) begin
      c = (int'(r_last) + k) % NCH;
      if (!r_any && busy[c] && !abort[c] && rd_left[c] != 0) begin
        r_any = 1'b1; r_pick = CW'(c);
      end
    end
  end

  always_ff @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
      rs <= R_IDLE; r_ch <= '0; r_last <= CW'(NCH - 1);
      ARVALID <= 1'b0; ARADDR <= '0; RREADY <= 1'b0;
    end else
      case (rs)
        R_IDLE: if (r_any && int'(f_cnt) < DEPTH) begin
          ARADDR <= {rd_ptr[r_pick], 2'b00}; ARVALID <= 1'b1;
          r_ch <= r_pick; r_last <= r_pick; rs <= R_ADDR;
        end
        R_ADDR: if (ARREADY) begin            // ARVALID is high here
          ARVALID <= 1'b0; RREADY <= 1'b1; rs <= R_DATA;
        end
        default: if (RVALID) begin
          RREADY <= 1'b0; rs <= R_IDLE;
        end
      endcase
  end

  always_comb begin
    rd_good = '0; rd_bad = '0; rd_fly = '0;
    if (rs != R_IDLE) rd_fly[r_ch] = 1'b1;
    if (rs == R_DATA && RVALID) begin
      if (RRESP == 2'(RESP_OKAY) && !drop[r_ch]) rd_good[r_ch] = 1'b1;
      else if (RRESP != 2'(RESP_OKAY))           rd_bad[r_ch]  = 1'b1;
    end
  end
  assign f_push = |rd_good;

  // ---- Write engine ------------------------------------------------
  typedef enum logic [1:0] {W_IDLE, W_REQ, W_RESP} wstate_e;
  wstate_e ws;
  logic [CW-1:0] w_ch;

  always_ff @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
      ws <= W_IDLE; w_ch <= '0;
      AWVALID <= 1'b0; WVALID <= 1'b0; BREADY <= 1'b0;
      AWADDR <= '0; WDATA <= '0;
    end else
      case (ws)
        W_IDLE: if (f_cnt != 0 && !drop[f_ch]) begin
          AWADDR <= {wr_ptr[f_ch], 2'b00};
          WDATA <= fifo[f_rp][31:0];
          AWVALID <= 1'b1; WVALID <= 1'b1;
          w_ch <= f_ch; ws <= W_REQ;
        end
        W_REQ: begin
          // Each handshake completes on its own edge.
          if (AWREADY) AWVALID <= 1'b0;
          if (WREADY)  WVALID  <= 1'b0;
          if ((AWREADY || !AWVALID) && (WREADY || !WVALID)) begin
            BREADY <= 1'b1; ws <= W_RESP;
          end
        end
        default: if (BVALID) begin
          BREADY <= 1'b0; ws <= W_IDLE;
        end
      endcase
  end
  assign WSTRB = 4'hF;

  // A word is popped when its write is issued, or dropped if its
  // channel is dropping.
  assign f_pop = ws == W_IDLE && f_cnt != 0;
  always_comb begin
    popped = '0;
    if (f_pop) popped[f_ch] = 1'b1;
    wr_good = '0; wr_bad = '0; wr_fly = '0;
    if (ws != W_IDLE) wr_fly[w_ch] = 1'b1;
    if (ws == W_RESP && BVALID) begin
      if (BRESP == 2'(RESP_OKAY)) wr_good[w_ch] = 1'b1;
      else                        wr_bad[w_ch]  = 1'b1;
    end
  end

  always_ff @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
      f_wp <= '0; f_rp <= '0; f_cnt <= '0;
    end else begin
      if (f_push) begin
        fifo[f_wp] <= {r_ch, RDATA};
        f_wp <= (f_wp == PW'(DEPTH - 1)) ? '0 : f_wp + 1;
      end
      if (f_pop)
        f_rp <= (f_rp == PW'(DEPTH - 1)) ? '0 : f_rp + 1;
      f_cnt <= f_cnt + f_push - f_pop;
    end
  end
endmodule
