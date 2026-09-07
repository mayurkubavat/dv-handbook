// top.sv -- a two-clock block for Chapter 3's worked example.
//
// Specification (the part that matters for this chapter):
//   * regblock runs on the bus clock bclk; datapath runs on the core clock
//     cclk. The two clocks are asynchronous to each other.
//   * Every signal that crosses from bclk to cclk shall pass through a
//     synchronizer, or be transferred with a handshake if it is wider
//     than one bit.
//   * Every register shall have a defined value after reset, except the
//     datapath's last_cfg, which the specification marks "don't care until
//     the first enable".
//
// This design honors the first rule for `en` and breaks it for `cfg`, which
// crosses eight bits wide with no synchronizer and no handshake. The chapter's
// tools find that; lint does not.
module top (
  input  logic       bclk,
  input  logic       brst_n,
  input  logic       cclk,
  input  logic       crst_n,
  input  logic       wr_en,
  input  logic       wr_addr,
  input  logic [7:0] wr_data,
  output logic [7:0] count,
  output logic [7:0] acc,
  output logic [7:0] last_cfg
);
  logic       en_b;
  logic [7:0] cfg_b;
  logic       en_c;

  regblock u_regs (
    .clk     (bclk),
    .rst_n   (brst_n),
    .wr_en   (wr_en),
    .wr_addr (wr_addr),
    .wr_data (wr_data),
    .en      (en_b),
    .cfg     (cfg_b)
  );

  // The enable crosses through a two-flop synchronizer: as specified.
  sync2 #(.WIDTH(1)) u_sync_en (
    .clk   (cclk),
    .rst_n (crst_n),
    .d     (en_b),
    .q     (en_c)
  );

  // The configuration bus crosses with nothing at all: the bug.
  datapath u_dp (
    .clk   (cclk),
    .rst_n (crst_n),
    .en    (en_c),
    .cfg   (cfg_b),
    .count (count),
    .acc   (acc),
    .last_cfg (last_cfg)
  );
endmodule
