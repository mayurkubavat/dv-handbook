// bins ev[] = {[0:7]} with (item % 2 == 0): four bins, one per even
// value; samples of 0 and 2 hit two; the standard gives 50.00 (a tool
// that drops the filter and makes one bin prints 100.00) (c15)
module top;
  bit [2:0] v;
  covergroup cg; coverpoint v {
    bins ev[] = {[0:7]} with (item % 2 == 0); }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 2; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c15 PASS");
    else $display("PROBE c15 FAIL");
    $finish;
  end
endmodule
