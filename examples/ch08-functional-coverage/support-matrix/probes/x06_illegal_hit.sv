// illegal_bins value sampled: illegal_bins il = {3} and 3 is sampled, so
// the standard requires a run-time error; a simulator that stops here
// prints no verdict and the runner records "no run", which is the right
// cell; reaching the line after the sample is the wrong result (x06)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins ok[] = {[0:2]}; illegal_bins il = {3}; }
  endgroup
  cg g;
  initial begin
    g = new;
    v = 0; g.sample(); v = 3; g.sample();
    $display("cov=%0.2f after an illegal value", g.get_inst_coverage());
    $display("PROBE x06 FAIL");
    $finish;
  end
endmodule
