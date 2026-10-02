// wildcard bins: hi = {2'b1?} and lo = {2'b0?}; one sample of 2 hits hi
// only; the standard gives 50.00 (c11)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    wildcard bins hi = {2'b1?}; wildcard bins lo = {2'b0?}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 2; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c11 PASS");
    else $display("PROBE c11 FAIL");
    $finish;
  end
endmodule
