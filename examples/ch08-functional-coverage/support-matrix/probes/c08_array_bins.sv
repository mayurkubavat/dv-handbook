// array bins: bins b[] = {[0:3]} is four bins, one per value; samples of
// 0 and 1 hit two of them; the standard gives 50.00 (c08)
module top;
  bit [3:0] v;
  covergroup cg; coverpoint v { bins b[] = {[0:3]}; } endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c08 PASS");
    else $display("PROBE c08 FAIL");
    $finish;
  end
endmodule
