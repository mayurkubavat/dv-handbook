// option.weight re-stated on two 2-bit coverpoints: a (weight 3) hits two
// bins of four and b (weight 1) hits all four; the weighted average
// (3*50 + 1*100)/4 is 62.50 (a tool that ignores the weights and divides
// 6 bins hit by 8 prints 75.00) (x13)
module top;
  bit [1:0] a, b;
  covergroup cg;
    coverpoint a { option.weight = 3; }
    coverpoint b { option.weight = 1; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample(); a = 1; b = 1; g.sample();
    a = 0; b = 2; g.sample(); a = 1; b = 3; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 62.5)) $display("PROBE x13 PASS");
    else $display("PROBE x13 FAIL");
    $finish;
  end
endmodule
