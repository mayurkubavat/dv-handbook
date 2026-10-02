// sized array bins bins b[2] = {[0:7]} after one sample: two bins of
// four values each, one sample of 0 hits the first; the standard gives
// 50.00 (a tool that makes eight bins prints 12.50) (x14)
module top;
  bit [2:0] v;
  covergroup cg; coverpoint v { bins b[2] = {[0:7]}; } endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE x14 PASS");
    else $display("PROBE x14 FAIL");
    $finish;
  end
endmodule
