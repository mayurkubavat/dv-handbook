// hand-rolled randomize using $urandom_range inside a class method: the
// fallback both simulators can run without any solver
class pkt; bit [7:0] a; function int my_randomize();
  a = 8'($urandom_range(10, 20)); return 1; endfunction endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int i = 0; i < 30; i++) begin
      if (p.my_randomize() != 1) ok = 0; if (p.a < 10 || p.a > 20) ok = 0;
    end
    $display("a=%0d", p.a);
    if (ok) $display("PROBE r31 PASS"); else $display("PROBE r31 FAIL");
    $finish; end
endmodule
