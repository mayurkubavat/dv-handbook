// covergroup embedded in a class, sampling a member: the class's 2-bit
// field takes 0, 1, 2; the standard gives 75.00 (c03)
class item;
  bit [1:0] v;
  covergroup cg; coverpoint v; endgroup
  function new(); cg = new; endfunction
  function void put(bit [1:0] x); v = x; cg.sample(); endfunction
endclass
module top;
  item it;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    it = new;
    it.put(0); it.put(1); it.put(2);
    $display("cov=%0.2f", it.cg.get_inst_coverage());
    if (near(it.cg.get_inst_coverage(), 75.0)) $display("PROBE c03 PASS");
    else $display("PROBE c03 FAIL");
    $finish;
  end
endmodule
