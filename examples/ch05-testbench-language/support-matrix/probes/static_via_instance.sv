// A static property read through an instance handle, and nothing else.
class counter;
  static int made = 0;
  function new(); made++; endfunction
endclass
module top;
  counter a, b;
  initial begin
    a = new(); b = new();
    if (a.made == 2 && b.made == 2) $display("PROBE static_instance PASS");
    else $display("PROBE static_instance FAIL");
    $finish;
  end
endmodule
