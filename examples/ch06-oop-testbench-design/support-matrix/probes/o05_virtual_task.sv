// virtual task through a base handle, with an output argument
class base; virtual task t(output int r); r = 1; endtask endclass
class derived extends base; virtual task t(output int r); r = 2; endtask endclass
module top; base b; derived d; int r1, r2;
  initial begin d = new; b = d; b.t(r1); d.t(r2);
    $display("via_base=%0d via_derived=%0d", r1, r2);
    if (r1 == 2 && r2 == 2) $display("PROBE o05 PASS");
    else $display("PROBE o05 FAIL"); $finish; end
endmodule
