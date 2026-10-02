// cross of two coverpoints, read as g.ab.get_inst_coverage(): two 1-bit
// coverpoints and their cross of four bins; samples (0,0) and (1,1) hit
// two; the standard gives 50.00 for the cross (c16)
module top;
  bit a, b;
  covergroup cg; coverpoint a; coverpoint b; ab: cross a, b; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample(); a = 1; b = 1; g.sample();
    $display("cross=%0.2f", g.ab.get_inst_coverage());
    if (near(g.ab.get_inst_coverage(), 50.0)) $display("PROBE c16 PASS");
    else $display("PROBE c16 FAIL");
    $finish;
  end
endmodule
