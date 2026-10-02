// cross of two auto-bin coverpoints, judged through the group: two 2-bit
// coverpoints and a cross of 16; one sample (0,0) gives 25, 25 and 6.25,
// whose average is 18.75 (a tool that divides 3 bins hit by 24 prints
// 12.50) (x04)
module top;
  bit [1:0] a, b;
  covergroup cg; ca: coverpoint a; cb: coverpoint b; ab: cross ca, cb;
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample();
    $display("group=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 18.75)) $display("PROBE x04 PASS");
    else $display("PROBE x04 FAIL");
    $finish;
  end
endmodule
