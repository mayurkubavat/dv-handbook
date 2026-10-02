// cross of two auto-bin coverpoints, read as a member: two 2-bit
// coverpoints give a cross of 16 bins; one sample (0,0) hits one; the
// standard gives 6.25 for the cross (c31)
module top;
  bit [1:0] a, b;
  covergroup cg; coverpoint a; coverpoint b; ab: cross a, b; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample();
    $display("cross=%0.2f", g.ab.get_inst_coverage());
    if (near(g.ab.get_inst_coverage(), 6.25)) $display("PROBE c31 PASS");
    else $display("PROBE c31 FAIL");
    $finish;
  end
endmodule
