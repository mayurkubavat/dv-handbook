module bigmem #(parameter int AW = 13) (input logic clk, input logic we, input logic [AW-1:0] wa, ra,
              input logic [7:0] wd, output logic [7:0] rd);
  logic [7:0] mem [2**AW];
  always_ff @(posedge clk) begin if (we) mem[wa] <= wd; rd <= mem[ra]; end
endmodule
