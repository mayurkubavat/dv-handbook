// A static property read through the class scope operator, with no
// object in hand. The row beside this one reads the same kind of member
// through an instance; the two are separated because one tool accepts
// only the second form.
class counter;
  static int made = 0;
  function new(); made++; endfunction
endclass
module top;
  counter c;
  initial begin
    if (counter::made != 0) $display("PROBE static_scope FAIL");
    else begin
      c = new();
      if (counter::made == 1) $display("PROBE static_scope PASS");
      else $display("PROBE static_scope FAIL");
    end
    $finish;
  end
endmodule
