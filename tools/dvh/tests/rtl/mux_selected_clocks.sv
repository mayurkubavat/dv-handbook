// mux_selected_clocks.sv -- one clock mux per block, same two sources.
//
// Both muxes choose between the same pair of asynchronous clocks, and on
// opposite selections, so the two registers never run on one clock. Keying
// a domain on the *names* of the sources reached made these two networks
// equal, and the crossing between them was dropped before anything could
// report it: zero crossings, exit zero, on a per-block clock mux.
module mux_selected_clocks (input logic ca, cb, sel, rst_n, d, output logic q);
  logic g1, g2, a;
  assign g1 = sel ? ca : cb;
  assign g2 = sel ? cb : ca;
  always_ff @(posedge g1 or negedge rst_n)
    if (!rst_n) a <= 1'b0; else a <= d;
  always_ff @(posedge g2 or negedge rst_n)
    if (!rst_n) q <= 1'b0; else q <= a;
endmodule
