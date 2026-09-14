// pre_randomize and post_randomize run once per call, in that order,
// and post_randomize sees the new value
class pkt; rand bit [7:0] a; int npre, npost, order_ok, seen;
  function void pre_randomize(); npre++; seen = a; endfunction
  function void post_randomize(); npost++;
    if (npre == npost) order_ok++; endfunction
endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int i = 0; i < 5; i++) if (p.randomize() != 1) ok = 0;
    $display("npre=%0d npost=%0d order_ok=%0d", p.npre, p.npost, p.order_ok);
    if (ok && p.npre == 5 && p.npost == 5 && p.order_ok == 5)
      $display("PROBE r16 PASS"); else $display("PROBE r16 FAIL");
    $finish; end
endmodule
