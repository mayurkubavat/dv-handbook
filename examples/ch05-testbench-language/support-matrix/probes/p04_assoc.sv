// associative arrays, int and string keys
module top;
  int    by_addr [int];
  int    by_name [string];
  int    k; string s; int n;
  initial begin
    by_addr[32'h1000] = 1; by_addr[32'h2000] = 2; by_addr[5] = 3;
    by_name["alpha"] = 10; by_name["beta"] = 20;
    $display("num=%0d exists(5)=%0d exists(6)=%0d", by_addr.num(), by_addr.exists(5), by_addr.exists(6));
    n = 0;
    if (by_addr.first(k) != 0) do begin $display("  key %0d -> %0d", k, by_addr[k]); n++; end while (by_addr.next(k) != 0);
    if (by_name.first(s) != 0) do begin $display("  key %s -> %0d", s, by_name[s]); end while (by_name.next(s) != 0);
    by_addr.delete(5);
    if (n == 3 && by_addr.num() == 2 && by_name["beta"] == 20) $display("PROBE p04 PASS");
    else $display("PROBE p04 FAIL");
    $finish;
  end
endmodule
