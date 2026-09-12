module top; string a, b, c, s; int v;
  initial begin a = "hello"; b = {a, ", ", "world"}; c = b.substr(0, 4); a = "42"; v = a.atoi(); s = $sformatf("%0d-%s", v, c);
    $display("len=%0d sub=%s atoi=%0d s=%s", b.len(), c, v, s);
    if (b.len()==12 && c=="hello" && v==42 && s=="42-hello") $display("PROBE i09c PASS"); else $display("PROBE i09c FAIL"); $finish; end
endmodule
