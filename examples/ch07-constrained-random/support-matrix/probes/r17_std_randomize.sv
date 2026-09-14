// std::randomize(v) on a module variable: returns 1 and v changes
module top; bit [15:0] v; int ok, same; bit [15:0] v0;
  initial begin ok = 1; same = 0; v = 0;
    for (int i = 0; i < 8; i++) begin
      if (std::randomize(v) != 1) ok = 0;
      if (i == 0) v0 = v; else if (v == v0) same++; end
    $display("v=%0d same=%0d", v, same);
    if (ok && same < 7) $display("PROBE r17 PASS");
    else $display("PROBE r17 FAIL"); $finish; end
endmodule
