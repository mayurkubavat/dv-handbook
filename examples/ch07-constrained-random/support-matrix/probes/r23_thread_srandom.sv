// thread stability: two forked processes each seed their own RNG with
// process::self().srandom(7) and draw the same $urandom sequence
module top; bit [31:0] s1[4], s2[4]; int ok;
  initial begin ok = 1;
    fork
      begin process::self().srandom(7);
        for (int i = 0; i < 4; i++) s1[i] = $urandom(); end
      begin process::self().srandom(7);
        for (int i = 0; i < 4; i++) s2[i] = $urandom(); end
    join
    for (int i = 0; i < 4; i++) if (s1[i] != s2[i]) ok = 0;
    $display("s1[0]=%0d s2[0]=%0d", s1[0], s2[0]);
    if (ok) $display("PROBE r23 PASS"); else $display("PROBE r23 FAIL");
    $finish; end
endmodule
