// enum with four literals on 2 bits, the control for the three-literal
// case: one literal per bit pattern, one sampled; the standard gives
// 25.00, and so does a tool that bins by bit pattern (x15)
module top;
  typedef enum bit [1:0] {IDLE, BUSY, DONE, HALT} st_t;
  st_t s;
  covergroup cg; coverpoint s; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    s = IDLE; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 25.0)) $display("PROBE x15 PASS");
    else $display("PROBE x15 FAIL");
    $finish;
  end
endmodule
