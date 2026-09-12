// parameterized class: type and value parameters
class fifo #(type T = int, int DEPTH = 4);
  T q[$];
  function bit push(T v);
    if (q.size() >= DEPTH) return 0;
    q.push_back(v); return 1;
  endfunction
  function T pop(); return q.pop_front(); endfunction
  function int size(); return q.size(); endfunction
endclass

module top;
  fifo #(.T(logic [7:0]), .DEPTH(2)) f8;
  fifo #(string) fs;
  bit ok; logic [7:0] v; string s;
  initial begin
    f8 = new(); fs = new();
    ok = f8.push(8'hA1); ok = f8.push(8'hB2); ok = f8.push(8'hC3);  // third refused
    v = f8.pop();
    void'(fs.push("x")); s = fs.pop();
    $display("ok=%0d size=%0d v=%h s=%s", ok, f8.size(), v, s);
    if (ok == 0 && f8.size() == 1 && v == 8'hA1 && s == "x") $display("PROBE p14 PASS");
    else $display("PROBE p14 FAIL");
    $finish;
  end
endmodule
