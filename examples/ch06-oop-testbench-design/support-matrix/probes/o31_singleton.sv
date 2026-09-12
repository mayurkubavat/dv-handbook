// singleton pattern: a static handle and a static get() that builds it once
class cfg; int hits = 0; static cfg inst;
  static function cfg get(); if (inst == null) inst = new; return inst;
  endfunction endclass
module top; cfg a, b;
  initial begin a = cfg::get(); a.hits++; b = cfg::get(); b.hits++;
    $display("hits=%0d same=%0d", a.hits, (a == b));
    if (a.hits == 2 && a == b) $display("PROBE o31 PASS");
    else $display("PROBE o31 FAIL"); $finish; end
endmodule
