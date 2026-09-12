class counter; static int made = 0; int id;
  function new(); made++; id = made; endfunction
  static function int count(); return made; endfunction
endclass
module top; counter c1, c2; int f;
  function automatic int fact(int n); return (n <= 1) ? 1 : n * fact(n-1); endfunction
  initial begin c1 = new(); c2 = new(); f = fact(5);
    $display("made=%0d c2.id=%0d fact=%0d", c1.count(), c2.id, f);
    if (c1.count()==2 && c2.id==2 && f==120) $display("PROBE i13a PASS"); else $display("PROBE i13a FAIL"); $finish; end
endmodule
