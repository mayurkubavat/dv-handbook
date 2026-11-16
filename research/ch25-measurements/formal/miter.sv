// miter.sv -- the repaired FIFO (module fifo) beside one mutant
// (module fifo_m), the same inputs into both. The script asserts that
// the two agree at the ports: full and empty always, rd_data whenever
// the original is not empty. rd_data of an empty FIFO is left out
// because the contract gives it no meaning and the memory is not
// reset, so two copies may hold different words there from the start.
// What is compared is the definition of "equivalent" this check uses.
module miter (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       wr_en,
  input  logic       rd_en,
  input  logic [7:0] wr_data,
  output logic [7:0] rd_a,
  output logic [7:0] rd_b,
  output logic       full_a,
  output logic       full_b,
  output logic       empty_a,
  output logic       empty_b
);
  fifo   a (.clk, .rst_n, .wr_en, .wr_data, .rd_en, .rd_data (rd_a),
            .full (full_a), .empty (empty_a));
  fifo_m b (.clk, .rst_n, .wr_en, .wr_data, .rd_en, .rd_data (rd_b),
            .full (full_b), .empty (empty_b));
endmodule
