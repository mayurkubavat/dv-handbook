// virtual interface handle held by a class
interface bus_if(input logic clk);
  logic       valid;
  logic [7:0] data;
  logic       ready;
endinterface

class driver;
  virtual bus_if vif;
  function new(virtual bus_if v); vif = v; endfunction
  task send(logic [7:0] d);
    @(posedge vif.clk); vif.valid <= 1; vif.data <= d;
    @(posedge vif.clk); vif.valid <= 0;
  endtask
endclass

module top;
  logic clk = 0;
  always #5 clk <= ~clk;
  bus_if b(clk);
  always_ff @(posedge clk) b.ready <= b.valid;
  driver drv;
  initial begin
    b.valid = 0; b.data = 0;
    drv = new(b);
    drv.send(8'hC3);
    @(posedge clk);
    $display("ready=%0d data=%h", b.ready, b.data);
    if (b.data == 8'hC3) $display("PROBE p11 PASS");
    else $display("PROBE p11 FAIL");
    $finish;
  end
endmodule
