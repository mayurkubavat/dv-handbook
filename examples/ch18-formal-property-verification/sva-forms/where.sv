// where.sv -- the places a property can be written, one small top
// module for each place and each truth value. The counter stops at 9,
// so "q <= 9" holds and "q <= 8" does not.
module cnt (
  input  logic       clk,
  input  logic       rst,
  input  logic       en,
  output logic [3:0] q
);
  always_ff @(posedge clk)
    if (rst)                q <= '0;
    else if (en && q != 4'd9) q <= q + 4'd1;
endmodule

// A labeled concurrent assertion in the module itself.
module in_module_t (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  Bound_A: assert property (@(posedge clk) disable iff (rst) q <= 4'd9);
endmodule
module in_module_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  Bound_A: assert property (@(posedge clk) disable iff (rst) q <= 4'd8);
endmodule

// The same without a label.
module no_label_t (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  assert property (@(posedge clk) disable iff (rst) q <= 4'd9);
endmodule
module no_label_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  assert property (@(posedge clk) disable iff (rst) q <= 4'd8);
endmodule

// A checker module, attached with bind.
module chk #(parameter logic [3:0] TOP = 4'd9) (
  input logic clk, rst, input logic [3:0] q);
  Bound_A: assert property (@(posedge clk) disable iff (rst) q <= TOP);
endmodule
module bound_t (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
endmodule
module bound_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
endmodule
bind bound_t chk #(.TOP(4'd9)) u_chk (.clk, .rst, .q);
bind bound_f chk #(.TOP(4'd8)) u_chk (.clk, .rst, .q);

// default clocking and default disable iff, then a bare property.
module defaults_t (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  default clocking cb @(posedge clk); endclocking
  default disable iff (rst);
  Bound_A: assert property (q <= 4'd9);
endmodule
module defaults_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  default clocking cb @(posedge clk); endclocking
  default disable iff (rst);
  Bound_A: assert property (q <= 4'd8);
endmodule

// A concurrent assertion under an if in a clocked block.
module under_if_t (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  always_ff @(posedge clk)
    if (!rst) Bound_A: assert property (q <= 4'd9);
endmodule
module under_if_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  always_ff @(posedge clk)
    if (!rst) Bound_A: assert property (q <= 4'd8);
endmodule

// Immediate and deferred assertions, each false: a tool that reads
// them reports a counterexample.
module immediate_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  always_ff @(posedge clk)
    if (!rst) Bound_A: assert (q <= 4'd8);
endmodule
module immediate_comb_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  always_comb Bound_A: assert (rst || q <= 4'd8);
endmodule
module deferred_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  always_comb Bound_A: assert #0 (rst || q <= 4'd8);
endmodule
module final_f (input logic clk, rst, en, output logic [3:0] q);
  cnt u (.*);
  always_comb Bound_A: assert final (rst || q <= 4'd8);
endmodule
