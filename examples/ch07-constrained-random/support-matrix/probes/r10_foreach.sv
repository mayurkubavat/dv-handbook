// foreach constraint over a fixed array: element i equals 3*i + 1
class pkt; rand bit [7:0] arr[4];
  constraint c { foreach (arr[i]) arr[i] == 3 * i + 1; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int n = 0; n < 5; n++) begin
      if (p.randomize() != 1) ok = 0;
      foreach (p.arr[i]) if (p.arr[i] != 3 * i + 1) ok = 0; end
    $display("arr=%0d %0d %0d %0d", p.arr[0], p.arr[1], p.arr[2], p.arr[3]);
    if (ok) $display("PROBE r10 PASS"); else $display("PROBE r10 FAIL");
    $finish; end
endmodule
