// the chapter's central pattern: a queue of BASE handles holding mixed
// derived objects, iterated with a virtual call
class base; virtual function int f(); return 0; endfunction endclass
class d1 extends base; virtual function int f(); return 1; endfunction endclass
class d2 extends base; virtual function int f(); return 20; endfunction endclass
module top; base q[$]; d1 x; d2 y; int sum;
  initial begin x = new; y = new; q.push_back(x); q.push_back(y);
    q.push_back(x);
    foreach (q[i]) sum += q[i].f();
    $display("sum=%0d", sum);
    if (sum == 22) $display("PROBE o29 PASS");
    else $display("PROBE o29 FAIL"); $finish; end
endmodule
