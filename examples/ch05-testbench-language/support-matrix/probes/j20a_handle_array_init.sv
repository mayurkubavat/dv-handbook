class item; int v; function new(int x); v = x; endfunction endclass
module top; item arr[4]; int sum;
  initial begin arr[0] = new(1); arr[1] = new(2); arr[2] = new(3); arr[3] = new(4);
    sum = arr[0].v + arr[1].v + arr[2].v + arr[3].v;
    if (sum==10) $display("PROBE j20a PASS"); else $display("PROBE j20a FAIL"); $finish; end
endmodule
