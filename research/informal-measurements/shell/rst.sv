// Reset handling probes: async active-low, a register with no reset, an initial value.
module rst (input logic clk, input logic rst_n, input logic en,
            output logic [3:0] a, output logic [3:0] nr, output logic [3:0] iv);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) a <= 4'd0; else if (en) a <= a + 4'd1;
  always_ff @(posedge clk) if (en) nr <= a;          // never reset
  initial iv = 4'd5;
  always_ff @(posedge clk) iv <= iv;                 // initial value only
endmodule
