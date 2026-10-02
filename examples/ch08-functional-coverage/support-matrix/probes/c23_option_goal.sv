// option.goal = 50 on a group whose 2-bit coverpoint sees 0 and 1: the
// goal does not change the percentage; the standard gives 50.00 (c23)
module top;
  bit [1:0] v;
  covergroup cg; option.goal = 50; coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c23 PASS");
    else $display("PROBE c23 FAIL");
    $finish;
  end
endmodule
