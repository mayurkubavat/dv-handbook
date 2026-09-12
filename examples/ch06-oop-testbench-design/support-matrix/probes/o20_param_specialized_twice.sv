// the same parameterized class specialized twice; both live at once and
// each keeps its own parameter
class ring #(int N = 4); int data[N];
  function int depth(); return $size(data); endfunction endclass
module top; ring #(2) b2; ring #(16) b16;
  initial begin b2 = new; b16 = new;
    $display("d2=%0d d16=%0d", b2.depth(), b16.depth());
    if (b2.depth() == 2 && b16.depth() == 16) $display("PROBE o20 PASS");
    else $display("PROBE o20 FAIL"); $finish; end
endmodule
