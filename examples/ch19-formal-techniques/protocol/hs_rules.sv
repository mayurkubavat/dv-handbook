// hs_rules.sv -- the valid/ready rules of Chapter 9's hs_check, in one
// checker that serves both ends of a link.
//
// ROLE names the block under proof: SENDER drives valid and data,
// RECEIVER drives ready. The rules on the signals that block drives
// are asserted; the rules on the signals its neighbor drives are
// assumed. Held and Stable are rules on the sender; Answer (ready
// only in answer to valid) is a rule on the receiver, and ANSWER = 0
// leaves it out, for a protocol such as AXI where ready may come
// first. The file is new: hs_check.sv itself is not edited.
package hs_role_pkg;
  typedef enum bit {SENDER, RECEIVER} role_e;
endpackage

module hs_rules
  import hs_role_pkg::*;
#(parameter int W = 8, parameter role_e ROLE = SENDER,
  parameter bit ANSWER = 1) (
  input logic         clk, rst_n, valid, ready,
  input logic [W-1:0] data
);
  default clocking @(posedge clk); endclocking
  default disable iff (!rst_n);
  if (ROLE == SENDER) begin : g_snd       // the sender is proved
    Held_A:   assert property (valid && !ready |=> valid);
    Stable_A: assert property (valid && !ready |=> $stable(data));
    Wait_C:   cover  property (valid && !ready ##1 ready);
    if (ANSWER) begin : g_ans
      Answer_M: assume property (ready |-> valid);
    end
  end else begin : g_rcv                    // the receiver is proved
    Held_M:   assume property (valid && !ready |=> valid);
    Stable_M: assume property (valid && !ready |=> $stable(data));
    if (ANSWER) begin : g_ans
      Answer_A: assert property (ready |-> valid);
    end
  end
endmodule
