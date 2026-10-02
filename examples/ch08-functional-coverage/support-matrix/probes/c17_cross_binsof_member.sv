// cross with binsof ... intersect user bins, read as a member: the two
// user bins split the cross by a; samples (0,0) and (0,1) hit a0 and not
// a1; the standard gives 50.00 for the cross (c17)
module top;
  bit a, b;
  covergroup cg; coverpoint a; coverpoint b;
    ab: cross a, b {
      bins a0 = binsof(a) intersect {0};
      bins a1 = binsof(a) intersect {1}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample(); a = 0; b = 1; g.sample();
    $display("cross=%0.2f", g.ab.get_inst_coverage());
    if (near(g.ab.get_inst_coverage(), 50.0)) $display("PROBE c17 PASS");
    else $display("PROBE c17 FAIL");
    $finish;
  end
endmodule
