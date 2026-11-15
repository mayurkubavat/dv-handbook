// tb_goto.sv -- one rule, checked twice: by a concurrent assertion
// with goto repetition, and by a monitor written out as registers.
//
// The rule: after go, the tick that follows the second beat must
// carry last. Beats come at ticks 3 and 5 of each run, so last is due
// at tick 6. The good instance supplies it; the bad one never does.
`timescale 1ns/1ps
module rule #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                       // the tick counter
  always_ff @(posedge clk) t <= t + 4'd1;
  wire go   = (t == 1);
  wire beat = (t == 3) || (t == 5);
  wire last = (t == 6) && !BAD;

  // ---- as a property --------------------------------------------------
  int sva_fails = 0;
  Goto_A: assert property (@(posedge clk) go |-> beat[->2] ##1 last)
    else sva_fails++;

  // ---- as the automaton the property describes -----------------------
  // WAIT2 and WAIT1 count the beats still owed; DUE is the one tick in
  // which last must be seen. One attempt at a time, which is all this
  // stimulus needs.
  typedef enum logic [1:0] {IDLE, WAIT2, WAIT1, DUE} state_e;
  state_e st = IDLE;
  int     mon_fails = 0;
  always_ff @(posedge clk) begin
    case (st)
      IDLE:    if (go)   st <= beat ? WAIT1 : WAIT2;
      WAIT2:   if (beat) st <= WAIT1;
      WAIT1:   if (beat) st <= DUE;
      default: begin
        if (!last) mon_fails <= mon_fails + 1;
        st <= IDLE;
      end
    endcase
  end
endmodule

module tb_goto;
  logic clk = 0;
  always #5 clk <= ~clk;
  rule #(.BAD(0)) good (.clk);
  rule #(.BAD(1)) bad  (.clk);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    $display("last supplied:  assertion reports %0d, monitor reports %0d",
             good.sva_fails, good.mon_fails);
    $display("last missing:   assertion reports %0d, monitor reports %0d",
             bad.sva_fails, bad.mon_fails);
    if (bad.mon_fails != 1 || good.mon_fails != 0)
      $fatal(1, "the monitor is wrong");
    if (bad.sva_fails == 0)
      $display("verdict: the simulator missed the failure the monitor saw");
    else
      $display("verdict: the simulator now reports the failure");
    $finish;
  end
endmodule
