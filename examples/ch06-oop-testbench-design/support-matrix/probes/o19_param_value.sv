// parameterized class with a value parameter sizing a property
class ring #(int N = 4); int data[N];
  function int depth(); return $size(data); endfunction endclass
module top; ring #(8) b8;
  initial begin b8 = new; b8.data[7] = 1;
    $display("depth=%0d", b8.depth());
    if (b8.depth() == 8 && b8.data[7] == 1) $display("PROBE o19 PASS");
    else $display("PROBE o19 FAIL"); $finish; end
endmodule
