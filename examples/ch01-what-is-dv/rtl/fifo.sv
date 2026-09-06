// fifo.sv -- a synchronous FIFO, 16 entries of 8 bits, as its spec says.
//
// Interface contract (from the block specification):
//   * wr_en with !full  pushes wr_data; a push while full is ignored.
//   * rd_en with !empty pops rd_data;  a pop while empty is ignored.
//   * full is asserted when all DEPTH entries are occupied, and only then.
//   * empty is asserted when no entries are occupied, and only then.
//
// This design contains one deliberate bug. Chapter 1 explains where.
module fifo #(
  parameter int WIDTH = 8,
  parameter int DEPTH = 16
) (
  input  logic             clk,
  input  logic             rst_n,
  input  logic             wr_en,
  input  logic [WIDTH-1:0] wr_data,
  input  logic             rd_en,
  output logic [WIDTH-1:0] rd_data,
  output logic             full,
  output logic             empty
);
  localparam int PTR_W = $clog2(DEPTH);

  logic [WIDTH-1:0] mem [DEPTH];
  logic [PTR_W-1:0] wr_ptr, rd_ptr;
  logic [PTR_W-1:0] count;              // occupancy

  localparam logic [PTR_W-1:0] LAST = PTR_W'(DEPTH - 1);

  wire do_write = wr_en && !full;
  wire do_read  = rd_en && !empty;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count  <= '0;
    end else begin
      if (do_write) begin
        mem[wr_ptr] <= wr_data;
        wr_ptr      <= wr_ptr + 1'b1;
      end
      if (do_read) begin
        rd_ptr <= rd_ptr + 1'b1;
      end
      case ({do_write, do_read})
        2'b10:   count <= count + 1'b1;
        2'b01:   count <= count - 1'b1;
        default: count <= count;
      endcase
    end
  end

  assign rd_data = mem[rd_ptr];
  assign empty   = (count == '0);
  assign full    = (count == LAST);
endmodule
