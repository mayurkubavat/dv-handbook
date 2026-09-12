// $cast down the hierarchy when the object really is the derived type:
// returns 1 and the derived handle sees the derived property
class base; endclass
class derived extends base; int extra = 9; endclass
module top; base b; derived d, back; int ok;
  initial begin d = new; b = d; ok = $cast(back, b);
    $display("ok=%0d extra=%0d", ok, (back != null) ? back.extra : -1);
    if (ok == 1 && back != null && back.extra == 9) $display("PROBE o14 PASS");
    else $display("PROBE o14 FAIL"); $finish; end
endmodule
