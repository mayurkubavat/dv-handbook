// $urandom(seed): seeding the calling thread twice with the same value
// replays the same five-value sequence
module top; bit [31:0] s1[5], s2[5]; int ok;
  initial begin ok = 1;
    void'($urandom(42)); for (int i = 0; i < 5; i++) s1[i] = $urandom();
    void'($urandom(42)); for (int i = 0; i < 5; i++) s2[i] = $urandom();
    for (int i = 0; i < 5; i++) if (s1[i] != s2[i]) ok = 0;
    $display("s1[0]=%0d s2[0]=%0d", s1[0], s2[0]);
    if (ok) $display("PROBE r20 PASS"); else $display("PROBE r20 FAIL");
    $finish; end
endmodule
