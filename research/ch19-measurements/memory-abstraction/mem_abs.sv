// mem_abs.sv -- a RAM with write-to-read forwarding, and a wrapper
// that checks it at one symbolic address.
//
// mem_store is the storage: a synchronous RAM with a registered read
// that returns the old word when the same address is written in the
// same cycle. fwd_ram adds forwarding, so that its own read returns
// the new word in that case. BUG = 1 compares only the low address
// bit, so a write to another address can be forwarded.

module mem_store #(parameter int AW = 4, parameter int DW = 8) (
  input  logic          clk,
  input  logic          we,
  input  logic [AW-1:0] waddr, raddr,
  input  logic [DW-1:0] wdata,
  output logic [DW-1:0] rdata
);
  logic [DW-1:0] m [2**AW];
  always_ff @(posedge clk) begin
    if (we) m[waddr] <= wdata;
    rdata <= m[raddr];
  end
endmodule

module fwd_ram #(parameter int AW = 4, parameter int DW = 8,
                 parameter bit BUG = 0) (
  input  logic          clk, rst_n,
  input  logic          we,
  input  logic [AW-1:0] waddr, raddr,
  input  logic [DW-1:0] wdata,
  output logic [DW-1:0] rdata
);
  logic [DW-1:0] m_rdata, wdata_q;
  logic          fwd_q;
  wire hit = BUG ? (waddr[0] == raddr[0]) : (waddr == raddr);
  mem_store #(.AW(AW), .DW(DW)) u_mem (.clk, .we, .waddr, .raddr,
                                       .wdata, .rdata(m_rdata));
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) fwd_q <= 1'b0;
    else        fwd_q <= we && hit;
  always_ff @(posedge clk) wdata_q <= wdata;
  assign rdata = fwd_q ? wdata_q : m_rdata;
endmodule

// mem_top: the RAM plus the checking logic for one address sa, a free
// input that the script holds constant with an assumption.
//   sv, sv_ok  the last word written to sa, and whether there is one
//   chk_q      the read of the previous cycle was of sa, after a write
//   exp_q      what that read must return (with forwarding)
//   mchk_q, mexp_q  the same for the storage alone (old word)
module mem_top #(parameter int AW = 4, parameter int DW = 8,
                 parameter bit BUG = 0) (
  input  logic          clk, rst_n,
  input  logic          we,
  input  logic [AW-1:0] waddr, raddr, sa,
  input  logic [DW-1:0] wdata,
  output logic [DW-1:0] rdata
);
  fwd_ram #(.AW(AW), .DW(DW), .BUG(BUG)) u_ram (.*);
  logic [DW-1:0] sv, exp_q, mexp_q;
  logic          sv_ok, chk_q, mchk_q;
  wire wr_sa = we && waddr == sa;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      sv_ok <= 1'b0; chk_q <= 1'b0; mchk_q <= 1'b0;
    end else begin
      if (wr_sa) sv_ok <= 1'b1;
      chk_q  <= raddr == sa && (sv_ok || wr_sa);
      mchk_q <= raddr == sa && sv_ok;
    end
  always_ff @(posedge clk) begin
    if (wr_sa) sv <= wdata;
    exp_q  <= wr_sa ? wdata : sv;
    mexp_q <= sv;
  end
endmodule
