module top; event done; int sum;
  initial begin sum = 0;
    fork
      begin #1 sum += 10; -> done; end
      begin @done; sum += 1; end
    join
    if (sum==11) $display("PROBE j19a PASS"); else $display("PROBE j19a FAIL"); $finish; end
endmodule
