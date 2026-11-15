// dma_ifs.sv -- the two buses the DMA sits between, as interfaces.
//
// One APB3 port the CPU programs it through, one AXI4-Lite port it moves
// data on. The response and strobe fields are 32 bits wide here because
// version 1 declares them that way; version 2's narrower ports connect
// to the low bits. Every testbench component reaches the pins through a
// virtual handle to one of these, samples through the clocking block
// (the values a flop would capture at the edge) and drives with
// nonblocking assignments at the same edge, so no component races the
// DUT.

interface apb_if (input logic clk);
  logic        psel, penable, pwrite;
  logic [31:0] paddr, pwdata, prdata;
  logic        pready, pslverr;
  logic        irq;              // the DMA's interrupt, carried alongside
  clocking cb @(posedge clk);
    input psel, penable, pwrite, paddr, pwdata, prdata, pready, pslverr;
    input irq;
  endclocking
endinterface

interface axil_if (input logic clk);
  // Read address and read data channels
  logic [31:0] araddr;
  logic        arvalid, arready;
  logic [31:0] rdata, rresp;
  logic        rvalid, rready;
  // Write address, write data and write response channels
  logic [31:0] awaddr;
  logic        awvalid, awready;
  logic [31:0] wdata, wstrb;
  logic        wvalid, wready;
  logic [31:0] bresp;
  logic        bvalid, bready;
  clocking cb @(posedge clk);
    input araddr, arvalid, arready, rdata, rresp, rvalid, rready;
    input awaddr, awvalid, awready, wdata, wstrb, wvalid, wready;
    input bresp, bvalid, bready;
  endclocking
endinterface
