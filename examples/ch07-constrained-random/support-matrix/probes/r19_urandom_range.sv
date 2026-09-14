// $urandom_range(5,10) stays inclusive in range, reversed arguments too,
// and $urandom varies; no class, no solver
module top; int ok, same; bit [31:0] u0, u;
  initial begin ok = 1; same = 0;
    for (int i = 0; i < 50; i++) begin
      u = $urandom_range(5, 10); if (u < 5 || u > 10) ok = 0;
      u = $urandom_range(10, 5); if (u < 5 || u > 10) ok = 0;
      u = $urandom(); if (i == 0) u0 = u; else if (u == u0) same++; end
    $display("same=%0d", same);
    if (ok && same < 40) $display("PROBE r19 PASS");
    else $display("PROBE r19 FAIL"); $finish; end
endmodule
