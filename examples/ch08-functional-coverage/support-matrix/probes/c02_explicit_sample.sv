// covergroup with explicit sample(): a 2-bit auto-bin coverpoint sampled
// with 0 and 1; the standard gives 50.00 (c02)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c02 PASS");
    else $display("PROBE c02 FAIL");
    $finish;
  end
endmodule
