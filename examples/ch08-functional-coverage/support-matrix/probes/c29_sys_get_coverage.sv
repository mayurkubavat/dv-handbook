// $get_coverage, the system function for the overall covergroup
// percentage: the only group's 2-bit coverpoint sees 0 and 1; the
// standard gives 50.00 (c29)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v; endgroup
  cg g;
  real c;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample();
    c = $get_coverage();
    $display("cov=%0.2f", c);
    if (near(c, 50.0)) $display("PROBE c29 PASS");
    else $display("PROBE c29 FAIL");
    $finish;
  end
endmodule
