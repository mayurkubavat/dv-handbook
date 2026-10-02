// transition bins (0 => 1), (0 => 1 => 3) and (2 => 3): the sequence
// 0, 1, 3 hits the first two and not the third; the standard gives
// 66.67 (c10)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins t1 = (0 => 1); bins t2 = (0 => 1 => 3); bins t3 = (2 => 3); }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample(); v = 3; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 66.67)) $display("PROBE c10 PASS");
    else $display("PROBE c10 FAIL");
    $finish;
  end
endmodule
