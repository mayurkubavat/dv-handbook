// covergroup sampled by a clocking event @(posedge clk): a 2-bit auto-bin
// coverpoint sees 0, 1, 2 on three edges; the standard gives 75.00 (c01)
module top;
  bit clk; bit [1:0] v;
  covergroup cg @(posedge clk); coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    for (int i = 0; i < 3; i++) begin
      v = i[1:0]; #1 clk = 1; #1 clk = 0;
    end
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 75.0)) $display("PROBE c01 PASS");
    else $display("PROBE c01 FAIL");
    $finish;
  end
endmodule
