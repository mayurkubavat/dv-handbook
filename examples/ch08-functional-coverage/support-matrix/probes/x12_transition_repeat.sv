// transition repetition (0 [*2]) beside (1 => 2): the sequence 0, 0, 1
// hits the repetition and not the second bin; the standard gives 50.00
// (x12)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v {
    bins rep = (0 [*2]); bins t = (1 => 2); }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); g.sample(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE x12 PASS");
    else $display("PROBE x12 FAIL");
    $finish;
  end
endmodule
