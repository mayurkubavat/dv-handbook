// rr_arb.sv -- an N-port arbiter, the shape of the DMA's read-engine
// arbitration on its own. ROUND = 1: round robin, the first
// requesting port after the last one granted. ROUND = 0: fixed
// priority, port 0 first; the ports are then not interchangeable.
module rr_arb #(parameter int N = 4, parameter bit ROUND = 1) (
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
    if (!rst_n) begin
      gnt <= '0; last <= W'(N - 1);
    end else begin
      gnt <= pick;
      for (int c = 0; c < N; c++)
        if (pick[c]) last <= W'(c);
    end
endmodule
