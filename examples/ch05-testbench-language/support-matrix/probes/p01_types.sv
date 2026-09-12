// 2-state vs 4-state types
module top;
  logic [7:0] l;  bit [7:0] b;  int i = 0;  integer j = 0;  byte s;
  initial begin
    $display("logic init=%b bit init=%b int=%0d integer=%b", l, b, i, j);
    l = 8'bx; b = l;
    $display("logic=x -> bit=%b isunknown(l)=%0d isunknown(b)=%0d", b, $isunknown(l), $isunknown(b));
    s = 8'd200;  $display("byte 200 -> %0d (signed)", s);
    if (l === 8'bxxxxxxxx && b === 8'b0) $display("PROBE p01 PASS");
    else $display("PROBE p01 FAIL");
    $finish;
  end
endmodule
