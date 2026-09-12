module top; mailbox #(int) mb; int v;
  initial begin mb = new(); mb.put(5); mb.get(v);
    if (v==5) $display("PROBE j19b PASS"); else $display("PROBE j19b FAIL"); $finish; end
endmodule
