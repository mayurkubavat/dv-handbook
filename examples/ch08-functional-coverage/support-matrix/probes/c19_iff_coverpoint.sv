// iff guard on a coverpoint: coverpoint v iff (en) on 2 bits; 0 is
// sampled with en high and 1 with en low, so one of four bins is hit;
// the standard gives 25.00 (c19)
module top;
  bit en; bit [1:0] v;
  covergroup cg; coverpoint v iff (en); endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    en = 1; v = 0; g.sample(); en = 0; v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 25.0)) $display("PROBE c19 PASS");
    else $display("PROBE c19 FAIL");
    $finish;
  end
endmodule
