// $cast on an enum: refuses a value outside the set and says so with a
// zero return, leaving the variable as it was.
typedef enum logic [1:0] {A = 0, B = 1, C = 2} e_t;
module top;
  e_t e; int ok;
  initial begin
    e = A;
    ok = $cast(e, 2'd3);
    if (ok == 0 && e == A) $display("PROBE enum_cast PASS");
    else $display("PROBE enum_cast FAIL");
    $finish;
  end
endmodule
