// bus_if.sv -- one bundle of signals, two views of it.
//
// The interface holds the wires. Each modport is a direction list: what a
// module connected through it may drive and what it may only read. The
// design sees `dut`; the testbench sees `tb`; the same wire is an input on
// one side and an output on the other.
interface bus_if (input logic clk);
  logic       valid;
  logic       ready;
  logic [7:0] data;
  modport dut (input clk, input valid, input data, output ready);
  modport tb  (input clk, output valid, output data, input ready);
endinterface
