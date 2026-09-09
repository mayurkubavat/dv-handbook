// crossing_via_latch.sv -- a crossing that passes through a latch.
//
// A latch is a state element, so the path is not direct and cannot be a
// synchronizer. Stopping the walk at the latch would hide the crossing
// entirely, which is worse than mis-classifying it.
module crossing_via_latch (input logic bclk, brst_n, cclk, crst_n, d, en,
               output logic q);
  logic a, lat;
  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) a <= 1'b0; else a <= d;
  always_latch if (en) lat = a;
  always_ff @(posedge cclk or negedge crst_n)
    if (!crst_n) q <= 1'b0; else q <= lat;
endmodule
