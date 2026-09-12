module top; int q[$]; int x;
  initial begin q.push_back(3); q.push_back(1); q.push_front(7); x=q.pop_front();
    $display("size=%0d x=%0d q[0]=%0d q[$]=%0d", q.size(), x, q[0], q[$]);
    q.delete();
    if (x==7 && q.size()==0) $display("PROBE i05a PASS"); else $display("PROBE i05a FAIL"); $finish; end
endmodule
