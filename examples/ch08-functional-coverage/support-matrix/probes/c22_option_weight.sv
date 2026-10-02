// option.weight on coverpoints: a (weight 3) hits one of two bins, b
// (weight 1) hits both; the weighted average (3*50 + 1*100)/4 is 62.50
// (a tool that ignores the weights prints 75.00) (c22)
module top;
  bit a, b;
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
    a = 0; b = 0; g.sample(); a = 0; b = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 62.5)) $display("PROBE c22 PASS");
    else $display("PROBE c22 FAIL");
    $finish;
  end
endmodule
