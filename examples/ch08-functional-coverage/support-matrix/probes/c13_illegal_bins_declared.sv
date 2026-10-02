// illegal_bins declared and not hit: bins ok[] = {[0:2]} and
// illegal_bins il = {3}; one sample of 0 hits one of three counted bins;
// the standard gives 33.33 (c13)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins ok[] = {[0:2]}; illegal_bins il = {3}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 33.33)) $display("PROBE c13 PASS");
    else $display("PROBE c13 FAIL");
    $finish;
  end
endmodule
