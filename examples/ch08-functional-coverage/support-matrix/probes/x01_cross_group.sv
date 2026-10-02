// cross with auto cross bins, judged through the group: ca and cb (two
// bins each) and their cross of four; samples (0,0) and (1,1) give
// 100, 100 and 50, whose average is 83.33 (a tool that divides total
// bins hit by total bins, 6/8, prints 75.00) (x01)
module top;
  bit a, b;
  covergroup cg; ca: coverpoint a; cb: coverpoint b; ab: cross ca, cb;
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample(); a = 1; b = 1; g.sample();
    $display("group=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 83.33)) $display("PROBE x01 PASS");
    else $display("PROBE x01 FAIL");
    $finish;
  end
endmodule
