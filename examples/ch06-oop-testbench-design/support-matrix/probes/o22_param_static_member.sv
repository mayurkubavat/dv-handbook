// a static member of a parameterized class belongs to the specialization:
// counter#(1) and counter#(2) keep separate counts
class counter #(int K = 0); static int count = 0;
  function new(); count++; endfunction endclass
module top; counter #(1) a1, a2; counter #(2) b1;
  initial begin a1 = new; a2 = new; b1 = new;
    $display("c1=%0d c2=%0d", counter#(1)::count, counter#(2)::count);
    if (counter#(1)::count == 2 && counter#(2)::count == 1)
      $display("PROBE o22 PASS"); else $display("PROBE o22 FAIL"); $finish; end
endmodule
