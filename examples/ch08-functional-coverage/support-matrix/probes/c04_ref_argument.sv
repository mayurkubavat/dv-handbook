// covergroup with a ref formal argument, two instances on two variables:
// a sees 0, 1 (50.00) and b sees all four values (100.00) (c04)
module top;
  bit [1:0] a, b;
  covergroup cg(ref bit [1:0] x); coverpoint x; endgroup
  cg g1, g2;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g1 = new(a); g2 = new(b);
    a = 0; g1.sample(); a = 1; g1.sample();
    for (int i = 0; i < 4; i++) begin b = i[1:0]; g2.sample(); end
    $display("g1=%0.2f g2=%0.2f", g1.get_inst_coverage(),
             g2.get_inst_coverage());
    if (near(g1.get_inst_coverage(), 50.0) &&
        near(g2.get_inst_coverage(), 100.0)) $display("PROBE c04 PASS");
    else $display("PROBE c04 FAIL");
    $finish;
  end
endmodule
