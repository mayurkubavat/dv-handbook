// vr.sv -- one valid/ready checker used both ways, and a stage to
// check with it.
//
// vr_rules states the two rules of a valid/ready channel (valid is
// held until ready; data is stable while it waits). ASSUME = 0 makes
// them assertions on a channel the block under proof drives;
// ASSUME = 1 makes them assumptions on a channel it receives.
module vr_rules #(parameter int W = 8, parameter bit ASSUME = 0) (
  input logic         clk, rst_n, valid, ready,
  input logic [W-1:0] data
);
  default clocking @(posedge clk); endclocking
  default disable iff (!rst_n);
  if (ASSUME) begin : g_env
    Held_M:   assume property (valid && !ready |=> valid);
    Stable_M: assume property (valid && !ready |=> $stable(data));
  end else begin : g_chk
    Held_A:   assert property (valid && !ready |=> valid);
    Stable_A: assert property (valid && !ready |=> $stable(data));
    Wait_C:   cover  property (valid && !ready ##1 ready);
  end
endmodule

// vr_stage: PASS = 1 wires input to output (it keeps the rules only
// if its input keeps them); PASS = 0 is a pipeline register, which
// keeps them whatever its input does.
module vr_stage #(parameter int W = 8, parameter bit PASS = 1) (
  input  logic         clk, rst_n,
  input  logic         i_valid, o_ready,
  input  logic [W-1:0] i_data,
  output logic         o_valid, i_ready,
  output logic [W-1:0] o_data
);
  if (PASS) begin : g_wire
    assign o_valid = i_valid;
    assign o_data  = i_data;
    assign i_ready = o_ready;
  end else begin : g_reg
    assign i_ready = !o_valid || o_ready;
    always_ff @(posedge clk or negedge rst_n)
      if (!rst_n)       o_valid <= 1'b0;
      else if (i_ready) o_valid <= i_valid;
    always_ff @(posedge clk)
      if (i_ready) o_data <= i_data;
  end
endmodule

// vr_top: the stage with the checker on its output (assertions, or
// assumptions when OUT_ASSUME = 1, which is the mistake measured in
// part F) and, when ENV = 1, on its input as assumptions.
module vr_top #(parameter bit PASS = 1, parameter bit ENV = 0,
                parameter bit OUT_ASSUME = 0) (
  input  logic       clk, rst_n, i_valid, o_ready,
  input  logic [7:0] i_data,
  output logic       o_valid, i_ready,
  output logic [7:0] o_data
);
  vr_stage #(.PASS(PASS)) u_stage (.*);
  vr_rules #(.ASSUME(OUT_ASSUME)) u_out (.clk, .rst_n, .valid(o_valid),
                                         .ready(o_ready), .data(o_data));
  if (ENV) begin : g_env
    vr_rules #(.ASSUME(1)) u_in (.clk, .rst_n, .valid(i_valid),
                                 .ready(i_ready), .data(i_data));
  end
endmodule
