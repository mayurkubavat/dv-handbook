// rr_arb.sv -- an N-port arbiter, the shape of the DMA's read-engine
// arbitration on its own, and a check that it is symmetric.
//
// ROUND = 1: round robin, the first requesting port after the last
// one granted. ROUND = 0: fixed priority, port 0 first. FREE_LAST = 1
// gives `last` no reset value, so that the arbiter starts from every
// value of it; FREE_LAST = 0 resets it to N - 1, as the DMA resets
// its own pointer.
module rr_arb #(parameter int N = 4, parameter bit ROUND = 1,
                parameter bit FREE_LAST = 0) (
  input  logic         clk, rst_n,
  input  logic [N-1:0] req,
  output logic [N-1:0] gnt
);
  localparam int W = $clog2(N);
  logic [W-1:0] last;
  logic [N-1:0] pick;
  always_comb begin
    int c;
    pick = '0;
    for (int k = 1; k <= N; k++) begin
      c = ROUND ? (int'(last) + k) % N : k - 1;
      if (pick == '0 && req[c]) pick[c] = 1'b1;
    end
  end
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) gnt <= '0;
    else        gnt <= pick;
  if (FREE_LAST) begin : g_free           // no reset: any start value
    always_ff @(posedge clk)
      if (rst_n)
        for (int c = 0; c < N; c++)
          if (pick[c]) last <= W'(c);
  end else begin : g_reset
    always_ff @(posedge clk or negedge rst_n)
      if (!rst_n) last <= W'(N - 1);
      else
        for (int c = 0; c < N; c++)
          if (pick[c]) last <= W'(c);
  end
endmodule

// rr_rot: two round-robin arbiters, the second fed the requests of
// the first rotated by one port. With free starts (FREE_LAST = 1) the
// script assumes the second's `last` is the first's plus one in the
// first cycle after reset; the check is that its grants are then the
// first's rotated by one port in every cycle, which is what makes a
// rotation of the ports a symmetry of the transition relation. With
// FREE_LAST = 0 both reset `last` to N - 1, which no rotation fixes.
module rr_rot #(parameter int N = 4, parameter bit FREE_LAST = 1) (
  input  logic         clk, rst_n,
  input  logic [N-1:0] req,
  output logic [N-1:0] gnt0, gnt1
);
  logic first;
  rr_arb #(.N(N), .FREE_LAST(FREE_LAST)) u0 (.clk, .rst_n, .req,
                                             .gnt(gnt0));
  rr_arb #(.N(N), .FREE_LAST(FREE_LAST)) u1 (
    .clk, .rst_n, .req({req[N-2:0], req[N-1]}), .gnt(gnt1));
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) first <= 1'b1;
    else        first <= 1'b0;
endmodule
