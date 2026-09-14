// std::randomize(v) with an inline constraint: v stays below 10
module top; bit [15:0] v; int ok;
  initial begin ok = 1;
    for (int i = 0; i < 20; i++) begin
      if (std::randomize(v) with { v < 10; } != 1) ok = 0;
      if (v >= 10) ok = 0; end
    $display("v=%0d", v);
    if (ok) $display("PROBE r18 PASS"); else $display("PROBE r18 FAIL");
    $finish; end
endmodule
