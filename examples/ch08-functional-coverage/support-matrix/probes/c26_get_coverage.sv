// get_coverage(), the type-level percentage over two instances: the first
// samples 0 and 1, the second samples 2, so the type has hit three of
// four bins; the standard gives 75.00 (c26). The result is assigned to
// a real before the check: on 5.052, passing get_coverage() straight into
// a user function's argument is an internal compiler fault.
module top;
  covergroup cg with function sample(bit [1:0] x); coverpoint x; endgroup
  cg g1, g2;
  real c;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g1 = new; g2 = new;
    g1.sample(0); g1.sample(1); g2.sample(2);
    c = g1.get_coverage();
    $display("cov=%0.2f", c);
    if (near(c, 75.0)) $display("PROBE c26 PASS");
    else $display("PROBE c26 FAIL");
    $finish;
  end
endmodule
