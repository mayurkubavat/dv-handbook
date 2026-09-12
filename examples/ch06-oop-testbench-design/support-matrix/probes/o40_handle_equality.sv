// comparing two handles for identity (==, !=), and against null
class pkt; int n; endclass
module top; pkt a, b, c;
  initial begin a = new; b = a; c = new;
    $display("ab=%0d ac=%0d anull=%0d", (a == b), (a != c), (a != null));
    if (a == b && a != c && a != null) $display("PROBE o40 PASS");
    else $display("PROBE o40 FAIL"); $finish; end
endmodule
