// tb_fixed.sv -- the fix, which works on either value set and either tool.
//
// Drive the line to its inactive level, then to its active level a moment
// later. The simulator sees 1 -> 0, which is an edge, whatever the
// variable started at. The published two-line form does the second write
// with a non-blocking assignment in the same timestep; the event-driven
// simulator sees that edge and the statically scheduled one, which
// compares values between evaluations, does not. An edge
// across time is seen by both.
module tb_fixed;
  logic       clk = 0;
  bit         rst_n;
  logic [7:0] d = 8'h00, q;
  dut_reg u (.clk, .rst_n, .d, .q);
  always #5 clk <= ~clk;
  initial begin
    rst_n = 1;            // inactive, now
    #1 rst_n = 0;         // active, one time unit later: an edge in time
    #1 $display("tb_fixed: q=%02h, no clock edge yet %0s", q,
                 q === 8'hA5 ? "(reset happened)" : "(reset never happened)");
    rst_n = 1;
    $finish;
  end
endmodule
