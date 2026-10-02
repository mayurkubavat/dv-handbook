// ignore_bins on a cross via binsof, read as a member: ignoring every
// tuple with a == 1 leaves two cross bins; one sample (0,0) hits one;
// the standard gives 50.00 for the cross (c18)
module top;
  bit a, b;
  covergroup cg; coverpoint a; coverpoint b;
    ab: cross a, b { ignore_bins ig = binsof(a) intersect {1}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample();
    $display("cross=%0.2f", g.ab.get_inst_coverage());
    if (near(g.ab.get_inst_coverage(), 50.0)) $display("PROBE c18 PASS");
    else $display("PROBE c18 FAIL");
    $finish;
  end
endmodule
