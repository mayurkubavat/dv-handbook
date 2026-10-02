// cross of bare variables, judged through the group: cross a, b with no
// coverpoints declared creates implicit ones of two bins each and a
// cross of four; samples (0,0) and (1,1) give 100, 100 and 50, whose
// average is 83.33 (a tool that drops the cross and its implicit
// coverpoints has an empty group and prints 100.00) (x05)
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
    $display("group=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 83.33)) $display("PROBE x05 PASS");
    else $display("PROBE x05 FAIL");
    $finish;
  end
endmodule
