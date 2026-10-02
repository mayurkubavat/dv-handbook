// ignore_bins covering a whole named bin: lo = {0,1}, hi = {2,3} and
// ignore_bins ig = {2,3} empties hi, so lo is the only bin; one sample
// of 0 gives 100.00 (a tool that keeps hi in the denominator prints
// 50.00) (x08)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins lo = {0, 1}; bins hi = {2, 3}; ignore_bins ig = {2, 3}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 100.0)) $display("PROBE x08 PASS");
    else $display("PROBE x08 FAIL");
    $finish;
  end
endmodule
