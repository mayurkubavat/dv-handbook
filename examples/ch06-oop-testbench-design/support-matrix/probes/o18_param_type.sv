// parameterized class with a type parameter
class box #(type T = int); T val;
  function int width(); return $bits(val); endfunction endclass
module top; box #(bit [7:0]) b8; box #(longint) b64;
  initial begin b8 = new; b64 = new; b8.val = 8'hA5; b64.val = 64'd5;
    $display("w8=%0d w64=%0d", b8.width(), b64.width());
    if (b8.width() == 8 && b64.width() == 64 && b8.val == 8'hA5)
      $display("PROBE o18 PASS"); else $display("PROBE o18 FAIL"); $finish; end
endmodule
