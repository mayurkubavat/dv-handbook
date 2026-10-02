// stop() before every sample: the group is stopped before 0 and 1 are
// sampled, so nothing is counted; the standard gives 0.00 (a tool that
// drops stop() prints 50.00) (x16)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    g.stop(); v = 0; g.sample(); g.stop(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 0.0)) $display("PROBE x16 PASS");
    else $display("PROBE x16 FAIL");
    $finish;
  end
endmodule
