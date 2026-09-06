// counter_if.sv -- the interface the UVM test uses to reach the pins.
interface counter_if (input logic clk);
  logic       rst_n;
  logic       en;
  logic [7:0] count;
endinterface
