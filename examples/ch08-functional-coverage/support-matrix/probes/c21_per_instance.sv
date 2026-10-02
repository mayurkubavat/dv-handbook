// option.per_instance with two instances of one group: the first samples
// 0 (25.00), the second samples 0 and 1 (50.00); each instance reports
// its own percentage (c21)
module top;
  covergroup cg with function sample(bit [1:0] x);
    option.per_instance = 1; coverpoint x;
  endgroup
  cg g1, g2;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g1 = new; g2 = new;
    g1.sample(0); g2.sample(0); g2.sample(1);
    $display("g1=%0.2f g2=%0.2f", g1.get_inst_coverage(),
             g2.get_inst_coverage());
    if (near(g1.get_inst_coverage(), 25.0) &&
        near(g2.get_inst_coverage(), 50.0)) $display("PROBE c21 PASS");
    else $display("PROBE c21 FAIL");
    $finish;
  end
endmodule
