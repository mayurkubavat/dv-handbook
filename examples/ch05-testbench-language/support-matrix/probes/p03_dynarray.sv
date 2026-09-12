// dynamic arrays
module top;
  int d[];  int e[];
  initial begin
    d = new[4];
    foreach (d[k]) d[k] = k*k;
    e = new[6](d);                  // resize, copying old contents
    $display("d.size=%0d e.size=%0d e[3]=%0d e[5]=%0d", d.size(), e.size(), e[3], e[5]);
    d.delete();
    if (d.size() == 0 && e.size() == 6 && e[3] == 9) $display("PROBE p03 PASS");
    else $display("PROBE p03 FAIL");
    $finish;
  end
endmodule
