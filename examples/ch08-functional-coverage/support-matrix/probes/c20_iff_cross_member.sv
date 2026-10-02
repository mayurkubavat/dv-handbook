// iff guard on a cross, read as a member: cross a, b iff (en); (0,0) is
// sampled with en high and (1,1) with en low, so one of four cross bins
// is hit; the standard gives 25.00 for the cross (c20)
module top;
  bit en, a, b;
  covergroup cg; coverpoint a; coverpoint b; ab: cross a, b iff (en);
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    en = 1; a = 0; b = 0; g.sample(); en = 0; a = 1; b = 1; g.sample();
    $display("cross=%0.2f", g.ab.get_inst_coverage());
    if (near(g.ab.get_inst_coverage(), 25.0)) $display("PROBE c20 PASS");
    else $display("PROBE c20 FAIL");
    $finish;
  end
endmodule
