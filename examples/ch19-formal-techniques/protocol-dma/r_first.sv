// r_first.sv -- ghost state for a property of the DMA that holds only
// if the slave keeps its rules: the read response the DMA accepts is
// the one the slave offered first. When RVALID is high and the DMA is
// not ready, the offered response is captured; the property compares
// it with what the DMA takes on the handshake. Bound into dma_v2; it
// reads the design and drives nothing.
module r_first (
  input logic        clk, rst_n, rvalid, rready,
  input logic [33:0] rword
);
  logic        wait_q;               // a response is waiting
  logic [33:0] first_q;              // the response first offered
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n)                     wait_q <= 1'b0;
    else if (rvalid && rready)      wait_q <= 1'b0;
    else if (rvalid && !wait_q)     wait_q <= 1'b1;
  always_ff @(posedge clk)
    if (rvalid && !rready && !wait_q) first_q <= rword;
endmodule

bind dma_v2 r_first u_rf (.clk(PCLK), .rst_n(PRESETn), .rvalid(RVALID),
                          .rready(RREADY), .rword({RRESP, RDATA}));
