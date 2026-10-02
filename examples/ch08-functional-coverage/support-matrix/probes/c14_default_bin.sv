// bins rest = default: lo = {0}, mid = {1} and a default bin for the
// rest; samples of 0 and 3 hit lo and the default bin, which does not
// count; the standard gives 50.00 (c14)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins lo = {0}; bins mid = {1}; bins rest = default; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 3; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c14 PASS");
    else $display("PROBE c14 FAIL");
    $finish;
  end
endmodule
