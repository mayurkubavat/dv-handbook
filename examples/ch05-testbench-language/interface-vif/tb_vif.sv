// tb_vif.sv -- a class holding the interface through a virtual interface.
//
// A virtual interface is a variable whose value is a handle to an interface
// instance. Like any variable it starts null, and using it then is the
// single cause of every virtual-interface failure a testbench has. So the
// driver checks before it drives, and the testbench shows both outcomes:
// once before the handle is set, once after.
class driver;
  virtual bus_if.tb vif;
  task send(logic [7:0] d);
    if (vif == null) begin
      $display("driver: vif is null, nothing to drive");
      return;
    end
    @(posedge vif.clk);
    vif.valid <= 1; vif.data <= d;
    @(posedge vif.clk);
    while (!vif.ready) @(posedge vif.clk);
    vif.valid <= 0;
  endtask
endclass

module tb_vif;
  logic clk = 0;
  logic [7:0] taken;
  bus_if bus (.clk);
  sink   u   (.bus(bus.dut), .taken);
  driver drv = new;
  always #5 clk <= ~clk;
  initial begin
    bus.valid = 0; bus.data = 0;
    drv.send(8'h01);              // before the handle is set
    drv.vif = bus;                // the handle now names the instance
    drv.send(8'h02);
    drv.send(8'h03);
    repeat (2) @(posedge clk);
    $display("sink took %0d words", taken);
    $finish;
  end
endmodule
