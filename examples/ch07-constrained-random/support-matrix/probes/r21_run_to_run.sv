// Run-to-run reproducibility: prints the first values from $urandom and a
// constrained randomize(). The note compares two runs of the same binary.
class pkt; rand bit [7:0] a; constraint c { a inside {[10:200]}; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    $display("urandom %0d %0d %0d", $urandom(), $urandom(), $urandom());
    for (int i = 0; i < 3; i++) begin
      if (p.randomize() != 1) ok = 0; $display("randomize %0d", p.a); end
    if (ok) $display("PROBE r21 PASS"); else $display("PROBE r21 FAIL");
    $finish; end
endmodule
