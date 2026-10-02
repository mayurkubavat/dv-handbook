// cross of bare variables, read as a member: cross a, b with no
// coverpoints declared creates implicit ones; samples (0,0) and (1,1)
// hit two of four cross bins; the standard gives 50.00 for the cross
// (c32)
module top;
  bit a, b;
  covergroup cg; ab: cross a, b; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample(); a = 1; b = 1; g.sample();
    $display("cross=%0.2f", g.ab.get_inst_coverage());
    if (near(g.ab.get_inst_coverage(), 50.0)) $display("PROBE c32 PASS");
    else $display("PROBE c32 FAIL");
    $finish;
  end
endmodule
