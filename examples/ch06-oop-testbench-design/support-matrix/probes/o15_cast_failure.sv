// $cast down the hierarchy when the object is a sibling type: the function
// form returns 0 and leaves the target null, with no runtime error
class base; endclass
class d1 extends base; endclass
class d2 extends base; endclass
module top; base b; d1 x; d2 y; int ok;
  initial begin x = new; b = x; ok = $cast(y, b);
    $display("ok=%0d y_null=%0d", ok, (y == null));
    if (ok == 0 && y == null) $display("PROBE o15 PASS");
    else $display("PROBE o15 FAIL"); $finish; end
endmodule
