// ignore_bins on an array of bins: bins b[] = {[0:3]} with ignore_bins
// ig = {3} leaves three bins; samples of 0, 1, 2 hit all of them; the
// standard gives 100.00 (a tool that keeps 3 in the denominator prints
// 75.00) (c12)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v { bins b[] = {[0:3]}; ignore_bins ig = {3}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample(); v = 2; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 100.0)) $display("PROBE c12 PASS");
    else $display("PROBE c12 FAIL");
    $finish;
  end
endmodule
