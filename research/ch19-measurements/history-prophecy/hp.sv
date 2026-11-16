// hp.sv -- a history variable and a prophecy variable.
//
// grant_unit holds a request until go, and grants it in that cycle.
// BUG = 1 also grants on go with nothing pending. hist_top adds the history
// variable `seen`: a request has arrived since the last grant. SVA
// has no operator for "at some earlier cycle", so this bit is how
// the property gets to name the unbounded past.
module grant_unit #(parameter bit BUG = 0) (
  input  logic clk, rst_n, req, go,
  output logic gnt
);
  logic pend;
  assign gnt = go && (pend || BUG);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) pend <= 1'b0;
    else        pend <= gnt ? req : (pend || req);
endmodule

module hist_top #(parameter bit BUG = 0) (
  input  logic clk, rst_n, req, go,
  output logic gnt
);
  grant_unit #(.BUG(BUG)) u (.*);
  logic seen;                       // history variable
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) seen <= 1'b0;
    else        seen <= gnt ? req : (seen || req);
endmodule

// proph_top: the k-th word out of the book's FIFO against the k-th
// word in. k is a free input held constant by the script. pv is a
// prophecy: a free, constant guess of the word the k-th pop will
// return, which an assumption checks when that pop happens. hv is
// the history version of the same thing: the k-th pushed word,
// recorded when it is pushed.
module proph_top #(parameter int DEPTH = 4) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data, pv,
  input  logic [3:0] k,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic [4:0] n_in, n_out;
  logic [7:0] hv;
  wire push_k = u.do_write && n_in  == {1'b0, k};
  wire pop_k  = u.do_read  && n_out == {1'b0, k};
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      n_in <= '0; n_out <= '0;
    end else begin
      if (u.do_write && n_in  != 5'd31) n_in  <= n_in  + 5'd1;
      if (u.do_read  && n_out != 5'd31) n_out <= n_out + 5'd1;
    end
  always_ff @(posedge clk)
    if (push_k) hv <= wr_data;
endmodule
