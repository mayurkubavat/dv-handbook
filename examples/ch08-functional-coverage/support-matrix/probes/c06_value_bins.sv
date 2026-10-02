// explicit value bins: bins lo = {0, 1} and bins hi = {2, 3}; one sample
// of 0 hits lo only; the standard gives 50.00 (c06)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v { bins lo = {0, 1}; bins hi = {2, 3}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c06 PASS");
    else $display("PROBE c06 FAIL");
    $finish;
  end
endmodule
