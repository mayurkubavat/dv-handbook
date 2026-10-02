// enum coverpoint with auto bins, one per literal: three literals on a
// 2-bit base type, one sampled; the standard gives 33.33 (a tool that
// makes one bin per bit pattern prints 25.00) (c30)
module top;
  typedef enum bit [1:0] {IDLE, BUSY, DONE} st_t;
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
    if (near(g.get_inst_coverage(), 33.33)) $display("PROBE c30 PASS");
    else $display("PROBE c30 FAIL");
    $finish;
  end
endmodule
