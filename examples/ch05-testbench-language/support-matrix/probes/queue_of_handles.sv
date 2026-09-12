// A queue whose elements are class handles: the shape of a scoreboard.
class item;
  int v;
  function new(int v_); v = v_; endfunction
endclass
module top;
  item q [$];
  item h;
  int sum = 0;
  initial begin
    h = new(1); q.push_back(h);
    h = new(2); q.push_back(h);
    while (q.size() > 0) begin h = q.pop_front(); sum += h.v; end
    if (sum == 3) $display("PROBE queue_of_handles PASS");
    else $display("PROBE queue_of_handles FAIL");
    $finish;
  end
endmodule
