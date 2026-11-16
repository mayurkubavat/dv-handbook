// vr.sv -- a valid/ready stage to check with hs_rules, from both
// sides.
//
// vr_stage: PASS = 1 wires input to output, so it keeps the rules
// only if its input keeps them; PASS = 0 is a pipeline register,
// which keeps them whatever its input does.
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

// vr_top: the stage with the checker on its output, where the stage
// is the sender, and, when ENV = 1, on its input, where it is the
// receiver. WRONG = 1 binds the output's checker with the role of the
// stage's neighbor instead, the mistake of part D.
module vr_top
  import hs_role_pkg::*;
#(parameter bit PASS = 1, parameter bit ENV = 0,
  parameter bit WRONG = 0) (
  input  logic       clk, rst_n, i_valid, o_ready,
  input  logic [7:0] i_data,
  output logic       o_valid, i_ready,
  output logic [7:0] o_data
);
  vr_stage #(.PASS(PASS)) u_stage (.*);
  hs_rules #(.ROLE(WRONG ? RECEIVER : SENDER)) u_out (
    .clk, .rst_n, .valid(o_valid), .ready(o_ready), .data(o_data));
  if (ENV) begin : g_env
    hs_rules #(.ROLE(RECEIVER)) u_in (.clk, .rst_n, .valid(i_valid),
                                        .ready(i_ready), .data(i_data));
  end
endmodule
