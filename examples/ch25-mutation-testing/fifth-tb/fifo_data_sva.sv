// fifo_data_sva.sv -- the data check the temporal-properties chapter's
// checker does not make: every word popped is the oldest word pushed
// and not yet popped.
//
// A bound module that drives nothing. It reads the FIFO's ports only,
// and judges a push and a pop by the contract, as that chapter's
// checker does: a push is wr_en with !full, a pop is rd_en with
// !empty. Accepted pushes go into a queue; on every accepted pop,
// rd_data (visible before the edge) must equal the queue's head. The
// check reads no internal signal, so it judges the contract and not
// the implementation.
module fifo_data_sva #(parameter int WIDTH = 8) (
  input logic             clk,
  input logic             rst_n,
  input logic             wr_en,
  input logic             rd_en,
  input logic             full,
  input logic             empty,
  input logic [WIDTH-1:0] wr_data,
  input logic [WIDTH-1:0] rd_data
);
  logic [WIDTH-1:0] model [$];
  wire push = wr_en && !full;
  wire pop  = rd_en && !empty;

  always @(posedge clk or negedge rst_n)
    if (!rst_n) model.delete();
    else begin
      if (pop) begin
        Data_A: assert (model.size() > 0 && rd_data == model[0])
          else $error("Data_A: read %02h, expected %s", rd_data,
                      model.size() > 0 ? $sformatf("%02h", model[0])
                                       : "nothing (model empty)");
        if (model.size() > 0) void'(model.pop_front());
      end
      if (push) model.push_back(wr_data);
    end
endmodule
