// range-to-range transition bin ([0:1] => [2:3]) beside (3 => 0): the
// sequence 0, 2 hits the first and not the second; the standard gives
// 50.00 (c33)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins t = ([0:1] => [2:3]); bins u = (3 => 0); }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 2; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c33 PASS");
    else $display("PROBE c33 FAIL");
    $finish;
  end
endmodule
