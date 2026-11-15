// hs_sink.sv -- the receiving end of the valid/ready handshake. It
// copies the offered word on the first tick of an offer and answers on
// the second. That is correct only against a source that keeps the
// rules: the word copied must still be the word on offer when ready
// rises.
module hs_sink (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       valid,
  input  logic [7:0] data,
  output logic       ready,
  output logic [7:0] word
);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      ready <= 1'b0;
      word  <= '0;
    end else begin
      ready <= valid && !ready;
      if (valid && !ready) word <= data;
    end

  // The designer's property, beside the logic it describes.
  Taken_A: assert property (@(posedge clk) disable iff (!rst_n)
             ready |-> word == data);
endmodule
