// packed union: two views of the same bits
module top;
  typedef struct packed { logic [7:0] hi; logic [7:0] lo; } halves_t;
  typedef union packed { logic [15:0] word; halves_t half; } view_t;
  view_t v;
  initial begin
    v.word = 16'hBEEF;
    $display("word=%h hi=%h lo=%h", v.word, v.half.hi, v.half.lo);
    v.half.lo = 8'h00;
    if (v.word == 16'hBE00 && v.half.hi == 8'hBE) $display("PROBE p07 PASS");
    else $display("PROBE p07 FAIL");
    $finish;
  end
endmodule
