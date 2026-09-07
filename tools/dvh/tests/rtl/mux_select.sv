// mux_select.sv -- a crossing that arrives through a multiplexer's select.
//
// sel_b is written on bclk and steers a multiplexer read on cclk. It is a
// one-bit unsynchronized control crossing: the textbook case. A data-cone
// walk that skips the select port, as a clock walk correctly does, reports
// this design as clean.
module mux_select (
  input  logic       bclk,
  input  logic       brst_n,
  input  logic       cclk,
  input  logic       crst_n,
  input  logic       sel_in,
  input  logic [7:0] a,
  input  logic [7:0] b,
  output logic [7:0] out
);
  logic sel_b;

  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) sel_b <= 1'b0;
    else         sel_b <= sel_in;

  always_ff @(posedge cclk or negedge crst_n)
    if (!crst_n) out <= 8'h00;
    else         out <= sel_b ? a : b;
endmodule
